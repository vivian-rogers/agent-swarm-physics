"""Entropy-production and coupling estimators for binary activity spins (H05).

Aguilera, Ito & Kolchinsky (PRL 136, 077101, 2026): nonequilibrium maximum-entropy lower bound on
entropy production (EP) from trajectory observables. Here the observables are the pairwise,
antisymmetric, time-lagged ones of the parallel-update form

    g_ij(t) = s_i(t+1) s_j(t) - s_i(t) s_j(t+1),   i < j,   s in {-1, +1}.

Because g(reversed transition) = -g(transition), the dual needs forward samples only:

    Sigma_g = max_theta  theta . <g>  -  ln < exp(-theta . g) >.

theta is fitted on training days (L2 penalty, lambda chosen by inner day-blocked CV) and the
objective is evaluated on held-out days. For a stationary parallel kinetic Ising model,
theta_ij ~ J_ij - J_ji.

Everything here is numpy/scipy; no project data is touched in this module.
"""
from __future__ import annotations

import numpy as np
from scipy.optimize import minimize
from scipy.special import expit, logsumexp

LAMBDAS = (1e-4, 1e-3, 1e-2, 3e-2, 1e-1, 1.0)


# ----------------------------------------------------------------------------- observables
def pair_index(n: int):
    """Upper-triangle pair indices (i < j)."""
    i, j = np.triu_indices(n, k=1)
    return i, j


def transitions(S: np.ndarray, day: np.ndarray):
    """Consecutive within-day pairs of rows. S: (T, N) in {-1,+1}; day: (T,) labels, rows sorted by time.

    Returns (S_prev, S_next, day_of_transition)."""
    ok = day[1:] == day[:-1]
    return S[:-1][ok], S[1:][ok], day[1:][ok]


def g_matrix(S_prev: np.ndarray, S_next: np.ndarray, pi=None, pj=None, dtype=np.float32):
    """Antisymmetric pairwise observables g_ij = s_i' s_j - s_i s_j' for the given pairs (default: all i<j)."""
    if pi is None:
        pi, pj = pair_index(S_prev.shape[1])
    Sp = S_prev.astype(dtype)
    Sn = S_next.astype(dtype)
    return Sn[:, pi] * Sp[:, pj] - Sp[:, pi] * Sn[:, pj]


# ----------------------------------------------------------------------------- dual objective
def _neg_obj(theta, G, gbar, lam):
    a = -(G @ theta)                       # -theta.g_t
    lse = logsumexp(a) - np.log(len(a))    # ln mean exp(-theta.g)
    f = theta @ gbar - lse - 0.5 * lam * theta @ theta
    w = np.exp(a - logsumexp(a))           # softmax weights
    grad = gbar + G.T @ w - lam * theta    # d/dtheta [-ln mean e^{-theta g}] = <g>_w
    return -f, -grad


def objective(theta, G):
    """Unpenalized dual objective on a sample (the EP bound evaluated at theta)."""
    if G.shape[0] == 0:
        return np.nan
    a = -(G @ theta)
    return float(theta @ G.mean(0) - (logsumexp(a) - np.log(len(a))))


def fit_theta(G, lam=1e-2, theta0=None, maxiter=500):
    G = np.asarray(G, dtype=np.float64)
    d = G.shape[1]
    gbar = G.mean(0)
    th0 = np.zeros(d) if theta0 is None else theta0
    r = minimize(_neg_obj, th0, args=(G, gbar, lam), jac=True, method="L-BFGS-B",
                 options={"maxiter": maxiter, "gtol": 1e-7})
    return r.x


def _folds(days: np.ndarray, k: int):
    u = np.unique(days)
    k = max(2, min(k, len(u)))
    fold_of_day = {d: i % k for i, d in enumerate(u)}
    return np.array([fold_of_day[d] for d in days]), k


def choose_lambda(G, days, lambdas=LAMBDAS, k_inner=3):
    """Pick lambda by inner day-blocked CV (mean held-out objective)."""
    f, k = _folds(days, k_inner)
    if k < 2 or len(np.unique(days)) < 2:
        return lambdas[-1]
    scores = []
    for lam in lambdas:
        vals, ws = [], []
        for q in range(k):
            tr, te = f != q, f == q
            if te.sum() == 0 or tr.sum() == 0:
                continue
            th = fit_theta(G[tr], lam)
            vals.append(objective(th, G[te])); ws.append(te.sum())
        scores.append(np.average(vals, weights=ws) if vals else -np.inf)
    return lambdas[int(np.argmax(scores))]


def ep_heldout(G, days, k=5, lambdas=LAMBDAS, k_inner=3, return_theta=True):
    """Held-out pairwise EP bound (nats per transition), day-blocked K-fold with nested lambda choice.

    Returns dict: sigma (weighted mean over test folds), se (between-fold), per_fold, insample
    (plug-in maximum on all data; biased upward), theta (refit on all data with the modal lambda)."""
    G = np.asarray(G, dtype=np.float64)
    days = np.asarray(days)
    f, k = _folds(days, k)
    vals, ws, lams = [], [], []
    for q in range(k):
        tr, te = f != q, f == q
        if te.sum() == 0 or tr.sum() == 0:
            continue
        lam = choose_lambda(G[tr], days[tr], lambdas, k_inner)
        th = fit_theta(G[tr], lam)
        vals.append(objective(th, G[te])); ws.append(te.sum()); lams.append(lam)
    vals, ws = np.array(vals), np.array(ws)
    sigma = float(np.average(vals, weights=ws))
    se = float(np.std(vals, ddof=1) / np.sqrt(len(vals))) if len(vals) > 1 else np.nan
    out = {"sigma": sigma, "se": se, "per_fold": vals.tolist(), "lambdas": lams, "T": int(len(G)), "d": int(G.shape[1])}
    if return_theta:
        lam_all = float(np.median(lams))
        th = fit_theta(G, lam_all)
        out["theta"] = th
        out["insample"] = objective(fit_theta(G, 0.0), G)
    return out


def ep_gauss_crossfit(G, days, k=5, ridge=1e-3):
    """Cross-fitted Newton-step (Gaussian) EP bound, nats per transition.

    One Newton step of the dual from theta = 0 gives theta_1 = 2 K^-1 gbar and the bound 2 gbar' K^-1 gbar,
    K = Cov(g). The plug-in is biased up by ~2 tr(K^-1 Cov(gbar)); cross-fitting removes that without an iid
    assumption: Sigma_N = 2 mean_{a != b} gbar_a' K^-1 gbar_b over day-blocked folds a, b. Unbiased for the
    Gaussian bound (can be negative); noise floor ~ sqrt(2d)/T instead of d/T for the held-out ML fit."""
    G = np.asarray(G, dtype=np.float64)
    days = np.asarray(days)
    f, k = _folds(days, k)
    K = np.cov(G, rowvar=False).reshape(G.shape[1], G.shape[1])
    K = K + ridge * np.trace(K) / max(len(K), 1) * np.eye(len(K))
    means = np.array([G[f == q].mean(0) for q in range(k) if (f == q).any()])
    W = np.linalg.solve(K, means.T).T          # K^-1 gbar_a
    M = means @ W.T                             # M[a, b] = gbar_a' K^-1 gbar_b
    kk = len(means)
    off = (M.sum() - np.trace(M)) / (kk * (kk - 1))
    # between-fold spread of the per-fold cross terms, as a rough SE
    per = np.array([(M[a].sum() - M[a, a]) / (kk - 1) for a in range(kk)])
    return {"sigma": float(2 * off), "se": float(2 * per.std(ddof=1) / np.sqrt(kk)), "plugin": float(2 * G.mean(0) @ np.linalg.solve(K, G.mean(0))),
            "T": int(len(G)), "d": int(G.shape[1])}


# ----------------------------------------------------------------------------- pair level
def pair_ep_gauss(G: np.ndarray):
    """Per-column bias-corrected Gaussian (Newton-step) EP bound: 2 (gbar^2 - s^2/T) / s^2.

    Weak-asymmetry expansion of the dual: f(theta) ~ 2 theta gbar - theta^2 Var/2  =>  2 gbar^2 / Var.
    Unbiased numerator; can be negative. NaN where Var = 0 or T < 2."""
    G = np.asarray(G, dtype=np.float64)
    T = G.shape[0]
    if T < 2:
        return np.full(G.shape[1], np.nan)
    m = G.mean(0)
    v = G.var(0, ddof=1)
    with np.errstate(invalid="ignore", divide="ignore"):
        out = 2.0 * (m ** 2 - v / T) / v
    out[v == 0] = np.nan
    return out


def pair_ep_exact(G: np.ndarray):
    """Per-column exact 1-observable bound (plug-in, biased upward): max_theta theta gbar - ln mean e^{-theta g}."""
    out = np.empty(G.shape[1])
    for c in range(G.shape[1]):
        g = G[:, c].astype(np.float64)
        if np.all(g == 0):
            out[c] = 0.0
            continue
        th = fit_theta(g[:, None], 0.0)
        out[c] = objective(th, g[:, None])
    return out


# ----------------------------------------------------------------------------- correlations
def lagged_corr(S_prev, S_next):
    """C[i, j] = corr(s_i(t+1), s_j(t)); NaN for constant spins."""
    X = S_next.astype(np.float64)
    Y = S_prev.astype(np.float64)
    X = X - X.mean(0)
    Y = Y - Y.mean(0)
    sx = X.std(0)
    sy = Y.std(0)
    with np.errstate(invalid="ignore", divide="ignore"):
        C = (X.T @ Y) / len(X) / np.outer(sx, sy)
    return C


def contemp_corr(S):
    X = S.astype(np.float64)
    X = X - X.mean(0)
    s = X.std(0)
    with np.errstate(invalid="ignore", divide="ignore"):
        return (X.T @ X) / len(X) / np.outer(s, s)


# ----------------------------------------------------------------------------- kinetic Ising
def tod_basis(minute: np.ndarray, knots=(0, 10, 30, 60, 120, 240, 480)):
    """Piecewise-linear (hat) basis over minute-of-window: the shared daily-schedule field."""
    minute = np.asarray(minute, dtype=np.float64)
    k = np.asarray(knots, dtype=np.float64)
    B = np.zeros((len(minute), len(k)))
    for c in range(len(k)):
        left = k[c - 1] if c > 0 else None
        right = k[c + 1] if c + 1 < len(k) else None
        x = minute
        b = np.zeros_like(x)
        if left is None:
            b = np.where(x <= k[c], 1.0, 0.0)
        else:
            b = np.where((x >= left) & (x <= k[c]), (x - left) / (k[c] - left), b)
        if right is None:
            b = np.where(x >= k[c], 1.0, b)
        else:
            b = np.where((x > k[c]) & (x <= right), (right - x) / (right - k[c]), b)
        B[:, c] = b
    return B


def _logit_negll(w, X, y, lam, pen):
    z = X @ w
    # y in {0,1}; log-likelihood = y z - log(1+e^z)
    ll = y @ z - np.logaddexp(0, z).sum()
    p = expit(z)
    g = X.T @ (y - p)
    n = len(y)
    return -(ll / n - 0.5 * lam * (pen * w) @ w), -(g / n - lam * pen * w)


def fit_kinetic_ising(S_prev, S_next, F=None, lam=1e-3):
    """Logistic regression per spin: P(s_i' = +1 | s, F) = sigmoid(2 (h_i + F b_i + sum_j J_ij s_j)).

    S_prev, S_next: (T, N) in {-1,+1}. F: (T, p) field covariates (e.g. tod_basis), unpenalized.
    Returns J (N, N) including the diagonal (self-coupling), and the field coefficients."""
    T, N = S_prev.shape
    X = [np.ones((T, 1)), S_prev.astype(np.float64)]
    if F is not None:
        X.append(F)
    X = np.hstack(X)
    pen = np.zeros(X.shape[1])
    pen[1:1 + N] = 1.0
    J = np.zeros((N, N))
    H = np.zeros((N, X.shape[1] - N))
    for i in range(N):
        y = (S_next[:, i] > 0).astype(np.float64)
        if y.min() == y.max():
            J[i] = np.nan
            continue
        r = minimize(_logit_negll, np.zeros(X.shape[1]), args=(X, y, lam, pen), jac=True, method="L-BFGS-B",
                     options={"maxiter": 500})
        w = r.x / 2.0  # P = sigmoid(2H)
        J[i] = w[1:1 + N]
        H[i] = np.r_[w[0], w[1 + N:]]
    return J, H


# ----------------------------------------------------------------------------- simulator
def simulate_kinetic_ising(J, h, n_days, day_len, burn=200, rng=None, h_t=None, restart=None):
    """Parallel-update kinetic Ising sampled like the village: n_days separate days of day_len bins.

    J: (N,N) couplings (diag = self-coupling). h: (N,) fields. h_t: optional (day_len,) common field
    added to every spin (daily schedule). restart: None = each day starts from the stationary chain
    (burn-in steps); 'off' = each day starts with every spin at -1 (a cold daily restart).
    Returns S (n_days*day_len, N) int8 and day labels."""
    rng = np.random.default_rng(rng)
    N = len(h)
    S = np.empty((n_days * day_len, N), dtype=np.int8)
    days = np.repeat(np.arange(n_days), day_len)
    s = np.where(rng.random(N) < 0.5, 1, -1).astype(np.float64)
    for d in range(n_days):
        if restart == "off":
            s = -np.ones(N)
        else:
            for _ in range(burn):
                H = h + J @ s
                s = np.where(rng.random(N) < expit(2 * H), 1.0, -1.0)
        for t in range(day_len):
            H = h + J @ s + (h_t[t] if h_t is not None else 0.0)
            s = np.where(rng.random(N) < expit(2 * H), 1.0, -1.0)
            S[d * day_len + t] = s
    return S, days


def true_ep_stationary(J, S_prev, S_next):
    """Exact steady-state EP per step of the parallel kinetic Ising: sum_{i<j} (J_ij - J_ji) <g_ij>."""
    i, j = pair_index(J.shape[0])
    G = g_matrix(S_prev, S_next, i, j, dtype=np.float64)
    return float(((J[i, j] - J[j, i]) * G.mean(0)).sum())


# ----------------------------------------------------------------------------- surrogates
def shuffle_configurations(S, days, rng=None):
    """Permute whole configurations within each day (keeps simultaneous structure, kills time order)."""
    rng = np.random.default_rng(rng)
    out = S.copy()
    for d in np.unique(days):
        idx = np.flatnonzero(days == d)
        out[idx] = S[rng.permutation(idx)]
    return out


def circular_shift_agents(S, days, rng=None):
    """Independent circular shift of each agent within each day (keeps autocorrelation, kills cross-agent lags)."""
    rng = np.random.default_rng(rng)
    out = S.copy()
    for d in np.unique(days):
        idx = np.flatnonzero(days == d)
        L = len(idx)
        for a in range(S.shape[1]):
            out[idx, a] = np.roll(S[idx, a], rng.integers(L))
    return out


def reverse_time(S, days):
    """Reverse the order of bins within each day (and the day order)."""
    out_S, out_d = [], []
    for d in np.unique(days)[::-1]:
        idx = np.flatnonzero(days == d)
        out_S.append(S[idx[::-1]]); out_d.append(days[idx])
    return np.vstack(out_S), np.concatenate(out_d)
