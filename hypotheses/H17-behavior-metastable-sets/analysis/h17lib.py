"""H17 Markov-state-model toolkit (numpy/scipy only).

Sequences are stored concatenated: x (int states 0..q-1) with seg (int segment id = agent-day), so that
lagged pairs never cross a day boundary. Soft states are an (n, q) float array with the same seg.

Contents
- load_states / sequences_from_table: any categorical (hard) or probability-vector (soft) table, incl. Jev output
- counts per segment at lag tau; bootstrap by segment (agent-day)
- T estimators (non-reversible MLE; additive reversibilization), stationary distribution, implied timescales
- PCCA+ (Roeblitz & Weber inner simplex + crispness optimization), coarse-grained matrix, crispness
- Chapman-Kolmogorov test on crisp sets; full-state CK error
- committors (forward/backward, non-reversible), TPT reactive flux and rate, mean first-passage times
- plug-in MSM entropy production; sticky-only rival R1; mixing time
- nulls: shuffle within segment (N1), sojourn-preserving run permutation (N2), semi-Markov reference (N3)
- day-blocked held-out log-likelihood (M0, R1, M1; order 2), per-agent / shrinkage MSMs, I^2
- soft-state estimators: soft counts and the shifted estimator C(tau0)^-1 C(tau0+tau)
"""
from __future__ import annotations

import json
import math
from pathlib import Path

import numpy as np
from scipy.optimize import fmin
from scipy.sparse.csgraph import connected_components

ROOT = Path(__file__).resolve().parents[3]


# ============================================================================ loading
def load_states(path_or_df, agent_col="agent", day_col="pt_date", order_col=None, state_col=None,
                prob_cols=None, prob_json_col=None, state_names=None, grid=True):
    """Normalize any state table to (agent, pt_date, order, state[, p_0..p_{q-1}]) sorted, plus state names.

    Hard labels: state_col (codes or strings). Soft labels: prob_cols (list of columns) or prob_json_col (a JSON dict
    {state: prob} per row, the Jev `behavior_probs` format). order_col: an integer bin index (grid tables, e.g. the
    5-min window index `w` or `minute`) or a timestamp (event tables). On grids, steps are consecutive bins; a missing
    bin breaks the segment (a new segment starts after a gap)."""
    import polars as pl
    df = pl.read_parquet(path_or_df) if isinstance(path_or_df, (str, Path)) else path_or_df
    if prob_json_col is not None:
        dicts = [json.loads(s) if isinstance(s, str) else (s or {}) for s in df[prob_json_col].to_list()]
        names = state_names or sorted({k for d in dicts for k in d})
        P = np.array([[float(d.get(k, 0.0)) for k in names] for d in dicts], dtype=np.float64)
        P = P / np.clip(P.sum(1, keepdims=True), 1e-12, None)
        df = df.with_columns([pl.Series(f"p_{i}", P[:, i]) for i in range(len(names))])
        prob_cols = [f"p_{i}" for i in range(len(names))]
        if state_col is None:
            df = df.with_columns(pl.Series("_hard", np.array(names, dtype=object)[P.argmax(1)].tolist()))
            state_col = "_hard"
    if state_col is None and prob_cols is not None:
        P = df.select(prob_cols).to_numpy()
        df = df.with_columns(pl.Series("_hard", P.argmax(1).astype(np.int64)))
        state_col = "_hard"
    if df[state_col].dtype in (pl.Utf8, pl.Categorical, pl.String):
        names = state_names or sorted(df[state_col].cast(pl.Utf8).unique().to_list())
        code = {s: i for i, s in enumerate(names)}
        df = df.with_columns(pl.col(state_col).cast(pl.Utf8).replace_strict(code, return_dtype=pl.Int16).alias("state"))
    else:
        names = state_names or [str(i) for i in range(int(df[state_col].max()) + 1)]
        df = df.with_columns(pl.col(state_col).cast(pl.Int16).alias("state"))
    df = df.filter(pl.col("state").is_not_null() & (pl.col("state") >= 0))
    keep = [pl.col(agent_col).cast(pl.Int16).alias("agent"), pl.col(day_col).cast(pl.Utf8).alias("pt_date")]
    if order_col is None:
        raise ValueError("order_col is required (bin index or timestamp)")
    if df[order_col].dtype.is_temporal():
        df = df.sort(agent_col, order_col).with_columns(
            pl.col(order_col).rank("ordinal").over([agent_col, day_col]).cast(pl.Int64).alias("order"))
        grid = False
    else:
        df = df.with_columns(pl.col(order_col).cast(pl.Int64).alias("order"))
    cols = keep + [pl.col("order"), pl.col("state")] + ([pl.col(c) for c in prob_cols] if prob_cols else [])
    out = df.select(cols).sort("agent", "pt_date", "order")
    return out, names, (prob_cols is not None), grid


def sequences_from_table(df, grid=True, soft=False, q=None):
    """Concatenated arrays from a normalized table: x, seg, seg_agent, seg_day (and P if soft).

    A segment is one agent-day; on grids a gap in the bin index starts a new segment."""
    agent = df["agent"].to_numpy().astype(np.int64)
    day = df["pt_date"].to_numpy()
    order = df["order"].to_numpy().astype(np.int64)
    x = df["state"].to_numpy().astype(np.int64)
    n = len(x)
    newseg = np.ones(n, dtype=bool)
    if n > 1:
        same = (agent[1:] == agent[:-1]) & (day[1:] == day[:-1])
        if grid:
            same &= (order[1:] - order[:-1]) == 1
        newseg[1:] = ~same
    seg = np.cumsum(newseg) - 1
    starts = np.flatnonzero(newseg)
    out = {"x": x, "seg": seg, "seg_agent": agent[starts], "seg_day": day[starts], "q": q or int(x.max()) + 1}
    if soft:
        pc = [c for c in df.columns if c.startswith("p_")]
        out["P"] = df.select(pc).to_numpy().astype(np.float64)
    return out


def subset(S, segmask):
    """Restrict a sequence dict to the segments where segmask is True (renumbering segments)."""
    keep = segmask[S["seg"]]
    newid = np.cumsum(segmask) - 1
    out = {"x": S["x"][keep], "seg": newid[S["seg"][keep]], "seg_agent": S["seg_agent"][segmask],
           "seg_day": S["seg_day"][segmask], "q": S["q"]}
    if "P" in S:
        out["P"] = S["P"][keep]
    return out


# ============================================================================ counts
def seg_counts(x, seg, q, tau, nseg=None):
    """Per-segment count matrices at lag tau: array (nseg, q, q)."""
    nseg = int(seg.max()) + 1 if nseg is None else nseg
    if len(x) <= tau:
        return np.zeros((nseg, q, q))
    ok = seg[:-tau] == seg[tau:]
    idx = seg[:-tau][ok] * q * q + x[:-tau][ok] * q + x[tau:][ok]
    return np.bincount(idx, minlength=nseg * q * q).reshape(nseg, q, q).astype(np.float64)


def block_counts(x, seg, q, tau, block_len):
    """Lagged pairs assigned to contiguous within-segment blocks of block_len steps (by the pair's start).

    Returns (nblocks, q, q) and the segment of each block (for agent lookups)."""
    n = len(x)
    seg_start = np.flatnonzero(np.r_[True, seg[1:] != seg[:-1]])
    pos = np.arange(n) - np.repeat(seg_start, np.diff(np.append(seg_start, n)))
    bid_local = pos // block_len
    key = seg * 100000 + bid_local
    _, block = np.unique(key, return_inverse=True)
    nb = int(block.max()) + 1
    block_seg = np.zeros(nb, dtype=np.int64)
    block_seg[block] = seg
    ok = seg[:-tau] == seg[tau:]
    idx = block[:-tau][ok] * q * q + x[:-tau][ok] * q + x[tau:][ok]
    return np.bincount(idx, minlength=nb * q * q).reshape(nb, q, q).astype(np.float64), block_seg


def counts(x, seg, q, tau):
    if len(x) <= tau:
        return np.zeros((q, q))
    ok = seg[:-tau] == seg[tau:]
    idx = x[:-tau][ok] * q + x[tau:][ok]
    return np.bincount(idx, minlength=q * q).reshape(q, q).astype(np.float64)


def soft_counts(P, seg, tau):
    ok = seg[:-tau] == seg[tau:]
    return P[:-tau][ok].T @ P[tau:][ok]


def boot_weights(nseg, R, rng):
    """Multinomial bootstrap weights over segments (R, nseg)."""
    return rng.multinomial(nseg, np.full(nseg, 1.0 / nseg), size=R).astype(np.float64)


# ============================================================================ estimators
def active_set(C):
    """Largest strongly connected set of the count graph (indices)."""
    q = C.shape[0]
    A = (C + 0) > 0
    n, lab = connected_components(A, directed=True, connection="strong")
    if n == 1:
        return np.arange(q)
    sizes = np.array([C[lab == k].sum() for k in range(n)])
    return np.flatnonzero(lab == sizes.argmax())


def T_mle(C):
    """Non-reversible MLE (row-normalized), restricted to the largest strongly connected set."""
    a = active_set(C)
    Ca = C[np.ix_(a, a)]
    rs = Ca.sum(1, keepdims=True)
    return Ca / np.where(rs > 0, rs, 1.0), a


def stationary(T):
    w, v = np.linalg.eig(T.T)
    k = np.argmin(np.abs(w - 1.0))
    pi = np.real(v[:, k])
    pi = np.abs(pi) / np.abs(pi).sum()
    return pi


def reversibilize(T, pi):
    """Additive reversibilization (T + Pi^-1 T^T Pi)/2: same pi, real spectrum."""
    return 0.5 * (T + (T.T * pi[None, :]) / pi[:, None])


def eig_sorted(T):
    w = np.linalg.eigvals(T)
    return w[np.argsort(-np.abs(w))]


def its_from_T(T, tau, k=4):
    """Implied timescales t_2..t_k (in units of the lag grid) from |eigenvalues|."""
    w = np.abs(eig_sorted(T))[1:k]
    with np.errstate(divide="ignore", invalid="ignore"):
        t = -tau / np.log(np.clip(w, 1e-300, 1 - 1e-15))
    out = np.full(k - 1, np.nan)
    out[: len(t)] = t
    return out


def its_from_C(C, tau, k=4, rev=False):
    T, a = T_mle(C)
    if len(a) < 2:
        return np.full(k - 1, np.nan)
    if rev:
        T = reversibilize(T, stationary(T))
    return its_from_T(T, tau, k)


def mixing_time(T, eps=0.25, kmax=400):
    pi = stationary(T)
    M = np.eye(len(T))
    for k in range(1, kmax + 1):
        M = M @ T
        if 0.5 * np.abs(M - pi[None, :]).sum(1).max() <= eps:
            return k
    return np.nan


def sticky_fit(C):
    """Sticky-only rival R1: T_ii = s_i, jumps go to nu (jump-in frequencies). Returns T (full q)."""
    q = len(C)
    rs = C.sum(1)
    s = np.where(rs > 0, np.diag(C) / np.where(rs > 0, rs, 1), 0.0)
    off = C - np.diag(np.diag(C))
    nu = off.sum(0)
    nu = nu / max(nu.sum(), 1e-12)
    T = np.zeros((q, q))
    for i in range(q):
        d = 1 - nu[i]
        T[i] = (1 - s[i]) * nu / (d if d > 1e-12 else 1)
        T[i, i] = s[i]
    T = T / np.clip(T.sum(1, keepdims=True), 1e-12, None)
    return T


def ep_plugin(C):
    """Plug-in entropy production per step (nats) from a count matrix (pairs with both counts > 0)."""
    n = C.sum()
    if n <= 0:
        return np.nan
    F = C / n
    m = (C > 0) & (C.T > 0)
    iu = np.triu(m, 1)
    a, b = F[iu], F.T[iu]
    return float(np.sum((a - b) * np.log(a / b)))


def lump_counts(C, labels, m):
    L = np.zeros((len(labels), m))
    L[np.arange(len(labels)), labels] = 1
    return L.T @ C @ L


# ============================================================================ PCCA+
def _fill_A(Ared, X):
    m = X.shape[1]
    A = np.zeros((m, m))
    A[1:, 1:] = Ared
    A[1:, 0] = -A[1:, 1:].sum(1)
    A[0, :] = -np.min(X[:, 1:] @ A[1:, :], axis=0)
    A /= A[0, :].sum()
    return A


def pcca(T, pi, m):
    """PCCA+ memberships chi (q, m) for a reversible T with stationary pi."""
    q = len(T)
    sq = np.sqrt(pi)
    S = (sq[:, None] * T) / sq[None, :]
    S = 0.5 * (S + S.T)
    w, U = np.linalg.eigh(S)
    o = np.argsort(-w)
    w, U = w[o], U[:, o]
    X = U[:, :m] / sq[:, None]
    for i in range(m):
        X[:, i] /= math.sqrt(np.dot(X[:, i] ** 2, pi))
    X[:, 0] = np.abs(X[:, 0])
    # inner simplex algorithm
    c = X.copy()
    ortho = c.copy()
    ind = np.zeros(m, dtype=int)
    ind[0] = int(np.argmax(np.linalg.norm(c, axis=1)))
    ortho = ortho - c[ind[0]][None, :]
    for k in range(1, m):
        temp = ortho[ind[k - 1]].copy()
        nrm = np.linalg.norm(temp)
        if nrm > 0:
            temp = temp / nrm
        ortho = ortho - np.outer(ortho @ temp, temp)
        d = np.linalg.norm(ortho, axis=1)
        d[ind[:k]] = -1
        ind[k] = int(np.argmax(d))
    try:
        A0 = np.linalg.inv(c[ind])
    except np.linalg.LinAlgError:
        A0 = np.linalg.pinv(c[ind])

    def obj(v):
        A = _fill_A(v.reshape(m - 1, m - 1), X)
        return -np.sum(A ** 2 / A[0][None, :])

    if m > 1:
        v = fmin(obj, A0[1:, 1:].ravel(), disp=False, xtol=1e-6, ftol=1e-8, maxiter=4000)
        A = _fill_A(v.reshape(m - 1, m - 1), X)
    else:
        A = A0
    chi = X @ A
    chi = np.clip(chi, 0, None)
    chi = chi / np.clip(chi.sum(1, keepdims=True), 1e-12, None)
    return chi, w


def coarse_grain(T, pi, chi):
    W = chi.T * pi[None, :]
    M = W @ chi
    return np.linalg.solve(M, W @ T @ chi)


def eigengap_m(T_rev, mset=(2, 3, 4)):
    w = np.sort(np.real(np.linalg.eigvals(T_rev)))[::-1]
    best, gap = None, -np.inf
    for m in mset:
        if m < len(w):
            g = w[m - 1] - w[m]
            if g > gap:
                best, gap = m, g
    return best, w


def msm_sets(C, m=None):
    """Point MSM at one lag: T, active set, pi, reversibilized T, m, chi, crisp labels, crispness, metastability."""
    T, a = T_mle(C)
    pi = stationary(T)
    Tr = reversibilize(T, pi)
    m_auto, w = eigengap_m(Tr)
    m = m or m_auto
    if m is None or m >= len(a):
        return {"T": T, "active": a, "pi": pi, "Tr": Tr, "m": None}
    chi, _ = pcca(Tr, pi, m)
    lab = chi.argmax(1)
    crisp = float(np.sum(pi * chi.max(1)))
    Tcg = coarse_grain(T, pi, chi)
    return {"T": T, "active": a, "pi": pi, "Tr": Tr, "m": m, "m_auto": m_auto, "eig_rev": w, "chi": chi,
            "labels": lab, "crispness": crisp, "metastability": float(np.trace(Tcg) / m), "Tcg": Tcg}


# ============================================================================ CK test
def ck_sets(Cs_by_k, T, active, labels, m, kmax=5):
    """Crisp-set CK test. Cs_by_k[k] = count matrix at lag k*tau (full q). Returns (est, pred) arrays (kmax, m)."""
    est = np.full((kmax, m), np.nan)
    pred = np.full((kmax, m), np.nan)
    Tk = np.eye(len(T))
    for k in range(1, kmax + 1):
        Tk = Tk @ T
        C = Cs_by_k[k][np.ix_(active, active)]
        for A in range(m):
            inA = labels == A
            rows = C[inA]
            if rows.sum() <= 0:
                continue
            est[k - 1, A] = rows[:, inA].sum() / rows.sum()
            w0 = rows.sum(1) / rows.sum()
            pred[k - 1, A] = float(w0 @ Tk[inA][:, inA].sum(1))
    return est, pred


def ck_full_error(Cs_by_k, T, active, pi, kmax=5):
    errs = []
    Tk = np.eye(len(T))
    for k in range(1, kmax + 1):
        Tk = Tk @ T
        C = Cs_by_k[k][np.ix_(active, active)]
        rs = C.sum(1, keepdims=True)
        Te = C / np.where(rs > 0, rs, 1)
        errs.append(float(np.sum(pi[:, None] * np.abs(Tk - Te)) / len(T)))
    return np.array(errs)


# ============================================================================ committors / TPT
def committor(T, A, B, forward=True, pi=None):
    q = len(T)
    if not forward:
        pi = stationary(T) if pi is None else pi
        T = (T.T * pi[None, :]) / pi[:, None]  # time reversal
    A, B = np.atleast_1d(A), np.atleast_1d(B)
    I = np.setdiff1d(np.arange(q), np.concatenate([A, B]))
    h = np.zeros(q)
    if forward:
        h[B] = 1.0
    else:
        h[A] = 1.0
    if len(I):
        M = np.eye(len(I)) - T[np.ix_(I, I)]
        rhs = T[np.ix_(I, B)].sum(1) if forward else T[np.ix_(I, A)].sum(1)
        try:
            h[I] = np.linalg.solve(M, rhs)
        except np.linalg.LinAlgError:
            h[I] = np.linalg.lstsq(M, rhs, rcond=None)[0]
    return h


def tpt(T, pi, A, B, tau=1.0):
    qp = committor(T, A, B, True)
    qm = committor(T, A, B, False, pi)
    f = pi[:, None] * qm[:, None] * T * qp[None, :]
    np.fill_diagonal(f, 0)
    A = np.atleast_1d(A)
    notA = np.setdiff1d(np.arange(len(T)), A)
    F = f[np.ix_(A, notA)].sum()
    k_AB = F / max(np.sum(pi * qm), 1e-12)
    return {"q_plus": qp, "q_minus": qm, "flux_per_step": float(F), "rate_AB_per_unit": float(k_AB / tau),
            "delta": qp - (1 - qm)}


def mfpt(T, target, tau=1.0):
    """Mean first-passage time from every state to the target set (units of tau)."""
    q = len(T)
    target = np.atleast_1d(target)
    I = np.setdiff1d(np.arange(q), target)
    m = np.zeros(q)
    if len(I):
        M = np.eye(len(I)) - T[np.ix_(I, I)]
        m[I] = np.linalg.solve(M, np.ones(len(I))) * tau
    return m


# ============================================================================ nulls
def null_shuffle(x, seg, rng):
    """N1: permute states within each segment."""
    key = seg + rng.random(len(x))
    o = np.argsort(key, kind="stable")
    return x[o]


def runs_of(x, seg):
    """Run decomposition: (run_state, run_len, run_seg)."""
    n = len(x)
    if n == 0:
        return np.array([], int), np.array([], int), np.array([], int)
    br = np.ones(n, dtype=bool)
    br[1:] = (x[1:] != x[:-1]) | (seg[1:] != seg[:-1])
    st = np.flatnonzero(br)
    ln = np.diff(np.append(st, n))
    return x[st], ln, seg[st]


def null_sojourn(x, seg, rng, max_pass=20):
    """N2: permute the interior runs of each segment (the first and last run stay in place, because they are
    censored by the day boundaries); adjacent identical states are broken up by random swaps.

    Returns (surrogate x, fraction of runs left merged)."""
    rs, rl, rg = runs_of(x, seg)
    out = np.empty_like(x)
    pos = 0
    merged = 0
    bounds = np.flatnonzero(np.r_[True, rg[1:] != rg[:-1], True])
    for b0, b1 in zip(bounds[:-1], bounds[1:]):
        s, l = rs[b0:b1].copy(), rl[b0:b1].copy()
        k = len(s)
        if k > 3:
            inner = np.arange(1, k - 1)
            p = rng.permutation(inner)
            s[inner], l[inner] = s[p], l[p]
            for _ in range(max_pass):
                bad = np.flatnonzero(s[1:] == s[:-1]) + 1
                if len(bad) == 0:
                    break
                for i in bad:
                    if s[i] != s[i - 1]:
                        continue
                    ii = i if i < k - 1 else i - 1  # move an interior run
                    if ii < 1:
                        continue
                    for _try in range(10):
                        j = int(rng.integers(1, k - 1))
                        if j == ii or s[j] == s[ii]:
                            continue
                        nb = sorted({q_ for q_ in (ii - 1, ii, j - 1, j) if 0 <= q_ < k - 1})
                        before = sum(s[q_] == s[q_ + 1] for q_ in nb)
                        s[ii], s[j] = s[j], s[ii]
                        after = sum(s[q_] == s[q_ + 1] for q_ in nb)
                        if after < before:
                            l[ii], l[j] = l[j], l[ii]
                            break
                        s[ii], s[j] = s[j], s[ii]
            merged += int(np.sum(s[1:] == s[:-1]))
        n = int(l.sum())
        out[pos:pos + n] = np.repeat(s, l)
        pos += n
    return out, merged / max(len(rs), 1)


def null_semimarkov(x, seg, q, rng):
    """N3: empirical embedded jump chain + resampled per-state interior dwell lengths. The first and last run of each
    segment (censored by the day boundaries) stay in place, as in N2; the interior is simulated."""
    rs, rl, rg = runs_of(x, seg)
    J = np.zeros((q, q))
    same = rg[1:] == rg[:-1]
    np.add.at(J, (rs[:-1][same], rs[1:][same]), 1)
    rsum = J.sum(1, keepdims=True)
    J = np.where(rsum > 0, J / np.where(rsum > 0, rsum, 1), 1.0 / max(q - 1, 1) * (1 - np.eye(q)))
    first = np.r_[True, rg[1:] != rg[:-1]]
    last = np.r_[rg[1:] != rg[:-1], True]
    interior = ~first & ~last
    pools = [rl[(rs == s) & interior] if np.any((rs == s) & interior) else rl[rs == s] for s in range(q)]
    cdf = np.cumsum(J, 1)
    out = x.copy()
    fi, la = np.flatnonzero(first), np.flatnonzero(last)
    starts = np.r_[0, np.cumsum(rl)][:-1]
    for f_, l_ in zip(fi, la):
        if l_ - f_ < 2:
            continue
        p0 = starts[f_] + rl[f_]
        p1 = starts[l_]
        s = rs[f_]
        pos = p0
        while pos < p1:
            s = min(int(np.searchsorted(cdf[s], rng.random() * cdf[s, -1])), q - 1)
            pool = pools[s]
            d = int(pool[rng.integers(len(pool))]) if len(pool) else 1
            d = min(d, p1 - pos)
            out[pos:pos + d] = s
            pos += d
    return out


def trim_boundary_state(x, seg, state):
    """Post hoc: drop the leading and trailing runs of `state` in every segment (e.g. idle before the first and after
    the last action of an agent-day). Returns (x, seg) and the fraction of `state` steps removed."""
    rs, rl, rg = runs_of(x, seg)
    first = np.r_[True, rg[1:] != rg[:-1]]
    last = np.r_[rg[1:] != rg[:-1], True]
    drop_run = (first | last) & (rs == state)
    keep = ~np.repeat(drop_run, rl)
    tot = np.sum(x == state)
    return x[keep], seg[keep], float(np.sum(drop_run * rl) / tot) if tot else 0.0


# ============================================================================ held-out likelihood
def day_folds(days, k=None):
    ud = np.array(sorted(set(days.tolist())))
    k = min(5, len(ud)) if k is None else min(k, len(ud))
    fold_of_day = {d: i % k for i, d in enumerate(ud)}
    return np.array([fold_of_day[d] for d in days]), k


def loglik_pairs(Ctest, P):
    P = np.clip(P, 1e-12, None)
    return float(np.sum(Ctest * np.log(P))), float(Ctest.sum())


def heldout_models(Cseg, segfold, k, alpha=0.5):
    """Day-blocked held-out log-lik per lagged pair: M0 occupancy, R1 sticky, M1 MSM. Returns per-fold arrays."""
    out = {"M0": [], "R1": [], "M1": [], "n": []}
    for f in range(k):
        tr = Cseg[segfold != f].sum(0)
        te = Cseg[segfold == f].sum(0)
        if te.sum() == 0 or tr.sum() == 0:
            continue
        q = len(tr)
        occ = tr.sum(0) + alpha
        P0 = np.tile(occ / occ.sum(), (q, 1))
        P1 = (tr + alpha) / (tr + alpha).sum(1, keepdims=True)
        PR = sticky_fit(tr + alpha)
        for name, P in (("M0", P0), ("R1", PR), ("M1", P1)):
            out[name].append(loglik_pairs(te, P)[0])
        out["n"].append(te.sum())
    return {kk: np.array(v) for kk, v in out.items()}


def order2_heldout(x, seg, segfold, k, q, alpha=0.5):
    """Held-out log-lik per transition, order 1 vs order 2 (tau = 1), day-blocked."""
    ok = (seg[:-2] == seg[2:])
    a, b, c = x[:-2][ok], x[1:-1][ok], x[2:][ok]
    f = segfold[seg[:-2][ok]]
    res = {"o1": [], "o2": [], "n": []}
    for ff in range(k):
        tr, te = f != ff, f == ff
        if te.sum() == 0 or tr.sum() == 0:
            continue
        C2 = np.bincount((a[tr] * q + b[tr]) * q + c[tr], minlength=q ** 3).reshape(q * q, q) + alpha
        C1 = np.bincount(b[tr] * q + c[tr], minlength=q * q).reshape(q, q) + alpha
        P2 = C2 / C2.sum(1, keepdims=True)
        P1 = C1 / C1.sum(1, keepdims=True)
        res["o2"].append(np.log(P2[a[te] * q + b[te], c[te]]).sum())
        res["o1"].append(np.log(P1[b[te], c[te]]).sum())
        res["n"].append(te.sum())
    return {kk: np.array(v) for kk, v in res.items()}


def agent_heldout(Cseg, seg_agent, segfold, k, alpha=0.5, shrink=10.0):
    """Per-agent day-blocked held-out log-lik (lagged pairs) of pooled, own and shrinkage MSMs.

    Returns dict with per-agent totals and the fraction of agents where own-or-shrinkage beats pooled."""
    agents = np.unique(seg_agent)
    q = Cseg.shape[1]
    tot = {a: {"pooled": 0.0, "own": 0.0, "shrink": 0.0, "n": 0.0} for a in agents}
    for f in range(k):
        trm = segfold != f
        Cp = Cseg[trm].sum(0) + alpha
        Pp = Cp / Cp.sum(1, keepdims=True)
        for a in agents:
            te = Cseg[(segfold == f) & (seg_agent == a)].sum(0)
            if te.sum() == 0:
                continue
            Ca = Cseg[trm & (seg_agent == a)].sum(0)
            Po = (Ca + alpha) / (Ca + alpha).sum(1, keepdims=True)
            Cs = Ca + shrink * Pp
            Ps = Cs / Cs.sum(1, keepdims=True)
            tot[a]["pooled"] += loglik_pairs(te, Pp)[0]
            tot[a]["own"] += loglik_pairs(te, Po)[0]
            tot[a]["shrink"] += loglik_pairs(te, Ps)[0]
            tot[a]["n"] += te.sum()
    ok = [a for a in agents if tot[a]["n"] > 0]
    beats = [max(tot[a]["own"], tot[a]["shrink"]) > tot[a]["pooled"] for a in ok]
    shr = [tot[a]["shrink"] > tot[a]["pooled"] for a in ok]
    return {"per_agent": {int(a): tot[a] for a in ok}, "frac_beats": float(np.mean(beats)) if ok else np.nan,
            "frac_shrink": float(np.mean(shr)) if ok else np.nan}


def i_squared(y, se):
    y, se = np.asarray(y, float), np.asarray(se, float)
    ok = np.isfinite(y) & np.isfinite(se) & (se > 0)
    y, se = y[ok], se[ok]
    if len(y) < 2:
        return np.nan, np.nan
    w = 1 / se ** 2
    ybar = np.sum(w * y) / w.sum()
    Q = float(np.sum(w * (y - ybar) ** 2))
    df = len(y) - 1
    return (max(0.0, (Q - df) / Q) if Q > 0 else 0.0), Q


# ============================================================================ soft states
def soft_its(P, seg, tau, k=4):
    C = soft_counts(P, seg, tau)
    T = C / np.clip(C.sum(1, keepdims=True), 1e-12, None)
    return its_from_T(T, tau, k)


def shifted_its(P, seg, tau, tau0=1, k=4, ridge=1e-8):
    """Eigenvalues of C(tau0)^-1 C(tau0+tau) -> lambda^tau, robust to window-independent classifier noise."""
    C0 = soft_counts(P, seg, tau0)
    C1 = soft_counts(P, seg, tau0 + tau)
    q = len(C0)
    K = np.linalg.solve(C0 + ridge * np.trace(C0) / q * np.eye(q), C1)
    return its_from_T(K, tau, k)


# ============================================================================ helpers
def plateau_lag(taus, t2, tol=0.15, max_tau=15):
    for i in range(len(taus) - 1):
        if taus[i] > max_tau:
            break
        if np.isfinite(t2[i]) and np.isfinite(t2[i + 1]) and t2[i] > 0 and abs(t2[i + 1] - t2[i]) / t2[i] < tol:
            return taus[i]
    return None


def jsonable(o):
    if isinstance(o, dict):
        return {str(k): jsonable(v) for k, v in o.items()}
    if isinstance(o, (list, tuple)):
        return [jsonable(v) for v in o]
    if isinstance(o, np.ndarray):
        return jsonable(o.tolist())
    if isinstance(o, (np.floating, float)):
        return None if not np.isfinite(o) else float(o)
    if isinstance(o, (np.integer,)):
        return int(o)
    if isinstance(o, complex):
        return [o.real, o.imag]
    return o
