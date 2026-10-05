"""H11 round 2 estimators: conditional logit (choice among projects), conditional Poisson (fixed effects), MH odds
ratios, DerSimonian-Laird pooling, and the skeleton replay for the project-size distribution (R1e/f).

All estimators take plain numpy arrays so the synthetic worlds (analysis/round2.py synth) and the real run share them.
"""
from __future__ import annotations

import math
import os

for _v in ("POLARS_MAX_THREADS", "OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "2")

import numpy as np  # noqa: E402
import polars as pl  # noqa: E402
from scipy import stats  # noqa: E402


# ============================================================================================ grouped helpers
def _starts(gid: np.ndarray) -> np.ndarray:
    """gid sorted; start index of every group."""
    return np.flatnonzero(np.r_[True, gid[1:] != gid[:-1]])


def _gmax(v, st):
    return np.maximum.reduceat(v, st)


def _gsum(v, st):
    return np.add.reduceat(v, st, axis=0)


def _expand(gv, st, n):
    cnt = np.diff(np.r_[st, n])
    return np.repeat(gv, cnt, axis=0)


# ============================================================================================ conditional logit
def clogit(X: np.ndarray, gid: np.ndarray, y: np.ndarray, cluster: np.ndarray | None = None,
           ridge: np.ndarray | float | None = None, offset: np.ndarray | None = None, weights_y: bool = False,
           max_iter: int = 60, tol: float = 1e-9) -> dict:
    """Grouped multinomial (conditional) logit, Newton-Raphson.

    X rows sorted by gid; y = 1 for the chosen row (weights_y: y holds counts, i.e. conditional Poisson, where the
    group total is conditioned on). ridge: L2 penalty per column (or scalar). cluster: one id per group, for the
    sandwich covariance. Returns beta, se (sandwich if cluster else model-based), cov, ll (unpenalized)."""
    n, k = X.shape
    st = _starts(gid)
    G = len(st)
    off = np.zeros(n) if offset is None else offset
    yv = y.astype(float)
    ny = _gsum(yv, st)                      # 1 per group for logit, total count for Poisson
    R = np.zeros(k) if ridge is None else (np.full(k, ridge) if np.isscalar(ridge) else np.asarray(ridge, float))
    b = np.zeros(k)
    ll_old = -np.inf
    for _ in range(max_iter):
        eta = X @ b + off
        m = _expand(_gmax(eta, st), st, n)
        e = np.exp(eta - m)
        se_ = _gsum(e, st)
        p = e / _expand(se_, st, n)
        ll = float((yv * (eta - m)).sum() - (ny * np.log(se_)).sum())
        pen = 0.5 * float((R * b * b).sum())
        xbar = _gsum(p[:, None] * X, st)                      # G x k
        grad = (yv[:, None] * X).sum(0) - (ny[:, None] * xbar).sum(0) - R * b
        Xc = X - _expand(xbar, st, n)
        H = (Xc * (p * _expand(ny, st, n))[:, None]).T @ Xc + np.diag(R)
        try:
            step = np.linalg.solve(H, grad)
        except np.linalg.LinAlgError:
            step = np.linalg.lstsq(H, grad, rcond=None)[0]
        # damped step
        t = 1.0
        while t > 1e-4:
            bn = b + t * step
            eta_n = X @ bn + off
            m_n = _expand(_gmax(eta_n, st), st, n)
            se_n = _gsum(np.exp(eta_n - m_n), st)
            ll_n = float((yv * (eta_n - m_n)).sum() - (ny * np.log(se_n)).sum()) - 0.5 * float((R * bn * bn).sum())
            if ll_n >= ll - pen - 1e-10:
                break
            t /= 2
        b = bn
        if abs(ll_n - (ll - pen)) < tol:
            break
        ll_old = ll_n
    # final quantities
    eta = X @ b + off
    m = _expand(_gmax(eta, st), st, n)
    e = np.exp(eta - m)
    se_ = _gsum(e, st)
    p = e / _expand(se_, st, n)
    ll = float((yv * (eta - m)).sum() - (ny * np.log(se_)).sum())
    xbar = _gsum(p[:, None] * X, st)
    Xc = X - _expand(xbar, st, n)
    H = (Xc * (p * _expand(ny, st, n))[:, None]).T @ Xc + np.diag(R)
    Hinv = np.linalg.pinv(H)
    if cluster is not None:
        sc = _gsum((yv[:, None] - (p * _expand(ny, st, n))[:, None]) * X, st)   # G x k scores
        cl = np.asarray(cluster)
        _, inv = np.unique(cl, return_inverse=True)
        S = np.zeros((inv.max() + 1, k))
        np.add.at(S, inv, sc)
        nc = S.shape[0]
        meat = S.T @ S * (nc / max(nc - 1, 1))
        cov = Hinv @ meat @ Hinv
    else:
        cov = Hinv
    return {"beta": b, "se": np.sqrt(np.clip(np.diag(cov), 0, None)), "cov": cov, "ll": ll, "n_groups": G,
            "converged": bool(np.isfinite(ll))}


def clogit_ll(X, gid, y, b, offset=None) -> np.ndarray:
    """Per-group log-likelihood at b (for held-out evaluation)."""
    n = X.shape[0]
    st = _starts(gid)
    off = np.zeros(n) if offset is None else offset
    eta = X @ b + off
    m = _expand(_gmax(eta, st), st, n)
    se_ = _gsum(np.exp(eta - m), st)
    yv = y.astype(float)
    return _gsum(yv * (eta - m), st) - _gsum(yv, st) * np.log(se_)


# ============================================================================================ pooling and tests
def dl_pool(est, se) -> dict:
    """DerSimonian-Laird random-effects pooled estimate."""
    est, se = np.asarray(est, float), np.asarray(se, float)
    ok = np.isfinite(est) & np.isfinite(se) & (se > 0)
    est, se = est[ok], se[ok]
    if len(est) == 0:
        return {"est": None, "se": None, "lo": None, "hi": None, "tau2": None, "k": 0}
    w = 1 / se ** 2
    mu_f = (w * est).sum() / w.sum()
    Q = (w * (est - mu_f) ** 2).sum()
    k = len(est)
    tau2 = max(0.0, (Q - (k - 1)) / (w.sum() - (w ** 2).sum() / w.sum())) if k > 1 else 0.0
    ws = 1 / (se ** 2 + tau2)
    mu = (ws * est).sum() / ws.sum()
    s = math.sqrt(1 / ws.sum())
    return {"est": float(mu), "se": s, "lo": float(mu - 1.96 * s), "hi": float(mu + 1.96 * s), "tau2": float(tau2), "k": k,
            "Q": float(Q)}


def mh_or(y: np.ndarray, x: np.ndarray, strata: np.ndarray) -> dict:
    """Mantel-Haenszel OR of y for binary x within strata, with the Robins-Breslow-Greenland 95% CI."""
    y, x = y.astype(bool), x.astype(bool)
    _, inv = np.unique(strata, return_inverse=True)
    K = inv.max() + 1
    a = np.bincount(inv, weights=(x & y), minlength=K)
    b = np.bincount(inv, weights=(x & ~y), minlength=K)
    c = np.bincount(inv, weights=(~x & y), minlength=K)
    d = np.bincount(inv, weights=(~x & ~y), minlength=K)
    n = a + b + c + d
    keep = n > 0
    a, b, c, d, n = a[keep], b[keep], c[keep], d[keep], n[keep]
    R = a * d / n
    S = b * c / n
    if R.sum() == 0 or S.sum() == 0:
        return {"or": None, "lo": None, "hi": None, "n_exposed_events": int(a.sum())}
    orr = R.sum() / S.sum()
    P = (a + d) / n
    Qq = (b + c) / n
    var = ((P * R).sum() / (2 * R.sum() ** 2) + ((P * S + Qq * R).sum()) / (2 * R.sum() * S.sum())
           + (Qq * S).sum() / (2 * S.sum() ** 2))
    se = math.sqrt(var)
    return {"or": float(orr), "lo": float(orr * math.exp(-1.96 * se)), "hi": float(orr * math.exp(1.96 * se)),
            "log_or": float(math.log(orr)), "se_log": se, "n_exposed_events": int(a.sum())}


def wald(est, se, df=None):
    """Wald interval; df given -> t(df) critical value (small number of clusters, amendment A1)."""
    if est is None or se is None or not np.isfinite(se) or se <= 0:
        return {"est": est, "se": se, "lo": None, "hi": None, "z": None, "p": None}
    z = est / se
    q = 1.96 if df is None else float(stats.t.ppf(0.975, max(df, 1)))
    p = 2 * stats.norm.sf(abs(z)) if df is None else 2 * stats.t.sf(abs(z), max(df, 1))
    return {"est": float(est), "se": float(se), "lo": float(est - q * se), "hi": float(est + q * se), "z": float(z),
            "p": float(p), "sig": bool(abs(z) > q)}


# ============================================================================================ R1 designs
def r1_design(c: pl.DataFrame, variant: str):
    """Columns for the R1 models from a cands frame (one unit). Returns X, names."""
    a = c["a"].to_numpy().astype(float)
    loga = np.where(a > 0, np.log(np.maximum(a, 1)), 0.0)
    z0 = (a == 0).astype(float)
    ls = np.log1p(c["s"].to_numpy().astype(float))
    h = c["h"].to_numpy().astype(float)
    if variant == "pa":
        return np.c_[loga, z0], ["alpha", "zero"]
    if variant in ("full", "fe"):
        X, nm = np.c_[loga, z0, ls, h], ["alpha", "zero", "log_size", "habit"]
        if variant == "fe":
            Y = c["Y"].to_numpy()
            u, inv = np.unique(Y, return_inverse=True)
            D = np.zeros((len(Y), len(u)))
            D[np.arange(len(Y)), inv] = 1.0
            X = np.c_[X, D]
            nm = nm + [f"fe:{x}" for x in u]
        return X, nm
    if variant == "lead":
        al = np.log1p(c["a_lead"].to_numpy().astype(float))
        return np.c_[np.log1p(a), al, ls, h], ["lag", "lead", "log_size", "habit"]
    raise ValueError(variant)


def r2_design(c: pl.DataFrame, variant: str):
    ls = np.log1p(c["s"].to_numpy().astype(float))
    h = c["h"].to_numpy().astype(float)
    f = {k: np.log1p(c[k].to_numpy().astype(float)) for k in ("c", "c_lead", "m_read", "m_unread", "m_lead")}
    base = [h, ls]
    nb = ["habit", "log_size"]
    if variant == "base":
        return np.c_[tuple(base)], nb
    if variant == "C":
        return np.c_[tuple(base + [f["c"]])], nb + ["C"]
    if variant == "M":
        return np.c_[tuple(base + [f["m_read"]])], nb + ["M_read"]
    if variant == "joint":
        ks = ["c", "c_lead", "m_read", "m_unread", "m_lead"]
        return np.c_[tuple(base + [f[k] for k in ks])], nb + ["C", "C_lead", "M_read", "M_unread", "M_lead"]
    raise ValueError(variant)


# ============================================================================================ R1 replay
def replay(skel: pl.DataFrame, kernel: str, beta: np.ndarray | None, rng: np.random.Generator, L: int = 4) -> dict:
    """Redraw the targets of entries and recruits on the real skeleton of one unit; stays and births kept.
    kernel: 'fit' (beta over [alpha, zero, log_size, habit]), 'yule' (weight = total cumulative size), 'uniform'.
    Returns the final size statistics."""
    s = skel.sort("g", "agent")
    agents = sorted(s["agent"].unique().to_list())
    ai = {a: i for i, a in enumerate(agents)}
    G = int(s["g"].max()) + 1
    evs = s["ev"].to_list()
    gs = s["g"].to_numpy()
    ags = np.array([ai[a] for a in s["agent"].to_list()])
    P = s["project"].n_unique() + int(sum(e in ("recruit", "entry") for e in evs)) + 2
    win = np.zeros((len(agents), G, P), dtype=np.int32)     # windows per agent, g, project (simulated)
    tot_win = np.zeros((G, P), dtype=np.int32)
    exists = np.zeros(P, dtype=bool)
    cur = -np.ones(len(agents), dtype=np.int64)
    nxt = 0
    real_exist_g = {}
    # real "did the target exist" for entries
    first_g = dict(s.group_by("project").agg(pl.col("g").min()).iter_rows())
    projs = s["project"].to_list()
    cum_tot = np.zeros(P)        # cumulative windows before current g (all agents)
    cum_ag = np.zeros((len(agents), P))
    g_done = -1
    pending = []
    for idx in range(len(evs)):
        g = gs[idx]
        if g != g_done:
            # commit all choices of windows < g into cumulative counts
            for (ia, p, gg) in pending:
                cum_tot[p] += 1
                cum_ag[ia, p] += 1
                exists[p] = True
            pending = []
            g_done = g
        ia, e = ags[idx], evs[idx]
        if e == "stay" and cur[ia] >= 0:
            p = cur[ia]
        elif e == "birth" or (e == "entry" and first_g[projs[idx]] >= g):
            p = nxt
            nxt += 1
        else:
            cand = np.flatnonzero(exists)
            if e != "entry":
                cand = cand[cand != cur[ia]]
            if len(cand) == 0:
                p = nxt
                nxt += 1
            else:
                if kernel == "uniform":
                    w = np.ones(len(cand))
                elif kernel == "yule":
                    w = cum_tot[cand].astype(float)
                else:
                    lo = max(g - L, 0)
                    a = tot_win[lo:g, cand].sum(axis=0) - win[ia, lo:g, cand].sum(axis=0)
                    a = a.astype(float)
                    sz = cum_tot[cand] - cum_ag[ia, cand]
                    h = (cum_ag[ia, cand] > 0).astype(float)
                    u = (beta[0] * np.where(a > 0, np.log(np.maximum(a, 1)), 0) + beta[1] * (a == 0) + beta[2] * np.log1p(sz)
                         + beta[3] * h)
                    w = np.exp(u - u.max())
                w = w / w.sum()
                p = cand[rng.choice(len(cand), p=w)]
        cur[ia] = p
        win[ia, g, p] += 1
        tot_win[g, p] += 1
        pending.append((ia, p, g))
    return size_stats_from(win.sum(axis=1))


def size_stats_from(M: np.ndarray) -> dict:
    """M: agents x projects window counts."""
    size = M.sum(axis=0)
    size = size[size > 0]
    n = size.sum()
    sh = size / n
    H = float(-(sh * np.log(sh)).sum())
    reach = (M > 0).sum(axis=0)
    reach = reach[M.sum(axis=0) > 0]
    shared = float(size[reach >= 2].sum() / n)
    return {"top_share": float(sh.max()), "eff_n": float(math.exp(H)), "shared_share": shared, "n_proj": int(len(size))}


def observed_size_stats(skel: pl.DataFrame) -> dict:
    t = skel.group_by("agent", "project").len()
    ags = sorted(t["agent"].unique().to_list())
    pr = sorted(t["project"].unique().to_list())
    ai = {a: i for i, a in enumerate(ags)}
    pi = {p: i for i, p in enumerate(pr)}
    M = np.zeros((len(ags), len(pr)))
    for a, p, n in t.iter_rows():
        M[ai[a], pi[p]] = n
    return size_stats_from(M)
