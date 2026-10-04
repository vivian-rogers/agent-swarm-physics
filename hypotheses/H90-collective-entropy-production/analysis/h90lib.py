"""H90 library: collective entropy production beyond the parts (AIK max-ent bound with nested observable sets).

Estimator (Aguilera, Ito & Kolchinsky 2026; Newton-step form): for antisymmetric observables g of a stationary process,
Sigma_g ~= 2 <g>' K^-1 <g>. Cross-fitted over day folds as in H05/H14's `ep_gauss_crossfit` / `newton_subsets`
(re-implemented here, not imported): sigma = 2 mean_{a != b} gbar_a' K^-1 gbar_b, unbiased at Sigma = 0.
Nested sets: sigma_coll = Sigma(single + coupling) - Sigma(single) >= 0 in the population.

Surrogates: per-agent block flips (H76 amendment A1: time-reverse each agent's block with probability 1/2; the floor)
and per-agent block shifts (circular shift of each agent's trimmed-day sequence by whole blocks; the HH kill null).

Data layout: a period is a list of days; each day is a dict with
  'agents'  global agent indices (into the period's agent list) present that day
  'X'       (n_agents_day, T, K) trimmed soft states (behavior, K = 5) or (n_agents_day, T) 0/1 spins (talk/activity)
Every array here is already restricted to the DQ8 all-present window of the day (contiguous).
"""
from __future__ import annotations

import os

for _v in ("POLARS_MAX_THREADS", "OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "2")

import json  # noqa: E402
from pathlib import Path  # noqa: E402

import numpy as np  # noqa: E402

ROOT = Path(__file__).resolve().parents[3]
SH = ROOT / "data/processed/shared"
OUTD = ROOT / "data/processed/H90-collective-entropy-production"

COARSE = ["absent", "work", "explore", "coord", "wait"]
CPL_STATES = [1, 2, 3, 4]          # behavior coupling observables on work, explore, coord, wait (absent excluded)
PAIRS5 = [(a, b) for a in range(5) for b in range(a + 1, 5)]
BLOCK = {"behavior": 6, "talk": 30, "activity": 30}      # 30-min blocks
STEPS_PER_H = {"behavior": 12, "talk": 60, "activity": 60}
RIDGE = 1e-3


# ============================================================================ features
def partner_weights(present: np.ndarray, kind: str, w: np.ndarray | None = None, room: np.ndarray | None = None) -> np.ndarray:
    """(n, n) row-stochastic partner matrix among the day's present agents (global ids `present`).
    kind: 'all' | 'named' (weights w[j, i] = messages by j naming i) | 'unnamed' (w_ji = w_ij = 0) | 'same' | 'cross'.
    Rows with no partner are zero."""
    n = len(present)
    off = ~np.eye(n, dtype=bool)
    if kind == "all":
        M = off.astype(float)
    elif kind == "named":
        M = w[np.ix_(present, present)].T.astype(float) * off          # M[i, j] = w[j, i]
    elif kind == "unnamed":
        ww = w[np.ix_(present, present)]
        M = ((ww == 0) & (ww.T == 0) & off).astype(float)
    elif kind == "same":
        r = room[present]
        M = ((r[:, None] == r[None, :]) & off & (r[:, None] >= 0)).astype(float)
    elif kind == "cross":
        r = room[present]
        M = ((r[:, None] != r[None, :]) & off & (r[:, None] >= 0) & (r[None, :] >= 0)).astype(float)
    else:
        raise ValueError(kind)
    rs = M.sum(1, keepdims=True)
    return np.divide(M, rs, out=np.zeros_like(M), where=rs > 0)


def day_features(day: dict, channel: str, n_glob: int, sets: dict, pairs: list | None = None) -> np.ndarray:
    """Antisymmetric observables for one trimmed day. Returns (T_samples, d) with the column layout of `layout`.
    sets: {name: (n, n) partner matrix over the day's present agents} (order defines the layout)."""
    ag = np.asarray(day["agents"])
    X = day["X"]
    if channel == "behavior":
        A, B = X[:, :-1, :], X[:, 1:, :]                               # (n, T-1, 5)
        T = A.shape[1]
        if T < 1:
            return np.zeros((0, 0))
        single = np.zeros((T, n_glob, len(PAIRS5)), np.float32)
        for k, (a, b) in enumerate(PAIRS5):
            single[:, ag, k] = (A[:, :, a] * B[:, :, b] - A[:, :, b] * B[:, :, a]).T
        cols = [single.reshape(T, -1)]
        for nm, M in sets.items():
            c = np.zeros((T, n_glob, len(CPL_STATES)), np.float32)
            for k, a in enumerate(CPL_STATES):
                s0, s1 = A[:, :, a], B[:, :, a]                         # (n, T)
                h0, h1 = M @ s0, M @ s1
                c[:, ag, k] = (s1 * h0 - s0 * h1).T
            cols.append(c.reshape(T, -1))
    else:
        S = X.astype(np.float32)
        if S.shape[1] < 3:
            return np.zeros((0, 0))
        s0, s1, s2 = S[:, :-2], S[:, 1:-1], S[:, 2:]
        T = s0.shape[1]
        single = np.zeros((T, n_glob, 2), np.float32)
        p001 = (1 - s0) * (1 - s1) * s2
        p100 = s0 * (1 - s1) * (1 - s2)
        p011 = (1 - s0) * s1 * s2
        p110 = s0 * s1 * (1 - s2)
        single[:, ag, 0] = (p001 - p100).T
        single[:, ag, 1] = (p011 - p110).T
        cols = [single.reshape(T, -1)]
        for nm, M in sets.items():
            c = np.zeros((T, n_glob), np.float32)
            h0, h1 = M @ s0, M @ s1
            c[:, ag] = (s1 * h0 - s0 * h1).T
            cols.append(c)
        if pairs is not None:                                           # full pairwise (N2): g_ij = s_i' s_j - s_i s_j'
            pos = {g: k for k, g in enumerate(ag)}
            c = np.zeros((T, len(pairs)), np.float32)
            for k, (i, j) in enumerate(pairs):
                if i in pos and j in pos:
                    a, b = pos[i], pos[j]
                    c[:, k] = s1[a] * s0[b] - s0[a] * s1[b]
            cols.append(c)
    return np.concatenate(cols, 1)


def layout(channel: str, n_glob: int, set_names: list, n_pairs: int = 0) -> dict:
    """Column index arrays: 'single', 'single_i' (list per agent), and one entry per coupling set (+ 'pairs')."""
    per = len(PAIRS5) if channel == "behavior" else 2
    cpl = len(CPL_STATES) if channel == "behavior" else 1
    out = {"single": np.arange(n_glob * per), "single_i": [np.arange(i * per, (i + 1) * per) for i in range(n_glob)]}
    blocks = [np.zeros(n_glob * per, int)]
    off = n_glob * per
    for b, nm in enumerate(set_names, start=1):
        out[nm] = np.arange(off, off + n_glob * cpl)
        blocks.append(np.full(n_glob * cpl, b))
        off += n_glob * cpl
    if n_pairs:
        out["pairs"] = np.arange(off, off + n_pairs)
        blocks.append(np.full(n_pairs, len(set_names) + 1))
        off += n_pairs
    out["d"] = off
    out["block"] = np.concatenate(blocks)
    return out


# ============================================================================ sufficient statistics and estimator
def day_stats(G: np.ndarray):
    G = G.astype(np.float64)
    return G.shape[0], G.sum(0), G.T @ G


def fold_ids(n_days: int, k: int | None = None) -> np.ndarray:
    k = min(10, n_days) if k is None else k
    return np.arange(n_days) % k


RIDGE_HO = 1.0     # held-out ridge c: lambda_k = c (K_kk + block mean diag) (A1 c chosen on synthetic; A2 block floor)


def newton_from_stats(stats: list, subsets: dict, folds: np.ndarray, mult: np.ndarray | None = None,
                      ridge: float | None = None, block: np.ndarray | None = None) -> dict:
    """Held-out Newton bound (primary, amendment A1). For each day fold f: theta_f = 2 (K_-f + lambda I)^-1 mu_-f on
    the other folds (per-column ridge lambda_k = c (K_kk + block mean diag), A2), and the second-order AIK dual on fold f,
    L_f = 2 theta_f' mu_f - 1/2 theta_f' K_f theta_f. Returns the n-weighted mean of L_f per subset. L(theta) is a lower
    bound (to second order) for ANY theta fitted without fold f, so overfitting lowers it instead of inflating it.
    stats: list of (n_d, s1_d, s2_d); mult: bootstrap multiplicity per day (copies stay in the day's fold)."""
    c = RIDGE_HO if ridge is None else ridge
    m = np.ones(len(stats)) if mult is None else mult
    fs = [f for f in np.unique(folds) if (m[folds == f] > 0).any()]
    if len(fs) < 2:
        return {nm: np.nan for nm in subsets}
    fst = {}
    for f in fs:
        idx = np.nonzero((folds == f) & (m > 0))[0]
        fst[f] = (sum(m[d] * stats[d][0] for d in idx), sum(m[d] * stats[d][1] for d in idx),
                  sum(m[d] * stats[d][2] for d in idx))
    tot = (sum(v[0] for v in fst.values()), sum(v[1] for v in fst.values()), sum(v[2] for v in fst.values()))
    out = {nm: 0.0 for nm in subsets}
    wsum = 0.0
    for f in fs:
        nf, s1f, s2f = fst[f]
        if nf < 2:
            continue
        nt, s1t, s2t = tot[0] - nf, tot[1] - s1f, tot[2] - s2f
        mut, muf = s1t / nt, s1f / nf
        Kt = (s2t - nt * np.outer(mut, mut)) / max(nt - 1, 1)
        Kf = (s2f - nf * np.outer(muf, muf)) / max(nf - 1, 1)
        dK = np.clip(np.diag(Kt), 0, None)
        if block is not None:                       # block floor: lambda_k = c (K_kk + mean diag of k's block)
            bm = np.array([dK[block == b].mean() for b in range(block.max() + 1)])
            lam_all = c * (dK + bm[block])
        else:
            lam_all = c * dK
        for nm, cols in subsets.items():
            cols = np.asarray(cols)
            if len(cols) == 0:
                out[nm] = np.nan
                continue
            Ks = Kt[np.ix_(cols, cols)]
            tr = np.trace(Ks)
            if tr <= 0:
                continue
            lam = np.clip(lam_all[cols], 1e-12 * tr / len(cols), None)
            th = 2 * np.linalg.solve(Ks + np.diag(lam), mut[cols])     # per-column ridge: nested sets shrink alike
            out[nm] += nf * (2 * th @ muf[cols] - 0.5 * th @ Kf[np.ix_(cols, cols)] @ th)
        wsum += nf
    return {nm: (v / wsum if wsum > 0 and np.isfinite(v) else np.nan) for nm, v in out.items()}


def newton_xprod_from_stats(stats: list, subsets: dict, folds: np.ndarray, mult: np.ndarray | None = None,
                            ridge: float = RIDGE) -> dict:
    """H05/H14's cross-product form (companion only; unstable when d ~ n, see amendment A1).
    stats: list of (n_d, s1_d, s2_d); folds: fold id per day; mult: bootstrap multiplicity per day (copies stay in the
    day's fold). Returns {name: sigma per system step}."""
    m = np.ones(len(stats)) if mult is None else mult
    keep = m > 0
    if keep.sum() < 2:
        return {nm: np.nan for nm in subsets}
    n = sum(m[d] * stats[d][0] for d in range(len(stats)))
    s1 = sum(m[d] * stats[d][1] for d in range(len(stats)))
    s2 = sum(m[d] * stats[d][2] for d in range(len(stats)))
    mu = s1 / n
    K = (s2 - n * np.outer(mu, mu)) / max(n - 1, 1)
    fs = [f for f in np.unique(folds[keep])]
    means = []
    for f in fs:
        idx = np.nonzero((folds == f) & keep)[0]
        nf = sum(m[d] * stats[d][0] for d in idx)
        if nf > 0:
            means.append(sum(m[d] * stats[d][1] for d in idx) / nf)
    means = np.array(means)
    mm = len(means)
    out = {}
    for nm, cols in subsets.items():
        cols = np.asarray(cols)
        if len(cols) == 0 or mm < 2:
            out[nm] = np.nan
            continue
        Ks = K[np.ix_(cols, cols)]
        tr = np.trace(Ks)
        if tr <= 0:
            out[nm] = 0.0
            continue
        Ks = Ks + ridge * tr / len(cols) * np.eye(len(cols))
        Ms = means[:, cols]
        W = np.linalg.solve(Ks, Ms.T).T
        M = Ms @ W.T
        out[nm] = float(2 * (M.sum() - np.trace(M)) / (mm * (mm - 1)))
    return out


def exact_dual_cf(Gs: list, cols: np.ndarray, folds: np.ndarray, ridge: float | None = None,
                  block: np.ndarray | None = None) -> float:
    """Companion: theta = 2 (K_tr + Lambda)^-1 gbar_tr on training folds (the A2 block-floored ridge), and the exact AIK
    dual on the held-out fold, theta'gbar_te - ln mean_te exp(-theta'g); n-weighted mean over folds."""
    c = RIDGE_HO if ridge is None else ridge
    vals, ws = [], []
    for f in np.unique(folds):
        tr = [G[:, cols] for G, ff in zip(Gs, folds) if ff != f and len(G)]
        te = [G[:, cols] for G, ff in zip(Gs, folds) if ff == f and len(G)]
        if not tr or not te:
            continue
        Gt = np.concatenate(tr).astype(np.float64)
        Ge = np.concatenate(te).astype(np.float64)
        K = np.cov(Gt, rowvar=False).reshape(len(cols), len(cols))
        dK = np.clip(np.diag(K), 0, None)
        if block is not None:
            b = block[cols]
            lam = c * (dK + np.array([dK[b == v].mean() for v in b]))
        else:
            lam = c * dK
        lam = np.clip(lam, 1e-12 * max(np.trace(K), 1e-12) / len(cols), None)
        th = 2 * np.linalg.solve(K + np.diag(lam), Gt.mean(0))
        z = Ge @ th
        zm = (-z).max()
        vals.append(z.mean() - (zm + np.log(np.mean(np.exp(-z - zm)))))
        ws.append(len(Ge))
    return float(np.average(vals, weights=ws)) if vals else np.nan


# ============================================================================ surrogates
def block_flip(days: list, B: int, rng: np.random.Generator) -> list:
    out = []
    for d in days:
        X = d["X"].copy()
        T = X.shape[1]
        for i in range(X.shape[0]):
            for s in range(0, T, B):
                if rng.random() < 0.5:
                    X[i, s:s + B] = X[i, s:s + B][::-1]
        out.append({**d, "X": X})
    return out


def block_shift(days: list, B: int, rng: np.random.Generator) -> list:
    out = []
    for d in days:
        X = d["X"].copy()
        T = X.shape[1]
        nb = T // B
        for i in range(X.shape[0]):
            if nb >= 2:
                k = int(rng.integers(1, nb)) * B
            else:
                k = int(rng.integers(1, max(T, 2)))
            X[i] = np.roll(X[i], k, axis=0)
        out.append({**d, "X": X})
    return out


# ============================================================================ period pipeline
DEFAULT_SETS = ("all", "named", "unnamed")


def build_stats(days: list, channel: str, n_glob: int, w: np.ndarray | None, set_names=DEFAULT_SETS,
                room: np.ndarray | None = None, pairs: list | None = None, keep_G: bool = False):
    stats, Gs = [], []
    for d in days:
        pres = np.asarray(d["agents"])
        rm = d.get("room", room)
        sets = {nm: partner_weights(pres, nm, w, rm) for nm in set_names}
        G = day_features(d, channel, n_glob, sets, pairs)
        if G.shape[0] == 0:
            G = np.zeros((0, layout(channel, n_glob, list(set_names), len(pairs) if pairs else 0)["d"]), np.float32)
        stats.append(day_stats(G))
        if keep_G:
            Gs.append(G)
    return stats, Gs


def subsets_for(lay: dict, set_names, per_agent: bool = True) -> dict:
    sub = {"single": lay["single"]}
    for nm in set_names:
        sub[f"single+{nm}"] = np.r_[lay["single"], lay[nm]]
    if "pairs" in lay:
        sub["single+pairs"] = np.r_[lay["single"], lay["pairs"]]
    if per_agent:
        for i, c in enumerate(lay["single_i"]):
            sub[f"agent{i}"] = c
    return sub


def summarize(raw: dict, n_glob: int, set_names) -> dict:
    s1 = raw["single"]
    out = {"Sigma1": s1, "sum_sigma_i": float(np.nansum([raw.get(f"agent{i}", 0.0) for i in range(n_glob)]))}
    for nm in set_names:
        out[f"Sigma1_{nm}"] = raw[f"single+{nm}"]
        out[f"coll_{nm}"] = raw[f"single+{nm}"] - s1
    if "single+pairs" in raw:
        out["Sigma1_pairs"] = raw["single+pairs"]
        out["coll_pairs"] = raw["single+pairs"] - s1
    out["addr"] = out.get("coll_named", np.nan) - out.get("coll_unnamed", np.nan)
    tot = out.get("Sigma1_all", np.nan)
    out["rho_coll"] = out["coll_all"] / tot if (np.isfinite(tot) and tot > 0) else np.nan
    return out


def period_estimate(days: list, channel: str, n_glob: int, w, set_names=DEFAULT_SETS, room=None, pairs=None,
                    per_agent=True, folds=None):
    lay = layout(channel, n_glob, list(set_names), len(pairs) if pairs else 0)
    stats, _ = build_stats(days, channel, n_glob, w, set_names, room, pairs)
    folds = fold_ids(len(days)) if folds is None else folds
    raw = newton_from_stats(stats, subsets_for(lay, set_names, per_agent), folds, block=lay["block"])
    return summarize(raw, n_glob, set_names), stats, lay, folds


def bootstrap(stats, lay, folds, n_glob, set_names, B, rng, per_agent=False) -> dict:
    sub = subsets_for(lay, set_names, per_agent)
    acc = []
    nd = len(stats)
    for _ in range(B):
        mult = np.bincount(rng.integers(0, nd, nd), minlength=nd).astype(float)
        acc.append(summarize(newton_from_stats(stats, sub, folds, mult, block=lay["block"]), n_glob, set_names))
    keys = acc[0].keys()
    return {k: [float(np.nanpercentile([a[k] for a in acc], 2.5)), float(np.nanpercentile([a[k] for a in acc], 97.5))]
            for k in keys}


def null_dist(days, channel, n_glob, w, kind, R, rng, set_names=DEFAULT_SETS, room=None, pairs=None, folds=None):
    B = BLOCK[channel]
    f = block_shift if kind == "shift" else block_flip
    out = []
    for _ in range(R):
        s, _, _, _ = period_estimate(f(days, B, rng), channel, n_glob, w, set_names, room, pairs, per_agent=False,
                                     folds=folds)
        out.append(s)
    return out


def pval(obs: float, null: list) -> float:
    v = np.array([x for x in null if np.isfinite(x)])
    if not np.isfinite(obs) or len(v) == 0:
        return np.nan
    return float((1 + (v >= obs).sum()) / (len(v) + 1))


def per_agent_hour(sig: float, channel: str, nbar: float) -> float:
    return sig * STEPS_PER_H[channel] / nbar if nbar > 0 else np.nan


def write_json(path: Path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)

    def enc(o):
        if hasattr(o, "item"):
            return o.item()
        if isinstance(o, np.ndarray):
            return o.tolist()
        return str(o)
    path.write_text(json.dumps(obj, indent=1, default=enc))
