"""H101 core: exact maximum-entropy hierarchy on small agent subsets (n <= 12), entropies and ratios.

Models (all exponential families over the 2^n binary patterns, fitted by damped Newton on the convex dual with a
Gaussian prior of variance PRIOR_VAR per parameter, i.e. lambda = 1 / (PRIOR_VAR * T)):
  ind   h_i
  K     h_i + V(K), K = 1..n          (shared item-popularity field; Tkacik's population-count constraint)
  pair  h_i + J_ij
  pairK h_i + J_ij + V(K)             (K-pairwise)
Empirical entropy: plug-in + Miller-Madow. Fitted-model entropies: + k_eff / (2T) (first-order overfit correction,
k_eff = number of features whose empirical mean is strictly inside (0, 1)).

Ratios (per subset; units aggregate as ratios of sums):
  I_N   = S1 - SN
  rho_raw = (S1 - S2) / I_N            Schneidman I2/IN
  phi     = (S1 - SK) / I_N            shared-field share
  rho_F   = (SK - S2K) / (SK - SN)     pairwise sufficiency after field removal (primary)
  r_HO    = (S2K - SN) / I_N           higher-order remainder
"""
from __future__ import annotations

import numpy as np

PRIOR_VAR = 4.0


TRUNC = True   # models live on the support K >= 1 (items used by >= 1 subset agent); see card "Model"


def states(n: int) -> np.ndarray:
    idx = np.arange(1 if TRUNC else 0, 2 ** n)
    return ((idx[:, None] >> np.arange(n)[None, :]) & 1).astype(np.float64)


_FEAT_CACHE: dict = {}


def features(n: int, kind: str) -> np.ndarray:
    key = (n, kind)
    if key in _FEAT_CACHE:
        return _FEAT_CACHE[key]
    S = states(n)
    cols = [S]
    if kind in ("pair", "pairK"):
        iu, ju = np.triu_indices(n, 1)
        cols.append(S[:, iu] * S[:, ju])
    if kind in ("K", "pairK"):
        K = S.sum(1).astype(int)
        cols.append((K[:, None] == np.arange(2, n + 1)[None, :]).astype(np.float64))
    F = np.concatenate(cols, axis=1)
    _FEAT_CACHE[key] = F
    return F


def encode(X: np.ndarray) -> np.ndarray:
    """T x n binary matrix -> pattern index."""
    X = np.asarray(X, dtype=np.int64)
    return (X << np.arange(X.shape[1])[None, :]).sum(1)


def counts(X: np.ndarray) -> np.ndarray:
    """Pattern counts on the model support (index 0 = all-zero pattern dropped when TRUNC)."""
    n = X.shape[1]
    c = np.bincount(encode(X), minlength=2 ** n).astype(np.float64)
    return c[1:] if TRUNC else c


def support(X: np.ndarray) -> np.ndarray:
    """Rows on the support (K >= 1 when TRUNC)."""
    X = np.asarray(X)
    return X[X.sum(1) > 0] if TRUNC else X


def entropy_plugin(c: np.ndarray, mm: bool = True) -> float:
    T = c.sum()
    p = c[c > 0] / T
    H = float(-(p * np.log(p)).sum())
    if mm:
        H += (len(p) - 1) / (2 * T)
    return H


def fit_maxent(c: np.ndarray, n: int, kind: str, prior_var: float = PRIOR_VAR, iters: int = 60, tol: float = 1e-9):
    """Return (theta, model probabilities p, entropy S (uncorrected), k_eff)."""
    F = features(n, kind)
    T = c.sum()
    mu = F.T @ (c / T)
    lam = 1.0 / (prior_var * T)
    d = F.shape[1]
    th = np.zeros(d)
    # independent start for the h block
    m = np.clip(mu[:n], 1e-4, 1 - 1e-4)
    th[:n] = np.log(m / (1 - m))
    for _ in range(iters):
        E = F @ th
        E -= E.max()
        w = np.exp(E)
        p = w / w.sum()
        Ef = F.T @ p
        g = Ef - mu + lam * th
        if np.max(np.abs(g)) < tol:
            break
        C = (F * p[:, None]).T @ F - np.outer(Ef, Ef)
        H = C + lam * np.eye(d)
        try:
            step = np.linalg.solve(H, g)
        except np.linalg.LinAlgError:
            step = np.linalg.lstsq(H, g, rcond=None)[0]
        # damped line search on the dual objective
        def obj(t):
            e = F @ t
            mx = e.max()
            return mx + np.log(np.exp(e - mx).sum()) - t @ mu + 0.5 * lam * t @ t
        f0 = obj(th)
        a = 1.0
        while a > 1e-4:
            tn = th - a * step
            if obj(tn) <= f0 + 1e-12:
                break
            a *= 0.5
        th = th - a * step
    E = F @ th
    E -= E.max()
    w = np.exp(E)
    p = w / w.sum()
    pp = p[p > 0]
    S = float(-(pp * np.log(pp)).sum())
    k_eff = int(((mu > 0) & (mu < 1)).sum())
    return th, p, S, k_eff


def hierarchy(X: np.ndarray, prior_var: float = PRIOR_VAR, correct: bool = True) -> dict:
    """All entropies for one T x n binary sample (rows off the support are dropped first). Returns dict with S1, SK,
    S2, S2K, SN and the ratios; `correct` adds the first-order corrections (k/2T, Miller-Madow)."""
    X = support(np.asarray(X))
    T, n = X.shape
    c = counts(X)
    out = {"T": int(T), "n": int(n), "rate": float(X.mean()), "meanK": float(X.sum(1).mean()),
           "m_patterns": int((c > 0).sum())}
    ent = {}
    fits = {}
    for kind, key in (("ind", "S1"), ("K", "SK"), ("pair", "S2"), ("pairK", "S2K")):
        th, p, S, k = fit_maxent(c, n, kind, prior_var)
        ent[key] = S + (k / (2 * T) if correct else 0.0)
        fits[kind] = (th, p)
    ent["SN"] = entropy_plugin(c, mm=correct)
    out.update(ent)
    out.update(ratios(ent))
    out["_fits"] = fits
    return out


def ratios(e: dict) -> dict:
    IN = e["S1"] - e["SN"]
    beyond = e["SK"] - e["SN"]
    return {"I_N": IN, "I_2": e["S1"] - e["S2"], "I_K": e["S1"] - e["SK"], "I_2K": e["S1"] - e["S2K"],
            "rho_raw": (e["S1"] - e["S2"]) / IN if IN > 0 else np.nan,
            "phi": (e["S1"] - e["SK"]) / IN if IN > 0 else np.nan,
            "rho_F": (e["SK"] - e["S2K"]) / beyond if beyond > 0 else np.nan,
            "r_HO": (e["S2K"] - e["SN"]) / IN if IN > 0 else np.nan}


def agg(rows: list[dict]) -> dict:
    """Ratio of sums over subsets/days, weighted by T (entropies are per item)."""
    w = np.array([r["T"] for r in rows], float)
    tot = {k: float((w * np.array([r[k] for r in rows])).sum() / w.sum()) for k in ("S1", "SK", "S2", "S2K", "SN")}
    out = ratios(tot)
    out.update({k: tot[k] for k in tot})
    out["T"] = float(w.sum())
    return out


def sample_from(p: np.ndarray, n: int, T: int, rng: np.random.Generator) -> np.ndarray:
    idx = rng.choice(len(p), size=T, p=p) + (1 if (TRUNC and len(p) == 2 ** n - 1) else 0)
    return ((idx[:, None] >> np.arange(n)[None, :]) & 1).astype(np.int8)


# ----------------------------------------------------------------------------------------------- shared-field null
def latent_field_fit(X: np.ndarray, L: int = 4, iters: int = 200, rng: np.random.Generator | None = None):
    """Latent-class model: item class z in 1..L with weight pi_z; s_i | z ~ Bernoulli(q_iz). EM. Conditionally
    independent given the latent item field (a field-only world with heterogeneous agents)."""
    rng = rng or np.random.default_rng(0)
    X = np.asarray(X, float)
    T, n = X.shape
    K = X.sum(1)
    # init by K quantiles
    order = np.argsort(K + 1e-3 * rng.random(T))
    z = np.zeros(T, int)
    for j, chunk in enumerate(np.array_split(order, L)):
        z[chunk] = j
    R = np.zeros((T, L))
    R[np.arange(T), z] = 1
    for _ in range(iters):
        pi = R.mean(0) + 1e-12
        q = np.clip((R.T @ X + 0.5) / (R.sum(0)[:, None] + 1.0), 1e-4, 1 - 1e-4)  # L x n
        ll = X @ np.log(q).T + (1 - X) @ np.log(1 - q).T + np.log(pi)[None, :]
        ll -= ll.max(1, keepdims=True)
        Rn = np.exp(ll)
        Rn /= Rn.sum(1, keepdims=True)
        if np.abs(Rn - R).max() < 1e-6:
            R = Rn
            break
        R = Rn
    pi = R.mean(0)
    q = np.clip((R.T @ X + 0.5) / (R.sum(0)[:, None] + 1.0), 1e-4, 1 - 1e-4)
    return pi, q


def latent_field_sample(pi, q, T, rng):
    z = rng.choice(len(pi), size=T, p=pi / pi.sum())
    return (rng.random((T, q.shape[1])) < q[z]).astype(np.int8)


def item_shuffle(X: np.ndarray, rng) -> np.ndarray:
    """Permute each agent's column independently (rates kept, co-usage destroyed)."""
    Y = np.empty_like(X)
    for j in range(X.shape[1]):
        Y[:, j] = X[rng.permutation(X.shape[0]), j]
    return Y
