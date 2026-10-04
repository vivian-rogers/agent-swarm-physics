"""H67 library: call-clock read-out loop gain (g_lag), the matched-lag in-flight placebo, the equal-time dial on the
same data, the shift null and a simulator on real call grids. No project imports except infra/shared (nulls).

Main objects
  counts(calls, msgs)        per receiving call: R_all, R_m (read, posted within w before t_call), R_o, P (in-flight,
                             posted within w after t_call), named / unnamed splits, lagged reads, own previous talk
  design(df, variant)        rows and regressors for one model variant
  fit(df, variant, B)        within-cell (agent x day x call class) OLS; block bootstrap; J1*, g_lag and variants
  equal_time(calls)          H25's equal-time talk dial on the same trimmed windows (1-min spins, 30-min blocks)
  simulate(calls, ...)       talk on a real call grid with planted read-out coupling, shared fields, bursts, edges
"""
from __future__ import annotations

import os

for _v in ("POLARS_MAX_THREADS", "OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ.setdefault(_v, "4")

import bisect  # noqa: E402
import sys  # noqa: E402
from pathlib import Path  # noqa: E402

import numpy as np  # noqa: E402
import polars as pl  # noqa: E402

ROOT = Path(__file__).resolve().parents[3]
DM_W = [1.0, 1.0, 1.0, 1.0]
sys.path.insert(0, str(ROOT / "infra/shared"))
import nulls  # noqa: E402

OUT = ROOT / "data/processed/H67-lagged-criticality-dial"
W_CAP = 120.0      # cap on the matched window (s)
W_MIN = 1.0

EXO = ["E_h", "E_n", "E_nme"]
VARIANTS = {
    # name: (regressors, contrasts) ; contrast = list of (coef, weight)
    "main": ["R_m", "R_o", "P", "R_l1", "R_l2", "y_l1"] + EXO,
    "noexo": ["R_m", "R_o", "P", "R_l1", "R_l2", "y_l1"],
    "all": ["R_all", "P", "R_l1", "R_l2", "y_l1"] + EXO,
    "named": ["R_m_n", "R_m_u", "R_o", "P_n", "P_u", "R_l1", "R_l2", "y_l1"] + EXO,
    "naive": ["R_all"],
    # decision-time matched design (Amendment A1): per delta-bin hop-1 reads (h1_b) and unread-at-c (u_b) counts
    "dm": ["h1_0", "h1_1", "h1_2", "h1_3", "u_0", "u_1", "u_2", "u_3", "e_all", "R_o_dm", "R_l1", "R_l2", "y_l1"] + EXO,
    "dm_noexo": ["h1_0", "h1_1", "h1_2", "h1_3", "u_0", "u_1", "u_2", "u_3", "e_all", "R_o_dm", "R_l1", "R_l2",
                 "y_l1"],
    "dm_named": ["h1u_0", "h1u_1", "h1u_2", "h1u_3", "uu_0", "uu_1", "uu_2", "uu_3", "h1_n", "u_n", "e_all",
                 "R_o_dm", "R_l1", "R_l2", "y_l1"] + EXO,
}
DM_EDGES = np.array([0.0, 15.0, 30.0, 60.0, 120.0])     # decision-time lag bins (s) before the recipient's call start


# ============================================================================================ counting
def _count(sorted_t: np.ndarray, lo: np.ndarray, hi: np.ndarray, right_closed=False) -> np.ndarray:
    """Number of times in [lo, hi) (or (lo, hi] when right_closed)."""
    if right_closed:
        return np.searchsorted(sorted_t, hi, "right") - np.searchsorted(sorted_t, lo, "right")
    return np.searchsorted(sorted_t, hi, "left") - np.searchsorted(sorted_t, lo, "left")


def counts(calls: pl.DataFrame, msgs: pl.DataFrame) -> pl.DataFrame:
    """Per-call read counts. calls: agent, day, room, t_prev, t_call, t_first, talk (+ anything). msgs: t, day, room,
    agent (sender), mentions_roster (list of agent codes)."""
    c = calls.sort("agent", "day", "t_call").with_row_index("_r")
    w = np.minimum(np.minimum((c["t_first"] - c["t_call"]).to_numpy(), (c["t_call"] - c["t_prev"]).fill_null(np.inf)
                              .to_numpy()), W_CAP)
    w = np.where(np.isfinite(w), np.maximum(w, W_MIN), np.nan)
    n = c.height
    out = {k: np.zeros(n, np.int32) for k in ("R_all", "R_m", "P", "R_m_n", "P_n", "R_all_n")}
    tc = c["t_call"].to_numpy()
    tp = c["t_prev"].fill_null(np.nan).to_numpy()
    ag = c["agent"].to_numpy()
    valid = np.isfinite(tp) & np.isfinite(w)
    # group messages by (day, room) and by (day, room, sender); named by (day, room, recipient)
    m = msgs.select("t", "day", "room", "agent", "mentions_roster")
    groups = {}
    for (d, r), g in m.group_by(["day", "room"]):
        t = np.sort(g["t"].to_numpy())
        own = {a: np.sort(gg["t"].to_numpy()) for (a,), gg in g.group_by(["agent"])}
        nm = (g.explode("mentions_roster").drop_nulls("mentions_roster")
              .filter(pl.col("mentions_roster") != pl.col("agent")))
        named = {a: np.sort(gg["t"].to_numpy()) for (a,), gg in nm.group_by(["mentions_roster"])}
        groups[(d, r)] = (t, own, named)
    cd = c.select("day", "room").to_numpy()
    keys = {}
    for i, (d, r) in enumerate(map(tuple, cd)):
        keys.setdefault((d, r), []).append(i)
    empty = np.zeros(0)
    for k, idx in keys.items():
        if k not in groups:
            continue
        idx = np.asarray(idx)
        idx = idx[valid[idx]]
        if not len(idx):
            continue
        t, own, named = groups[k]
        lo, hi, ww = tp[idx], tc[idx], w[idx]
        out["R_all"][idx] = _count(t, lo, hi)
        out["R_m"][idx] = _count(t, hi - ww, hi)
        out["P"][idx] = _count(t, hi, hi + ww, right_closed=True)
        # own messages and named messages per recipient agent
        for a in np.unique(ag[idx]):
            j = idx[ag[idx] == a]
            ot = own.get(a, empty)
            if len(ot):
                lo_j, hi_j, w_j = tp[j], tc[j], w[j]
                out["R_all"][j] -= _count(ot, lo_j, hi_j)
                out["R_m"][j] -= _count(ot, hi_j - w_j, hi_j)
                out["P"][j] -= _count(ot, hi_j, hi_j + w_j, right_closed=True)
            nt = named.get(a, empty)
            if len(nt):
                out["R_all_n"][j] = _count(nt, tp[j], tc[j])
                out["R_m_n"][j] = _count(nt, tc[j] - w[j], tc[j])
                out["P_n"][j] = _count(nt, tc[j], tc[j] + w[j], right_closed=True)
    res = c.with_columns([pl.Series(k, v) for k, v in out.items()]).with_columns(
        pl.Series("w", w), pl.Series("valid", valid))
    res = res.with_columns(
        (pl.col("R_all") - pl.col("R_m")).alias("R_o"),
        (pl.col("R_m") - pl.col("R_m_n")).alias("R_m_u"),
        (pl.col("P") - pl.col("P_n")).alias("P_u"),
        pl.col("R_all").shift(1).over(["agent", "day"]).fill_null(0).alias("R_l1"),
        pl.col("R_all").shift(2).over(["agent", "day"]).fill_null(0).alias("R_l2"),
        pl.col("talk").cast(pl.Int8).shift(1).over(["agent", "day"]).fill_null(0).alias("y_l1"),
    )
    return res.drop("_r")


def decision_times(msgs: pl.DataFrame, calls: pl.DataFrame) -> pl.DataFrame:
    """Attach s = t_call of the sender's latest call at or before the message (its decision time); null when the
    sender makes no calls in the unit (the Claude Code agent)."""
    if "s" in msgs.columns:
        return msgs
    cc = calls.select(pl.col("agent"), pl.col("t_call").alias("s"), pl.col("t_call").alias("_k")).sort("_k")
    m = msgs.with_row_index("_i").sort("t")
    m = m.join_asof(cc, left_on="t", right_on="_k", by="agent", strategy="backward").drop("_k")
    return m.sort("_i").drop("_i")


def dm_counts(d: pl.DataFrame, msgs: pl.DataFrame) -> pl.DataFrame:
    """Decision-time matched counts (Amendment A1). For call c of agent i at t_c and peer messages m in i's room with
    decision time s_m in (t_c - 120 s, t_c): status hop-1 read (t_prev <= p_m < t_c), earlier read (p_m < t_prev) or
    unread at c (p_m >= t_c), binned by delta = t_c - s_m (DM_EDGES). Unread messages were decided before c's own
    decision, so they cannot be replies to c, and within a delta bin they share the read messages' exposure to any
    common field. Named = the message names i (mentions_roster)."""
    msgs = decision_times(msgs, d)
    nb = len(DM_EDGES) - 1
    n = d.height
    H = np.zeros((n, nb), np.int32)
    U = np.zeros((n, nb), np.int32)
    Hn = np.zeros(n, np.int32)
    Un = np.zeros(n, np.int32)
    Hu = np.zeros((n, nb), np.int32)
    Uu = np.zeros((n, nb), np.int32)
    E = np.zeros(n, np.int32)
    m = msgs.filter(pl.col("s").is_not_null())
    mask = np.zeros(m.height, np.int64)
    if m["mentions_roster"].dtype != pl.Null:
        for k, lst in enumerate(m["mentions_roster"].to_list()):
            if lst:
                for a in lst:
                    if a is not None and 0 <= a < 63:
                        mask[k] |= np.int64(1) << np.int64(a)
    m = m.with_columns(pl.Series("mm", mask))
    tc = d["t_call"].to_numpy()
    tp = d["t_prev"].fill_null(np.nan).to_numpy()
    ag = d["agent"].to_numpy().astype(np.int64)
    valid = d["valid"].to_numpy()
    key_c = {}
    for i, (dd, rr) in enumerate(d.select("day", "room").iter_rows()):
        key_c.setdefault((dd, rr), []).append(i)
    for (dd, rr), g in m.group_by(["day", "room"]):
        if (dd, rr) not in key_c:
            continue
        g = g.sort("s")
        s_ = g["s"].to_numpy()
        p_ = g["t"].to_numpy()
        snd = g["agent"].to_numpy().astype(np.int64)
        mm = g["mm"].to_numpy().astype(np.int64)
        ci = np.asarray(key_c[(dd, rr)])
        ci = ci[valid[ci]]
        if not len(ci):
            continue
        i0 = np.searchsorted(s_, tc[ci] - DM_EDGES[-1], "right")
        i1 = np.searchsorted(s_, tc[ci], "left")
        k = i1 - i0
        if k.sum() == 0:
            continue
        rep = np.repeat(np.arange(len(ci)), k)
        off = np.arange(k.sum()) - np.repeat(np.cumsum(k) - k, k)
        mi = np.repeat(i0, k) + off
        cc = ci[rep]
        keep = snd[mi] != ag[cc]
        cc, mi = cc[keep], mi[keep]
        delta = tc[cc] - s_[mi]
        b = np.clip(np.searchsorted(DM_EDGES, delta, "right") - 1, 0, nb - 1)
        p = p_[mi]
        hop1 = (p < tc[cc]) & (p >= tp[cc])
        earl = p < tp[cc]
        unr = p >= tc[cc]
        named = ((mm[mi] >> ag[cc]) & 1).astype(bool)
        np.add.at(H, (cc[hop1], b[hop1]), 1)
        np.add.at(U, (cc[unr], b[unr]), 1)
        np.add.at(E, cc[earl], 1)
        np.add.at(Hn, cc[hop1 & named], 1)
        np.add.at(Un, cc[unr & named], 1)
        np.add.at(Hu, (cc[hop1 & ~named], b[hop1 & ~named]), 1)
        np.add.at(Uu, (cc[unr & ~named], b[unr & ~named]), 1)
    cols = [pl.Series(f"h1_{j}", H[:, j]) for j in range(nb)] + [pl.Series(f"u_{j}", U[:, j]) for j in range(nb)]
    cols += [pl.Series(f"h1u_{j}", Hu[:, j]) for j in range(nb)] + [pl.Series(f"uu_{j}", Uu[:, j]) for j in range(nb)]
    cols += [pl.Series("h1_n", Hn), pl.Series("u_n", Un), pl.Series("e_all", E)]
    out = d.with_columns(cols)
    return out.with_columns((pl.col("R_all") - pl.sum_horizontal([f"h1_{j}" for j in range(nb)])).alias("R_o_dm"))


def all_counts(calls: pl.DataFrame, msgs: pl.DataFrame) -> pl.DataFrame:
    """counts() then dm_counts(); msgs gets decision times from the unit's calls. Adds the post hoc (A2) column
    since_talk = seconds since the recipient's own last talk output before t_call (null if none that day)."""
    msgs = decision_times(msgs, calls)
    d = dm_counts(counts(calls, msgs), msgs)
    own = (d.filter(pl.col("talk")).select("agent", "day", pl.col("t_first").alias("t_last_talk"))
           .sort("t_last_talk"))
    d = d.sort("t_call").join_asof(own, left_on="t_call", right_on="t_last_talk", by=["agent", "day"],
                                   strategy="backward")
    return d.with_columns((pl.col("t_call") - pl.col("t_last_talk")).alias("since_talk")).sort("agent", "day",
                                                                                               "t_call")


# ============================================================================================ estimator
QUIET_S = None     # post hoc A2: when set, keep only calls whose recipient has not talked in the last QUIET_S seconds


def _rows(df: pl.DataFrame, trim: bool = True) -> pl.DataFrame:
    f = pl.col("valid") & ~pl.col("first_of_day")
    if trim:
        f = f & pl.col("trim")
    if QUIET_S is not None and "since_talk" in df.columns:
        f = f & (pl.col("since_talk").is_null() | (pl.col("since_talk") > QUIET_S))
    return df.filter(f)


BLOCK_MODE = "hour"     # Amendment A1: 1-hour blocks everywhere (day blocks were anti-conservative in synthetic nulls)


def _blocks(df: pl.DataFrame) -> np.ndarray:
    """Bootstrap blocks: 1-hour blocks within days (BLOCK_MODE 'hour'); 'day' = days when >= 3 days."""
    if BLOCK_MODE == "day" and df["day"].n_unique() >= 3:
        return df["day"].to_numpy().astype(np.int64)
    hr = ((df["t_call"] - df["t_call"].min()) // 3600).cast(pl.Int64).to_numpy()
    return df["day"].to_numpy().astype(np.int64) * 1000 + hr


def block_stats(df: pl.DataFrame, regs: list[str]):
    """Within-cell demeaned cross-products per bootstrap block. Returns (blocks, XtX[b,k,k], Xty[b,k], n[b])."""
    cell = (df["agent"].cast(pl.Int64) * 100000 + df["day"].cast(pl.Int64) * 10 + df["cls"].cast(pl.Int64))
    d = df.select(regs + ["talk"]).cast(pl.Float64).with_columns(cell.alias("_cell"))
    d = d.with_columns([(pl.col(x) - pl.col(x).mean().over("_cell")).alias(x) for x in regs + ["talk"]])
    X = d.select(regs).to_numpy()
    y = d["talk"].to_numpy()
    b = _blocks(df)
    ub, inv = np.unique(b, return_inverse=True)
    B = len(ub)
    k = len(regs)
    XtX = np.zeros((B, k, k))
    Xty = np.zeros((B, k))
    nb = np.bincount(inv, minlength=B)
    order = np.argsort(inv, kind="stable")
    Xs, ys, invs = X[order], y[order], inv[order]
    starts = np.r_[0, np.cumsum(nb)[:-1]]
    for j in range(B):
        sl = slice(starts[j], starts[j] + nb[j])
        Xj = Xs[sl]
        XtX[j] = Xj.T @ Xj
        Xty[j] = Xj.T @ ys[sl]
    return ub, inv, XtX, Xty, nb


def _solve(A, v):
    try:
        return np.linalg.solve(A, v)
    except np.linalg.LinAlgError:
        return np.linalg.lstsq(A, v, rcond=None)[0]


def scale_stats(df_all: pl.DataFrame, msgs: pl.DataFrame, rows: pl.DataFrame, inv_blocks, ub):
    """Per-block reads, messages and talk calls for m_bar and r_bar (trimmed rows; messages inside each day's window)."""
    blk = _blocks(rows)
    _, binv = np.unique(blk, return_inverse=True)
    reads = np.bincount(binv, weights=rows["R_all"].to_numpy(), minlength=len(ub))
    talks = np.bincount(binv, weights=rows["talk"].cast(pl.Float64).to_numpy(), minlength=len(ub))
    # messages by call-making agents posted inside the trimmed window, assigned to the block of the nearest row
    win = rows.group_by("day").agg(pl.col("ap_lo").first(), pl.col("ap_hi").first())
    callers = set(df_all["agent"].unique().to_list())
    mm = (msgs.join(win, on="day").filter((pl.col("t") >= pl.col("ap_lo")) & (pl.col("t") <= pl.col("ap_hi"))))
    n_all = np.zeros(len(ub))
    n_call = np.zeros(len(ub))
    if mm.height:
        if BLOCK_MODE == "day" and rows["day"].n_unique() >= 3:
            mb = mm["day"].to_numpy().astype(np.int64)
        else:
            mb = mm["day"].to_numpy().astype(np.int64) * 1000 + ((mm["t"] - rows["t_call"].min()) // 3600).cast(
                pl.Int64).to_numpy()
        pos = np.searchsorted(ub, mb)
        ok = (pos < len(ub)) & (ub[np.minimum(pos, len(ub) - 1)] == mb)
        isc = np.array([a in callers for a in mm["agent"].to_list()])
        n_all = np.bincount(pos[ok], minlength=len(ub)).astype(float)
        n_call = np.bincount(pos[ok & isc], minlength=len(ub)).astype(float)
    return reads, talks, n_all, n_call


def fit(df: pl.DataFrame, msgs: pl.DataFrame, variant: str = "main", trim: bool = True, B: int = 200,
        seed: int = 0, regs: list[str] | None = None) -> dict:
    regs = regs or VARIANTS[variant]
    rows = _rows(df, trim)
    if rows.height < 200 or rows["R_all"].sum() == 0:
        return {"ok": False, "n_rows": rows.height}
    regs = [r for r in regs if r in rows.columns and rows[r].std() > 0] if variant != "naive" else regs
    ub, inv, XtX, Xty, nb = block_stats(rows, regs)
    if len(ub) < 4:
        return {"ok": False, "n_rows": rows.height, "n_blocks": len(ub)}
    reads, talks, n_all, n_call = scale_stats(df, msgs, rows, inv, ub)

    def est(wts):
        A = np.tensordot(wts, XtX, 1)
        v = np.tensordot(wts, Xty, 1)
        beta = dict(zip(regs, _solve(A + 1e-9 * np.eye(len(regs)), v)))
        rbar = (wts @ reads) / max(wts @ n_all, 1e-9)
        mbar = (wts @ n_call) / max(wts @ talks, 1e-9)
        return beta, rbar, mbar

    def summarise(beta, rbar, mbar):
        o = {f"b_{k}": v for k, v in beta.items()}
        o["rbar"], o["mbar"] = rbar, mbar
        gmul = rbar * mbar
        bp = beta.get("P", 0.0)
        if variant in ("main", "noexo"):
            J = beta["R_m"] - bp
            o["J1"] = J
            o["g"] = gmul * J
            o["g3"] = gmul * (J + beta.get("R_l1", 0) - bp + beta.get("R_l2", 0) - bp)
        elif variant == "all":
            o["J1"] = beta["R_all"] - bp
            o["g"] = gmul * o["J1"]
        elif variant == "named":
            o["J1_named"] = beta.get("R_m_n", np.nan) - beta.get("P_n", 0.0)
            o["J1_unnamed"] = beta.get("R_m_u", np.nan) - beta.get("P_u", 0.0)
        elif variant in ("dm", "dm_noexo"):
            wts_ = DM_W
            J = sum(wts_[b] * (beta.get(f"h1_{b}", 0.0) - beta.get(f"u_{b}", 0.0)) for b in range(4)
                    if f"h1_{b}" in beta and f"u_{b}" in beta) / max(sum(wts_[b] for b in range(4)
                                                                          if f"h1_{b}" in beta and f"u_{b}" in beta), 1e-12)
            o["J1"] = J
            o["g"] = gmul * J
            o["g3"] = gmul * (J + beta.get("R_l1", 0.0) + beta.get("R_l2", 0.0))
            for b in range(4):
                if f"h1_{b}" in beta and f"u_{b}" in beta:
                    o[f"J1_bin{b}"] = beta[f"h1_{b}"] - beta[f"u_{b}"]
            o["b_unread_mean"] = sum(wts_[b] * beta.get(f"u_{b}", 0.0) for b in range(4)) / max(sum(wts_), 1e-12)
        elif variant == "dm_named":
            wts_ = DM_W
            ok = [b for b in range(4) if f"h1u_{b}" in beta and f"uu_{b}" in beta]
            o["J1_unnamed"] = sum(wts_[b] * (beta[f"h1u_{b}"] - beta[f"uu_{b}"]) for b in ok) / max(
                sum(wts_[b] for b in ok), 1e-12)
            o["J1_named"] = beta.get("h1_n", np.nan) - beta.get("u_n", 0.0)
        elif variant == "naive":
            o["J1"] = beta["R_all"]
            o["g"] = gmul * o["J1"]
        return o

    global DM_W
    DM_W = [float(rows[f"h1_{b}"].sum()) if f"h1_{b}" in rows.columns else 0.0 for b in range(4)]
    w0 = np.ones(len(ub))
    point = summarise(*est(w0))
    rng = np.random.default_rng(seed)
    boots = []
    for _ in range(B):
        wts = np.bincount(rng.integers(0, len(ub), len(ub)), minlength=len(ub)).astype(float)
        boots.append(summarise(*est(wts)))
    res = {"ok": True, "n_rows": rows.height, "n_blocks": len(ub), "n_reads": float(reads.sum()),
           "n_msgs": float(n_all.sum()), "regs": regs}
    for k, v in point.items():
        res[k] = float(v)
        bv = np.array([b[k] for b in boots], float)
        bv = bv[np.isfinite(bv)]
        if len(bv) > 10:
            res[k + "_lo"], res[k + "_hi"] = (float(x) for x in np.percentile(bv, [2.5, 97.5]))
            res[k + "_se"] = float(bv.std(ddof=1))
    return res


# ============================================================================================ equal-time dial
def minute_grid(df: pl.DataFrame, min_calls: int = 20):
    """1-min talk spins per day on the all-present window (agents with >= min_calls receiving calls that day)."""
    days, mins = [], []
    for (d,), g in df.filter(pl.col("trim")).group_by(["day"], maintain_order=True):
        lo, hi = g["ap_lo"][0], g["ap_hi"][0]
        if hi - lo < 1800:
            continue
        T = int((hi - lo) // 60) + 1
        ags = (df.filter(pl.col("day") == d).group_by("agent").len().filter(pl.col("len") >= min_calls)["agent"]
               .sort().to_list())
        if len(ags) < 3:
            continue
        S = np.zeros((T, len(ags)))
        tk = g.filter(pl.col("talk") & pl.col("agent").is_in(ags))
        ai = {a: k for k, a in enumerate(ags)}
        mi = ((tk["t_first"].to_numpy() - lo) // 60).astype(int)
        ok = (mi >= 0) & (mi < T)
        S[mi[ok], [ai[a] for a in np.asarray(tk["agent"].to_list())[ok]]] = 1.0
        days.append(S)
        mins.append(np.arange(T))
    return days, mins


def equal_time(df: pl.DataFrame, B: int = 200, seed: int = 0) -> dict:
    days, mins = minute_grid(df)
    if not days:
        return {"g_eq": np.nan}
    g = nulls.stat_cw_gain(days, mins, 30)
    out = {"g_eq": g, "n_days_eq": len(days), "N_eq": float(np.mean([d.shape[1] for d in days]))}
    if len(days) >= 3 and B > 0:
        rng = np.random.default_rng(seed)
        bs = []
        for _ in range(B):
            ix = rng.integers(0, len(days), len(days))
            bs.append(nulls.stat_cw_gain([days[i] for i in ix], [mins[i] for i in ix], 30))
        out["g_eq_lo"], out["g_eq_hi"] = (float(x) for x in np.nanpercentile(bs, [2.5, 97.5]))
    return out


# ============================================================================================ shift null
def shift_msgs(msgs: pl.DataFrame, calls: pl.DataFrame, rng) -> pl.DataFrame:
    """Each sender's messages on each day shifted by +-U(5, 30) min, circularly within the day's call span."""
    span = calls.group_by("day").agg(pl.col("t_call").min().alias("lo"), pl.col("t_call").max().alias("hi"))
    m = msgs.join(span, on="day", how="inner")
    keys = m.select("day", "agent").unique()
    off = rng.uniform(300, 1800, keys.height) * rng.choice([-1, 1], keys.height)
    m = m.join(keys.with_columns(pl.Series("off", off)), on=["day", "agent"])
    L = pl.col("hi") - pl.col("lo")
    return m.with_columns((pl.col("lo") + ((pl.col("t") - pl.col("lo") + pl.col("off")) % L)).alias("t")).select(
        msgs.columns).sort("t")


# ============================================================================================ simulator
def ou_field(t0: float, t1: float, tau: float, sigma: float, rng, dt: float = 10.0):
    n = int((t1 - t0) / dt) + 2
    a = np.exp(-dt / tau)
    x = np.zeros(n)
    e = rng.normal(0, sigma * np.sqrt(1 - a * a), n)
    x[0] = rng.normal(0, sigma)
    for k in range(1, n):
        x[k] = a * x[k - 1] + e[k]
    return t0, dt, np.exp(x - sigma ** 2 / 2)


def simulate(calls: pl.DataFrame, g_true: float, rbar: float, rng, base_scale: float = 0.7, ou_tau: float = 300.0,
             ou_sigma: float = 0.5, burst: bool = False, edge: float = 1.5, base: dict | None = None):
    """Talk on the real call grid. Each call's talk probability = base(agent, class) * shared OU field * edge
    (first 20 min of the day) * burst pulses (optional, per room: rate 1/20 min, 3 min long, x4) + J * reads at the
    call (hop 1 only), J = g_true / rbar. One message per talk call, posted at the call's t_first in its room.
    Returns (calls with simulated 'talk', msgs frame)."""
    J = g_true / max(rbar, 1e-9)
    c = calls.sort("t_call")
    if base is None:
        base = {(a, k): v for a, k, v in calls.group_by("agent", "cls").agg(pl.col("talk").mean()).iter_rows()}
    talk = np.zeros(c.height, bool)
    ag = c["agent"].to_numpy()
    cl = c["cls"].to_numpy()
    rm = c["room"].fill_null(-1).to_numpy()
    tc = c["t_call"].to_numpy()
    tf = c["t_first"].to_numpy()
    tp = c["t_prev"].fill_null(np.nan).to_numpy()
    dy = c["day"].to_numpy()
    room_t: dict = {}       # (day, room) -> sorted list of (t, agent)
    room_ts: dict = {}
    fields = {}
    bursts = {}
    day_start = {d: tc[dy == d].min() for d in np.unique(dy)}
    day_end = {d: tc[dy == d].max() for d in np.unique(dy)}
    pending = []            # heap-like list of (t_first, day, room, agent) not yet posted
    import heapq
    for k in range(c.height):
        d, r, a = dy[k], rm[k], ag[k]
        t = tc[k]
        while pending and pending[0][0] < t:
            tt, dd, rr, aa, ss = heapq.heappop(pending)
            lst = room_ts.setdefault((dd, rr), [])
            lab = room_t.setdefault((dd, rr), [])
            pos = bisect.bisect(lst, tt)
            lst.insert(pos, tt)
            lab.insert(pos, aa)
        if d not in fields:
            fields[d] = ou_field(day_start[d] - 60, day_end[d] + 600, ou_tau, ou_sigma, rng)
        f0, fdt, fv = fields[d]
        F = fv[min(int((t - f0) / fdt), len(fv) - 1)]
        p = base.get((a, cl[k]), 0.05) * base_scale * F
        if t - day_start[d] < 1200:
            p *= edge
        if burst:
            if (d, r) not in bursts:
                L = day_end[d] - day_start[d] + 600
                nb = rng.poisson(L / 1200)
                bursts[(d, r)] = np.sort(rng.uniform(day_start[d], day_end[d], nb))
            bs = bursts[(d, r)]
            j = np.searchsorted(bs, t)
            if j > 0 and t - bs[j - 1] < 180:
                p *= 4.0
        if J > 0 and np.isfinite(tp[k]):
            lst = room_ts.get((d, r))
            if lst:
                i0, i1 = bisect.bisect_left(lst, tp[k]), bisect.bisect_left(lst, t)
                nread = sum(1 for z in room_t[(d, r)][i0:i1] if z != a)
                p += J * nread
        if rng.random() < min(p, 0.95):
            talk[k] = True
            heapq.heappush(pending, (tf[k], d, r, a, t))
    sim = c.with_columns(pl.Series("talk", talk))
    m = sim.filter(pl.col("talk")).select(pl.col("t_first").alias("t"), "day", "room", "agent",
                                          pl.col("t_call").alias("s")).with_columns(
        pl.lit(None, dtype=pl.List(pl.Int8)).alias("mentions_roster")).sort("t")
    return sim, m
