"""H12 core library: random-matrix spectra with surrogate edges, and bias-corrected participation ratios.

Used by scheme/build.py, analysis/synthetic.py, analysis/run_units.py, analysis/ne34.py and analysis/confirm.py.
Threads are pinned to 1 per process (callers use at most 2 processes).
"""
from __future__ import annotations

import os

for _v in ("OMP_NUM_THREADS", "VECLIB_MAXIMUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ.setdefault(_v, "1")
os.environ.setdefault("POLARS_MAX_THREADS", "2")

import datetime as dt  # noqa: E402
import json  # noqa: E402
import subprocess  # noqa: E402
import sys  # noqa: E402
from pathlib import Path  # noqa: E402

import numpy as np  # noqa: E402

ROOT = Path(__file__).resolve().parents[3]
HYP = ROOT / "hypotheses/H12-groupthink-dimensional-collapse"
OUT = ROOT / "data/processed/H12-groupthink-dimensional-collapse"
SH = ROOT / "data/processed/shared"
FIG = HYP / "figures"
SEED = 20261003

# Data version (round 1b, 2026-10-04). "r1": round-1 activity spins from shared activity_bins (which dropped about
# half of all events, DQ8). "fixed": spins rebuilt from activity_bins_fixed into OUT/r1b/ (units, agents_units,
# spins); statement inputs (stmt_index, stmt_white_d64) do not depend on activity_bins and stay in OUT. Set with the
# env var H12_DATA_VERSION or the scripts' --data-version flag (set before import, inherited by spawned workers).
DATA_VERSION = os.environ.get("H12_DATA_VERSION", "r1")
assert DATA_VERSION in ("r1", "fixed"), DATA_VERSION
AB = SH / ("activity_bins_fixed.parquet" if DATA_VERSION == "fixed" else "activity_bins.parquet")
OUTV = OUT / "r1b" if DATA_VERSION == "fixed" else OUT      # activity-derived tables and arm-(a) spin results
STALLS_FIXED = SH / "outages_fixed/stall_minutes.parquet"   # H38's rule on the fixed table (shared sidecar)
sys.path.insert(0, str(ROOT / "infra/shared"))
from common import REVISION, holdout_mask, load_holdout  # noqa: E402,F401

# Step changes inside goal periods: same split dates as H01 (h01common.GOAL_SPLITS), for comparability.
GOAL_SPLITS = {36: ["2026-03-24"], 38: ["2026-04-14", "2026-04-20"],
               51: ["2026-07-09", "2026-08-05", "2026-08-25", "2026-09-03"]}


def unit_of(goal_no: int, pt_date: str) -> str:
    cuts = GOAL_SPLITS.get(int(goal_no))
    if not cuts:
        return str(int(goal_no))
    k = sum(pt_date >= c for c in cuts)
    return f"{int(goal_no)}{'abcdefgh'[k]}"


def stable_seed(obj) -> int:
    import zlib
    return zlib.crc32(json.dumps(obj, sort_keys=True, default=str).encode()) % 2**31


def git_commit() -> str:
    r = subprocess.run(["git", "-C", str(ROOT), "rev-parse", "--short", "HEAD"], capture_output=True, text=True)
    dirty = subprocess.run(["git", "-C", str(ROOT), "status", "--porcelain", "--", str(HYP)],
                           capture_output=True, text=True).stdout
    return (r.stdout.strip() or "none") + ("+uncommitted" if dirty.strip() else "")


def write_provenance(built_by: str, tables: list[str], params: dict, path: Path | None = None):
    path = path or (OUT / "_provenance.json")
    prov = json.loads(path.read_text()) if path.exists() else {}
    prov[built_by] = {"built_by": built_by, "git_commit": git_commit(),
                      "inputs": [{"source": "ai-village", "revision": REVISION, "tables": tables}],
                      "params": params, "built_at": dt.datetime.now(dt.timezone.utc).isoformat()}
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(prov, indent=1))


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


# ---------------------------------------------------------------------------------------------- round 1b (DQ8 design)
def trim_rows(A: np.ndarray) -> np.ndarray:
    """All-present window of one day (H38's operator rule, DQ8 `all_present_window`): bins in which every agent with
    at least one active bin that day is between its first and last active bin. A: N x L (+1 active, -1 not)."""
    act = A > 0
    has = act.any(1)
    if not has.any():
        return np.zeros(A.shape[1], bool)
    L = A.shape[1]
    first = np.argmax(act, axis=1); last = L - 1 - np.argmax(act[:, ::-1], axis=1)
    idx = np.arange(L)
    inside = (idx[None, :] >= first[:, None]) & (idx[None, :] <= last[:, None])
    return inside[has].all(0)


def blockshift_surrogate(days: list[np.ndarray], mins: list[np.ndarray], rng: np.random.Generator, block_min: int = 30) -> np.ndarray:
    """Independent circular shift (>= 1) of each agent's series within each (day, 30-min block of minute index) of the
    kept bins (DQ8 `nulls.block_shift`; H25/H38 N1). days: N x L_d arrays (rows already trimmed); mins: their minutes."""
    out = []
    for A, m in zip(days, mins):
        B = np.empty_like(A)
        blk = np.asarray(m) // block_min
        N = A.shape[0]
        for b in np.unique(blk):
            ix = np.flatnonzero(blk == b)
            Lb = len(ix)
            if Lb < 2:
                B[:, ix] = A[:, ix]
                continue
            sh = rng.integers(1, Lb, size=N)
            ar = (np.arange(Lb)[None, :] - sh[:, None]) % Lb
            B[:, ix] = A[np.arange(N)[:, None], ix[ar]]
        out.append(B)
    return np.concatenate(out, axis=1)


def spectrum_test_blockshift(days: list[np.ndarray], mins: list[np.ndarray], n_surr: int, rng: np.random.Generator,
                             q: float = 0.95) -> dict:
    """Round-1b corrected null for spin spectra: rows are trimmed BEFORE the surrogates are drawn (caller), and the edge
    is the q-quantile of the top eigenvalue under block shifts (size 0.05 on independent swarms in the DQ8 table, vs
    0.19 for the cross-day edge on trimmed grids and 0.62 on whole-day grids)."""
    X = np.concatenate(days, axis=1)
    keep = X.std(1) > 0
    days = [d[keep] for d in days]
    X = X[keep]
    w = corr_eig(X)
    null = np.empty((n_surr, len(w)))
    for s in range(n_surr):
        Y = blockshift_surrogate(days, mins, rng)
        null[s] = corr_eig(Y) if (Y.std(1) > 0).all() else np.nan
    null = null[np.isfinite(null).all(1)]
    edge = float(np.quantile(null[:, 0], q)) if len(null) else np.nan
    qk = np.quantile(null, q, axis=0) if len(null) else np.full(len(w), np.nan)
    above = w > qk
    return {"eig": w, "edge": edge, "k": int((w > edge).sum()), "k_rank": int(np.argmin(above)) if not above.all() else len(w),
            "T": int(X.shape[1]), "N": int(X.shape[0])}


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
