"""H37 estimators (numpy only; no project data touched here). Used by synthetic.py, explore.py and confirm_g34.py.

Reply-level objects: arrays over replies e with speaker j = agent_b, target i = agent_a (codes 0..N-1), stance s_e.

  fe_fit            two-way fixed effects s = mu + a_speaker + b_target (+ gamma x) by least squares
  fe_contrast       gamma-hat for a binary relation x, agent fields absorbed
  pair_matrix       symmetric pair means (both directions), counts
  residual_matrix   pair means of two-way-FE residuals (agent fields removed at reply level)
  ground_state      best two-camp split (exact for N <= 22, else multi-restart descent); optional fixed camp sizes
  frustration_gs    unsatisfied |J| weight of the ground state, and its sign-shuffle null
  tau3_folds        H22's cross-fitted tau3 and tau3(dc) from three reply folds (h22lib.tau3_from, double_center)
  partition_accuracy, auc, mantel

H22's estimators are imported (h22lib), never copied or modified.
"""
from __future__ import annotations

import itertools
import sys
from pathlib import Path

import numpy as np

H22 = Path(__file__).resolve().parents[2] / "H22-private-goals-spin-glass" / "analysis"
sys.path.append(str(H22))  # appended: H22 also has a synthetic.py
import h22lib  # noqa: E402

SIGN = {"agree": 1, "support": 1, "neutral": 0, "oppose": -1, "undermine": -1}


# ----------------------------------------------------------------------------- reply level


def _design(spk, tgt, N, x=None):
    n = len(spk)
    cols = [np.ones(n)]
    A = np.zeros((n, N - 1)); B = np.zeros((n, N - 1))
    for k in range(1, N):
        A[:, k - 1] = spk == k
        B[:, k - 1] = tgt == k
    X = np.column_stack(cols + [A, B])
    if x is not None:
        X = np.column_stack([X, np.asarray(x, float)])
    return X


def fe_fit(s, spk, tgt, N, x=None):
    """OLS with speaker and target fixed effects (+ optional covariates x, shape [n] or [n, k]). Returns beta, resid."""
    X = _design(np.asarray(spk), np.asarray(tgt), N, x)
    keep = np.abs(X).sum(0) > 0
    beta, *_ = np.linalg.lstsq(X[:, keep], np.asarray(s, float), rcond=None)
    full = np.zeros(X.shape[1]); full[keep] = beta
    return full, np.asarray(s, float) - X @ full


def fe_contrast(s, spk, tgt, N, x, cov=None):
    """gamma-hat for binary relation x (1 = same), speaker/target fixed effects absorbed; cov = extra covariates."""
    xx = np.asarray(x, float)[:, None]
    if cov is not None:
        xx = np.column_stack([np.asarray(cov, float).reshape(len(xx), -1), xx])
    beta, _ = fe_fit(s, spk, tgt, N, xx)
    return float(beta[-1])


def two_way_resid(s, spk, tgt, N):
    return fe_fit(s, spk, tgt, N)[1]


def pair_matrix(spk, tgt, s, N, nmin=1):
    S = np.zeros((N, N)); C = np.zeros((N, N))
    np.add.at(S, (spk, tgt), s); np.add.at(C, (spk, tgt), 1)
    S = S + S.T; C = C + C.T
    with np.errstate(invalid="ignore", divide="ignore"):
        M = S / C
    M[C < nmin] = np.nan
    np.fill_diagonal(M, np.nan)
    return M, C


def residual_matrix(spk, tgt, s, N, nmin=1):
    r = two_way_resid(s, spk, tgt, N)
    return pair_matrix(spk, tgt, r, N, nmin)


# ----------------------------------------------------------------------------- camps


def _energy_all(J, configs):
    return -0.5 * np.einsum("ci,ij,cj->c", configs, J, configs)


def ground_state(J, sizes=None, restarts=300, rng=None):
    """Best +-1 assignment maximizing sum_{i<j} J_ij xi_i xi_j (missing = 0).

    sizes=(k, N-k): restrict to camps of that size (exact enumeration). Exact for N <= 22, else descent."""
    A = np.nan_to_num(np.asarray(J, float)); np.fill_diagonal(A, 0); A = (A + A.T) / 2
    N = A.shape[0]
    if sizes is not None:
        k = sizes[0]
        best, bx = -np.inf, None
        for S in itertools.combinations(range(N), k):
            x = -np.ones(N); x[list(S)] = 1
            e = 0.5 * x @ A @ x
            if e > best:
                best, bx = e, x
        return bx, best
    if N <= 22:
        best, bx = -np.inf, None
        for start in range(0, 2 ** (N - 1), 1 << 16):
            ids = np.arange(start, min(2 ** (N - 1), start + (1 << 16)))
            bits = ((ids[:, None] >> np.arange(N - 1)[None, :]) & 1).astype(float) * 2 - 1
            X = np.column_stack([np.ones(len(ids)), bits])
            e = 0.5 * np.einsum("ci,ij,cj->c", X, A, X)
            m = np.argmax(e)
            if e[m] > best:
                best, bx = e[m], X[m]
        return bx, best
    rng = np.random.default_rng(rng)
    best, bx = -np.inf, None
    for _ in range(restarts):
        x = rng.choice([-1.0, 1.0], N)
        while True:
            g = -2 * x * (A @ x)  # change of 0.5 x A x when flipping i
            i = np.argmax(g)
            if g[i] <= 1e-12:
                break
            x[i] = -x[i]
        e = 0.5 * x @ A @ x
        if e > best:
            best, bx = e, x.copy()
    return bx, best


def frustration_gs(J, nnull=200, rng=None, restarts=300):
    """Unsatisfied |J| weight fraction in the ground state, sign-shuffle null (magnitudes kept, signs permuted)."""
    rng = np.random.default_rng(rng)
    A = np.nan_to_num(np.asarray(J, float)); np.fill_diagonal(A, 0)
    N = A.shape[0]
    iu = np.triu_indices(N, 1)
    v = A[iu]
    tot = np.abs(v).sum()
    if tot == 0:
        return {"f": np.nan}

    def f_of(M):
        x, e = ground_state(M, rng=rng, restarts=restarts)
        return float((tot - e) / (2 * tot))  # e = sat - unsat
    f = f_of(A)
    nulls = []
    for _ in range(nnull):
        M = np.zeros_like(A); M[iu] = rng.permutation(np.sign(v)) * np.abs(v); M = M + M.T
        nulls.append(f_of(M))
    nulls = np.array(nulls)
    return {"f": f, "null_mean": float(nulls.mean()), "null_q05": float(np.quantile(nulls, 0.05)),
            "p_low": float((1 + np.sum(nulls <= f)) / (1 + len(nulls))), "p_neg": float(np.mean(v < 0)), "n_edges": int((v != 0).sum())}


def faction_score(J, nnull=200, rng=None, restarts=300):
    """Satisfied weight of the best split relative to total |J| (1 - 2f), vs the sign-shuffle null (higher = more factional)."""
    fr = frustration_gs(J, nnull, rng, restarts)
    if not np.isfinite(fr.get("f", np.nan)):
        return fr
    fr["score"] = 1 - 2 * fr["f"]
    fr["p_factional"] = fr["p_low"]
    return fr


def partition_accuracy(x_hat, x_true):
    x_hat = np.sign(np.asarray(x_hat)); x_true = np.sign(np.asarray(x_true))
    a = np.mean(x_hat == x_true)
    return float(max(a, 1 - a))


def chance_accuracy(x_true, sizes):
    """Distribution of partition_accuracy over all camp splits with the given sizes."""
    N = len(x_true)
    out = []
    for S in itertools.combinations(range(N), sizes[0]):
        x = -np.ones(N); x[list(S)] = 1
        out.append(partition_accuracy(x, x_true))
    return np.array(out)


# ----------------------------------------------------------------------------- balance


def tau3_folds(spk, tgt, s, N, fold, resid=True, nmin=1):
    """Cross-fitted tau3, tau3(dc) from three reply folds (fold in {0,1,2}); pair means of two-way residuals if resid."""
    Js = []
    for f in range(3):
        m = fold == f
        if resid:
            M, C = residual_matrix(spk[m], tgt[m], s[m], N, nmin)
        else:
            M, C = pair_matrix(spk[m], tgt[m], s[m], N, nmin)
        Js.append(np.nan_to_num(M))
    t = h22lib.tau3_from(*Js)[0]
    tdc = h22lib.tau3_from(*(h22lib.double_center(M) for M in Js))[0]
    return t, tdc


# ----------------------------------------------------------------------------- misc


def auc(pos, neg):
    pos = np.asarray(pos, float); neg = np.asarray(neg, float)
    pos = pos[np.isfinite(pos)]; neg = neg[np.isfinite(neg)]
    if len(pos) == 0 or len(neg) == 0:
        return np.nan
    from scipy.stats import rankdata
    r = rankdata(np.concatenate([pos, neg]))
    return float((r[:len(pos)].sum() - len(pos) * (len(pos) + 1) / 2) / (len(pos) * len(neg)))


def mantel(A, B, nperm=5000, rng=None):
    """Pearson r between upper triangles of A and B (finite pairs), agent-permutation null on B."""
    rng = np.random.default_rng(rng)
    N = A.shape[0]
    iu = np.triu_indices(N, 1)
    a, b = A[iu], B[iu]
    ok = np.isfinite(a) & np.isfinite(b)
    if ok.sum() < 4:
        return {"r": np.nan}
    r = np.corrcoef(a[ok], b[ok])[0, 1]
    null = []
    for _ in range(nperm):
        p = rng.permutation(N)
        bb = B[np.ix_(p, p)][iu]
        ok2 = np.isfinite(a) & np.isfinite(bb)
        null.append(np.corrcoef(a[ok2], bb[ok2])[0, 1] if ok2.sum() >= 4 else np.nan)
    null = np.array(null); null = null[np.isfinite(null)]
    return {"r": float(r), "p_greater": float((1 + np.sum(null >= r)) / (1 + len(null))), "n_pairs": int(ok.sum())}


def bh(p, q=0.1):
    p = np.asarray(p, float)
    n = len(p)
    o = np.argsort(p)
    thr = q * np.arange(1, n + 1) / n
    passed = p[o] <= thr
    k = np.max(np.flatnonzero(passed)) + 1 if passed.any() else 0
    sig = np.zeros(n, bool); sig[o[:k]] = True
    return sig


def significant_negative_pairs(spk, tgt, s, N, nmin=3, q=0.1):
    """Per-pair one-sample t on two-way-FE residuals (both directions); BH-FDR on the lower tail."""
    from scipy.stats import t as tdist
    r = two_way_resid(s, spk, tgt, N)
    lo = np.minimum(spk, tgt); hi = np.maximum(spk, tgt)
    out = []
    for i in range(N):
        for j in range(i + 1, N):
            m = (lo == i) & (hi == j)
            n = int(m.sum())
            if n < nmin:
                continue
            x = r[m]
            sd = x.std(ddof=1) if n > 1 else 0
            if sd == 0:
                continue
            tt = x.mean() / (sd / np.sqrt(n))
            out.append((i, j, n, float(x.mean()), float(tdist.cdf(tt, n - 1))))
    if not out:
        return [], np.array([])
    p = np.array([o[4] for o in out])
    sig = bh(p, q)
    return [o for o, g in zip(out, sig) if g], p


def agent_scores(spk, tgt, s, N):
    """Per-agent received and given residual stance (speaker/target fields from the two-way FE), as z-scores."""
    beta, _ = fe_fit(s, spk, tgt, N)
    a = np.r_[0, beta[1:N]]; b = np.r_[0, beta[N:2 * N - 1]]
    present_s = np.bincount(spk, minlength=N) > 0
    present_t = np.bincount(tgt, minlength=N) > 0

    def z(v, m):
        out = np.full(N, np.nan)
        if m.sum() > 1:
            out[m] = (v[m] - v[m].mean()) / (v[m].std() + 1e-12)
        return out
    return {"given": a, "received": b, "z_given": z(a, present_s), "z_received": z(b, present_t)}


def adjusted_rand(a, b):
    """Adjusted Rand index of two labelings (Hubert & Arabie)."""
    from math import comb
    a = np.asarray(a); b = np.asarray(b)
    ua, ia = np.unique(a, return_inverse=True); ub, ib = np.unique(b, return_inverse=True)
    M = np.zeros((len(ua), len(ub)), int)
    np.add.at(M, (ia, ib), 1)
    n = len(a)
    s_ij = sum(comb(int(x), 2) for x in M.ravel())
    s_a = sum(comb(int(x), 2) for x in M.sum(1)); s_b = sum(comb(int(x), 2) for x in M.sum(0))
    exp = s_a * s_b / comb(n, 2) if n > 1 else 0
    mx = (s_a + s_b) / 2
    return float((s_ij - exp) / (mx - exp)) if mx != exp else 0.0
