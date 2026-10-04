"""H99 round 2 library: call-clock design and kernel (R1), minute grids from the call skeleton (R2), the scheduler-removal
stack on minute grids, the room partition of the collective memory, and the call-skeleton simulator.

Times: float seconds since 2025-01-01 UTC (scheme/build_r2.py). Every statistic is a ratio of sums or an OLS fit on
sums kept per 1-h bootstrap block, so blocks can be resampled.
"""
from __future__ import annotations

import math
from collections import defaultdict

import numpy as np
import polars as pl

BLOCK = 30
KMAX = 2

# ============================================================================== R1: call-clock design
POOLED = ["Y1", "Y2", "R1", "R1o", "P0", "X1", "X0", "R2", "X2", "Eh", "En"]
SPLIT = ["Y1", "Y2", "R1n", "R1u", "R1o", "P0n", "P0u", "X1", "X0", "R2n", "R2u", "X2", "Eh", "En"]


def _cnt(arr, lo, hi):
    """messages with lo <= t < hi (arrays of bounds)."""
    if arr is None or len(arr) == 0:
        return np.zeros(len(lo), np.int32)
    return (np.searchsorted(arr, hi, "left") - np.searchsorted(arr, lo, "left")).astype(np.int32)


def _cnt_open(arr, lo, hi):
    """messages with lo < t < hi."""
    if arr is None or len(arr) == 0:
        return np.zeros(len(lo), np.int32)
    return np.clip(np.searchsorted(arr, hi, "left") - np.searchsorted(arr, lo, "right"), 0, None).astype(np.int32)


def call_design(calls: pl.DataFrame, msgs: pl.DataFrame, wmax=120.0):
    """One row per receiving call with hop counts (see README Round 2, R1). Returns a polars frame (all calls)."""
    out = []
    for d in sorted(calls["day"].unique().to_list()):
        C = calls.filter(pl.col("day") == d).sort("agent", "t", "turn_id")
        M = msgs.filter(pl.col("day") == d).sort("t")
        mt = M["t"].to_numpy()
        mr = M["room"].fill_null(-1).to_numpy()
        ma = M["agent"].to_numpy()
        mn = M["named"].to_list()
        T_room = {r: mt[mr == r] for r in np.unique(mr)}
        T_ra = {(r, a): mt[(mr == r) & (ma == a)] for r in np.unique(mr) for a in np.unique(ma[mr == r])}
        T_a = {a: mt[ma == a] for a in np.unique(ma)}
        nm = defaultdict(list)
        nm_all = defaultdict(list)
        for t_, r_, a_, L in zip(mt, mr, ma, mn):
            for b in (L or []):
                if b != a_:
                    nm[(r_, b)].append(t_)
                    nm_all[b].append(t_)
        T_n = {k: np.array(v) for k, v in nm.items()}
        T_nall = {k: np.array(v) for k, v in nm_all.items()}
        ag = C["agent"].to_numpy()
        t = C["t"].to_numpy()
        tf = C["tf"].to_numpy()
        rm = C["room"].fill_null(-1).to_numpy()
        tp = np.r_[np.nan, t[:-1]]
        tp[np.r_[True, ag[1:] != ag[:-1]]] = np.nan
        w = np.clip(tf - t, 1.0, wmax)
        first = np.isnan(tp)
        tp = np.where(first, t - w, tp)
        a1 = np.maximum(tp, t - w)
        n = len(t)
        res = {k: np.zeros(n, np.int32) for k in ("R1", "R1n", "R1o", "R1on", "P0", "P0n", "X1", "X0", "Xr", "Rall", "Ralln")}
        keys = defaultdict(list)
        for i in range(n):
            keys[(rm[i], ag[i])].append(i)
        for (r, a), ix in keys.items():
            ix = np.array(ix)
            tt, aa, pp, ww = t[ix], a1[ix], tp[ix], w[ix]
            room, own, own_all = T_room.get(r), T_ra.get((r, a)), T_a.get(a)
            nam, nam_all = T_n.get((r, a)), T_nall.get(a)
            r1 = _cnt(room, aa, tt) - _cnt(own, aa, tt)
            r1n = _cnt(nam, aa, tt)
            ro = _cnt(room, pp, aa) - _cnt(own, pp, aa)
            ron = _cnt(nam, pp, aa)
            p0 = _cnt_open(room, tt, tt + ww) - _cnt_open(own, tt, tt + ww)
            p0n = _cnt_open(nam, tt, tt + ww)
            x1 = (_cnt(mt, aa, tt) - _cnt(own_all, aa, tt)) - r1
            x0 = (_cnt_open(mt, tt, tt + ww) - _cnt_open(own_all, tt, tt + ww)) - p0
            xr = (_cnt(mt, pp, tt) - _cnt(own_all, pp, tt)) - (r1 + ro)
            if r < 0:  # no room: nothing readable; everything counts as cross-room
                r1[:] = 0; r1n[:] = 0; ro[:] = 0; ron[:] = 0; p0[:] = 0; p0n[:] = 0
            for k, v in (("R1", r1), ("R1n", r1n), ("R1o", ro), ("R1on", ron), ("P0", p0), ("P0n", p0n), ("X1", x1),
                         ("X0", x0), ("Xr", xr), ("Rall", r1 + ro), ("Ralln", r1n + ron)):
                res[k][ix] = v
        D = C.select("turn_id", "agent", "day", "t", "tf", "room", "is_chat", "is_wake", "talk", "active", "E_h", "E_n",
                     "trim", "ap_lo").with_columns(*[pl.Series(k, v) for k, v in res.items()],
                                                   pl.Series("first", first))
        out.append(D)
    D = pl.concat(out)
    D = D.sort("agent", "day", "t", "turn_id").with_columns(
        pl.col("talk").cast(pl.Float64).alias("Y"),
        pl.col("talk").cast(pl.Float64).shift(1).over("agent", "day").alias("Y1"),
        pl.col("talk").cast(pl.Float64).shift(2).over("agent", "day").alias("Y2"),
        pl.col("Rall").shift(1).over("agent", "day").alias("R2"),
        pl.col("Ralln").shift(1).over("agent", "day").alias("R2n"),
        pl.col("Xr").shift(1).over("agent", "day").alias("X2"),
        pl.int_range(pl.len()).over("agent", "day").alias("pos"),
    ).with_columns((pl.col("R1") - pl.col("R1n")).alias("R1u"), (pl.col("P0") - pl.col("P0n")).alias("P0u"),
                   (pl.col("R2") - pl.col("R2n")).alias("R2u"),
                   pl.col("E_h").cast(pl.Float64).alias("Eh"), pl.col("E_n").cast(pl.Float64).alias("En"))
    return D


def fit_rows(D: pl.DataFrame, cols):
    """Within (agent, day, class) demeaned OLS pieces per 1-h block: returns (XtX blocks, Xty blocks, n)."""
    F = D.filter(pl.col("trim") & (pl.col("pos") >= 2) & pl.col("room").is_not_null())
    if F.height < 200:
        return None
    F = F.with_columns((pl.col("agent").cast(pl.Int64) * 100000 + pl.col("day").cast(pl.Int64) * 10
                        + pl.col("is_chat").cast(pl.Int64) * 2 + pl.col("is_wake").cast(pl.Int64)).alias("g"),
                       (pl.col("day").cast(pl.Int64) * 1000 + ((pl.col("t") - pl.col("ap_lo")) // 3600).cast(pl.Int64)).alias("blk"))
    allc = ["Y"] + list(cols)
    F = F.with_columns([(pl.col(c).cast(pl.Float64) - pl.col(c).cast(pl.Float64).mean().over("g")).alias(c) for c in allc])
    X = F.select(cols).to_numpy()
    y = F["Y"].to_numpy()
    blk = F["blk"].to_numpy()
    ub, inv = np.unique(blk, return_inverse=True)
    k = X.shape[1]
    XtX = np.zeros((len(ub), k, k))
    Xty = np.zeros((len(ub), k))
    for b in range(len(ub)):
        s = inv == b
        XtX[b] = X[s].T @ X[s]
        Xty[b] = X[s].T @ y[s]
    return XtX, Xty, F.height


def ols_boot(pieces, cols, B=200, rng=None):
    XtX, Xty, n = pieces
    rng = rng or np.random.default_rng(0)
    k = len(cols)
    ridge = 1e-9 * np.eye(k)
    beta = np.linalg.solve(XtX.sum(0) + ridge, Xty.sum(0))
    nb = len(XtX)
    draws = np.full((B, k), np.nan)
    if nb >= 4:
        for b in range(B):
            ix = rng.integers(0, nb, nb)
            try:
                draws[b] = np.linalg.solve(XtX[ix].sum(0) + ridge, Xty[ix].sum(0))
            except np.linalg.LinAlgError:
                pass
    return dict(zip(cols, beta)), {c: draws[:, i] for i, c in enumerate(cols)}, nb, n


def rho_self(D: pl.DataFrame):
    """Single-agent lag-1-call autocorrelation of talk, centred within (agent, day, 30-min block); sums per 1-h block."""
    F = D.filter(pl.col("trim")).sort("agent", "day", "t", "turn_id").with_columns(
        ((pl.col("t") - pl.col("ap_lo")) // 1800).cast(pl.Int64).alias("b30"),
        ((pl.col("t") - pl.col("ap_lo")) // 3600).cast(pl.Int64).alias("b60"))
    F = F.with_columns((pl.col("Y") - pl.col("Y").mean().over("agent", "day", "b30")).alias("yc"))
    F = F.with_columns(pl.col("yc").shift(-1).over("agent", "day", "b30").alias("yn"))
    G = (F.filter(pl.col("yn").is_not_null())
         .group_by("day", "b60").agg((pl.col("yc") * pl.col("yn")).sum().alias("num"),
                                     ((pl.col("yc") ** 2 + pl.col("yn") ** 2) / 2).sum().alias("den")))
    return G.select("num", "den").to_numpy()


def ratio_boot(S, B=400, rng=None):
    rng = rng or np.random.default_rng(1)
    est = S[:, 0].sum() / S[:, 1].sum() if S[:, 1].sum() > 0 else np.nan
    if len(S) < 4:
        return est, np.nan, np.nan, np.nan
    d = []
    for _ in range(B):
        ix = rng.integers(0, len(S), len(S))
        den = S[ix, 1].sum()
        d.append(S[ix, 0].sum() / den if den > 0 else np.nan)
    d = np.array(d)
    d = d[np.isfinite(d)]
    return est, float(np.percentile(d, 2.5)), float(np.percentile(d, 97.5)), float(d.std(ddof=1))


def ci(v):
    v = np.asarray(v, float)
    v = v[np.isfinite(v)]
    if len(v) < 20:
        return np.nan, np.nan, np.nan
    return float(np.percentile(v, 2.5)), float(np.percentile(v, 97.5)), float(v.std(ddof=1))


def kernel_summary(D, msgs_trim_n, talk_trim_n, r_bar, B=200, seed=0):
    """R1 kernel: pooled and named/unnamed fits; placebo-corrected contrasts and loop gains."""
    rng = np.random.default_rng(seed)
    out = {}
    m_bar = msgs_trim_n / talk_trim_n if talk_trim_n else np.nan
    out["m_bar"], out["r_bar"] = m_bar, r_bar
    pp = fit_rows(D, POOLED)
    ps = fit_rows(D, SPLIT)
    if pp is None or ps is None:
        return out
    bp, dp, nb, n = ols_boot(pp, POOLED, B, rng)
    bs, ds, _, _ = ols_boot(ps, SPLIT, B, rng)
    out["n_calls"], out["n_blocks"] = n, nb
    con = {
        "beta_R1": (bp["R1"], dp["R1"]), "beta_P0": (bp["P0"], dp["P0"]), "beta_X1": (bp["X1"], dp["X1"]),
        "beta_X0": (bp["X0"], dp["X0"]), "beta_R2": (bp["R2"], dp["R2"]), "beta_X2": (bp["X2"], dp["X2"]),
        "rho_Y1": (bp["Y1"], dp["Y1"]),
        "J1_inflight": (bp["R1"] - bp["P0"], dp["R1"] - dp["P0"]),
        "J1_room": (bp["R1"] - bp["X1"], dp["R1"] - dp["X1"]),
        "J0_room": (bp["P0"] - bp["X0"], dp["P0"] - dp["X0"]),
        "J2_room": (bp["R2"] - bp["X2"], dp["R2"] - dp["X2"]),
        "beta_R1n": (bs["R1n"], ds["R1n"]), "beta_R1u": (bs["R1u"], ds["R1u"]),
        "beta_P0n": (bs["P0n"], ds["P0n"]), "beta_P0u": (bs["P0u"], ds["P0u"]),
        "beta_R2n": (bs["R2n"], ds["R2n"]), "beta_R2u": (bs["R2u"], ds["R2u"]),
        "J1n_inflight": (bs["R1n"] - bs["P0n"], ds["R1n"] - ds["P0n"]),
        "J1u_inflight": (bs["R1u"] - bs["P0u"], ds["R1u"] - ds["P0u"]),
        "J1u_room": (bs["R1u"] - bs["X1"], ds["R1u"] - ds["X1"]),
        "J2n_room": (bs["R2n"] - bs["X2"], ds["R2n"] - ds["X2"]),
        "J2u_room": (bs["R2u"] - bs["X2"], ds["R2u"] - ds["X2"]),
    }
    for k, (e, dr) in con.items():
        lo, hi, se = ci(dr)
        out[k], out[k + "_lo"], out[k + "_hi"], out[k + "_se"] = float(e), lo, hi, se
    sc = m_bar * r_bar
    for k in ("J1_inflight", "J1_room", "J2_room", "J0_room"):
        g = "g" + k[1:]
        out[g], out[g + "_lo"], out[g + "_hi"], out[g + "_se"] = (out[k] * sc, out[k + "_lo"] * sc, out[k + "_hi"] * sc,
                                                                  out[k + "_se"] * sc)
    # ratios with bootstrap CI
    for name, num, den in (("ratio_P0_R1_named", ds["P0n"], ds["R1n"]), ("ratio_J2_J1", dp["R2"] - dp["X2"], dp["R1"] - dp["P0"]),
                           ("ratio_named_unnamed", ds["R1n"] - ds["P0n"], ds["R1u"] - ds["P0u"])):
        e_num = {"ratio_P0_R1_named": bs["P0n"], "ratio_J2_J1": bp["R2"] - bp["X2"], "ratio_named_unnamed": bs["R1n"] - bs["P0n"]}[name]
        e_den = {"ratio_P0_R1_named": bs["R1n"], "ratio_J2_J1": bp["R1"] - bp["P0"], "ratio_named_unnamed": bs["R1u"] - bs["P0u"]}[name]
        out[name] = float(e_num / e_den) if e_den != 0 else np.nan
        r = num / den
        lo, hi, _ = ci(r)
        out[name + "_lo"], out[name + "_hi"] = lo, hi
    return out


# ============================================================================== minute grids
def expect_grid(C: pl.DataFrame, ags, L, talk_col="talk"):
    """Talk expected from the call skeleton alone: E_it = 1 - prod over agent i's calls whose t_first falls in minute t
    of (1 - b), b = the agent x day x call-class talk rate of the frame. Independent talk at the real calls has
    E[s_it | skeleton] = E_it exactly."""
    st = C.group_by("agent", "is_chat", "is_wake").agg(pl.col(talk_col).cast(pl.Float64).mean().alias("b"))
    C = C.join(st, on=["agent", "is_chat", "is_wake"], how="left").filter(pl.col("agent").is_in(ags))
    pos = {a: i for i, a in enumerate(ags)}
    lg = np.zeros((len(ags), L))
    ai = np.array([pos[a] for a in C["agent"].to_list()], int)
    mf = C["mf"].to_numpy()
    b = np.clip(C["b"].to_numpy(), 0, 0.999)
    ok = (mf >= 0) & (mf < L)
    np.add.at(lg, (ai[ok], mf[ok]), np.log1p(-b[ok]))
    return 1 - np.exp(lg)


def call_grid(calls: pl.DataFrame, ws_by_day: dict, talk_col="talk"):
    """Minute grid from the call skeleton: per day, present agents (trim agents), keep = minutes inside [ap_lo, ap_hi],
    talk spin = a talking call's t_first falls in the minute; act-only = an active non-talking call starts in it;
    occ = number of receiving calls starting in the minute. Minute index = floor((t - calendar.win_start)/60)."""
    days, keeps, acts, occs, agents_l, rooms_l, dlist, exps = [], [], [], [], [], [], [], []
    for d in sorted(calls["day"].unique().to_list()):
        C = calls.filter(pl.col("day") == d)
        Ct = C.filter(pl.col("trim"))
        if Ct.height == 0:
            continue
        ags = sorted(Ct["agent"].unique().to_list())
        ap_lo, ap_hi = float(Ct["ap_lo"][0]), float(Ct["ap_hi"][0])
        ws = ws_by_day[d]
        m_lo = int(math.ceil((ap_lo - ws) / 60 - 1e-9))
        m_hi = int(math.floor((ap_hi - ws) / 60)) - 1
        if m_hi - m_lo + 1 < 30:
            continue
        L = m_hi + 2
        pos = {a: i for i, a in enumerate(ags)}
        S = np.zeros((len(ags), L), np.int8)
        A = np.zeros((len(ags), L), np.int8)
        O = np.zeros((len(ags), L), np.int16)
        Cp = C.filter(pl.col("agent").is_in(ags))
        ai = np.array([pos[a] for a in Cp["agent"].to_list()])
        mf = Cp["mf"].to_numpy()
        mi = Cp["minute"].to_numpy()
        tk = Cp[talk_col].to_numpy().astype(bool)
        ac = Cp["active"].to_numpy().astype(bool)
        ok = (mf >= 0) & (mf < L) & tk
        S[ai[ok], mf[ok]] = 1
        ok2 = (mi >= 0) & (mi < L)
        np.add.at(O, (ai[ok2], mi[ok2]), 1)
        ok3 = ok2 & ac & ~tk
        A[ai[ok3], mi[ok3]] = 1
        keep = np.zeros(L, bool)
        keep[m_lo:m_hi + 1] = True
        rmode = (Ct.filter(pl.col("room").is_not_null()).group_by("agent", "room").agg(pl.len().alias("k"))
                 .sort("k", descending=True).group_by("agent").agg(pl.col("room").first()))
        rmap = dict(zip(rmode["agent"].to_list(), rmode["room"].to_list()))
        rooms_l.append(np.array([rmap.get(a, -1) if rmap.get(a) is not None else -1 for a in ags]))
        exps.append(expect_grid(C, ags, L, talk_col))
        dlist.append(d)
        days.append(S)
        keeps.append(keep)
        acts.append(A)
        occs.append(O)
        agents_l.append(np.array(ags))
    return {"talk": days, "keep": keeps, "actonly": acts, "occ": occs, "agents": agents_l, "rooms": rooms_l, "days": dlist,
            "expect": exps}


def center(S, keep, occ=None, block=BLOCK):
    """Centre each agent's spins within (30-min block[, occupancy class]) over kept minutes. Returns X (N x L float),
    ok (L bool: kept minute in a block with >= 5 kept minutes)."""
    S = np.asarray(S, float)
    N, L = S.shape
    X = np.zeros((N, L))
    ok = np.zeros(L, bool)
    idx = np.flatnonzero(keep)
    blk = idx // block
    for b in np.unique(blk):
        j = idx[blk == b]
        if len(j) < 5:
            continue
        ok[j] = True
        Y = S[:, j]
        if occ is None:
            X[:, j] = Y - Y.mean(1, keepdims=True)
        else:
            cl = np.minimum(np.asarray(occ)[:, j], 4)
            cl = np.where(cl == 0, 0, np.where(cl <= 3, 1, 2))
            for i in range(N):
                for c in (0, 1, 2):
                    s = cl[i] == c
                    if s.any():
                        X[i, j[s]] = Y[i, s] - Y[i, s].mean()
    return X, ok


FIELDS = ["n_min", "c", "p"] + [f"{a}{k}" for k in range(1, KMAX + 1) for a in ("cc", "cd", "qq", "qd")]


def sums_X(Xs, oks, block=BLOCK, boot_min=60):
    """Round-1 sums (h99lib.binary_sums) from pre-centred X arrays and valid-minute masks."""
    out = []
    for X, ok in zip(Xs, oks):
        N = X.shape[0]
        if N < 3 or ok.sum() < 10:
            continue
        L = X.shape[1]
        M = X.sum(0) / math.sqrt(N)
        c = M ** 2
        q = (X ** 2).sum(0) - c
        p = q / (N - 1)
        t = np.arange(L)
        for h in np.unique(t[ok] // boot_min):
            sel = ok & (t // boot_min == h)
            r = dict.fromkeys(FIELDS, 0.0)
            r["n_min"], r["c"], r["p"] = float(sel.sum()), float(c[sel].sum()), float(p[sel].sum())
            js = np.flatnonzero(sel)
            for k in range(1, KMAX + 1):
                a = js[js + k < L]
                b = a + k
                v = ok[b] & (a // block == b // block)
                a, b = a[v], b[v]
                if not len(a):
                    continue
                cc = M[a] * M[b]
                tt = (X[:, a] * X[:, b]).sum(0)
                r[f"cc{k}"] = float(cc.sum())
                r[f"cd{k}"] = float(((c[a] + c[b]) / 2).sum())
                r[f"qq{k}"] = float((tt - cc).sum())
                r[f"qd{k}"] = float(((q[a] + q[b]) / 2).sum())
            out.append([r[f] for f in FIELDS])
    return np.array(out, float).reshape(-1, len(FIELDS))


def est_X(tot):
    s = dict(zip(FIELDS, tot))
    o = {"g_chi": 1 - s["p"] / s["c"] if s["c"] > 0 else np.nan}
    for k in range(1, KMAX + 1):
        rc = s[f"cc{k}"] / s[f"cd{k}"] if s[f"cd{k}"] > 0 else np.nan
        rp = s[f"qq{k}"] / s[f"qd{k}"] if s[f"qd{k}"] > 0 else np.nan
        o[f"rho_c{k}"], o[f"rho_p{k}"] = rc, rp
        if np.isfinite(rc) and np.isfinite(rp) and np.isfinite(o["g_chi"]) and o["g_chi"] < 1:
            o[f"drho{k}"] = rc - min(max(rp, 1e-3), 0.999) ** (1 - o["g_chi"])
        else:
            o[f"drho{k}"] = np.nan
    return o


GSTATS = ["g_chi", "rho_c1", "rho_p1", "drho1", "drho2"]


def boot_X(rows, B=400, rng=None):
    rng = rng or np.random.default_rng(0)
    e = est_X(rows.sum(0)) if len(rows) else {k: np.nan for k in GSTATS}
    out = dict(e)
    out["n_min"] = float(rows[:, 0].sum()) if len(rows) else 0.0
    out["n_blocks"] = len(rows)
    if len(rows) < 4:
        for k in GSTATS:
            out[k + "_lo"] = out[k + "_hi"] = out[k + "_se"] = np.nan
        return out
    dr = {k: [] for k in GSTATS}
    for _ in range(B):
        ee = est_X(rows[rng.integers(0, len(rows), len(rows))].sum(0))
        for k in GSTATS:
            dr[k].append(ee[k])
    for k in GSTATS:
        lo, hi, se = ci(dr[k])
        out[k + "_lo"], out[k + "_hi"], out[k + "_se"] = lo, hi, se
    return out


def resid_occ(Xs, oks, occs, block=BLOCK):
    """V1: residualize each agent's block-centred talk on its own call occupancy (calls starting in the minute, and
    any-call indicator), both centred within the same 30-min blocks; one OLS per agent-day (2 slopes)."""
    out = []
    for X, ok, O in zip(Xs, oks, occs):
        O = np.asarray(O, float)
        Oc, _ = center(O, ok)
        Ic, _ = center((O > 0).astype(float), ok)
        R = X.copy()
        for i in range(X.shape[0]):
            z = np.c_[Oc[i, ok], Ic[i, ok]]
            G = z.T @ z
            if np.linalg.matrix_rank(G) < 2:
                continue
            b = np.linalg.solve(G + 1e-9 * np.eye(2), z.T @ X[i, ok])
            R[i, ok] = X[i, ok] - z @ b
        out.append(R)
    return out


def resid_actfield(Xs, oks, As, block=BLOCK):
    """V4: residualize each agent's centred talk on the leave-one-out collective act-only mode at lags -1, 0, +1
    (OLS per agent over the unit's days)."""
    regs = defaultdict(lambda: [np.zeros((3, 3)), np.zeros(3)])
    feats = []
    for X, ok, A in zip(Xs, oks, As):
        Ac, _ = center(A, ok)
        N, L = X.shape
        tot = Ac.sum(0)
        F = []
        for i in range(N):
            loo = tot - Ac[i]
            z = np.zeros((L, 3))
            z[:, 1] = loo
            z[1:, 0] = loo[:-1]
            z[:-1, 2] = loo[1:]
            # lags must stay inside the block and on valid minutes
            t = np.arange(L)
            bad0 = np.r_[True, ~ok[:-1] | (t[1:] // block != t[:-1] // block)]
            bad2 = np.r_[~ok[1:] | (t[1:] // block != t[:-1] // block), True]
            z[bad0, 0] = 0
            z[bad2, 2] = 0
            z[~ok] = 0
            F.append(z)
        feats.append(F)
    # agent identity is per-day position; pool by position within day (agents differ per day) -> per (day, i) fit
    out = []
    for X, ok, F in zip(Xs, oks, feats):
        R = X.copy()
        for i in range(X.shape[0]):
            z = F[i][ok]
            y = X[i, ok]
            G = z.T @ z
            if np.linalg.matrix_rank(G) < 3:
                continue
            b = np.linalg.solve(G + 1e-9 * np.eye(3), z.T @ y)
            R[i, ok] = y - z @ b
        out.append(R)
    return out


def pair_sums(Xs, oks, rooms, block=BLOCK, boot_min=60):
    """Room partition: per 1-h block, sums of lag-1 and lag-0 pair covariances and sqrt variance products for
    same-room and cross-room pairs (per day; room code -1 excluded). Returns array (blocks x 6):
    [C1_same, V_same, C1_cross, V_cross, C0_same, C0_cross]."""
    out = []
    for X, ok, rm in zip(Xs, oks, rooms):
        rm = np.asarray(rm)
        N, L = X.shape
        t = np.arange(L)
        for h in np.unique(t[ok] // boot_min):
            sel = ok & (t // boot_min == h)
            js = np.flatnonzero(sel)
            a = js[js + 1 < L]
            b = a + 1
            v = ok[b] & (a // block == b // block)
            a, b = a[v], b[v]
            V = (X[:, sel] ** 2).sum(1)
            C1 = (X[:, a] @ X[:, b].T)
            C1 = (C1 + C1.T) / 2
            C0 = X[:, sel] @ X[:, sel].T
            r = np.zeros(6)
            for i in range(N):
                for j in range(i + 1, N):
                    if rm[i] < 0 or rm[j] < 0:
                        continue
                    sv = math.sqrt(V[i] * V[j])
                    if rm[i] == rm[j]:
                        r[0] += C1[i, j]; r[1] += sv; r[4] += C0[i, j]
                    else:
                        r[2] += C1[i, j]; r[3] += sv; r[5] += C0[i, j]
            out.append(r)
    return np.array(out, float).reshape(-1, 6)


def pair_est(S):
    t = S.sum(0)
    rs = t[0] / t[1] if t[1] > 0 else np.nan
    rx = t[2] / t[3] if t[3] > 0 else np.nan
    r0s = t[4] / t[1] if t[1] > 0 else np.nan
    r0x = t[5] / t[3] if t[3] > 0 else np.nan
    share = t[0] / (t[0] + t[2]) if (t[0] + t[2]) != 0 else np.nan
    return {"r1_same": rs, "r1_cross": rx, "r1_diff": rs - rx, "Pi": rs / rx if rx and np.isfinite(rx) else np.nan,
            "r0_same": r0s, "r0_cross": r0x, "share_same_lag1": share}


def pair_boot(S, B=400, rng=None):
    rng = rng or np.random.default_rng(2)
    e = pair_est(S)
    out = dict(e)
    if len(S) < 4:
        return out
    dr = defaultdict(list)
    for _ in range(B):
        ee = pair_est(S[rng.integers(0, len(S), len(S))])
        for k, v in ee.items():
            dr[k].append(v)
    for k in e:
        lo, hi, se = ci(dr[k])
        out[k + "_lo"], out[k + "_hi"], out[k + "_se"] = lo, hi, se
    return out


# ============================================================================== simulator on the call skeleton
def skeleton(calls: pl.DataFrame, msgs: pl.DataFrame):
    """Per-call arrays for the simulator (all receiving calls of the unit) plus real rates and naming share."""
    C = calls.sort("day", "t", "turn_id")
    st = (C.group_by("agent", "day", "is_chat", "is_wake").agg(pl.col("talk").cast(pl.Float64).mean().alias("b")))
    C = C.join(st, on=["agent", "day", "is_chat", "is_wake"], how="left")
    named_share = float((msgs["named"].list.len() > 0).mean()) if msgs.height else 0.0
    return {"C": C, "named_share": named_share}


def simulate(sk, rng, g1=0.0, hop=1, kappa=19.0, fast_amp=0.0, fast_tau=15.0, drive_amp=0.0, drive_tau=300.0,
             drive_room=False, r_bar=10.0):
    """Talk at every real receiving call. p = b (1 - g1) exp(field) + J * (unnamed + kappa * named reads at hop `hop`).
    Fields: fast village field (lifetime fast_tau s) and slow drive (village-wide or per room, lifetime drive_tau s), both
    log-normal multiplicative with unit mean. One synthetic message per talk call, posted at t_first in the call's room,
    naming one random other present agent of that room with probability named_share (real). Returns (calls with
    synthetic `talk`, synthetic msgs frame)."""
    C = sk["C"]
    q = sk["named_share"]
    out_talk = np.zeros(C.height, bool)
    msgs = []
    J_u = g1 / (r_bar * (1 + (kappa - 1) * max(q, 1e-6) / max(r_bar, 1))) if g1 > 0 else 0.0
    for d in sorted(C["day"].unique().to_list()):
        sel = np.flatnonzero(C["day"].to_numpy() == d)
        ag = C["agent"].to_numpy()[sel]
        t = C["t"].to_numpy()[sel]
        tf = C["tf"].to_numpy()[sel]
        rm = C["room"].fill_null(-1).to_numpy()[sel]
        b = C["b"].to_numpy()[sel]
        n = len(sel)
        # events: (time, type 0 = post, 1 = call, idx); posts are processed before calls at equal time
        ev_t = np.r_[tf, t]
        ev_k = np.r_[np.zeros(n, np.int8), np.ones(n, np.int8)]
        ev_i = np.r_[np.arange(n), np.arange(n)]
        order = np.lexsort((ev_k, ev_t))
        talk = np.zeros(n, bool)
        named_to = np.full(n, -1)
        rooms = sorted(set(rm.tolist()))
        ridx = {r: k for k, r in enumerate(rooms)}
        cum = np.zeros(len(rooms))           # posts per room so far
        own = defaultdict(lambda: np.zeros(len(rooms)))   # own posts per agent per room
        recv = defaultdict(lambda: np.zeros(len(rooms)))  # posts naming agent per room
        last = {}                            # agent -> (cum snapshot, own snapshot, recv snapshot)
        prev_reads = {}                      # agent -> (unnamed, named) reads at its previous call
        present = defaultdict(set)           # room -> agents seen calling there today
        f_fast, f_drive = 0.0, np.zeros(len(rooms))
        t_last = None
        for e in order:
            i, kind, te = ev_i[e], ev_k[e], ev_t[e]
            if t_last is not None and te > t_last:
                dtv = te - t_last
                if fast_amp > 0:
                    a = math.exp(-dtv / fast_tau)
                    f_fast = f_fast * a + math.sqrt(1 - a * a) * rng.standard_normal()
                if drive_amp > 0:
                    a = math.exp(-dtv / drive_tau)
                    if drive_room:
                        f_drive = f_drive * a + math.sqrt(1 - a * a) * rng.standard_normal(len(rooms))
                    else:
                        f_drive[:] = f_drive[0] * a + math.sqrt(1 - a * a) * rng.standard_normal()
            t_last = te
            r = rm[i]
            if r < 0:
                continue
            k = ridx[r]
            a_ = ag[i]
            if kind == 0:
                if talk[i]:
                    cum[k] += 1
                    own[a_][k] += 1
                    others = [x for x in present[r] if x != a_]
                    if others and rng.random() < q:
                        tgt = others[rng.integers(0, len(others))]
                        named_to[i] = tgt
                        recv[tgt][k] += 1
                continue
            present[r].add(a_)
            snap = last.get(a_)
            if snap is None:
                ru, rn = 0.0, 0.0
            else:
                c0, o0, n0 = snap
                tot = (cum[k] - c0[k]) - (own[a_][k] - o0[k])
                rn = recv[a_][k] - n0[k]
                ru = max(tot - rn, 0.0)
            last[a_] = (cum.copy(), own[a_].copy(), recv[a_].copy())
            if hop == 1:
                xu, xn = ru, rn
            else:
                xu, xn = prev_reads.get(a_, (0.0, 0.0))
            prev_reads[a_] = (ru, rn)
            p = b[i] * (1 - g1)
            fld = 0.0
            if fast_amp > 0:
                fld += fast_amp * f_fast - fast_amp ** 2 / 2
            if drive_amp > 0:
                fld += drive_amp * f_drive[k] - drive_amp ** 2 / 2
            if fld != 0.0:
                p *= math.exp(fld)
            p += J_u * (xu + kappa * xn)
            talk[i] = rng.random() < min(max(p, 0.0), 0.98)
        out_talk[sel] = talk
        for j in np.flatnonzero(talk):
            msgs.append((tf[j], d, int(rm[j]) if rm[j] >= 0 else None, int(ag[j]),
                         [int(named_to[j])] if named_to[j] >= 0 else []))
    Cs = C.with_columns(pl.Series("talk", out_talk))
    M = pl.DataFrame(msgs, schema={"t": pl.Float64, "day": pl.Int16, "room": pl.Int8, "agent": pl.Int8,
                                   "named": pl.List(pl.Int8)}, orient="row")
    return Cs, M
