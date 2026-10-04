"""H14 round 1b helpers: fast count-based estimators, detailed-balance and block-flip nulls, v3 soft observables.

Count-based Newton / cfx are H56's closed forms (`h56lib.newton_counts`, `cfx_counts`), copied here read-only
(identical to H14's `ep_newton` / `ep_cfx` on transition indicators; H56 verified equality). They are copied, not
imported, because cross-hypothesis imports are being retired (QUEUE.md); `newton_counts` should move to infra/shared.

Nulls:
  db_null_counts   detailed-balance surrogate (H14 N2): the reversible chain P_ab ~ (n_ab + n_ba)/2, restarted at every
                   segment start from the real start state with the real segment length; same estimator applied
  flip_null        block-reversal (sign-flip) surrogate: each contiguous block of transitions is time-reversed with
                   probability 1/2 (its count matrix transposed / its antisymmetric observables negated). Exact for a
                   reversible process up to block-boundary effects; works for soft observables, where no DB chain exists
"""
from __future__ import annotations

import os

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "VECLIB_MAXIMUM_THREADS", "POLARS_MAX_THREADS"):
    os.environ.setdefault(_v, "2")

import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "hypotheses/H05-rooms-cut/analysis"))
from ep import ep_gauss_crossfit  # noqa: E402  (H05's validated estimator, as in h14lib)


# ============================================================================ count-based estimators (H56 closed forms)
def _merge_folds(C_labels, k=None):
    Lb = len(C_labels)
    k = min(5, Lb) if k is None else k
    F = np.zeros((k,) + C_labels.shape[1:])
    for i in range(Lb):
        F[i % k] += C_labels[i]
    return F


def newton_counts(C_labels, ridge=1e-3):
    """Cross-fitted Newton-step bound (nats per transition) from per-label (day) count matrices (L, q, q), L >= 2."""
    C_labels = np.asarray(C_labels, dtype=np.float64)
    if len(C_labels) < 2:
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


def day_counts(a, b, day, q, nday):
    C = np.zeros((nday, q, q))
    np.add.at(C, (day, a, b), 1)
    return C


# ============================================================================ detailed-balance surrogate
def db_null_counts(a, b, day, seg_start_state, seg_len, seg_day, q, nday, R, rng):
    """R surrogate per-day count stacks (R, nday, q, q) from the reversible chain of the pooled counts.

    Each segment s is simulated from seg_start_state[s] for seg_len[s] transitions; its transitions get seg_day[s]."""
    C = np.zeros((q, q))
    np.add.at(C, (a, b), 1)
    S = (C + C.T) / 2.0
    rs = S.sum(1)
    P = np.where(rs[:, None] > 0, S / np.where(rs[:, None] > 0, rs[:, None], 1), np.eye(q))
    cP = np.cumsum(P, 1)
    cP[:, -1] = 1.0 + 1e-12
    nseg = len(seg_len)
    N = int(seg_len.sum())
    out = np.zeros((R, nday, q, q))
    if N == 0:
        return out
    # one long restarted chain: transitions t = 0..N-1; the state before transition t
    is_start = np.zeros(N, bool)
    st_idx = np.r_[0, np.cumsum(seg_len)[:-1]]
    is_start[st_idx] = True
    start_state = np.zeros(N, np.int64)
    start_state[st_idx] = seg_start_state
    tday = np.repeat(seg_day, seg_len)
    cur = np.zeros(R, np.int64)
    prev_arr = np.empty((R, N), np.int16)
    next_arr = np.empty((R, N), np.int16)
    U = rng.random((R, N))
    for t in range(N):
        if is_start[t]:
            cur[:] = start_state[t]
        nxt = (U[:, t, None] > cP[cur]).sum(1)
        prev_arr[:, t] = cur
        next_arr[:, t] = nxt
        cur = nxt
    code = (np.arange(R)[:, None] * nday + tday[None, :]) * q * q + prev_arr.astype(np.int64) * q + next_arr
    out = np.bincount(code.ravel(), minlength=R * nday * q * q).reshape(R, nday, q, q).astype(np.float64)
    return out


# ============================================================================ block-flip null
def block_counts(a, b, day, block, q):
    """Per-block count matrices (nb, q, q) and each block's day."""
    nb = int(block.max()) + 1 if len(block) else 0
    C = np.zeros((nb, q, q))
    np.add.at(C, (block, a, b), 1)
    bd = np.zeros(nb, np.int64)
    bd[block] = day
    return C, bd


def flip_null_counts(Cb, bd, nday, R, rng, est=newton_counts):
    out = np.empty(R)
    CbT = Cb.transpose(0, 2, 1)
    for r in range(R):
        f = rng.random(len(Cb)) < 0.5
        Cs = np.where(f[:, None, None], CbT, Cb)
        D = np.zeros((nday,) + Cb.shape[1:])
        np.add.at(D, bd, Cs)
        out[r] = est(D)
    return out


def blocks_of(seg, block_len):
    """Contiguous blocks of block_len transitions inside each segment (transition-indexed)."""
    n = len(seg)
    if n == 0:
        return np.zeros(0, np.int64)
    seg_start = np.flatnonzero(np.r_[True, seg[1:] != seg[:-1]])
    pos = np.arange(n) - np.repeat(seg_start, np.diff(np.append(seg_start, n)))
    key = seg.astype(np.int64) * 1_000_000 + pos // block_len
    _, bl = np.unique(key, return_inverse=True)
    return bl


# ============================================================================ soft observables (v3 vectors)
def soft_G(Pa, Pb):
    """Antisymmetric soft transition observables g_ab = p_t^a p_{t+1}^b - p_t^b p_{t+1}^a, a < b. (T, q(q-1)/2)."""
    q = Pa.shape[1]
    iu, ju = np.triu_indices(q, 1)
    return Pa[:, iu] * Pb[:, ju] - Pa[:, ju] * Pb[:, iu]


def newton_G(G, day, k=None):
    if G.shape[0] < 10 or len(np.unique(day)) < 2:
        return np.nan
    keep = np.any(G != 0, axis=0)
    if not keep.any():
        return np.nan
    k = min(5, len(np.unique(day))) if k is None else k
    return float(ep_gauss_crossfit(G[:, keep], day, k=k)["sigma"])


def flip_null_G(G, day, block, R, rng):
    out = np.empty(R)
    nb = int(block.max()) + 1
    for r in range(R):
        f = np.where(rng.random(nb) < 0.5, -1.0, 1.0)
        out[r] = newton_G(G * f[block][:, None], day)
    return out


def pval(null, obs):
    null = np.asarray(null)
    null = null[np.isfinite(null)]
    if not np.isfinite(obs) or len(null) == 0:
        return np.nan
    return float((1 + (null >= obs).sum()) / (len(null) + 1))


def eta2(v, lab):
    v = np.asarray(v, float)
    lab = np.asarray(lab)
    m = v.mean()
    sst = ((v - m) ** 2).sum()
    if sst == 0:
        return 0.0
    return float(sum(((lab == g).sum()) * (v[lab == g].mean() - m) ** 2 for g in np.unique(lab)) / sst)


def stratified_eta2(groups, rng, n_perm=10000):
    """Sum over periods of eta2(lab) with labels permuted within periods. groups: list of (values, labels)."""
    groups = [(np.asarray(v, float), np.asarray(lb)) for v, lb in groups if len(v) >= 4 and len(np.unique(lb)) >= 2]
    if not groups:
        return np.nan, np.nan
    obs = sum(eta2(v, lb) for v, lb in groups)
    null = np.array([sum(eta2(v, rng.permutation(lb)) for v, lb in groups) for _ in range(n_perm)])
    return float(obs), float((1 + (null >= obs - 1e-12).sum()) / (n_perm + 1))
