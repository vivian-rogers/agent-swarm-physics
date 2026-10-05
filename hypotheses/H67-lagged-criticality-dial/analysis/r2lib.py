"""H67 round-2 library (2026-10-05). New code only: h67lib.py is imported, never changed, so round 1 reproduces.

  R3  pair_rd(...)        H50's boundary RD on (message, recipient) pairs, re-implemented (H50 is never imported):
                          anchor calls within +-W, 2-s donut, local-linear limits at s = 0, minus the RD at placebo times
                          shifted by +-U(5, 30) min. Switches: trimming, bandwidth, cell-demeaned outcome, placebo on/off,
                          outcome = talk or the anchor call's read count (first stage).
      block_ols(...)      call-level OLS with optional cells and 1-h block bootstrap (rungs L7, L8).
  R4  multihop(...)       lagged in-flight design: talk_c on R^m, P, R^o at calls c..c-4 (+ exogenous items, y_{c-5}),
                          kernel increments D_k = b(R^m_{c-k}) - b(P_{c-k}), kernel delta(h), gains G_1..G_5.
  R1  chat_frame(...)     the regime-I chat clock: chat-mode receiving calls only, t_prev = previous chat call, exogenous
                          items summed since the previous chat call.
  Simulators on real call grids: simulate_kernel (multi-hop read-out kernel) and simulate_chat (chat-clock coupling,
  optional start-time error), both extending h67lib.simulate's world (OU field, day edge, optional bursts).
  Fano: phi_pred(g, sizes) is H111's formula (copied, not imported).
"""
from __future__ import annotations

import os

for _v in ("POLARS_MAX_THREADS", "OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "2")

import bisect  # noqa: E402
import heapq  # noqa: E402
import math  # noqa: E402

import numpy as np  # noqa: E402
import polars as pl  # noqa: E402

import h67lib as L  # noqa: E402

R2 = L.OUT / "round2"
KEYMUL = 1.0e9
DONUT = 2.0
K_HOPS = 5


# ============================================================================================ shared helpers
def hour_blocks(day: np.ndarray, t: np.ndarray, t0: float) -> np.ndarray:
    return day.astype(np.int64) * 1000 + ((t - t0) // 3600).astype(np.int64)


def boot_weights(nblk: int, B: int, rng):
    for _ in range(B):
        yield np.bincount(rng.integers(0, nblk, nblk), minlength=nblk).astype(float)


def pct(v):
    v = np.asarray(v, float)
    v = v[np.isfinite(v)]
    if len(v) < 10:
        return np.nan, np.nan, np.nan
    lo, hi = np.percentile(v, [2.5, 97.5])
    return float(lo), float(hi), float(v.std(ddof=1))


def cell_means(df: pl.DataFrame, y: str = "talk") -> np.ndarray:
    """Outcome demeaned within agent x day x call class (H67's cells), over the rows of df."""
    cell = df["agent"].cast(pl.Int64) * 100000 + df["day"].cast(pl.Int64) * 10 + df["cls"].cast(pl.Int64)
    return (df.select(pl.col(y).cast(pl.Float64)).with_columns(cell.alias("_c"))
            .select((pl.col(y) - pl.col(y).mean().over("_c")).alias("r"))["r"].to_numpy())


# ============================================================================================ R3: pair RD
def build_pairs(d: pl.DataFrame, msgs: pl.DataFrame, trim: bool):
    """(message, recipient) pairs by the ledger rule: recipient i != sender, i's first call with t_call > t_m is a
    valid receiving call (t_prev <= t_m) in the message's room on the same day. trim: messages inside the day's
    all-present window and read-out calls flagged trim. Returns arrays t_e, day_e, rec_e."""
    c = d.sort("agent", "t_call")
    ag = c["agent"].to_numpy().astype(np.int64)
    keys = ag * KEYMUL + c["t_call"].to_numpy()
    tp = c["t_prev"].fill_null(np.nan).to_numpy()
    rm = c["room"].fill_null(-1).to_numpy().astype(np.int64)
    dy = c["day"].to_numpy().astype(np.int64)
    tr = c["trim"].to_numpy()
    agents = np.unique(ag)
    m = msgs
    if trim:
        win = c.filter(pl.col("trim")).group_by("day").agg(pl.col("ap_lo").first(), pl.col("ap_hi").first())
        m = m.join(win, on="day").filter((pl.col("t") >= pl.col("ap_lo")) & (pl.col("t") <= pl.col("ap_hi")))
    tm = m["t"].to_numpy()
    dm = m["day"].to_numpy().astype(np.int64)
    rmm = m["room"].fill_null(-2).to_numpy().astype(np.int64)
    sm = m["agent"].fill_null(-1).to_numpy().astype(np.int64)
    T, D, R = [], [], []
    for a in agents:
        sel = sm != a
        q = a * KEYMUL + tm[sel]
        idx = np.searchsorted(keys, q, side="right")
        ok = idx < len(keys)
        idc = np.minimum(idx, len(keys) - 1)
        ok &= (ag[idc] == a) & (dy[idc] == dm[sel]) & (rm[idc] == rmm[sel]) & np.isfinite(tp[idc])
        ok &= tp[idc] <= tm[sel]
        if trim:
            ok &= tr[idc]
        T.append(tm[sel][ok])
        D.append(dm[sel][ok])
        R.append(np.full(ok.sum(), a, np.int64))
    return np.concatenate(T), np.concatenate(D), np.concatenate(R)


def _rd_rows(keys, ag, dy, first, tc, t_e, d_e, rec, W, extra_ok=None):
    lo = np.searchsorted(keys, rec * KEYMUL + t_e - W, side="left")
    hi = np.searchsorted(keys, rec * KEYMUL + t_e + W, side="left")
    cnt = hi - lo
    P = np.repeat(np.arange(len(t_e)), cnt)
    off = np.arange(cnt.sum()) - np.repeat(np.cumsum(cnt) - cnt, cnt)
    a = np.repeat(lo, cnt) + off
    s = tc[a] - t_e[P]
    ok = (ag[a] == rec[P]) & (dy[a] == d_e[P]) & (np.abs(s) >= DONUT) & ~first[a]
    if extra_ok is not None:
        ok &= extra_ok[a]
    return P[ok], a[ok], s[ok]


def _side_stats(blk_idx, nblk, s, y):
    side = (s >= 0).astype(np.int64)
    st = np.zeros((nblk, 2, 5))
    for k, v in enumerate((np.ones_like(s), s, s * s, y, s * y)):
        np.add.at(st[:, :, k], (blk_idx, side), v)
    return st


LOCAL_CONSTANT = False     # post hoc probe P1 (2026-10-05): side means instead of local-linear limits


def _ll(st):
    out = []
    for side in (0, 1):
        n, s1, s2, y1, sy = st[side]
        if LOCAL_CONSTANT:
            out.append(y1 / n if n >= 5 else np.nan)
            continue
        det = n * s2 - s1 * s1
        out.append((s2 * y1 - s1 * sy) / det if (n >= 5 and det > 0) else np.nan)
    return out[1] - out[0]


def pair_rd(d: pl.DataFrame, msgs: pl.DataFrame, W: float, trim: bool = False, demean: bool = False,
            placebo: bool = True, outcome: str = "talk", B: int = 200, seed: int = 1, n_pl: int = 2) -> dict:
    """H50's C2 gate (k = 1) on H67's tables. d: all_counts output (all receiving calls of the unit).
    demean: outcome demeaned in agent x day x call-class cells (cells computed on the anchor-eligible rows).
    outcome: 'talk' or 'R_all' (first stage: reads at the anchor call). Returns J (per pair), CI, n_pairs."""
    c = d.sort("agent", "t_call")
    if trim:
        c = c.filter(pl.col("trim"))
    ag = c["agent"].to_numpy().astype(np.int64)
    tc = c["t_call"].to_numpy()
    keys = ag * KEYMUL + tc
    dy = c["day"].to_numpy().astype(np.int64)
    first = c["first_of_day"].to_numpy().astype(bool)
    if demean:
        y = cell_means(c, outcome)
    else:
        y = c[outcome].cast(pl.Float64).to_numpy()
    t_e, d_e, rec = build_pairs(d, msgs, trim)
    if len(t_e) < 50:
        return {"ok": False, "n_pairs": int(len(t_e))}
    rng = np.random.default_rng(seed)
    t0 = float(tc.min())
    P, a, s = _rd_rows(keys, ag, dy, first, tc, t_e, d_e, rec, W)
    blk_e = hour_blocks(d_e, t_e, t0)
    ub = np.unique(blk_e)
    bi = np.searchsorted(ub, blk_e)
    nblk = len(ub)
    st = _side_stats(bi[P], nblk, s, y[a])
    sp = np.zeros_like(st)
    if placebo:
        span = c.group_by("day").agg(pl.col("t_call").min().alias("lo"), pl.col("t_call").max().alias("hi"))
        lo_d = dict(zip(span["day"].to_list(), span["lo"].to_list()))
        hi_d = dict(zip(span["day"].to_list(), span["hi"].to_list()))
        A = np.array([lo_d.get(x, np.nan) for x in d_e])
        Bh = np.array([hi_d.get(x, np.nan) for x in d_e])
        for _ in range(n_pl):
            sh = rng.uniform(300, 1800, len(t_e)) * rng.choice([-1, 1], len(t_e))
            tpl = t_e + sh
            tpl = np.where(tpl < A, 2 * A - tpl, tpl)
            tpl = np.where(tpl > Bh, 2 * Bh - tpl, tpl)
            tpl = np.clip(tpl, A, Bh)
            Pp, ap, spp = _rd_rows(keys, ag, dy, first, tc, tpl, d_e, rec, W)
            sp += _side_stats(bi[Pp], nblk, spp, y[ap])
        sp /= n_pl

    def est(w):
        R = np.tensordot(w, st, 1)
        J = _ll(R)
        if placebo:
            J -= _ll(np.tensordot(w, sp, 1))
        return J

    J = est(np.ones(nblk))
    bs = [est(w) for w in boot_weights(nblk, B, rng)]
    lo, hi, se = pct(bs)
    return {"ok": True, "J": float(J), "J_lo": lo, "J_hi": hi, "J_se": se, "n_pairs": int(len(t_e)),
            "n_rows": int(len(P)), "n_blocks": nblk}


# ============================================================================================ R3: call-level OLS
def block_ols(rows: pl.DataFrame, regs: list[str], cells: bool, B: int = 200, seed: int = 1, y: str = "talk"):
    """OLS of y on regs within cells (agent x day x class) or pooled (intercept only); 1-h block bootstrap.
    Returns (beta dict, list of bootstrap beta dicts)."""
    if cells:
        cell = rows["agent"].cast(pl.Int64) * 100000 + rows["day"].cast(pl.Int64) * 10 + rows["cls"].cast(pl.Int64)
    else:
        cell = pl.Series(np.zeros(rows.height, np.int64))
    dd = rows.select(regs + [y]).cast(pl.Float64).with_columns(cell.alias("_c"))
    dd = dd.with_columns([(pl.col(x) - pl.col(x).mean().over("_c")).alias(x) for x in regs + [y]])
    X = dd.select(regs).to_numpy()
    yy = dd[y].to_numpy()
    blk = L._blocks(rows)
    ub, inv = np.unique(blk, return_inverse=True)
    k = len(regs)
    XtX = np.zeros((len(ub), k, k))
    Xty = np.zeros((len(ub), k))
    for j in range(k):
        for l2 in range(j, k):
            v = np.bincount(inv, weights=X[:, j] * X[:, l2], minlength=len(ub))
            XtX[:, j, l2] = v
            XtX[:, l2, j] = v
        Xty[:, j] = np.bincount(inv, weights=X[:, j] * yy, minlength=len(ub))

    def sol(w):
        A = np.tensordot(w, XtX, 1) + 1e-9 * np.eye(k)
        return dict(zip(regs, L._solve(A, np.tensordot(w, Xty, 1))))

    rng = np.random.default_rng(seed)
    return sol(np.ones(len(ub))), [sol(w) for w in boot_weights(len(ub), B, rng)]


# ============================================================================================ R4: multi-hop
def _cnt_sum(t: np.ndarray, cs: np.ndarray, lo, hi, right_closed=False):
    """Count and sum of sorted times t in [lo, hi) (or (lo, hi]); cs = prefix sums of t with a leading 0."""
    side = "right" if right_closed else "left"
    a = np.searchsorted(t, lo, side)
    b = np.searchsorted(t, hi, side)
    return b - a, cs[b] - cs[a]


def hw_counts(d: pl.DataFrame, msgs: pl.DataFrame) -> pl.DataFrame:
    """Amendments B1-B2 (2026-10-05, before real data). B1: disjoint symmetric windows. Per call c, half-width
    h_c = min(latency, (t_c - t_prev)/2, (t_next - t_c)/2, 120 s); Rh_m = peer messages in (t_c - h_c, t_c) (read at
    c), Ph = peer messages in (t_c, t_c + h_c] (in flight at c, read at c+1); Rh_o = R_all - Rh_m - Ph_{c-1}
    (the remaining reads at c). Windows around adjacent call starts cannot overlap, so every message enters one
    regressor only. B2: offset sums SRh = sum over Rh_m of (t_c - t_m)/h_c and SPh = sum over Ph of (t_m - t_c)/h_c,
    so each window's effect is a + b x (x = distance from the boundary in units of h); the boundary limits a are
    compared (the regression form of a local-linear RD; it removes a field gradient across the window).
    d: output of h67lib.counts (needs R_all, t_prev, t_first, room)."""
    c = d.sort("agent", "day", "t_call").with_columns(
        pl.col("t_call").shift(-1).over(["agent", "day"]).alias("_tn"))
    lat = (c["t_first"] - c["t_call"]).to_numpy()
    tc = c["t_call"].to_numpy()
    tp = c["t_prev"].fill_null(np.nan).to_numpy()
    tn = c["_tn"].fill_null(np.inf).to_numpy()
    h = np.minimum.reduce([lat, (tc - tp) / 2, (tn - tc) / 2, np.full(len(tc), L.W_CAP)])
    ok = np.isfinite(h) & (h > 0)
    h = np.where(ok, np.maximum(h, 0.5), np.nan)
    ag = c["agent"].to_numpy()
    Rm = np.zeros(c.height)
    Ph = np.zeros(c.height)
    SR = np.zeros(c.height)
    SP = np.zeros(c.height)

    def prep(x):
        x = np.sort(x)
        return x, np.r_[0.0, np.cumsum(x)]
    groups = {}
    for (dd, r), g in msgs.select("t", "day", "room", "agent").group_by(["day", "room"]):
        groups[(dd, r)] = (prep(g["t"].to_numpy()), {a: prep(gg["t"].to_numpy()) for (a,), gg in g.group_by(["agent"])})
    keys = {}
    for i, (dd, r) in enumerate(c.select("day", "room").iter_rows()):
        keys.setdefault((dd, r), []).append(i)
    for k, idx in keys.items():
        if k not in groups:
            continue
        idx = np.asarray(idx)
        idx = idx[ok[idx]]
        if not len(idx):
            continue
        (t, cs), own = groups[k]
        n1, s1 = _cnt_sum(t, cs, tc[idx] - h[idx], tc[idx])
        n2, s2 = _cnt_sum(t, cs, tc[idx], tc[idx] + h[idx], right_closed=True)
        for a in np.unique(ag[idx]):
            sel = ag[idx] == a
            j = idx[sel]
            if a in own:
                ot, ocs = own[a]
                m1, u1 = _cnt_sum(ot, ocs, tc[j] - h[j], tc[j])
                m2, u2 = _cnt_sum(ot, ocs, tc[j], tc[j] + h[j], right_closed=True)
                n1[sel] -= m1
                s1[sel] -= u1
                n2[sel] -= m2
                s2[sel] -= u2
        Rm[idx], Ph[idx] = n1, n2
        SR[idx] = (n1 * tc[idx] - s1) / h[idx]
        SP[idx] = (s2 - n2 * tc[idx]) / h[idx]
    c = c.with_columns(pl.Series("Rh_m", Rm), pl.Series("Ph", Ph), pl.Series("SRh", SR), pl.Series("SPh", SP),
                       pl.Series("h", h)).drop("_tn")
    return c.with_columns((pl.col("R_all") - pl.col("Rh_m")
                           - pl.col("Ph").shift(1).over(["agent", "day"]).fill_null(0)).clip(0).alias("Rh_o"))


def add_lags(d: pl.DataFrame, K: int = K_HOPS) -> pl.DataFrame:
    """Per agent-day: position, Rh_m, Ph, Rh_o at calls c-k (k = 0..K-1, columns R_m_k, P_k, R_o_k) and y_{c-K}."""
    d = d.sort("agent", "day", "t_call").with_columns(pl.int_range(pl.len()).over(["agent", "day"]).alias("pos"))
    cols = [pl.col("Rh_m").alias("R_m_0"), pl.col("Ph").alias("P_0"), pl.col("Rh_o").alias("R_o_0"),
            pl.col("SRh").alias("SR_0"), pl.col("SPh").alias("SP_0")]
    for k in range(1, K):
        for v, src in (("R_m", "Rh_m"), ("P", "Ph"), ("R_o", "Rh_o"), ("SR", "SRh"), ("SP", "SPh")):
            cols.append(pl.col(src).shift(k).over(["agent", "day"]).fill_null(0).alias(f"{v}_{k}"))
    cols.append(pl.col("talk").cast(pl.Int8).shift(K).over(["agent", "day"]).fill_null(0).alias("y_lK"))
    return d.with_columns(cols)


def multihop_regs(K: int = K_HOPS, exo: bool = True, ylag: bool = True, slopes: bool = True) -> list[str]:
    r = [f"{v}_{k}" for k in range(K) for v in (("R_m", "P", "R_o", "SR", "SP") if slopes else ("R_m", "P", "R_o"))]
    if ylag:
        r.append("y_lK")
    if exo:
        r += L.EXO
    return r


def multihop(d: pl.DataFrame, msgs: pl.DataFrame, K: int = K_HOPS, B: int = 200, seed: int = 7, trim: bool = True,
             exo: bool = True, ylag: bool = True, slopes: bool = True, dl: pl.DataFrame | None = None) -> dict:
    """R4 lagged in-flight design. d: all_counts output. Returns D_k, delta(h), G_H (H = 1..K) with CIs."""
    if dl is None:
        dl = add_lags(hw_counts(d, msgs), K)
    rows = L._rows(dl, trim).filter(pl.col("pos") >= K)
    if rows.height < 500 or rows["R_all"].sum() == 0:
        return {"ok": False, "n_rows": rows.height}
    regs = [r for r in multihop_regs(K, exo, ylag, slopes) if rows[r].std() > 0]
    ub, inv, XtX, Xty, nb = L.block_stats(rows, regs)
    if len(ub) < 4:
        return {"ok": False, "n_rows": rows.height}
    reads, talks, n_all, n_call = L.scale_stats(dl, msgs, rows, inv, ub)

    def est(w):
        A = np.tensordot(w, XtX, 1) + 1e-9 * np.eye(len(regs))
        b = dict(zip(regs, L._solve(A, np.tensordot(w, Xty, 1))))
        rbar = (w @ reads) / max(w @ n_all, 1e-9)
        mbar = (w @ n_call) / max(w @ talks, 1e-9)
        Dk = np.array([b.get(f"R_m_{k}", 0.0) - b.get(f"P_{k}", 0.0) for k in range(K)])
        delta = np.cumsum(Dk)
        G = rbar * mbar * np.cumsum(delta)
        return Dk, delta, G, rbar * mbar, b

    Dk, delta, G, gm, b = est(np.ones(len(ub)))
    rng = np.random.default_rng(seed)
    bs = [est(w) for w in boot_weights(len(ub), B, rng)]
    out = {"ok": True, "n_rows": rows.height, "gmul": float(gm), "n_blocks": len(ub)}
    for k in range(K):
        out[f"D{k}"] = float(Dk[k])
        out[f"D{k}_lo"], out[f"D{k}_hi"], out[f"D{k}_se"] = pct([x[0][k] for x in bs])
        out[f"delta{k + 1}"] = float(delta[k])
        out[f"delta{k + 1}_lo"], out[f"delta{k + 1}_hi"], out[f"delta{k + 1}_se"] = pct([x[1][k] for x in bs])
        out[f"G{k + 1}"] = float(G[k])
        out[f"G{k + 1}_lo"], out[f"G{k + 1}_hi"], out[f"G{k + 1}_se"] = pct([x[2][k] for x in bs])
    out["b_y_lK"] = float(b.get("y_lK", np.nan))
    return out


# ============================================================================================ R1: chat clock
def chat_frame(calls: pl.DataFrame) -> pl.DataFrame:
    """Chat-mode receiving calls with t_prev = the previous chat-mode call of the same agent-day; exogenous items
    summed over all calls since the previous chat call (exclusive) up to this one (inclusive)."""
    c = calls.sort("agent", "day", "t_call").with_columns(
        [pl.col(e).cum_sum().over(["agent", "day"]).alias(f"_cum_{e}") for e in L.EXO])
    ch = c.filter(pl.col("is_chat") == 1).with_columns(
        pl.col("t_call").shift(1).over(["agent", "day"]).alias("t_prev"),
        *[(pl.col(f"_cum_{e}") - pl.col(f"_cum_{e}").shift(1).over(["agent", "day"]).fill_null(0)).alias(e)
          for e in L.EXO])
    # the first chat call of an agent-day has no previous chat call: invalid in counts() (t_prev null)
    return ch.drop([f"_cum_{e}" for e in L.EXO])


def chat_counts(calls: pl.DataFrame, msgs: pl.DataFrame) -> pl.DataFrame:
    return L.counts(chat_frame(calls), msgs)


# ============================================================================================ Fano (H111 formula)
def phi_pred(g: float, sizes) -> float:
    """H111's mean-field collective Fano ratio for rooms of the given sizes (copied from h111lib.phi_pred)."""
    sizes = [int(s) for s in sizes if s >= 1]
    N = sum(sizes)
    if N < 2 or not math.isfinite(g) or g >= 1:
        return float("nan")
    a = 1.0 / (1.0 - g) ** 2
    den = 0.0
    for n in sizes:
        den += a
        if n > 1:
            den += (n - 1) / (1.0 + g / (n - 1)) ** 2
    return N * a / den


def unit_phi_pred(g: float, present: pl.DataFrame) -> float:
    """Average over days (weighted by present agents) of phi_pred with that day's room sizes."""
    num = den = 0.0
    for (dd,), gdf in present.group_by(["day"]):
        sizes = gdf.group_by("room").len()["len"].to_list()
        p = phi_pred(g, sizes)
        if math.isfinite(p):
            num += p * gdf.height
            den += gdf.height
    return num / den if den else float("nan")


# ============================================================================================ simulators
def _world(c, rng, ou_tau, ou_sigma, burst):
    tc = c["t_call"].to_numpy()
    dy = c["day"].to_numpy()
    day_start = {d: tc[dy == d].min() for d in np.unique(dy)}
    day_end = {d: tc[dy == d].max() for d in np.unique(dy)}
    fields = {d: L.ou_field(day_start[d] - 60, day_end[d] + 600, ou_tau, ou_sigma, rng) for d in day_start}
    bursts = {}

    def mult(k, d, r, t, edge):
        f0, fdt, fv = fields[d]
        F = fv[min(int((t - f0) / fdt), len(fv) - 1)]
        m = F * (edge if t - day_start[d] < 1200 else 1.0)
        if burst:
            if (d, r) not in bursts:
                Ld = day_end[d] - day_start[d] + 600
                bursts[(d, r)] = np.sort(rng.uniform(day_start[d], day_end[d], rng.poisson(Ld / 1200)))
            bs = bursts[(d, r)]
            j = np.searchsorted(bs, t)
            if j > 0 and t - bs[j - 1] < 180:
                m *= 4.0
        return m
    return mult


def simulate_kernel(calls: pl.DataFrame, kernel, rng, base_scale: float = 0.7, ou_tau: float = 300.0,
                    ou_sigma: float = 0.5, burst: bool = False, edge: float = 1.5):
    """h67lib.simulate's world with a multi-hop read-out kernel: talk prob at call c += sum_h kernel[h-1] * reads
    at the same agent's call c-h+1 (same day). One message per talk call at t_first. kernel: per-read jumps J_h."""
    kernel = list(kernel)
    H = len(kernel)
    c = calls.sort("t_call")
    base = {(a, k): v for a, k, v in calls.group_by("agent", "cls").agg(pl.col("talk").mean()).iter_rows()}
    mult = _world(c, rng, ou_tau, ou_sigma, burst)
    ag, cl = c["agent"].to_numpy(), c["cls"].to_numpy()
    rm, tc = c["room"].fill_null(-1).to_numpy(), c["t_call"].to_numpy()
    tf, tp, dy = c["t_first"].to_numpy(), c["t_prev"].fill_null(np.nan).to_numpy(), c["day"].to_numpy()
    talk = np.zeros(c.height, bool)
    room_ts, room_ag, pending, hist = {}, {}, [], {}
    for k in range(c.height):
        d, r, a, t = dy[k], rm[k], ag[k], tc[k]
        while pending and pending[0][0] < t:
            tt, dd, rr, aa = heapq.heappop(pending)
            lst = room_ts.setdefault((dd, rr), [])
            pos = bisect.bisect(lst, tt)
            lst.insert(pos, tt)
            room_ag.setdefault((dd, rr), []).insert(pos, aa)
        nread = 0
        if np.isfinite(tp[k]):
            lst = room_ts.get((d, r))
            if lst:
                i0, i1 = bisect.bisect_left(lst, tp[k]), bisect.bisect_left(lst, t)
                nread = sum(1 for z in room_ag[(d, r)][i0:i1] if z != a)
        h = hist.get((a, d))
        if h is None or not np.isfinite(tp[k]):
            h = []
        h = [nread] + h[:H - 1]
        hist[(a, d)] = h
        p = base.get((a, cl[k]), 0.05) * base_scale * mult(k, d, r, t, edge)
        p += sum(kernel[j] * h[j] for j in range(len(h)))
        if rng.random() < min(p, 0.95):
            talk[k] = True
            heapq.heappush(pending, (tf[k], d, r, a))
    sim = c.with_columns(pl.Series("talk", talk))
    m = (sim.filter(pl.col("talk")).select(pl.col("t_first").alias("t"), "day", "room", "agent")
         .with_columns(pl.lit(None, dtype=pl.List(pl.Int8)).alias("mentions_roster")).sort("t"))
    return sim, m


def simulate_chat(calls: pl.DataFrame, J: float, rng, base_scale: float = 0.5, ou_tau: float = 300.0,
                  ou_sigma: float = 0.5, burst: bool = False, edge: float = 1.5, start_err: bool = False,
                  lat_med: float = 11.0, lat_sig: float = 0.5):
    """Chat-clock world (R1): talk prob at a chat-mode call += J * peer messages posted in the agent's room since its
    previous chat-mode call (all reads, whatever call read them); no coupling at computer-use calls.
    start_err: for chat calls with start_conf low, the true context time is t_first - L, L lognormal(log lat_med,
    lat_sig), clipped to (1 s, t_first - previous call start); visibility uses it, the returned frame keeps the
    recorded t_call. Messages: one per talk call at t_first."""
    c = calls.sort("t_call")
    base = {(a, k): v for a, k, v in calls.group_by("agent", "cls").agg(pl.col("talk").mean()).iter_rows()}
    mult = _world(c, rng, ou_tau, ou_sigma, burst)
    ag, cl = c["agent"].to_numpy(), c["cls"].to_numpy()
    rm, tc = c["room"].fill_null(-1).to_numpy(), c["t_call"].to_numpy()
    tf, tp, dy = c["t_first"].to_numpy(), c["t_prev"].fill_null(np.nan).to_numpy(), c["day"].to_numpy()
    isc = c["is_chat"].to_numpy() == 1
    low = (c["start_conf"].cast(pl.String) == "low").to_numpy()
    t_true = tc.copy()
    if start_err:
        Lt = np.exp(rng.normal(np.log(lat_med), lat_sig, c.height))
        cap = np.where(np.isfinite(tp), tf - tp - 0.5, np.inf)
        t_true = np.where(isc & low, tf - np.clip(Lt, 1.0, np.maximum(cap, 1.0)), tc)
    order = np.argsort(t_true, kind="stable")
    talk = np.zeros(c.height, bool)
    room_ts, room_ag, pending, last_chat = {}, {}, [], {}
    for k in order:
        d, r, a, t = dy[k], rm[k], ag[k], t_true[k]
        while pending and pending[0][0] < t:
            tt, dd, rr, aa = heapq.heappop(pending)
            lst = room_ts.setdefault((dd, rr), [])
            pos = bisect.bisect(lst, tt)
            lst.insert(pos, tt)
            room_ag.setdefault((dd, rr), []).insert(pos, aa)
        p = base.get((a, cl[k]), 0.05) * base_scale * mult(k, d, r, t, edge)
        if isc[k]:
            t0 = last_chat.get((a, d))
            if t0 is not None:
                lst = room_ts.get((d, r))
                if lst:
                    i0, i1 = bisect.bisect_left(lst, t0), bisect.bisect_left(lst, t)
                    p += J * sum(1 for z in room_ag[(d, r)][i0:i1] if z != a)
            last_chat[(a, d)] = t
        if rng.random() < min(p, 0.95):
            talk[k] = True
            heapq.heappush(pending, (tf[k], d, r, a))
    sim = c.with_columns(pl.Series("talk", talk))
    m = (sim.filter(pl.col("talk")).select(pl.col("t_first").alias("t"), "day", "room", "agent")
         .with_columns(pl.lit(None, dtype=pl.List(pl.Int8)).alias("mentions_roster")).sort("t"))
    return sim, m
