"""H02 shared library: kinetic / equilibrium Ising fits, surrogates, simulator, metrics.

Conventions (card, "Model"):
  spins s in {-1,+1}; logistic coefficients b are on 2*J (P(+1) = sigma(2H)); we report J = b/2.
  J[i, j] = influence of j (at t) on i (at t+1) for kinetic fits; net outgoing influence I_k = sum_j (J[j,k] - J[k,j]).
  L2 penalty (lambda, in logistic-coefficient units) on couplings and on block-field deviations; intercept unpenalized.
Thread use: callers set VECLIB/OMP thread caps before importing numpy.
"""
from __future__ import annotations

import numpy as np

BIG = 1e10  # penalty used to exclude a coefficient
LAM_J, LAM_D = 1.0, 1.0
BLOCK_MIN, MIN_LAST_BLOCK = 30, 10


# --------------------------------------------------------------------------- solver
def fit_logistic(X, Y01, pen, offset=None, B0=None, max_iter=60, tol=1e-7):
    """Batched L2-penalized logistic regression with a shared design.

    X: (T, p) design shared by all N outputs; Y01: (T, N) targets in {0,1}; pen: (N, p) or (p,) ridge weights.
    Minimizes, per output n: -sum_t loglik + 0.5 * sum_k pen[n,k] * b[n,k]^2.  Returns B (N, p) in logit units.
    """
    T, p = X.shape
    N = Y01.shape[1]
    pen = np.broadcast_to(pen, (N, p)).astype(float)
    B = np.zeros((N, p)) if B0 is None else B0.copy()
    off = np.zeros((T, N)) if offset is None else offset

    def objective(Bm):
        eta = X @ Bm.T + off
        ll = Y01 * eta - np.logaddexp(0.0, eta)
        return -ll.sum(0) + 0.5 * (pen * Bm ** 2).sum(1)

    obj = objective(B)
    active = np.ones(N, bool)
    for _ in range(max_iter):
        idx = np.flatnonzero(active)
        if idx.size == 0:
            break
        eta = X @ B[idx].T + off[:, idx]
        mu = 1.0 / (1.0 + np.exp(-eta))
        W = mu * (1 - mu)
        G = X.T @ (Y01[:, idx] - mu) - (pen[idx] * B[idx]).T  # (p, n)
        H = np.empty((idx.size, p, p))
        for a in range(idx.size):
            H[a] = (X * W[:, a:a + 1]).T @ X
        H[:, np.arange(p), np.arange(p)] += pen[idx]
        step = np.linalg.solve(H, G.T[..., None])[..., 0]  # (n, p)
        # backtracking per output
        t = np.ones(idx.size)
        Bn = B.copy()
        for _bt in range(20):
            Bn[idx] = B[idx] + t[:, None] * step
            on = objective(Bn)[idx]
            bad = on > obj[idx] + 1e-10
            if not bad.any():
                break
            t[bad] *= 0.5
        B[idx] = Bn[idx]
        obj_new = objective(B)
        conv = np.abs(t[:, None] * step).max(1) < tol
        obj[idx] = obj_new[idx]
        active[idx[conv]] = False
    return B


# --------------------------------------------------------------------------- data layout
def block_ids(day, minute):
    """(day, 30-min block) id per bin; a trailing block shorter than MIN_LAST_BLOCK merges into the previous one."""
    day = np.asarray(day); minute = np.asarray(minute)
    blk = minute // BLOCK_MIN
    out = np.empty_like(blk)
    for d in np.unique(day):
        m = day == d
        b = blk[m].copy()
        last = b.max()
        if last > 0 and (b == last).sum() < MIN_LAST_BLOCK:
            b[b == last] = last - 1
        out[m] = b
    keys = day.astype(np.int64) * 1000 + out
    _, inv = np.unique(keys, return_inverse=True)
    return inv


def one_hot(ids, n=None):
    n = ids.max() + 1 if n is None else n
    M = np.zeros((ids.size, n))
    M[np.arange(ids.size), ids] = 1.0
    return M


def boxcar(S, day, K=5):
    """Trailing K-bin mean of S within each day; first K-1 bins of a day are NaN."""
    T, N = S.shape
    out = np.full((T, N), np.nan)
    for d in np.unique(day):
        idx = np.flatnonzero(day == d)
        x = S[idx].astype(float)
        c = np.cumsum(np.vstack([np.zeros((1, N)), x]), 0)
        m = (c[K:] - c[:-K]) / K
        out[idx[K - 1:]] = m
    return out


def kinetic_design(S, day, minute, fields="block", lag="1", K=5):
    """Build (X, Y01, info) for the kinetic fit. S: (T, N) in {-1,+1}, sorted by (day, minute), contiguous per day."""
    T, N = S.shape
    nxt = np.flatnonzero((day[1:] == day[:-1]) & (minute[1:] == minute[:-1] + 1))  # t such that (t, t+1) valid
    src, dst = nxt, nxt + 1
    if lag == "1":
        C = S[src].astype(float)
        cols = [C]
        ncoup = N
    elif lag == "box":
        bx = boxcar(S, day, K)
        ok = ~np.isnan(bx[src]).any(1)
        src, dst = src[ok], dst[ok]
        cols = [S[src].astype(float), bx[src]]  # lag-1 self terms (cross excluded by penalty) + boxcars
        ncoup = 2 * N
    else:
        raise ValueError(lag)
    parts = [np.ones((src.size, 1))] + cols
    nb = 0
    if fields == "block":
        bid = block_ids(day, minute)[dst]
        _, bid = np.unique(bid, return_inverse=True)
        Bk = one_hot(bid)
        nb = Bk.shape[1]
        parts.append(Bk)
    X = np.hstack(parts)
    Y01 = (S[dst] > 0).astype(float)
    pen = np.zeros((N, X.shape[1]))
    pen[:, 1:1 + ncoup] = LAM_J
    pen[:, 1 + ncoup:] = LAM_D
    pen[:, 0] = 1e-8
    if lag == "box":
        lag1 = np.full((N, N), BIG); np.fill_diagonal(lag1, LAM_J)
        pen[:, 1:1 + N] = lag1
    return X, Y01, pen, {"N": N, "lag": lag, "nb": nb, "dst": dst, "src": src}


def equal_design(S, day, minute, fields="block"):
    T, N = S.shape
    parts = [np.ones((T, 1)), S.astype(float)]
    nb = 0
    if fields == "block":
        Bk = one_hot(block_ids(day, minute)); nb = Bk.shape[1]; parts.append(Bk)
    X = np.hstack(parts)
    Y01 = (S > 0).astype(float)
    pen = np.zeros((N, X.shape[1])); pen[:, 1:1 + N] = LAM_J; pen[:, 1 + N:] = LAM_D; pen[:, 0] = 1e-8
    pen[np.arange(N), 1 + np.arange(N)] = BIG  # no self term in pseudolikelihood
    return X, Y01, pen, {"N": N, "nb": nb}


def couplings(B, info):
    """J matrix (Ising units) from fitted coefficients. For 'box' returns the boxcar (cross) couplings."""
    N = info["N"]
    if info.get("lag") == "box":
        return B[:, 1 + N:1 + 2 * N] / 2.0
    return B[:, 1:1 + N] / 2.0


def fit_kinetic(S, day, minute, fields="block", lag="1", K=5):
    X, Y, pen, info = kinetic_design(S, day, minute, fields, lag, K)
    B = fit_logistic(X, Y, pen)
    return couplings(B, info), B, info


def fit_equal(S, day, minute, fields="block"):
    X, Y, pen, info = equal_design(S, day, minute, fields)
    B = fit_logistic(X, Y, pen)
    J = B[:, 1:1 + info["N"]] / 2.0
    np.fill_diagonal(J, 0.0)
    return J, (J + J.T) / 2.0, B


def net_influence(J):
    Jo = J.copy(); np.fill_diagonal(Jo, 0.0)
    return Jo.sum(0) - Jo.sum(1)  # sum_j J[j,k] - sum_j J[k,j]


def hub_strength(Jsym):
    Jo = np.abs(Jsym.copy()); np.fill_diagonal(Jo, 0.0)
    return Jo.sum(1)


# --------------------------------------------------------------------------- surrogates
def segments(day, minute, kind):
    """List of index arrays, one per segment, for circular shifts: kind 'day' or 'block'."""
    if kind == "day":
        keys = np.asarray(day)
    elif kind == "block":
        keys = block_ids(day, minute)
    else:
        raise ValueError(kind)
    order = np.argsort(keys, kind="stable")
    k = keys[order]
    cuts = np.flatnonzero(np.diff(k)) + 1
    return np.split(order, cuts)


def circular_shift(S, segs, rng):
    """Independent random circular shift of each agent's series within each segment."""
    out = np.empty_like(S)
    N = S.shape[1]
    for idx in segs:
        L = idx.size
        if L < 2:
            out[idx] = S[idx]; continue
        sh = rng.integers(1, L, size=N)
        ar = (np.arange(L)[:, None] - sh[None, :]) % L
        out[idx] = S[idx][ar, np.arange(N)[None, :]]
    return out


# --------------------------------------------------------------------------- simulator
def simulate(h0, Jself, Jx, D, Td, rng, blockfield=None, delay="none", K=5):
    """Parallel kinetic Ising, P(s_i(t+1)=+1) = sigma(2 H_i(t)).

    h0, Jself: (N,); Jx: (N, N) cross couplings (zero diagonal), Jx[i,j] = j -> i.
    blockfield: (D, nblocks, N) or None (field of the receiver's 30-min block).
    delay: 'none' (cross input s_j(t)) or 'box' (cross input = mean s_j over t-K+1..t).
    Returns S (D*Td, N) int8, day, minute.
    """
    N = h0.size
    S = np.empty((D, Td, N), np.int8)
    for d in range(D):
        s = np.where(rng.random(N) < 0.5, 1, -1).astype(float)
        hist = np.tile(s, (K, 1))
        for t in range(Td):
            S[d, t] = s
            if t == Td - 1:
                break
            x = hist.mean(0) if delay == "box" else s
            H = h0 + Jself * s + Jx @ x
            if blockfield is not None:
                b = min((t + 1) // BLOCK_MIN, blockfield.shape[1] - 1)
                H = H + blockfield[d, b]
            p = 1.0 / (1.0 + np.exp(-2.0 * H))
            s = np.where(rng.random(N) < p, 1.0, -1.0)
            hist = np.vstack([hist[1:], s])
    day = np.repeat(np.arange(D), Td)
    minute = np.tile(np.arange(Td), D)
    return S.reshape(D * Td, N), day, minute


# --------------------------------------------------------------------------- held-out comparison (N2)
def mean_field_covs(S, labs):
    """Per agent: mean spin of same-lab others (0 if none) and of other-lab agents. Returns (T, N, 2)."""
    T, N = S.shape
    out = np.zeros((T, N, 2))
    labs = np.asarray(labs)
    for i in range(N):
        same = (labs == labs[i]) & (np.arange(N) != i)
        other = labs != labs[i]
        if same.any():
            out[:, i, 0] = S[:, same].mean(1)
        if other.any():
            out[:, i, 1] = S[:, other].mean(1)
    return out


def loglik(eta, y):
    return (y * eta - np.logaddexp(0, eta))


def heldout(S, day, minute, labs):
    """Leave-one-day-out log-lik per transition (nats, summed over agents) for M1, M2, M3."""
    N = S.shape[1]
    X, Y, pen, info = kinetic_design(S, day, minute, "block", "1")
    dst = info["dst"]; dday = day[dst]
    nb_cols = X.shape[1] - (1 + N)
    blkcols = X[:, 1 + N:]
    mf = mean_field_covs(S.astype(float), labs)[info["src"]]  # (T', N, 2)
    rows = []
    for d in np.unique(day):
        tr, te = dday != d, dday == d
        keep_tr = blkcols[tr].sum(0) > 0; keep_te = blkcols[te].sum(0) > 0
        Xtr = np.hstack([X[tr][:, :1 + N], blkcols[tr][:, keep_tr]])
        ptr = np.zeros((N, Xtr.shape[1])); ptr[:, 1:1 + N] = LAM_J; ptr[:, 1 + N:] = LAM_D; ptr[:, 0] = 1e-8
        # M3: full couplings
        B3 = fit_logistic(Xtr, Y[tr], ptr)
        # M1: self only
        p1 = ptr.copy(); cp = np.full((N, N), BIG); np.fill_diagonal(cp, LAM_J); p1[:, 1:1 + N] = cp
        B1 = fit_logistic(Xtr, Y[tr], p1)
        # M2: self + same-lab mean + other-lab mean (per-agent designs)
        B2 = []
        for i in range(N):
            Xi = np.hstack([Xtr[:, :1], Xtr[:, 1 + i:2 + i], mf[tr, i, :], Xtr[:, 1 + N:]])
            pi = np.zeros(Xi.shape[1]); pi[1:4] = LAM_J; pi[4:] = LAM_D; pi[0] = 1e-8
            B2.append(fit_logistic(Xi, Y[tr][:, i:i + 1], pi)[0])
        # test day: refit intercept + block fields with coupling part frozen as offset
        Xte_f = np.hstack([np.ones((te.sum(), 1)), blkcols[te][:, keep_te]])
        pf = np.zeros(Xte_f.shape[1]); pf[1:] = LAM_D; pf[0] = 1e-8
        Ste = X[te][:, 1:1 + N]
        off3 = Ste @ B3[:, 1:1 + N].T
        off1 = Ste * np.diag(B1[:, 1:1 + N])[None, :]
        off2 = np.stack([B2[i][1] * Ste[:, i] + mf[te, i, :] @ B2[i][2:4] for i in range(N)], 1)
        res = {"day": int(d), "T": int(te.sum())}
        for name, off in [("M1", off1), ("M2", off2), ("M3", off3)]:
            Bf = fit_logistic(Xte_f, Y[te], pf, offset=off)
            eta = Xte_f @ Bf.T + off
            res[name] = float(loglik(eta, Y[te]).sum())
        rows.append(res)
    return rows



# --------------------------------------------------------------------------- metrics
def auc(scores, labels):
    scores = np.asarray(scores, float); labels = np.asarray(labels, bool)
    npos, nneg = labels.sum(), (~labels).sum()
    if npos == 0 or nneg == 0:
        return np.nan
    from scipy.stats import rankdata
    r = rankdata(scores)
    return (r[labels].sum() - npos * (npos + 1) / 2) / (npos * nneg)


def rank_of(values, k):
    """1-based rank of entry k when sorted descending (ties count against k)."""
    v = np.asarray(values)
    return int((v > v[k]).sum() + 1)


def bh_count(p, q=0.1):
    p = np.sort(np.asarray(p).ravel())
    m = p.size
    ok = p <= q * np.arange(1, m + 1) / m
    return int(np.flatnonzero(ok).max() + 1) if ok.any() else 0
