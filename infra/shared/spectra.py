"""Shared random-matrix spectra with surrogate edges, bias-corrected participation ratios and the near-duplicate share.
Functions only (no table). Moved here unchanged from H12
(hypotheses/H12-groupthink-dimensional-collapse/analysis/h12lib.py: "Spectra" and "Participation ratio" sections) and
generalized from H12's posthoc.py (near_dup_share). Tests: infra/shared/tests/test_spectra.py (reproduce H12's synthetic
numbers exactly, plus self-contained checks).

Spectra
  corr_eig(X)            eigenvalues (desc) of the equal-time correlation matrix of N x T spins
  overlap_eig(X)         eigenvalues of the content overlap Q_ij = <z_i . z_j>_t / d for N x T x d deviations
                         (missing windows = 0; unit mean-square scaling per agent)
  mp_edge(N, T)          Marchenko-Pastur edge (1 + sqrt(N/T))^2
  bartlett_tau(days)     effective-sample-size factor from within-day autocorrelations
  crossday_surrogate     agent i's day d <- the same agent's day (d + c_i) mod D (balanced offsets), aligned by minute
                         of the day's window, wrapped circularly: keeps each agent's daily profile and autocorrelation,
                         breaks same-day co-movement (H12's primary null)
  circshift_surrogate    independent within-day circular shift per agent (secondary null; misaligns daily profiles)
  lull_filter(X)         keep bins with >= 2 active agents (drops joint lulls, H02/H38)
  spectrum_test(days, n_surr, rng, kind="spin"|"content", null="crossday"|"circ", lull=False, q=0.95)
                         observed eigenvalues vs the q-quantile of the surrogate top eigenvalue: k = # above the edge
  mode_summary(v), label_separation(v, labels, rng)
Participation ratio
  pr_moments, pr_from_samples   unbiased (Gaussian / Wishart) a = (tr S)^2, b = tr S^2 and PR = a / b
  pr_rarefied(Y, agent, n, cap, draws, rng)   PR30: cap per agent, rarefy to n, ratio of mean moments
  pr_balanced(Y, agent, m, k, draws, rng)     PRday: m agents x k statements
  between_pr(Y, agent, rng)                   between-agent PR, noise-corrected by 4-way splits (+ finite-N correction)
Templating
  near_dup_share(V, agent, thr=0.95)          share of statements with a near-copy (cosine > thr) among the others,
                                              within the same agent and across agents (V rows unit-normalized)
  near_dup_share_by(df, V, by, min_n=20)      the same per group (e.g. per PT day, as H12's posthoc)

Thread use: numpy BLAS threads are capped at 2 here (set before numpy is first imported).
"""
from __future__ import annotations

import os

for _v in ("OMP_NUM_THREADS", "VECLIB_MAXIMUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ.setdefault(_v, "2")

import json  # noqa: E402
import zlib  # noqa: E402

import numpy as np  # noqa: E402

SEED = 20261003


def stable_seed(obj) -> int:
    """Deterministic seed from any JSON-able object (H12's convention: crc32 of the sorted JSON)."""
    return zlib.crc32(json.dumps(obj, sort_keys=True, default=str).encode()) % 2**31


# ----------------------------------------------------------------------------------------------------
# Spectra
# ----------------------------------------------------------------------------------------------------
def standardize_rows(X: np.ndarray) -> np.ndarray:
    X = X.astype(np.float64)
    X = X - X.mean(axis=1, keepdims=True)
    sd = X.std(axis=1, keepdims=True)
    return X / np.where(sd > 0, sd, 1.0)


def corr_eig(X: np.ndarray, vectors: bool = False):
    """X: N x T. Eigenvalues (descending) of the equal-time correlation matrix (and eigenvectors)."""
    Z = standardize_rows(X)
    C = Z @ Z.T / Z.shape[1]
    if vectors:
        w, V = np.linalg.eigh(C)
        return w[::-1], V[:, ::-1], C
    return np.linalg.eigvalsh(C)[::-1]


def overlap_eig(X: np.ndarray, vectors: bool = False):
    """X: N x T x d content deviations (missing windows = 0). Q_ij = <z_i . z_j>_t / d with unit mean-square scaling."""
    N, T, d = X.shape
    Z = X.reshape(N, T * d).astype(np.float64)
    s = np.sqrt((Z ** 2).mean(axis=1, keepdims=True))
    Z = Z / np.where(s > 0, s, 1.0)
    Q = Z @ Z.T / (T * d)
    if vectors:
        w, V = np.linalg.eigh(Q)
        return w[::-1], V[:, ::-1], Q
    return np.linalg.eigvalsh(Q)[::-1]


def mp_edge(N: int, T: float) -> float:
    return (1.0 + np.sqrt(N / T)) ** 2


def bartlett_tau(days: list[np.ndarray], maxlag: int = 60) -> float:
    """tau_B = 1 + 2 sum_tau mean_{i<j} rho_i(tau) rho_j(tau), autocorrelations within days only.
    days: list of N x L_d arrays (same agents). Uses unit-level standardization."""
    X = np.concatenate(days, axis=1).astype(np.float64)
    mu = X.mean(1, keepdims=True); sd = X.std(1, keepdims=True); sd[sd == 0] = 1
    N = X.shape[0]
    num = np.zeros((N, maxlag)); cnt = np.zeros(maxlag)
    for A in days:
        Z = (A - mu) / sd
        L = Z.shape[1]
        for tau in range(1, min(maxlag, L - 1) + 1):
            num[:, tau - 1] += (Z[:, :-tau] * Z[:, tau:]).sum(1)
            cnt[tau - 1] += L - tau
    rho = num / np.maximum(cnt, 1)
    s1 = rho.sum(0); s2 = (rho ** 2).sum(0)
    pair = (s1 ** 2 - s2) / (N * (N - 1))
    return float(1 + 2 * pair.sum())


def _pad_days(days: list[np.ndarray]):
    """Tile each day's series (agents x L_d [x d]) circularly to L_max. Returns P (N x D x Lmax [x d]) and lengths."""
    L = np.array([a.shape[1] for a in days])
    Lmax = int(L.max())
    P = np.stack([a[:, np.arange(Lmax) % a.shape[1]] for a in days], axis=1)
    return P, L


def crossday_surrogate(P: np.ndarray, L: np.ndarray, rng: np.random.Generator) -> np.ndarray:
    """Cross-day surrogate: agent i's day d <- the same agent's day (d + c_i) mod D, aligned by minute/window of the
    day's active window, wrapped circularly if the source day is shorter. Offsets c_i are balanced over agents."""
    N, D = P.shape[0], P.shape[1]
    c = rng.permutation(np.arange(N) % D)
    idx = (np.arange(D)[None, :] + c[:, None]) % D
    S = P[np.arange(N)[:, None], idx]  # N x D x Lmax [x d]
    return np.concatenate([S[:, d, :L[d]] for d in range(D)], axis=1)


def circshift_surrogate(days: list[np.ndarray], rng: np.random.Generator) -> np.ndarray:
    """Within-day independent circular shift per agent and day (secondary null; misaligns daily profiles)."""
    out = []
    for A in days:
        N, Ld = A.shape[0], A.shape[1]
        lag = rng.integers(0, Ld, size=N)
        idx = (np.arange(Ld)[None, :] + lag[:, None]) % Ld
        out.append(A[np.arange(N)[:, None], idx])
    return np.concatenate(out, axis=1)


def lull_filter(X: np.ndarray) -> np.ndarray:
    """Activity spins (N x T, +-1): keep bins with >= 2 active agents (drop H02's joint lulls)."""
    K = (X > 0).sum(0)
    return X[:, K >= 2]


def spectrum_test(days: list[np.ndarray], n_surr: int, rng: np.random.Generator, kind: str = "spin",
                  null: str = "crossday", lull: bool = False, q: float = 0.95) -> dict:
    """Observed eigenvalues vs a surrogate edge (q-quantile of the surrogate top eigenvalue).
    kind 'spin': days are N x L_d arrays; kind 'content': N x W_d x d arrays."""
    eig = corr_eig if kind == "spin" else overlap_eig
    Xobs = np.concatenate(days, axis=1)
    if lull:
        Xobs = lull_filter(Xobs)
    w = eig(Xobs)
    P, L = _pad_days(days) if null == "crossday" else (None, None)
    null_eigs = np.empty((n_surr, len(w)))
    for s in range(n_surr):
        Xs = crossday_surrogate(P, L, rng) if null == "crossday" else circshift_surrogate(days, rng)
        if lull:
            Xs = lull_filter(Xs)
        null_eigs[s] = eig(Xs)
    edge = float(np.quantile(null_eigs[:, 0], q))
    qk = np.quantile(null_eigs, q, axis=0)
    above = w > qk
    k_rank = int(np.argmin(above)) if not above.all() else len(w)  # sequential rank-wise count (secondary)
    return {"eig": w, "edge": edge, "k": int((w > edge).sum()), "k_rank": k_rank,
            "null_l1_med": float(np.median(null_eigs[:, 0])),
            "null_eigs_q95": np.quantile(null_eigs, q, axis=0), "null_eigs_med": np.median(null_eigs, axis=0),
            "T": int(Xobs.shape[1])}


def mode_summary(v: np.ndarray) -> dict:
    """Top-eigenvector shape: majority-sign share, IPR, and uniform-mode overlap |<v,u>|^2."""
    N = len(v)
    pos = (v > 0).mean()
    u = np.ones(N) / np.sqrt(N)
    return {"sign_share": float(max(pos, 1 - pos)), "ipr": float((v ** 4).sum()), "u_overlap": float((v @ u) ** 2)}


def label_separation(v: np.ndarray, labels: np.ndarray, rng: np.random.Generator, n_perm: int = 2000) -> float:
    """Permutation p-value that eigenvector loadings differ by label (between-group sum of squares)."""
    labs = np.unique(labels)
    if len(labs) < 2:
        return np.nan

    def bss(lab):
        return sum((lab == g).sum() * (v[lab == g].mean() - v.mean()) ** 2 for g in labs)
    obs = bss(labels)
    null = np.array([bss(rng.permutation(labels)) for _ in range(n_perm)])
    return float((1 + (null >= obs - 1e-12).sum()) / (1 + n_perm))


# ----------------------------------------------------------------------------------------------------
# Participation ratio
# ----------------------------------------------------------------------------------------------------
def pr_moments(Y: np.ndarray):
    """Unbiased (Gaussian/Wishart) estimates of a = (tr Sigma)^2 and b = tr Sigma^2 from n x d samples,
    plus the naive t1 = tr W, t2 = tr W^2 (W = centered scatter). Uses the n x n Gram when n < d."""
    n = Y.shape[0]
    nu = n - 1
    Yc = Y - Y.mean(0)
    G = Yc @ Yc.T if n < Y.shape[1] else Yc.T @ Yc
    t1 = float(np.trace(G)); t2 = float((G * G).sum())
    det = nu * nu * (nu + 2) * (nu - 1)
    a = (nu * (nu + 1) * t1 * t1 - 2 * nu * t2) / det
    b = (nu * nu * t2 - nu * t1 * t1) / det
    return a, b, t1, t2, nu


def pr_from_samples(Y: np.ndarray) -> dict:
    a, b, t1, t2, nu = pr_moments(Y)
    d = Y.shape[1]
    pr = a / b if b > 0 else np.nan
    w = np.linalg.eigvalsh((Y - Y.mean(0)).T @ (Y - Y.mean(0)) / nu)
    w = np.clip(w, 0, None); p = w / w.sum()
    er = float(np.exp(-(p[p > 0] * np.log(p[p > 0])).sum()))
    return {"pr": float(np.clip(pr, 1, d)) if np.isfinite(pr) else np.nan, "pr_naive": t1 * t1 / t2,
            "tv": t1 / nu, "erank": er}


def _erank(Y):
    Yc = Y - Y.mean(0)
    G = Yc @ Yc.T if Y.shape[0] < Y.shape[1] else Yc.T @ Yc
    w = np.clip(np.linalg.eigvalsh(G), 0, None)
    p = w / w.sum()
    p = p[p > 0]
    return float(np.exp(-(p * np.log(p)).sum()))


def pr_rarefied(Y: np.ndarray, agent: np.ndarray, n: int, cap: int | None, draws: int,
                rng: np.random.Generator, erank: bool = True) -> dict:
    """PR30-type statistic: cap each agent at `cap` statements, rarefy the pool to n, average unbiased a and b over
    draws and take the ratio (ratio of means: stabler than the mean of ratios). Returns nan if the pool < n."""
    d = Y.shape[1]
    if cap is not None:
        ua, cnt = np.unique(agent, return_counts=True)
        if np.minimum(cnt, cap).sum() < n:
            return {"pr": np.nan, "pr_naive": np.nan, "tv": np.nan, "erank": np.nan, "n_pool": int(np.minimum(cnt, cap).sum())}
    elif len(Y) < n:
        return {"pr": np.nan, "pr_naive": np.nan, "tv": np.nan, "erank": np.nan, "n_pool": len(Y)}
    A = B = T1 = T2 = ER = 0.0
    groups = {g: np.flatnonzero(agent == g) for g in np.unique(agent)} if cap is not None else None
    for _ in range(draws):
        if cap is not None:
            pool = np.concatenate([ix if len(ix) <= cap else rng.choice(ix, cap, replace=False) for ix in groups.values()])
        else:
            pool = np.arange(len(Y))
        sel = rng.choice(pool, n, replace=False)
        a, b, t1, t2, nu = pr_moments(Y[sel])
        A += a; B += b; T1 += t1; T2 += t2; ER += _erank(Y[sel]) if erank else 0.0
    pr = A / B if B > 0 else np.nan
    return {"pr": float(np.clip(pr, 1, d)) if np.isfinite(pr) else np.nan, "pr_naive": T1 * T1 / (T2 * draws) if T2 > 0 else np.nan,
            "tv": T1 / (draws * (n - 1)), "erank": ER / draws, "n_pool": int(len(Y))}


def pr_balanced(Y: np.ndarray, agent: np.ndarray, m: int, k: int, draws: int, rng: np.random.Generator,
                erank: bool = True) -> dict:
    """PRday: m agents with >= k statements, k statements each, bias-corrected PR of the m*k pooled statements,
    ratio of means over draws of agents and statements."""
    d = Y.shape[1]
    groups = {g: np.flatnonzero(agent == g) for g in np.unique(agent)}
    elig = [g for g, ix in groups.items() if len(ix) >= k]
    if len(elig) < m:
        return {"pr": np.nan, "tv": np.nan, "erank": np.nan, "n_elig": len(elig)}
    A = B = T1 = ER = 0.0
    for _ in range(draws):
        ags = rng.choice(elig, m, replace=False)
        sel = np.concatenate([rng.choice(groups[g], k, replace=False) for g in ags])
        a, b, t1, t2, nu = pr_moments(Y[sel])
        A += a; B += b; T1 += t1; ER += _erank(Y[sel]) if erank else 0.0
    pr = A / B if B > 0 else np.nan
    return {"pr": float(np.clip(pr, 1, d)) if np.isfinite(pr) else np.nan, "tv": T1 / (draws * (m * k - 1)),
            "erank": ER / draws, "n_elig": len(elig)}


def between_pr(Y: np.ndarray, agent: np.ndarray, rng: np.random.Generator, splits: int = 20, min_per: int = 8) -> dict:
    """Between-agent PR, unbiased for statement noise via random 4-way splits of each agent's statements:
    PR = mean[tr C_ab tr C_cd] / mean[tr(C_ab C_cd)], C_xy = symmetrized cross-covariance of agent means.
    Also returns the naive PR of the agent-mean covariance."""
    groups = [np.flatnonzero(agent == g) for g in np.unique(agent)]
    groups = [g for g in groups if len(g) >= min_per]
    N = len(groups)
    if N < 3:
        return {"pr_between": np.nan, "pr_between_naive": np.nan, "N": N}
    M = np.stack([Y[g].mean(0) for g in groups]); M = M - M.mean(0)
    Cn = M.T @ M / (N - 1)
    naive = np.trace(Cn) ** 2 / (Cn * Cn).sum()
    num = den = 0.0
    for _ in range(splits):
        Q = np.empty((4, N, Y.shape[1]))
        for i, g in enumerate(groups):
            p = rng.permutation(g)
            for j, part in enumerate(np.array_split(p, 4)):
                Q[j, i] = Y[part].mean(0)
        Q = Q - Q.mean(1, keepdims=True)
        Cab = (Q[0].T @ Q[1] + Q[1].T @ Q[0]) / (2 * (N - 1))
        Ccd = (Q[2].T @ Q[3] + Q[3].T @ Q[2]) / (2 * (N - 1))
        num += np.trace(Cab) * np.trace(Ccd); den += (Cab * Ccd).sum()
    p = num / den if den > 0 else np.nan
    nu = N - 1  # finite-N (Wishart over agents) correction: population PR from the sample between-agent PR
    pop = ((nu + 1) * p - 2) / (nu - p) if np.isfinite(p) and p < nu else np.nan
    return {"pr_between": float(p), "pr_between_naive": float(naive),
            "pr_between_pop": float(np.clip(pop, 1, Y.shape[1])) if np.isfinite(pop) else np.nan, "N": N}


# ----------------------------------------------------------------------------------------------------
# Templating / self-repetition
# ----------------------------------------------------------------------------------------------------
def near_dup_share(V: np.ndarray, agent: np.ndarray, thr: float = 0.95) -> dict:
    """V: n x D unit-normalized embeddings (e.g. raw bge rows of one day's chat statements); agent: n labels.
    dup_share: share of statements with another statement at cosine > thr; dup_within: ... by the same agent;
    dup_cross: ... by a different agent (H12 posthoc.py, step 4)."""
    V = np.asarray(V, dtype=np.float32)
    S = V @ V.T
    np.fill_diagonal(S, 0)
    a = np.asarray(agent)
    same = a[:, None] == a[None, :]
    return {"n": int(len(V)), "dup_share": float((S.max(1) > thr).mean()),
            "dup_within": float((np.where(same, S, 0).max(1) > thr).mean()),
            "dup_cross": float((np.where(~same, S, 0).max(1) > thr).mean())}


def near_dup_share_by(groups, V: np.ndarray, agent: np.ndarray, thr: float = 0.95, min_n: int = 20) -> list[dict]:
    """near_dup_share per group label (e.g. PT date); groups with < min_n statements are skipped (H12: 20)."""
    groups = np.asarray(groups)
    out = []
    for g in np.unique(groups):
        ix = np.flatnonzero(groups == g)
        if len(ix) < min_n:
            continue
        out.append({"group": g, **near_dup_share(V[ix], np.asarray(agent)[ix], thr)})
    return out
