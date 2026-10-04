"""H92 library: correlation-matrix estimators (zero, mean field, raw, Ledoit-Wolf to identity, Ledoit-Wolf to constant
correlation, RMT clipping at a calibrated or a Marchenko-Pastur edge), the surrogate edges, and the next-day forecast
loop. Matrices and synthetic days come from scheme/daymat.py (identical copy of H91's)."""
from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "scheme"))
import daymat as DM  # noqa: E402

import numpy as np  # noqa: E402
import polars as pl  # noqa: E402

ROOT = DM.ROOT
OUT = ROOT / "data/processed/H92-rmt-cleaned-forecast"
EST = ["E0_zero", "E1_mean", "E2_raw", "E3_lwi", "E4_lwcc", "E5_clip", "E6_clip_mp"]
N_SURR = 49
Q_EDGE = 0.95
SEED = 20261004
D = DM.D


# ============================================================================================ data -> sample matrix
def content_X(days: list[np.ndarray], present: list[np.ndarray]) -> np.ndarray:
    """days: list of N x W_d x d arrays for one agent set (absent agent-days are all-zero rows). Returns the N x T sample
    matrix (T = sum W_d * d), rows scaled to unit mean square (the overlap convention)."""
    X = np.concatenate([Z.reshape(Z.shape[0], -1) for Z in days], axis=1)
    s = np.sqrt((X ** 2).mean(1, keepdims=True))
    return X / np.where(s > 0, s, 1.0)


def spins_X(days: list[np.ndarray]) -> np.ndarray:
    """days: list of N x L_d spin arrays (absent agent-days are zeros), each already standardized per agent-day."""
    X = np.concatenate(days, axis=1)
    s = np.sqrt((X ** 2).mean(1, keepdims=True))
    return X / np.where(s > 0, s, 1.0)


def unitdiag(M: np.ndarray) -> np.ndarray:
    d = np.sqrt(np.clip(np.diag(M), 1e-12, None))
    C = M / d[:, None] / d[None, :]
    np.fill_diagonal(C, 1.0)
    return C


# ============================================================================================ estimators
def lw_identity(X: np.ndarray, S: np.ndarray) -> tuple[np.ndarray, float]:
    """Ledoit-Wolf (2004) shrinkage toward mu I (analytic intensity), on rows scaled to unit mean square."""
    N, T = X.shape
    mu = np.trace(S) / N
    d2 = np.sum((S - mu * np.eye(N)) ** 2) / N
    nx = (X ** 2).sum(0)
    b2bar = (np.sum(nx ** 2) / T - np.sum(S ** 2)) / (T * N)
    b2 = min(max(b2bar, 0.0), d2)
    s = b2 / d2 if d2 > 0 else 1.0
    return unitdiag(s * mu * np.eye(N) + (1 - s) * S), float(s)


def lw_constcorr(X: np.ndarray, S: np.ndarray) -> tuple[np.ndarray, float]:
    """Ledoit-Wolf (2003) shrinkage toward the constant-correlation target (analytic intensity)."""
    N, T = X.shape
    sd = np.sqrt(np.clip(np.diag(S), 1e-12, None))
    R = S / sd[:, None] / sd[None, :]
    rbar = (R.sum() - N) / (N * (N - 1))
    F = rbar * np.outer(sd, sd); np.fill_diagonal(F, np.diag(S))
    X2 = X ** 2
    pi_mat = X2 @ X2.T / T - S ** 2
    pi_hat = pi_mat.sum()
    th1 = (X ** 3) @ X.T / T - np.diag(S)[:, None] * S        # theta_{ii,ij}
    th2 = X @ (X ** 3).T / T - np.diag(S)[None, :] * S        # theta_{jj,ij}
    off = ~np.eye(N, dtype=bool)
    rho_hat = np.trace(pi_mat) + (rbar / 2) * np.sum((np.sqrt(np.diag(S))[None, :] / sd[:, None] * th1
                                                       + sd[:, None] / np.sqrt(np.diag(S))[None, :] * th2)[off])
    gam = np.sum((F - S) ** 2)
    kap = (pi_hat - rho_hat) / gam if gam > 0 else 0.0
    s = float(max(0.0, min(1.0, kap / T)))
    return unitdiag(s * F + (1 - s) * S), s


def clip(S: np.ndarray, edge: float) -> tuple[np.ndarray, int]:
    """Eigenvalue clipping (Laloux et al.): eigenvalues <= edge replaced by their mean (trace kept); unit diagonal."""
    w, V = np.linalg.eigh(S)
    noise = w <= edge
    k = int((~noise).sum())
    if noise.any():
        w = w.copy(); w[noise] = w[noise].mean()
    return unitdiag((V * w) @ V.T), k


def all_estimates(X: np.ndarray, edge_cal: float) -> dict:
    N, T = X.shape
    S = X @ X.T / T
    S = unitdiag(S)
    off = ~np.eye(N, dtype=bool)
    rbar = S[off].mean()
    E1 = np.full((N, N), rbar); np.fill_diagonal(E1, 1.0)
    E3, s3 = lw_identity(X, S)
    E4, s4 = lw_constcorr(X, S)
    E5, k5 = clip(S, edge_cal)
    mp = DM_mp_edge(N, T)
    E6, k6 = clip(S, mp)
    return {"E0_zero": np.eye(N), "E1_mean": E1, "E2_raw": S, "E3_lwi": E3, "E4_lwcc": E4, "E5_clip": E5, "E6_clip_mp": E6,
            "_meta": {"N": N, "T": T, "q": N / T, "edge_cal": edge_cal, "edge_mp": mp, "k_cal": k5, "k_mp": k6,
                      "shrink_lwi": s3, "shrink_lwcc": s4, "rbar": float(rbar),
                      "l1": float(np.linalg.eigvalsh(S)[-1])}}


def DM_mp_edge(N: int, T: float) -> float:
    return float((1 + np.sqrt(N / T)) ** 2)


# ============================================================================================ surrogate edges
def edge_content(days: list[np.ndarray], rng, n: int = N_SURR, q: float = Q_EDGE) -> float:
    """95th percentile of the top eigenvalue when each agent's window sequence is circularly shifted (independently,
    by >= 1 window) within each training day: keeps each agent's content, breaks same-window alignment."""
    l1 = []
    for _ in range(n):
        sd = []
        for Z in days:
            N, W = Z.shape[0], Z.shape[1]
            sh = rng.integers(1, W, N) if W > 1 else np.zeros(N, int)
            idx = (np.arange(W)[None, :] - sh[:, None]) % W
            sd.append(Z[np.arange(N)[:, None], idx])
        X = content_X(sd, None)
        l1.append(np.linalg.eigvalsh(unitdiag(X @ X.T / X.shape[1]))[-1])
    return float(np.quantile(l1, q))


def edge_spins(days: list[np.ndarray], mins: list[np.ndarray], rng, n: int = N_SURR, q: float = Q_EDGE,
               block: int = 30) -> float:
    """DQ8 trimmed block-shift edge: within each training day (already trimmed to the all-present window) and each
    30-min block, each agent's series is circularly shifted by >= 1 minute."""
    plans = []
    for A, m in zip(days, mins):
        blk = np.asarray(m) // block
        plans.append([np.flatnonzero(blk == b) for b in np.unique(blk)])
    l1 = []
    for _ in range(n):
        sd = []
        for A, segs in zip(days, plans):
            B = np.empty_like(A)
            N = A.shape[0]
            for ix in segs:
                Lb = len(ix)
                if Lb < 2:
                    B[:, ix] = A[:, ix]; continue
                sh = rng.integers(1, Lb, N)
                ar = (np.arange(Lb)[None, :] - sh[:, None]) % Lb
                B[:, ix] = A[np.arange(N)[:, None], ix[ar]]
            sd.append(B)
        X = spins_X(sd)
        l1.append(np.linalg.eigvalsh(unitdiag(X @ X.T / X.shape[1]))[-1])
    return float(np.quantile(l1, q))


# ============================================================================================ scoring
def mse_off(C: np.ndarray, Q: np.ndarray) -> float:
    off = ~np.eye(C.shape[0], dtype=bool)
    return float(np.mean((C[off] - Q[off]) ** 2))


def room_contrast(C: np.ndarray, rooms: np.ndarray):
    """Mean within-room minus mean between-room off-diagonal entry (needs >= 2 rooms with >= 2 agents)."""
    rooms = np.asarray(rooms)
    ok = rooms >= 0
    if ok.sum() < 4:
        return None
    vals, cnt = np.unique(rooms[ok], return_counts=True)
    if (cnt >= 2).sum() < 2:
        return None
    same = (rooms[:, None] == rooms[None, :]) & ok[:, None] & ok[None, :]
    diff = (rooms[:, None] != rooms[None, :]) & ok[:, None] & ok[None, :]
    np.fill_diagonal(same, False)
    if not same.any() or not diff.any():
        return None
    return float(C[same].mean() - C[diff].mean())


def boot_mean_ci(x: np.ndarray, rng, B: int = 2000):
    x = np.asarray(x, float); x = x[np.isfinite(x)]
    if len(x) < 3:
        return (float(x.mean()) if len(x) else np.nan, None, None)
    bs = [rng.choice(x, len(x)).mean() for _ in range(B)]
    return float(x.mean()), float(np.quantile(bs, 0.025)), float(np.quantile(bs, 0.975))


def spearman(a, b) -> float:
    a, b = np.asarray(a, float), np.asarray(b, float)
    ok = np.isfinite(a) & np.isfinite(b)
    if ok.sum() < 4:
        return np.nan
    ra = pl.Series(a[ok]).rank().to_numpy(); rb = pl.Series(b[ok]).rank().to_numpy()
    return float(np.corrcoef(ra, rb)[0, 1])
