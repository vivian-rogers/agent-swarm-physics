"""H54 estimators shared by the synthetic validation, exploration, natives and confirm.py (pure numpy)."""
from __future__ import annotations

import math

import numpy as np
from scipy import stats


def unit(x, axis=-1):
    x = np.asarray(x, dtype=np.float64)
    n = np.linalg.norm(x, axis=axis, keepdims=True)
    return x / np.where(n > 0, n, 1.0)


# ------------------------------------------------------------------------------ target identification
def colcenter(S: np.ndarray) -> np.ndarray:
    """Genericness correction: subtract each kickoff's (column's) mean score over the OTHER rows."""
    S = np.asarray(S, float)
    P = S.shape[0]
    M = np.where(np.eye(P, dtype=bool), np.nan, S)
    return S - np.nanmean(M, axis=0, keepdims=True)


def own_percentiles(S: np.ndarray, mask: np.ndarray | None = None) -> np.ndarray:
    """Per row p: share of decoys q != p (finite, and mask[p, q] if given) with S[p, q] < S[p, p] (ties half)."""
    P = S.shape[0]
    out = np.full(P, np.nan)
    for p in range(P):
        if not np.isfinite(S[p, p]):
            continue
        d = np.delete(S[p], p)
        if mask is not None:
            d = d[np.delete(mask[p], p)]
        d = d[np.isfinite(d)]
        if len(d):
            out[p] = ((d < S[p, p]).sum() + 0.5 * (d == S[p, p]).sum()) / len(d)
    return out


def top1(S: np.ndarray, mask: np.ndarray | None = None) -> np.ndarray:
    P = S.shape[0]
    out = np.full(P, np.nan)
    for p in range(P):
        if not np.isfinite(S[p, p]):
            continue
        row = S[p].copy()
        if mask is not None:
            row[~mask[p]] = np.nan
            row[p] = S[p, p]
        out[p] = float(np.nanargmax(row) == p)
    return out


def wilcoxon_gt(x, mu=0.5) -> float:
    x = np.asarray(x, float)
    x = x[np.isfinite(x)] - mu
    x = x[x != 0]
    if len(x) < 3:
        return np.nan
    return float(stats.wilcoxon(x, alternative="greater").pvalue)


def p1_verdict(pi: np.ndarray, t1: np.ndarray) -> dict:
    pi = pi[np.isfinite(pi)]
    t1 = t1[np.isfinite(t1)]
    med, top = float(np.median(pi)), float(np.mean(t1))
    pw = wilcoxon_gt(pi)
    ok = med >= 0.90 and top >= 0.50 and pw < 0.001
    bad = med < 0.75 or top < 0.25
    return {"n": int(len(pi)), "median_pi": med, "top1": top, "p_wilcoxon": pw,
            "verdict": "supported" if ok else ("failed" if bad else "mixed")}


# ------------------------------------------------------------------------------ spread
def rarefied_q(groups, n: int = 5, B: int = 50, rng=None) -> float:
    rng = rng if rng is not None else np.random.default_rng(0)
    gs = [g for g in groups if len(g) >= n]
    k = len(gs)
    if k < 3:
        return np.nan
    acc = 0.0
    for _ in range(B):
        V = np.vstack([unit(g[rng.choice(len(g), n, replace=False)].mean(0)) for g in gs])
        G = V @ V.T
        acc += (G.sum() - np.trace(G)) / (k * (k - 1))
    return acc / B


def pairwise_q(V) -> float:
    V = np.asarray(V)
    k = len(V)
    if k < 2:
        return np.nan
    G = V @ V.T
    return float((G.sum() - np.trace(G)) / (k * (k - 1)))


def spearman(x, y, alternative="two-sided"):
    x, y = np.asarray(x, float), np.asarray(y, float)
    m = np.isfinite(x) & np.isfinite(y)
    if m.sum() < 5:
        return np.nan, np.nan, int(m.sum())
    r = stats.spearmanr(x[m], y[m], alternative=alternative)
    return float(r.statistic), float(r.pvalue), int(m.sum())


def partial_spearman(x, y, Z):
    """Spearman of x and y after regressing both ranks on covariates Z (columns)."""
    x, y = np.asarray(x, float), np.asarray(y, float)
    Z = np.atleast_2d(np.asarray(Z, float).T).T if np.ndim(Z) == 1 else np.asarray(Z, float)
    m = np.isfinite(x) & np.isfinite(y) & np.all(np.isfinite(Z), axis=1)
    if m.sum() < 6:
        return np.nan, np.nan
    rx, ry = stats.rankdata(x[m]), stats.rankdata(y[m])
    X = np.column_stack([np.ones(m.sum()), np.apply_along_axis(stats.rankdata, 0, Z[m])])
    ex = rx - X @ np.linalg.lstsq(X, rx, rcond=None)[0]
    ey = ry - X @ np.linalg.lstsq(X, ry, rcond=None)[0]
    r = float(np.corrcoef(ex, ey)[0, 1])
    df = m.sum() - 2 - (X.shape[1] - 1)
    t = r * math.sqrt(df / max(1e-12, 1 - r * r))
    return r, float(2 * stats.t.sf(abs(t), df))


# ------------------------------------------------------------------------------ projects (Potts layer)
def naming_table(named, frozen, strata=None, n_perm: int = 5000, rng=None) -> dict:
    """Precision P(named|frozen), recall P(frozen|named), base rate P(named); Fisher one-sided; stratified permutation."""
    named = np.asarray(named, bool)
    frozen = np.asarray(frozen, bool)
    a = int((named & frozen).sum())
    b = int((~named & frozen).sum())
    c = int((named & ~frozen).sum())
    d = int((~named & ~frozen).sum())
    nf, nn = a + b, a + c
    base = (a + c) / max(1, len(named))
    prec = a / nf if nf else np.nan
    rec = a / nn if nn else np.nan
    pf = float(stats.fisher_exact([[a, b], [c, d]], alternative="greater").pvalue) if nf and nn else np.nan
    pperm = np.nan
    if strata is not None and nf:
        rng = rng if rng is not None else np.random.default_rng(1)
        strata = np.asarray(strata)
        obs = a
        groups = [np.flatnonzero(strata == s) for s in np.unique(strata)]
        cnt = 0
        for _ in range(n_perm):
            f2 = np.zeros_like(frozen)
            for g in groups:
                f2[g] = rng.permutation(frozen[g])
            cnt += (named & f2).sum() >= obs
        pperm = (cnt + 1) / (n_perm + 1)
    return {"n": int(len(named)), "n_frozen": nf, "n_named": nn, "named_and_frozen": a, "precision": prec, "recall": rec,
            "base_rate": base, "enrichment": (prec / base) if base and np.isfinite(prec) else np.nan,
            "p_fisher": pf, "p_perm_strat": pperm}


def p2_verdict(t: dict) -> str:
    if not t["n_frozen"]:
        return "n/a"
    if t["precision"] >= 0.6 and t["enrichment"] >= 2 and t["p_fisher"] < 0.05:
        return "supported"
    if t["precision"] <= 1.5 * t["base_rate"]:
        return "failed"
    return "mixed"


def logistic(y, X, l2: float = 1e-3, iters: int = 50):
    """Newton logistic regression with a tiny ridge; returns coef, se."""
    y = np.asarray(y, float)
    X = np.column_stack([np.ones(len(y)), np.asarray(X, float)])
    w = np.zeros(X.shape[1])
    for _ in range(iters):
        p = 1 / (1 + np.exp(-X @ w))
        g = X.T @ (y - p) - l2 * w
        H = (X * (p * (1 - p))[:, None]).T @ X + l2 * np.eye(len(w))
        step = np.linalg.solve(H, g)
        w += step
        if np.abs(step).max() < 1e-8:
            break
    p = 1 / (1 + np.exp(-X @ w))
    H = (X * (p * (1 - p))[:, None]).T @ X + l2 * np.eye(len(w))
    se = np.sqrt(np.diag(np.linalg.inv(H)))
    return w, se


# ------------------------------------------------------------------------------ natives
def swap_pairs(V: np.ndarray, G: np.ndarray, roles=None) -> tuple[float, int]:
    """Role-swap accuracy: pairs (i, j) with different roles where cos(v_i,g_i)+cos(v_j,g_j) > cos(v_i,g_j)+cos(v_j,g_i)."""
    S = V @ G.T
    n = len(V)
    roles = np.arange(n) if roles is None else np.asarray(roles)
    acc, tot = 0.0, 0
    for i in range(n):
        for j in range(i + 1, n):
            if roles[i] == roles[j]:
                continue
            d = S[i, i] + S[j, j] - S[i, j] - S[j, i]
            acc += 1.0 if d > 0 else (0.5 if d == 0 else 0.0)
            tot += 1
    return (acc / tot if tot else np.nan), tot


def swap_perm_p(V, G, roles=None, n_perm: int = 2000, rng=None) -> float:
    rng = rng if rng is not None else np.random.default_rng(2)
    obs, _ = swap_pairs(V, G, roles)
    roles = np.arange(len(V)) if roles is None else np.asarray(roles)
    # permute goal assignment by role (agents with the same role keep sharing a goal)
    ur = np.unique(roles)
    cnt = 0
    for _ in range(n_perm):
        perm = dict(zip(ur, rng.permutation(ur)))
        rep = {r: np.flatnonzero(roles == r)[0] for r in ur}
        G2 = np.vstack([G[rep[perm[r]]] for r in roles])
        a, _ = swap_pairs(V, G2, roles)
        cnt += a >= obs
    return (cnt + 1) / (n_perm + 1)


def centered_alignment(V, G) -> np.ndarray:
    """cos(v_i - mean v, g_i - mean g) per agent."""
    dv = V - V.mean(0)
    dg = G - G.mean(0)
    return np.sum(unit(dv) * unit(dg), axis=1)


def room_swap(V, rooms, k_by_room: dict) -> dict:
    """Each agent closer to its own room's kickoff than to the other room's (two rooms)."""
    rs = sorted(k_by_room)
    a, b = rs[0], rs[1]
    own = np.array([V[i] @ k_by_room[r] for i, r in enumerate(rooms)])
    oth = np.array([V[i] @ k_by_room[b if r == a else a] for i, r in enumerate(rooms)])
    return {"accuracy": float(np.mean(own > oth)), "n": int(len(V)), "mean_margin": float(np.mean(own - oth))}


def axis_separation(V, rooms, u) -> float:
    """Cohen's d of the two rooms' projections on axis u (room order: sorted codes; sign kept)."""
    rs = sorted(set(rooms))
    x = V @ unit(u)
    xa, xb = x[np.asarray(rooms) == rs[0]], x[np.asarray(rooms) == rs[1]]
    if len(xa) < 2 or len(xb) < 2:
        return np.nan
    sp = math.sqrt(((len(xa) - 1) * xa.var(ddof=1) + (len(xb) - 1) * xb.var(ddof=1)) / (len(xa) + len(xb) - 2))
    return float((xa.mean() - xb.mean()) / sp) if sp > 0 else np.nan


def exp_plateau_fit(d, y):
    """Fit y = A_inf + (A1 - A_inf) exp(-(d - d0)/tau) on a tau grid; return dict with BIC vs constant and linear."""
    d, y = np.asarray(d, float), np.asarray(y, float)
    m = np.isfinite(y)
    d, y = d[m], y[m]
    n = len(y)
    if n < 4:
        return None
    d0 = d.min()
    best = None
    for tau in np.geomspace(0.25, 4 * max(1.0, d.max() - d0), 60):
        e = np.exp(-(d - d0) / tau)
        X = np.column_stack([np.ones(n), e])
        c, *_ = np.linalg.lstsq(X, y, rcond=None)
        rss = float(((y - X @ c) ** 2).sum())
        if best is None or rss < best[0]:
            best = (rss, tau, c)
    rss_e, tau, c = best
    rss_c = float(((y - y.mean()) ** 2).sum())
    Xl = np.column_stack([np.ones(n), d])
    cl, *_ = np.linalg.lstsq(Xl, y, rcond=None)
    rss_l = float(((y - Xl @ cl) ** 2).sum())
    bic = lambda rss, k: n * math.log(max(rss, 1e-12) / n) + k * math.log(n)  # noqa: E731
    return {"tau": float(tau), "A_inf": float(c[0]), "A_1": float(c[0] + c[1]), "bic_exp": bic(rss_e, 3),
            "bic_const": bic(rss_c, 1), "bic_lin": bic(rss_l, 2), "n": n}
