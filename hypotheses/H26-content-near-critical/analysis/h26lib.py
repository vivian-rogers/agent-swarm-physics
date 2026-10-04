"""H26 estimators: drive-removed equal-time loop gains for content (32-d), activity and talk (scalars).

One estimand for every channel (H19's equal-time loop gain): g = 1 - 1/VR, VR = 1 + (N_r - 1) rho,
rho = sum_pairs tr C_ab / sum_pairs sqrt(S_a S_b), with S_a the split-half (sampling-noise-free) signal variance.

Data-structure agnostic: everything takes a `Panel` (one unit x one channel x one resolution), so the synthetic
validation, the real-data exploration and the confirm script run the same code.

Panel (n_obs observations = agent x time slot)
  agent (n,) int agent code; t (n,) int time-slot index (day index, or day*W + window); day (n,) int day index;
  wod (n,) int window-of-day (0 at day resolution); room (n,) int room code at that slot (-1 unknown);
  X (n, d) full-sample mean state; A, B (n, S, d) split-half means for S random splits (NaN rows = unavailable);
  grp (n,) int deviation group (agent at day and w30 resolution; agent-day at the within-day resolution wd);
  static (k0, d) orthonormal static-field directions (content only; None for scalars);
  exo: dict t -> (k_t, d) exogenous directions active at slot t (content), or None;
  Z (n, p) exogenous counts for scalar channels (L2 regression), or None.

Ladder levels: 0 = group-mean deviations; 1 = + static projection; 2 = + exogenous projection / regression
(no time-of-day removal, Amendment 1); 3 = 2 evaluated as within - cross (computed from the same contributions as 2);
4 = 2 + per-room-day projection of the top-3 directions of that room's slot-mean deviations on OTHER days.
"""
from __future__ import annotations

import os

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "VECLIB_MAXIMUM_THREADS", "NUMEXPR_NUM_THREADS"):
    os.environ[_v] = "2"

from dataclasses import dataclass, field, replace  # noqa: E402

import numpy as np  # noqa: E402


@dataclass
class Panel:
    agent: np.ndarray
    t: np.ndarray
    day: np.ndarray
    wod: np.ndarray
    room: np.ndarray
    X: np.ndarray
    A: np.ndarray
    B: np.ndarray
    grp: np.ndarray
    static: np.ndarray | None = None
    exo: dict | None = None
    Z: np.ndarray | None = None
    res: str = "day"          # "day" | "w30" (equal-time 30-min, deviations from agent unit mean) | "wd" (within-day)
    meta: dict = field(default_factory=dict)


def orthobasis(V, tol=1e-6):
    """Orthonormal rows spanning the rows of V (k, d)."""
    V = np.atleast_2d(np.asarray(V, float))
    V = V[np.isfinite(V).all(1) & (np.linalg.norm(V, axis=1) > 1e-12)]
    if len(V) == 0:
        return np.zeros((0, 0))
    U, s, Wt = np.linalg.svd(V, full_matrices=False)
    return Wt[s > tol * max(s.max(), 1e-12)]


def _project_out(M, Q):
    """Remove span(Q rows) from rows of M (last axis = d). Q (k, d) orthonormal."""
    if Q is None or Q.size == 0:
        return M
    return M - (M @ Q.T) @ Q


def _group_dev(M, grp, valid):
    """Deviations of rows of M from their group mean over valid rows; returns (dev, n_g per row)."""
    d = M.shape[-1]
    ug, inv = np.unique(grp, return_inverse=True)
    s = np.zeros((len(ug), d)); c = np.zeros(len(ug))
    Mv = np.where(valid[:, None], M, 0.0)
    np.add.at(s, inv, Mv); np.add.at(c, inv, valid.astype(float))
    mean = s / np.maximum(c, 1)[:, None]
    dev = np.where(valid[:, None], M - mean[inv], 0.0)
    return dev, c[inv]


def deviations(P: Panel, level: int):
    """Field-removed deviations (dX (n, d), dA, dB (n, S, d), okX (n,), okS (n, S)) at ladder level 0/1/2/4."""
    n, d = P.X.shape
    S = P.A.shape[1]
    okX = np.isfinite(P.X).all(1)
    X = np.where(okX[:, None], P.X, 0.0)
    dX, ng = _group_dev(X, P.grp, okX)
    okX = okX & (ng >= 2)
    f = np.where(ng >= 2, ng / np.maximum(ng - 1, 1), 0.0)
    dX = dX * np.sqrt(f)[:, None]
    dA = np.zeros_like(P.A); dB = np.zeros_like(P.B); okS = np.zeros((n, S), bool)
    for s in range(S):
        ok = np.isfinite(P.A[:, s]).all(1) & np.isfinite(P.B[:, s]).all(1)
        a, na = _group_dev(np.where(ok[:, None], P.A[:, s], 0.0), P.grp, ok)
        b, _ = _group_dev(np.where(ok[:, None], P.B[:, s], 0.0), P.grp, ok)
        ok = ok & (na >= 2)
        fa = np.where(na >= 2, na / np.maximum(na - 1, 1), 0.0)
        dA[:, s] = a * np.sqrt(fa)[:, None]; dB[:, s] = b * np.sqrt(fa)[:, None]; okS[:, s] = ok
    if level >= 1 and P.static is not None and P.static.size:
        dX = _project_out(dX, P.static); dA = _project_out(dA, P.static); dB = _project_out(dB, P.static)
    if level >= 2:
        if P.exo is not None:
            for tt in np.unique(P.t):
                Q = P.exo.get(int(tt))
                if Q is None or Q.size == 0:
                    continue
                if P.static is not None and P.static.size:
                    Q = orthobasis(np.vstack([P.static, Q]))
                m = P.t == tt
                dX[m] = _project_out(dX[m], Q); dA[m] = _project_out(dA[m], Q); dB[m] = _project_out(dB[m], Q)
        if P.Z is not None and P.Z.shape[1]:
            Zd, _ = _group_dev(P.Z.astype(float), P.grp, okX)
            beta, *_ = np.linalg.lstsq(Zd[okX], dX[okX], rcond=None)
            dX = dX - Zd @ beta
            for s in range(S):
                dA[:, s] -= Zd @ beta; dB[:, s] -= Zd @ beta
        # No time-of-day profile removal (Amendment 1): any estimated common profile biases within- and cross-room
        # covariances alike (pooled: -Var_total/n; cross-fitted: +Var(m)), because sampling noise dominates a
        # 30-min content state. Time of day is a global drive and is removed by L3 (within - cross).
        dX[~okX] = 0
    if level >= 4:
        dX, dA, dB = _l4(P, dX, dA, dB, okX)
    return dX, dA, dB, okX, okS


def _tod_remove(M, ok, wod, day):
    """Subtract, for each row, the mean of ok rows with the same window-of-day on other days."""
    out = M.copy()
    days = np.unique(day)
    for w in np.unique(wod):
        mw = (wod == w) & ok
        if mw.sum() < 3:
            continue
        tot = M[mw].sum(0); cnt = mw.sum()
        for dd in days:
            md = mw & (day == dd)
            if not md.any():
                continue
            c = cnt - md.sum()
            if c < 2:
                continue
            out[md] = M[md] - (tot - M[md].sum(0)) / c
    return out


def _l4(P, dX, dA, dB, okX, k=3):
    """Per room-day: project out the top-k directions of that room's slot-mean deviations on the other days.
    At day resolution with < 8 days, k = 1 (k = 3 would span almost all other-day room means)."""
    d = dX.shape[1]
    if d < 2:  # scalar channels: L4 = L2
        return dX, dA, dB
    if P.res == "day" and len(np.unique(P.day)) < 8:
        k = 1
    rooms = np.unique(P.room[P.room >= 0])
    keys = {}
    for r in rooms:
        for tt in np.unique(P.t[(P.room == r) & okX]):
            m = (P.room == r) & (P.t == tt) & okX
            if m.sum() >= 2:
                keys[(r, tt)] = (P.day[m][0], dX[m].mean(0))
    for r in rooms:
        days_r = sorted({v[0] for (rr, _), v in keys.items() if rr == r})
        for dd in days_r:
            M = np.array([v[1] for (rr, _), v in keys.items() if rr == r and v[0] != dd])
            if len(M) < k:
                continue
            _, _, Wt = np.linalg.svd(M - 0 * M.mean(0), full_matrices=False)
            Q = Wt[:k]
            m = (P.room == r) & (P.day == dd)
            dX[m] = _project_out(dX[m], Q); dA[m] = _project_out(dA[m], Q); dB[m] = _project_out(dB[m], Q)
    return dX, dA, dB


def contributions(P: Panel, dX, dA, dB, okX, okS, room=None):
    """Per-day additive sums: within/cross pair sums and counts (N x N), split-half signal sums per agent,
    room-mate and other-agent counts. Agents are re-indexed 0..N-1."""
    room = P.room if room is None else room
    ags, ai = np.unique(P.agent, return_inverse=True)
    days = np.unique(P.day)
    di = np.searchsorted(days, P.day)
    N, D = len(ags), len(days)
    Cw = np.zeros((D, N, N)); Nw = np.zeros((D, N, N)); Cc = np.zeros((D, N, N)); Nc = np.zeros((D, N, N))
    s_sum = np.zeros((D, N)); s_cnt = np.zeros((D, N))
    rm = np.zeros(D); oth = np.zeros(D); nobs = np.zeros(D)
    Ssplit = (dA * dB).sum(-1)  # (n, S)
    sval = np.where(okS, Ssplit, 0).sum(1); scnt = okS.sum(1)
    has = scnt > 0
    np.add.at(s_sum, (di[has], ai[has]), sval[has] / scnt[has])
    np.add.at(s_cnt, (di[has], ai[has]), 1.0)
    order = np.argsort(P.t, kind="stable")
    tt_sorted = P.t[order]
    starts = np.r_[0, np.flatnonzero(np.diff(tt_sorted)) + 1, len(order)]
    for k in range(len(starts) - 1):
        idx = order[starts[k]:starts[k + 1]]
        idx = idx[okX[idx]]
        if len(idx) < 2:
            continue
        G = dX[idx] @ dX[idx].T
        a = ai[idx]; r = room[idx]; dd = di[idx[0]]
        same = (r[:, None] == r[None, :]) & (r[:, None] >= 0)
        cross = (r[:, None] != r[None, :]) & (r[:, None] >= 0) & (r[None, :] >= 0)
        iu = np.triu_indices(len(idx), 1)
        aa, bb = a[iu[0]], a[iu[1]]
        lo, hi = np.minimum(aa, bb), np.maximum(aa, bb)
        g = G[iu]
        w = same[iu]; c = cross[iu]
        np.add.at(Cw[dd], (lo[w], hi[w]), g[w]); np.add.at(Nw[dd], (lo[w], hi[w]), 1)
        np.add.at(Cc[dd], (lo[c], hi[c]), g[c]); np.add.at(Nc[dd], (lo[c], hi[c]), 1)
        rm[dd] += (same.sum(1) - 1).clip(0).sum(); oth[dd] += len(idx) * (len(idx) - 1); nobs[dd] += len(idx)
    return dict(Cw=Cw, Nw=Nw, Cc=Cc, Nc=Nc, s_sum=s_sum, s_cnt=s_cnt, rm=rm, oth=oth, nobs=nobs, agents=ags, days=days)


def gains(C, w=None):
    """Loop gains from (optionally day-weighted) contributions."""
    D = C["Cw"].shape[0]
    w = np.ones(D) if w is None else np.asarray(w, float)
    S = np.tensordot(w, C["s_sum"], 1) / np.maximum(np.tensordot(w, C["s_cnt"], 1), 1e-12)
    okS = np.tensordot(w, C["s_cnt"], 1) > 0
    S = np.where(okS, np.maximum(S, 1e-9), np.nan)
    sq = np.sqrt(np.outer(S, S))
    out = {}
    for typ in ("w", "c"):
        num = np.tensordot(w, C["C" + typ], 1); cnt = np.tensordot(w, C["N" + typ], 1)
        m = np.isfinite(sq) & (cnt > 0)
        den = (cnt * np.where(m, sq, 0)).sum()
        out["rho_" + typ] = float(num[m].sum() / den) if den > 0 else np.nan
        out["den_" + typ] = float(den)
        out["npair_" + typ] = int((cnt > 0).sum())
    dw, dc = out["den_w"], out["den_c"]
    out["rho_all"] = float((out["rho_w"] * dw + (out["rho_c"] * dc if dc > 0 else 0)) / (dw + dc)) if dw + dc > 0 else np.nan
    nob = (w * C["nobs"]).sum()
    out["Nr"] = 1 + (w * C["rm"]).sum() / max(nob, 1e-12)
    out["Nall"] = 1 + (w * C["oth"]).sum() / max(nob, 1e-12)
    out["S_mean"] = float(np.nanmean(S))

    def g_of(Nm1, rho):
        if not np.isfinite(rho):
            return np.nan
        R = 1 + Nm1 * rho
        return float(1 - 1 / R) if R > 0 else -np.inf
    out["g_all"] = g_of(out["Nall"] - 1, out["rho_all"])
    out["g_room"] = g_of(out["Nr"] - 1, out["rho_w"])
    out["rho_ex_raw"] = out["rho_w"] - out["rho_c"] if np.isfinite(out["rho_c"]) else np.nan
    out["g_ex_raw"] = g_of(out["Nr"] - 1, out["rho_ex_raw"])
    # Amendment 1(c): the global-drive share is removed from the signal variance too (partial-correlation form);
    # otherwise strong common drives dilute S and bias g_ex down (synthetic activity at w30).
    out["rho_ex"] = out["rho_ex_raw"] / (1 - out["rho_c"]) if np.isfinite(out["rho_c"]) and out["rho_c"] < 1 else np.nan
    out["g_ex"] = g_of(out["Nr"] - 1, out["rho_ex"])
    return out


def bootstrap(C, B=400, rng=None, keys=("g_all", "g_room", "g_ex", "rho_w", "rho_c", "rho_ex")):
    rng = np.random.default_rng(0) if rng is None else rng
    D = C["Cw"].shape[0]
    res = {k: [] for k in keys}
    for _ in range(B):
        w = np.bincount(rng.integers(0, D, D), minlength=D)
        g = gains(C, w)
        for k in keys:
            res[k].append(g[k])
    return {k: np.array(v, float) for k, v in res.items()}


def ci(x, q=(2.5, 97.5)):
    x = np.asarray(x, float)
    x = x[np.isfinite(x)]
    if len(x) < 10:
        return [np.nan, np.nan]
    return [float(np.percentile(x, q[0])), float(np.percentile(x, q[1]))]


def run_level(P: Panel, level: int, room=None):
    lv = 2 if level == 3 else level
    dX, dA, dB, okX, okS = deviations(P, lv)
    C = contributions(P, dX, dA, dB, okX, okS, room=room)
    return C, gains(C), (dX, okX)


# ------------------------------------------------------------------------------------------------ nulls
def shuffle_time(P: Panel, rng):
    """N1: permute each agent's state rows among its own slots (within agent-day at the within-day resolution).
    Keeps each agent's real anisotropic fluctuations."""
    idx = np.arange(len(P.agent))
    perm = idx.copy()
    key = P.agent.astype(np.int64) * 100000 + (P.day if P.res == "wd" else 0)
    for g in np.unique(key):
        m = np.flatnonzero(key == g)
        perm[m] = rng.permutation(m)
    return replace(P, X=P.X[perm], A=P.A[perm], B=P.B[perm])


def permute_rooms(P: Panel, rng):
    """N2: room[a, t] <- room[pi(a), t] (room sizes per slot kept as far as presence allows)."""
    ags = np.unique(P.agent)
    pi = dict(zip(ags, rng.permutation(ags)))
    lut = {(a, t): r for a, t, r in zip(P.agent, P.t, P.room)}
    new = np.array([lut.get((pi[a], t), -1) for a, t in zip(P.agent, P.t)])
    # agents whose partner has no slot keep a random room among those present at t
    miss = new < 0
    if miss.any():
        for i in np.flatnonzero(miss):
            rs = P.room[(P.t == P.t[i]) & (P.room >= 0)]
            new[i] = rng.choice(rs) if len(rs) else -1
    return new


def n_eff(dX, okX):
    """Participation ratio of the pooled deviation covariance (effective fluctuation dimension)."""
    M = dX[okX]
    if len(M) < 3 or M.shape[1] < 2:
        return np.nan
    lam = np.clip(np.linalg.eigvalsh(M.T @ M / len(M)), 0, None)
    return float(lam.sum() ** 2 / (lam ** 2).sum())


def top_mode_gain(P: Panel, dX, okX):
    """Mode-resolved gain along the top direction of room-slot mean deviations (descriptive; selection-biased)."""
    if dX.shape[1] < 2:
        return np.nan
    means = []
    for r in np.unique(P.room[P.room >= 0]):
        for tt in np.unique(P.t[(P.room == r) & okX]):
            m = (P.room == r) & (P.t == tt) & okX
            if m.sum() >= 2:
                means.append(dX[m].mean(0))
    if len(means) < 3:
        return np.nan
    _, _, Wt = np.linalg.svd(np.array(means), full_matrices=False)
    return Wt[0]
