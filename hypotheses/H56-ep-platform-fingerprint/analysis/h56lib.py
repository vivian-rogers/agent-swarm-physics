"""H56 library: entropy production from transition-count matrices, count-matched window statistics, and
synthetic Markov chains with controlled entropy production.

The estimators reproduce H14's (imported read-only for the equality test) exactly from fold-level count matrices:
  newton_counts  H14 ep_newton = H05 ep_gauss_crossfit on antisymmetrized transition indicators
                 (K = Cov(g) has a closed form from counts: diag(n_ab + n_ba) - n gbar gbar^T, over n - 1)
  cfx_counts     H14 ep_cfx (cross-fitted exact dual with count-based Theta)
  plugin_counts  H14 ep_plugin (biased foil)
Folds follow H05/H14: sorted fold labels, label i -> fold i % k, k = min(5, #labels).
"""
from __future__ import annotations

import os

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "VECLIB_MAXIMUM_THREADS", "POLARS_MAX_THREADS"):
    os.environ.setdefault(_v, "2")

import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[3]
DATA = ROOT / "data/processed/H56-ep-platform-fingerprint"
H14 = ROOT / "hypotheses/H14-behavior-entropy-production/analysis"
VARIANTS = ["act_all", "act_agent", "coarse_all", "coarse_agent", "act_agent_b3", "coarse_agent_b3"]
QV = [11, 11, 6, 6, 11, 6]
ACT = ["shell", "click", "scroll", "look", "type", "chat", "idle", "consolidate", "search", "session", "other"]
COARSE = ["browse", "type", "shell", "chat", "idle", "consolidate"]


def h14():
    """H14's library, imported read-only (for equality tests and its simulator)."""
    if str(H14) not in sys.path:
        sys.path.insert(0, str(H14))
    import h14lib  # noqa: E402
    return h14lib


# ============================================================================ estimators from counts
def _merge_folds(C_labels, k=None):
    """C_labels: (L, q, q) count matrices for L sorted labels. Returns (k, q, q) fold matrices (label i -> i % k)."""
    L = len(C_labels)
    k = min(5, L) if k is None else k
    F = np.zeros((k,) + C_labels.shape[1:])
    for i in range(L):
        F[i % k] += C_labels[i]
    return F


def newton_counts(C_labels, ridge=1e-3, pairs=None):
    """Cross-fitted Newton-step bound (nats per transition) from per-label count matrices (L, q, q), L >= 2.
    pairs: optional list of (a, b), a < b, restricting the observables (a sub-bound)."""
    C_labels = np.asarray(C_labels, dtype=np.float64)
    L = len(C_labels)
    if L < 2:
        return np.nan
    F = _merge_folds(C_labels)
    C = F.sum(0)
    n = C.sum()
    if n < 3:
        return np.nan
    q = C.shape[0]
    iu, ju = np.triu_indices(q, 1)
    s = C[iu, ju] + C[ju, iu]
    keep = s > 0
    if pairs is not None:
        allowed = np.zeros(len(iu), bool)
        pset = set(map(tuple, pairs))
        for kk, (a, b) in enumerate(zip(iu, ju)):
            allowed[kk] = (a, b) in pset
        keep &= allowed
    if not keep.any():
        return np.nan
    iu, ju, s = iu[keep], ju[keep], s[keep]
    gbar = (C[iu, ju] - C[ju, iu]) / n
    K = (np.diag(s) - n * np.outer(gbar, gbar)) / (n - 1)
    K = K + ridge * np.trace(K) / len(K) * np.eye(len(K))
    nf = F.sum((1, 2))
    ok = nf > 0
    means = (F[ok][:, iu, ju] - F[ok][:, ju, iu]) / nf[ok][:, None]
    kk = len(means)
    if kk < 2:
        return np.nan
    W = np.linalg.solve(K, means.T).T
    M = means @ W.T
    return float(2 * (M.sum() - np.trace(M)) / (kk * (kk - 1)))


def cfx_counts(C_labels, alpha=0.5):
    """Cross-fitted exact AIK dual with Theta = ln((n_ab + a) / (n_ba + a)) from training folds (H14 ep_cfx)."""
    C_labels = np.asarray(C_labels, dtype=np.float64)
    if len(C_labels) < 2:
        return np.nan
    F = _merge_folds(C_labels)
    tot = F.sum(0)
    vals, ws = [], []
    for i in range(len(F)):
        te = F[i]
        tr = tot - te
        nte, ntr = te.sum(), tr.sum()
        if nte == 0 or ntr == 0:
            continue
        Th = np.log((tr + alpha) / (tr.T + alpha))
        zbar = (te * Th).sum() / nte
        lme = np.log((te * np.exp(-Th)).sum() / nte)
        vals.append(zbar - lme)
        ws.append(nte)
    return float(np.average(vals, weights=ws)) if vals else np.nan


def plugin_counts(C):
    C = np.asarray(C, dtype=np.float64)
    if C.ndim == 3:
        C = C.sum(0)
    n = C.sum()
    if n == 0:
        return np.nan
    m = (C > 0) & (C.T > 0)
    np.fill_diagonal(m, False)
    return float((C[m] / n * np.log(C[m] / C.T[m])).sum())


ESTIMATORS = {"newton": newton_counts, "cfx": cfx_counts, "plugin": plugin_counts}


def sector_pairs(q, state):
    """Pairs (a < b) that involve `state` (for sector sub-bounds, e.g. the idle sector)."""
    return [(min(state, x), max(state, x)) for x in range(q) if x != state]


# ============================================================================ subsampling
def stratified_subsample(C_labels, m, rng):
    """Hypergeometric subsample of exactly m transitions from per-label count matrices, allocated to labels in
    proportion to their counts (largest remainder). Returns (L, q, q) int counts."""
    C_labels = np.asarray(C_labels, dtype=np.int64)
    nl = C_labels.sum((1, 2))
    tot = nl.sum()
    if m >= tot:
        return C_labels.copy()
    share = nl * m / tot
    alloc = np.floor(share).astype(np.int64)
    rem = m - alloc.sum()
    if rem > 0:
        order = np.argsort(-(share - alloc))
        alloc[order[:rem]] += 1
    alloc = np.minimum(alloc, nl)
    out = np.zeros_like(C_labels)
    q = C_labels.shape[1]
    for i, ai in enumerate(alloc):
        if ai > 0:
            out[i] = rng.multivariate_hypergeometric(C_labels[i].ravel(), int(ai)).reshape(q, q)
    return out


def matched_pair(Cpre, Cpost, rng, R=4, est=("newton",), pairs=None, m=None):
    """Count-matched EP on two sides: both subsampled to m = min(n_pre, n_post) transitions, R draws averaged.
    Returns {est: (pre, post)}."""
    npre, npost = int(np.sum(Cpre)), int(np.sum(Cpost))
    m = min(npre, npost) if m is None else m
    out = {e: [np.zeros(R), np.zeros(R)] for e in est}
    for r in range(R):
        a = stratified_subsample(Cpre, m, rng)
        b = stratified_subsample(Cpost, m, rng)
        for e in est:
            if e == "newton":
                out[e][0][r], out[e][1][r] = newton_counts(a, pairs=pairs), newton_counts(b, pairs=pairs)
            else:
                f = ESTIMATORS[e]
                out[e][0][r], out[e][1][r] = f(a), f(b)
    return {e: (float(np.nanmean(v[0])), float(np.nanmean(v[1]))) for e, v in out.items()}


def event_stats(delta, level=None):
    """Event statistics from per-agent Delta_i: mean, t, sign share, relative change."""
    d = np.asarray(delta, float)
    d = d[np.isfinite(d)]
    n = len(d)
    if n < 2:
        return {"n": n, "dbar": np.nan, "t": np.nan, "fpos": np.nan, "rel": np.nan}
    se = d.std(ddof=1) / np.sqrt(n)
    t = d.mean() / se if se > 0 else np.nan
    rel = d.mean() / level if (level is not None and level > 0) else np.nan
    return {"n": n, "dbar": float(d.mean()), "t": float(t), "fpos": float((d > 0).mean()), "rel": float(rel)}


def did_stats(d_target, d_control):
    a, b = np.asarray(d_target, float), np.asarray(d_control, float)
    a, b = a[np.isfinite(a)], b[np.isfinite(b)]
    if len(a) < 2 or len(b) < 2:
        return {"n_t": len(a), "n_c": len(b), "did": np.nan, "t": np.nan}
    se = np.sqrt(a.var(ddof=1) / len(a) + b.var(ddof=1) / len(b))
    return {"n_t": len(a), "n_c": len(b), "did": float(a.mean() - b.mean()), "t": float((a.mean() - b.mean()) / se) if se > 0 else np.nan}


# ============================================================================ synthetic chains
def chain_from_params(B, F, U, s, stick):
    """Transition matrix: off-diagonal W_ab = B_ab exp((U_a - U_b)/2 + s F_ab / 2), rows normalized to 1 - stick_a,
    diagonal stick_a. B symmetric > 0 (conductances), F antisymmetric (forces), U potential (field)."""
    q = len(U)
    W = B * np.exp((U[:, None] - U[None, :]) / 2 + s * F / 2)
    np.fill_diagonal(W, 0)
    P = W / W.sum(1, keepdims=True) * (1 - stick)[:, None]
    P[np.diag_indices(q)] = stick
    return P


def stationary(P):
    w, v = np.linalg.eig(P.T)
    pi = np.real(v[:, np.argmin(np.abs(w - 1))])
    pi = np.abs(pi)
    return pi / pi.sum()


def true_ep(P):
    pi = stationary(P)
    J = pi[:, None] * P
    m = (J > 0) & (J.T > 0)
    np.fill_diagonal(m, False)
    return float((J[m] * np.log(J[m] / J.T[m])).sum())


def solve_s(B, F, U, stick, target, s_hi=50.0):
    """Drive strength s >= 0 such that the chain's true EP equals target (bisection)."""
    lo, hi = 0.0, 1.0
    while true_ep(chain_from_params(B, F, U, hi, stick)) < target and hi < s_hi:
        hi *= 2
    for _ in range(60):
        mid = 0.5 * (lo + hi)
        if true_ep(chain_from_params(B, F, U, mid, stick)) < target:
            lo = mid
        else:
            hi = mid
    return 0.5 * (lo + hi)


def random_template(q, rng, sparsity=0.4, stick_mean=0.4):
    B = np.exp(rng.normal(0, 1.0, (q, q)))
    B = (B + B.T) / 2
    mask = rng.random((q, q)) < sparsity
    mask = np.triu(mask, 1)
    mask = mask | mask.T
    B[mask] *= 0.05                      # weak links (sparse-ish chain)
    F = rng.normal(0, 1, (q, q))
    F = (F - F.T) / 2
    U = rng.normal(0, 1.0, q)
    stick = np.clip(rng.normal(stick_mean, 0.15, q), 0.05, 0.85)
    return B, F, U, stick


def simulate_counts(P, lengths, rng, blocks=4, start=None):
    """Simulate one Markov chain per day (vectorized over days) and return per-day per-block count matrices
    (D, blocks, q, q) and per-day transition totals."""
    q = len(P)
    lengths = np.asarray(lengths, int)
    D = len(lengths)
    Lmax = int(lengths.max()) + 1
    cP = np.cumsum(P, 1)
    cP[:, -1] = 1.0 + 1e-12
    pi = stationary(P)
    x = rng.choice(q, size=D, p=pi) if start is None else np.full(D, start)
    C = np.zeros((D, blocks, q, q), dtype=np.int64)
    U = rng.random((Lmax, D))
    for t in range(1, Lmax):
        live = t <= lengths
        if not live.any():
            break
        xn = (U[t][:, None] > cP[x]).sum(1)
        blk = np.minimum(((t - 1) * blocks) // np.maximum(lengths, 1), blocks - 1)
        idx = np.flatnonzero(live)
        np.add.at(C, (idx, blk[idx], x[idx], xn[idx]), 1)
        x = np.where(live, xn, x)
    return C


def insert_scaffold(P_agent, cadence, forced_next, rng, lengths, blocks=4):
    """Agent chain on q states plus one scaffold state (index q): after every `cadence`-th agent transition the
    chain enters the scaffold state, then is forced to `forced_next`. Returns (counts_with_scaffold (q+1 states),
    counts_agent_only_cut) per day and block."""
    q = len(P_agent)
    lengths = np.asarray(lengths, int)
    D = len(lengths)
    cP = np.cumsum(P_agent, 1)
    cP[:, -1] = 1.0 + 1e-12
    pi = stationary(P_agent)
    Cw = np.zeros((D, blocks, q + 1, q + 1), dtype=np.int64)
    Ca = np.zeros((D, blocks, q + 1, q + 1), dtype=np.int64)
    for d in range(D):
        L = lengths[d]
        x = rng.choice(q, p=pi)
        k = 0
        phase = rng.integers(0, cadence)
        for t in range(1, L + 1):
            blk = min(((t - 1) * blocks) // L, blocks - 1)
            k += 1
            if (k + phase) % cadence == 0:
                Cw[d, blk, x, q] += 1
                Cw[d, blk, q, forced_next] += 1
                x = forced_next          # agent-only chain is cut across the scaffold step
                continue
            xn = int((rng.random() > cP[x]).sum())
            Cw[d, blk, x, xn] += 1
            Ca[d, blk, x, xn] += 1
            x = xn
    return Cw, Ca
