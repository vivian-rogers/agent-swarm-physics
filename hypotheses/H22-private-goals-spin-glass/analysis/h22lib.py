"""H22 estimators (numpy only; no project data touched here). Used by synthetic.py, explore.py, confirm_tail.py.

Couplings are built from per-day sufficient statistics, so that any subset of days (folds, bootstrap draws,
permutation nulls) can be evaluated by arithmetic only.

Content coupling J^c (card O1): x_{i,w} = v_{i,w} - mean_{w' in day} v_{i,w'} (agent-day centering; >= 2 windows),
r_ij = sum_w <x_iw, x_jw> / sqrt(sum |x_iw|^2 sum |x_jw|^2) over windows observed for both, minus the cross-day
surrogate (i on day d with j on day e != d, same window index). Talk coupling J^t (O2): mean per-day Pearson
correlation minus the cross-day surrogate.

Moments (O3), balance index tau3 and triangle frustration (O4), treatment tests (O5), overlaps (O6).
"""
from __future__ import annotations

import itertools
import warnings

import numpy as np

# ----------------------------------------------------------------------------- generic helpers


def unit(X, axis=-1):
    X = np.asarray(X, dtype=np.float64)
    n = np.linalg.norm(X, axis=axis, keepdims=True)
    return X / np.where(n > 0, n, 1)


def triu_vals(M):
    i, j = np.triu_indices(M.shape[0], 1)
    return M[i, j]


def dl_meta(est, se):
    """DerSimonian-Laird random-effects summary."""
    from scipy.stats import norm
    est, se = np.asarray(est, float), np.asarray(se, float)
    ok = np.isfinite(est) & np.isfinite(se) & (se > 0)
    est, se = est[ok], se[ok]
    k = len(est)
    if k == 0:
        return {"k": 0}
    w = 1 / se ** 2
    mu_f = np.sum(w * est) / np.sum(w)
    Q = np.sum(w * (est - mu_f) ** 2)
    c = np.sum(w) - np.sum(w ** 2) / np.sum(w)
    tau2 = max(0.0, (Q - (k - 1)) / c) if k > 1 and c > 0 else 0.0
    ws = 1 / (se ** 2 + tau2)
    mu = np.sum(ws * est) / np.sum(ws)
    s = np.sqrt(1 / np.sum(ws))
    I2 = max(0.0, (Q - (k - 1)) / Q) if Q > 0 and k > 1 else 0.0
    return {"k": int(k), "mu": float(mu), "se": float(s), "lo": float(mu - 1.96 * s), "hi": float(mu + 1.96 * s),
            "z": float(mu / s), "p": float(2 * norm.sf(abs(mu / s))), "tau2": float(tau2), "I2": float(I2)}


# ----------------------------------------------------------------------------- content coupling statistics


class ContentStats:
    """Per-day sufficient statistics for the within-day content co-movement coupling.

    X: [D, N, W, n] window vectors (any values where O == 0), O: [D, N, W] observed (bool)."""

    def __init__(self, X, O, min_shared=10):
        X = np.asarray(X, dtype=np.float64)
        O = np.asarray(O, dtype=bool).copy()
        D, N, W, n = X.shape
        # agent-day centering; agent-days with < 2 observed windows are dropped
        cnt = O.sum(2)
        O[cnt < 2] = False
        cnt = O.sum(2)
        mean = np.where(cnt[..., None] > 0, (X * O[..., None]).sum(2) / np.maximum(cnt, 1)[..., None], 0.0)
        Xc = (X - mean[:, :, None, :]) * O[..., None]
        Of = O.astype(np.float64)
        S2 = (Xc ** 2).sum(-1)
        self.D, self.N, self.min_shared = D, N, min_shared
        self.Nr = np.einsum("diwk,djwk->dij", Xc, Xc)
        self.Pr = np.einsum("diw,djw->dij", S2, Of)
        self.Cr = np.einsum("diw,djw->dij", Of, Of)
        self.Ns = np.einsum("diwk,ejwk->deij", Xc, Xc)
        self.Ps = np.einsum("diw,ejw->deij", S2, Of)
        self.Cs = np.einsum("diw,ejw->deij", Of, Of)
        self.obs_windows = O.sum((0, 2))

    def thr(self, S):
        """Shared-window threshold: min_shared over the whole unit, scaled down for day subsets (>= 3)."""
        return max(2.0, self.min_shared * np.sum(S) / self.D)

    def r_real(self, S):
        S = np.asarray(S, bool)
        num = self.Nr[S].sum(0)
        a = self.Pr[S].sum(0)
        cnt = self.Cr[S].sum(0)
        with np.errstate(invalid="ignore", divide="ignore"):
            r = num / np.sqrt(a * a.T)
        r[cnt < self.thr(S)] = np.nan
        np.fill_diagonal(r, np.nan)
        return r

    def r_surr(self, S):
        S = np.asarray(S, bool)
        M = S[:, None] & S[None, :] & ~np.eye(self.D, dtype=bool)
        if not M.any():
            return np.full((self.N, self.N), np.nan)
        num = self.Ns[M].sum(0)
        a = self.Ps[M].sum(0)
        with np.errstate(invalid="ignore", divide="ignore"):
            r = num / np.sqrt(a * a.T)
        np.fill_diagonal(r, np.nan)
        return r

    def J(self, S):
        return self.r_real(S) - self.r_surr(S)

    def J_pseudo(self, S, rng):
        """Null coupling: each agent's days permuted independently within S (co-temporality destroyed)."""
        S = np.flatnonzero(np.asarray(S, bool))
        perm = np.stack([rng.permutation(S) for _ in range(self.N)])  # [N, |S|]
        ii, jj = np.meshgrid(np.arange(self.N), np.arange(self.N), indexing="ij")
        num = np.zeros((self.N, self.N)); a = np.zeros((self.N, self.N)); cnt = np.zeros((self.N, self.N))
        for t in range(len(S)):
            di, dj = perm[:, t][ii], perm[:, t][jj]
            num += self.Ns[di, dj, ii, jj]
            a += self.Ps[di, dj, ii, jj]
            cnt += self.Cs[di, dj, ii, jj]
        with np.errstate(invalid="ignore", divide="ignore"):
            r = num / np.sqrt(a * a.T)
        Sm = np.isin(np.arange(self.D), S)
        r[cnt < self.thr(Sm)] = np.nan
        np.fill_diagonal(r, np.nan)
        return r - self.r_surr(Sm)


class TalkStats:
    """Per-day talk-spin correlations c[d, i, j] and cross-day surrogate cs[d, e, i, j] (NaN where invalid)."""

    def __init__(self, c, cs):
        self.c = np.asarray(c, float)
        self.cs = np.asarray(cs, float)
        self.D, self.N = self.c.shape[0], self.c.shape[1]

    def J(self, S):
        S = np.asarray(S, bool)
        M = S[:, None] & S[None, :] & ~np.eye(self.D, dtype=bool)
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", RuntimeWarning)
            real = np.nanmean(self.c[S], 0)
            surr = np.nanmean(self.cs[M], 0) if M.any() else np.full_like(real, np.nan)
        J = real - surr
        np.fill_diagonal(J, np.nan)
        return J

    def J_pseudo(self, S, rng):
        S = np.flatnonzero(np.asarray(S, bool))
        perm = np.stack([rng.permutation(S) for _ in range(self.N)])
        ii, jj = np.meshgrid(np.arange(self.N), np.arange(self.N), indexing="ij")
        vals = []
        for t in range(len(S)):
            di, dj = perm[:, t][ii], perm[:, t][jj]
            v = self.cs[di, dj, ii, jj]
            v = np.where(di == dj, np.nan, v)
            vals.append(v)
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", RuntimeWarning)
            real = np.nanmean(np.stack(vals), 0)
        J = real - self.J_surr_only(np.isin(np.arange(self.D), S))
        np.fill_diagonal(J, np.nan)
        return J

    def J_surr_only(self, S):
        M = S[:, None] & S[None, :] & ~np.eye(self.D, dtype=bool)
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", RuntimeWarning)
            return np.nanmean(self.cs[M], 0)


def to_pseudo_days(X, O, k, wins_per_day=None):
    """Split each day's windows into k contiguous blocks, each treated as its own 'day' (short units, Amendment 1).

    X: [D, N, W, n]; O: [D, N, W]; wins_per_day: actual window count per day (default W). Returns X', O' with D*k days."""
    D, N, W, n = X.shape
    wpd = np.full(D, W) if wins_per_day is None else np.asarray(wins_per_day)
    B = int(np.ceil(wpd.max() / k))
    Xp = np.zeros((D * k, N, B, n)); Op = np.zeros((D * k, N, B), bool)
    for d in range(D):
        for w in range(min(W, int(wpd[d]))):
            b = min(k - 1, int(w * k // wpd[d]))
            start = int(np.ceil(b * wpd[d] / k))
            j = w - start
            if 0 <= j < B:
                Xp[d * k + b, :, j] = X[d, :, w]; Op[d * k + b, :, j] = O[d, :, w]
    return Xp, Op


# ----------------------------------------------------------------------------- agent selection and folds


def complete_agents(mats, keep=None):
    """Greedily drop agents until every listed matrix is finite on all off-diagonal pairs of the kept set."""
    N = mats[0].shape[0]
    keep = np.ones(N, bool) if keep is None else keep.copy()
    while keep.sum() > 2:
        bad = np.zeros(N)
        for M in mats:
            B = ~np.isfinite(M)
            np.fill_diagonal(B, False)
            B = B & keep[None, :] & keep[:, None]
            bad += B.sum(1)
        if bad[keep].max() == 0:
            break
        worst = np.flatnonzero(keep)[np.argmax(bad[keep])]
        keep[worst] = False
    return keep


def folds(D, k):
    f = np.arange(D) % k
    return [f == t for t in range(k)]


# ----------------------------------------------------------------------------- moments and frustration


def tau3_from(J1, J2, J3):
    """Balance index tau3 = tr(J1 J2 J3) / mean_pairs tr(Ja Jb)^{3/2} (zero diagonals, finite matrices)."""
    num = np.trace(J1 @ J2 @ J3)
    den = np.mean([np.sum(J1 * J2), np.sum(J1 * J3), np.sum(J2 * J3)])
    if den <= 0:
        return np.nan, num, den
    return float(num / den ** 1.5), float(num), float(den)


def tri_frustration(J):
    """Unweighted and |product|-weighted triangle frustration on a finite symmetric J (zero diag)."""
    N = J.shape[0]
    idx = np.array(list(itertools.combinations(range(N), 3)))
    if len(idx) == 0:
        return np.nan, np.nan, np.nan
    p = J[idx[:, 0], idx[:, 1]] * J[idx[:, 1], idx[:, 2]] * J[idx[:, 2], idx[:, 0]]
    F = float(np.mean(p < 0))
    Fw = float(np.sum(np.abs(p) * (p < 0)) / np.sum(np.abs(p))) if np.sum(np.abs(p)) > 0 else np.nan
    return F, Fw, float(np.mean(triu_vals(J) < 0))


_TRI_CACHE: dict = {}


def _tri_idx(N):
    if N not in _TRI_CACHE:
        idx = np.array(list(itertools.combinations(range(N), 3)))
        iu = {p: k for k, p in enumerate(zip(*np.triu_indices(N, 1)))}
        e = np.array([[iu[(a, b)], iu[(b, c)], iu[(a, c)]] for a, b, c in idx]) if len(idx) else np.zeros((0, 3), int)
        _TRI_CACHE[N] = e
    return _TRI_CACHE[N]


def sign_shuffle_null(J, nperm=2000, rng=None):
    """Triangle frustration under signs permuted across pairs (magnitudes in place)."""
    rng = np.random.default_rng(rng)
    N = J.shape[0]
    v = triu_vals(J)
    e = _tri_idx(N)
    if len(e) == 0:
        return {}
    mag = np.abs(v)
    sg = np.sign(v)
    Fn, Fwn = [], []
    for _ in range(nperm):
        s = rng.permutation(sg)
        p = (s * mag)[e].prod(1)
        Fn.append(np.mean(p < 0)); Fwn.append(np.sum(np.abs(p) * (p < 0)) / np.sum(np.abs(p)))
    p_obs = v[e].prod(1)
    F = np.mean(p_obs < 0); Fw = np.sum(np.abs(p_obs) * (p_obs < 0)) / np.sum(np.abs(p_obs))
    Fn, Fwn = np.array(Fn), np.array(Fwn)
    return {"F": float(F), "F_null_mean": float(Fn.mean()), "F_null_q05": float(np.quantile(Fn, 0.05)),
            "F_null_q95": float(np.quantile(Fn, 0.95)), "p_F_low": float((1 + np.sum(Fn <= F)) / (1 + nperm)),
            "Fw": float(Fw), "Fw_null_mean": float(Fwn.mean()), "Fw_null_q05": float(np.quantile(Fwn, 0.05)),
            "Fw_null_q95": float(np.quantile(Fwn, 0.95)), "p_Fw_low": float((1 + np.sum(Fwn <= Fw)) / (1 + nperm)),
            "p_neg": float(np.mean(v < 0))}


def gs_frustration(J, restarts=200, rng=None):
    """Fraction of |J| weight unsatisfied in the best Ising assignment found (single-flip descent, restarts)."""
    rng = np.random.default_rng(rng)
    N = J.shape[0]
    A = np.nan_to_num(J)
    np.fill_diagonal(A, 0)
    tot = np.abs(triu_vals(A)).sum()
    best = np.inf
    for _ in range(restarts):
        s = rng.choice([-1.0, 1.0], N)
        while True:
            h = A @ s
            gain = 2 * s * h  # energy change of flipping i: dE = 2 s_i h_i (E = -1/2 s A s)
            i = np.argmin(gain)
            if gain[i] >= -1e-12:
                break
            s[i] = -s[i]
        E = -0.5 * s @ A @ s
        best = min(best, E)
    # unsatisfied weight u: E = -(sat - unsat) = -(tot - 2u)
    return float((best + tot) / (2 * tot)) if tot > 0 else np.nan


def unit_moments(stats, D, keep=None, nboot=500, nnull=300, rng=None, compute_null=True):
    """O3/O4 for one unit. stats: ContentStats or TalkStats. Returns dict."""
    rng = np.random.default_rng(rng)
    f2, f3 = folds(D, 2), folds(D, 3)
    allS = np.ones(D, bool)
    JA, JB = stats.J(f2[0]), stats.J(f2[1])
    J1, J2, J3 = (stats.J(f) for f in f3)
    Jf = stats.J(allS)
    keep = complete_agents([Jf], keep)  # only the full-unit matrix must be complete; fold gaps count as 0 in traces
    k = np.flatnonzero(keep)
    out = {"N": int(len(k)), "agents": k.tolist(), "D": int(D)}
    if len(k) < 4:
        return out
    sub = lambda M: M[np.ix_(k, k)]
    JA, JB, J1, J2, J3, Jf = map(sub, (JA, JB, J1, J2, J3, Jf))
    out["fold_pair_coverage"] = float(np.mean([np.isfinite(triu_vals(M)).mean() for M in (JA, JB, J1, J2, J3)]))
    core = _moment_core(JA, JB, J1, J2, J3, len(k))
    if not core:
        return out
    out.update(core)
    out["J_full"] = np.nan_to_num(Jf)
    out["JA"], out["JB"] = np.nan_to_num(JA), np.nan_to_num(JB)
    out.update({"Jbar_full": float(np.mean(triu_vals(Jf))), "Jsd_full": float(np.std(triu_vals(Jf)))})
    # fold-preserving day bootstrap
    if nboot:
        fidx2 = [np.flatnonzero(f) for f in f2]
        fidx3 = [np.flatnonzero(f) for f in f3]
        bs = []
        for _ in range(nboot):
            w2 = [np.bincount(rng.choice(ix, len(ix)), minlength=D) for ix in fidx2]
            w3 = [np.bincount(rng.choice(ix, len(ix)), minlength=D) for ix in fidx3]
            Jb = [sub(_J_weighted(stats, w)) for w in w2 + w3]
            mc = _moment_core(*Jb, len(k))
            if mc:
                bs.append(mc)
        for key in ("S2", "sigma2", "kappa", "tau3", "tau3_dc", "rho_split", "Jbar", "sigma"):
            vals = np.array([b[key] for b in bs], float)
            vals = vals[np.isfinite(vals)]
            if len(vals):
                out[key + "_ci90"] = [float(np.quantile(vals, 0.05)), float(np.quantile(vals, 0.95))]
                out[key + "_se"] = float(np.std(vals))
    # noise null for S2 (and tau3 under no coupling)
    if compute_null and nnull:
        nullS2, nullrho, nullsig = [], [], []
        for _ in range(nnull):
            a = triu_vals(sub(stats.J_pseudo(f2[0], rng))); b = triu_vals(sub(stats.J_pseudo(f2[1], rng)))
            okp = np.isfinite(a) & np.isfinite(b)
            a, b = a[okp], b[okp]
            if len(a) < 3:
                continue
            nullS2.append(np.mean(a * b))
            nullsig.append(np.mean(a * b) - np.mean(a) * np.mean(b))
            nullrho.append(np.corrcoef(a, b)[0, 1] if np.std(a) > 0 and np.std(b) > 0 else np.nan)
        nullS2, nullsig, nullrho = np.array(nullS2), np.array(nullsig), np.array(nullrho, float)
        nullrho = nullrho[np.isfinite(nullrho)]
        out["S2_null_mean"] = float(nullS2.mean()); out["S2_null_q95"] = float(np.quantile(nullS2, 0.95))
        out["p_S2"] = float((1 + np.sum(nullS2 >= out["S2"])) / (1 + nnull))
        out["p_sigma2"] = float((1 + np.sum(nullsig >= out["sigma2"])) / (1 + nnull))
        out["rho_null_q95"] = float(np.quantile(nullrho, 0.95)) if len(nullrho) else None
        out["p_rho"] = float((1 + np.sum(nullrho >= out["rho_split"])) / (1 + len(nullrho))) if len(nullrho) and np.isfinite(out["rho_split"]) else None
    return out


def _J_weighted(stats, w):
    """Coupling from a day-weight vector (bootstrap multiplicities). Real part weights days; surrogate weights pairs."""
    w = np.asarray(w, float)
    if isinstance(stats, ContentStats):
        num = np.tensordot(w, stats.Nr, 1); a = np.tensordot(w, stats.Pr, 1); cnt = np.tensordot(w, stats.Cr, 1)
        with np.errstate(invalid="ignore", divide="ignore"):
            r = num / np.sqrt(a * a.T)
        r[cnt < stats.thr(w > 0)] = np.nan
        Wp = np.outer(w, w); np.fill_diagonal(Wp, 0)
        num_s = np.tensordot(Wp, stats.Ns, 2); a_s = np.tensordot(Wp, stats.Ps, 2)
        with np.errstate(invalid="ignore", divide="ignore"):
            rs = num_s / np.sqrt(a_s * a_s.T)
        J = r - rs
    else:
        c = stats.c; cs = stats.cs
        m = np.isfinite(c)
        real = np.nansum(w[:, None, None] * np.nan_to_num(c), 0) / np.maximum((w[:, None, None] * m).sum(0), 1e-12)
        real[(w[:, None, None] * m).sum(0) == 0] = np.nan
        Wp = np.outer(w, w); np.fill_diagonal(Wp, 0)
        ms = np.isfinite(cs)
        den = np.tensordot(Wp, ms.astype(float), 2)
        surr = np.tensordot(Wp, np.nan_to_num(cs), 2) / np.maximum(den, 1e-12)
        surr[den == 0] = np.nan
        J = real - surr
    np.fill_diagonal(J, np.nan)
    return J


def _moment_core(JA, JB, J1, J2, J3, N):
    a, b = triu_vals(JA), triu_vals(JB)
    ok = np.isfinite(a) & np.isfinite(b)
    a, b = a[ok], b[ok]
    J1, J2, J3 = (np.nan_to_num(M) for M in (J1, J2, J3))
    if len(a) < 3:
        return {}
    S2 = float(np.mean(a * b))
    Jbar = float(np.mean((a + b) / 2))
    sig2 = S2 - float(np.mean(a) * np.mean(b))
    sigma = float(np.sqrt(sig2)) if sig2 > 0 else np.nan
    kappa = float(np.sqrt(N) * Jbar / sigma) if np.isfinite(sigma) else np.nan
    rho = float(np.corrcoef(a, b)[0, 1]) if np.std(a) > 0 and np.std(b) > 0 else np.nan
    t3, num, den = tau3_from(J1, J2, J3)
    t3dc = tau3_from(double_center(J1), double_center(J2), double_center(J3))[0]
    if not np.isfinite(sigma):
        kappa = np.nan
    return {"S2": S2, "sigma2": sig2, "Jbar": Jbar, "sigma": sigma, "kappa": kappa, "rho_split": rho, "tau3": t3,
            "tau3_dc": t3dc, "tau3_num": num, "tau3_den": den}


def double_center(J):
    """Remove row/column mean couplings (the additive 'degree' and uniform modes): J_ij - Jbar_i - Jbar_j + Jbar."""
    N = J.shape[0]
    A = J.copy()
    np.fill_diagonal(A, 0)
    r = A.sum(1) / (N - 1)
    tot = A.sum() / (N * (N - 1))
    B = A - r[:, None] - r[None, :] + tot
    np.fill_diagonal(B, 0)
    return B


def frustration_block(m, rng=None, nperm=2000, gs=True):
    """O4 secondary statistics on the full-unit point estimate, reliable-edge subset and the GS frustration."""
    rng = np.random.default_rng(rng)
    Jf, JA, JB = m["J_full"], m["JA"], m["JB"]
    out = {"shuffle": sign_shuffle_null(Jf, nperm, rng)}
    rel = np.sign(JA) == np.sign(JB)
    np.fill_diagonal(rel, False)
    e = _tri_idx(Jf.shape[0])
    if len(e):
        relv = triu_vals(rel.astype(float)) > 0
        ok = relv[e].all(1)
        v = triu_vals(Jf)
        p = v[e[ok]].prod(1)
        pn = np.mean(v[relv] < 0) if relv.any() else np.nan
        out["reliable"] = {"n_edges": int(relv.sum()), "n_tri": int(ok.sum()), "F": float(np.mean(p < 0)) if ok.any() else np.nan,
                           "p_neg": float(pn), "F_rand": float(3 * pn * (1 - pn) ** 2 + pn ** 3) if np.isfinite(pn) else np.nan}
    if gs:
        g = gs_frustration(Jf, 200, rng)
        nulls = []
        v = triu_vals(Jf)
        iu = np.triu_indices(Jf.shape[0], 1)
        for _ in range(100):
            M = np.zeros_like(Jf)
            M[iu] = rng.permutation(np.sign(v)) * np.abs(v)
            M = M + M.T
            nulls.append(gs_frustration(M, 60, rng))
        nulls = np.array(nulls)
        out["gs"] = {"f": g, "null_mean": float(nulls.mean()), "null_q05": float(np.quantile(nulls, 0.05)),
                     "p_low": float((1 + np.sum(nulls <= g)) / (1 + len(nulls)))}
    return out


def family_block_residual(J, labs):
    """Subtract the lab x lab block mean coupling (family confound check for tau3 / F)."""
    labs = np.asarray(labs)
    R = J.copy()
    u = np.unique(labs)
    for a in u:
        for b in u:
            m = (labs[:, None] == a) & (labs[None, :] == b)
            np.fill_diagonal(m, False)
            if m.sum() >= 1:
                R[m] = J[m] - J[m].mean()
    np.fill_diagonal(R, 0)
    return R


# ----------------------------------------------------------------------------- treatment tests (O5)


def class_matrix(role_idx, lookup):
    """role_idx: int per agent (-1 = no role -> class 'U'); lookup: R x R array of class codes."""
    r = np.asarray(role_idx)
    C = np.full((len(r), len(r)), 0, dtype=np.int8)  # 0 = U
    ok = r >= 0
    C[np.ix_(ok, ok)] = lookup[np.ix_(r[ok], r[ok])]
    np.fill_diagonal(C, -1)
    return C


def residualize_same_lab(J, labs):
    labs = np.asarray(labs)
    i, j = np.triu_indices(len(labs), 1)
    y = J[i, j]
    x = (labs[i] == labs[j]).astype(float)
    X = np.c_[np.ones_like(x), x]
    ok = np.isfinite(y)
    beta = np.linalg.lstsq(X[ok], y[ok], rcond=None)[0]
    R = np.full_like(J, np.nan, dtype=float)
    R[i, j] = y - X @ beta
    R[j, i] = R[i, j]
    return R, float(beta[1])


def treatment_test(J, role_idx, lookup, codes, labs=None, nperm=5000, rng=None):
    """T_c = mean J(class c) - mean J(U) for each class code in `codes` (dict name -> code), with role permutation.

    role permutation: roles shuffled among agents holding a role (role_idx >= 0); multiplicities kept."""
    rng = np.random.default_rng(rng)
    out = {}
    for adj in (False, True):
        if adj and labs is None:
            continue
        M, beta = (residualize_same_lab(J, labs) if adj else (J, None))
        i, j = np.triu_indices(len(role_idx), 1)
        v = M[i, j]
        okp = np.isfinite(v)  # pairs below the shared-window threshold are dropped
        i, j, v = i[okp], j[okp], v[okp]

        def stats_for(ridx):
            C = class_matrix(ridx, lookup)[i, j]
            base = v[C == 0].mean() if (C == 0).any() else np.nan
            res = {}
            for name, code in codes.items():
                sel = np.isin(C, code if isinstance(code, (list, tuple)) else [code])
                res[name] = (v[sel].mean() - base) if sel.any() else np.nan
                res[name + "_mean"] = v[sel].mean() if sel.any() else np.nan
                res[name + "_n"] = int(sel.sum())
            res["U_mean"] = base
            return res

        obs = stats_for(np.asarray(role_idx))
        holders = np.flatnonzero(np.asarray(role_idx) >= 0)
        null = {name: [] for name in codes}
        for _ in range(nperm):
            r = np.asarray(role_idx).copy()
            r[holders] = rng.permutation(r[holders])
            s = stats_for(r)
            for name in codes:
                null[name].append(s[name])
        res = {"beta_same_lab": beta}
        for name in codes:
            nl = np.array(null[name], float)
            nl = nl[np.isfinite(nl)]
            o = obs[name]
            res[name] = {"T": float(o) if np.isfinite(o) else None, "mean": _f(obs[name + "_mean"]), "n": obs[name + "_n"],
                         "U_mean": _f(obs["U_mean"]),
                         "p_less": float((1 + np.sum(nl <= o)) / (1 + len(nl))) if np.isfinite(o) and len(nl) else None,
                         "p_greater": float((1 + np.sum(nl >= o)) / (1 + len(nl))) if np.isfinite(o) and len(nl) else None,
                         "null_sd": float(nl.std()) if len(nl) else None}
        out["family_adjusted" if adj else "raw"] = res
    return out


def _f(x):
    return float(x) if x is not None and np.isfinite(x) else None


# ----------------------------------------------------------------------------- overlaps (O6)


def overlap_stats(H1, H2, P, m_field=None, nshift=2000, rng=None, far_frac=0.5):
    """H1, H2: [D, N, n] half-split agent-day states (already day-field removed, any norm); P: [D, N] present.

    q(d, d') = mean_i u1_{i,d} . u2_{i,d'} (symmetrized), u = unit-normalized; q_self(d) = same at d = d'.
    Returns q matrix, q_self, q_inf (lags >= far_frac*D), M, W with the per-agent circular-shift null."""
    rng = np.random.default_rng(rng)
    D, N, n = H1.shape
    U1, U2 = unit(H1), unit(H2)
    U1 = U1 * P[..., None]; U2 = U2 * P[..., None]

    def qmat(U1, U2, P):
        G = np.einsum("din,ein->dei", U1, U2)       # [D, D, N]
        G = (G + G.transpose(1, 0, 2)) / 2
        cnt = np.einsum("di,ei->de", P.astype(float), P.astype(float))
        with np.errstate(invalid="ignore", divide="ignore"):
            q = G.sum(2) / cnt
        q[cnt < 3] = np.nan
        return q

    q = qmat(U1, U2, P)
    lag = np.abs(np.arange(D)[:, None] - np.arange(D)[None, :])
    iu = np.triu_indices(D, 1)

    def summ(q):
        qs = np.nanmean(np.diag(q))
        far = lag[iu] >= max(1, int(np.ceil(far_frac * D)))
        qv = q[iu]
        q_inf = np.nanmean(qv[far]) if np.any(far & np.isfinite(qv)) else np.nan
        q1 = np.nanmean(qv[lag[iu] == 1])
        M = (q1 - q_inf) / (qs - q_inf) if np.isfinite(qs - q_inf) and abs(qs - q_inf) > 1e-9 else np.nan
        # residual variance around lag means
        res = []
        for L in range(1, D):
            s = qv[(lag[iu] == L) & np.isfinite(qv)]
            if len(s) >= 2:
                res.append(s - s.mean())
        rv = np.var(np.concatenate(res)) if res else np.nan
        return qs, q_inf, q1, M, rv

    qs, q_inf, q1, M, rv = summ(q)
    null_rv = []
    for _ in range(nshift):
        off = rng.integers(D, size=N)
        idx = (np.arange(D)[:, None] + off[None, :]) % D
        S1 = U1[idx, np.arange(N)[None, :]]
        S2 = U2[idx, np.arange(N)[None, :]]
        Ps = P[idx, np.arange(N)[None, :]]
        null_rv.append(summ(qmat(S1, S2, Ps))[4])
    null_rv = np.array(null_rv, float)
    null_rv = null_rv[np.isfinite(null_rv)]
    W = rv / np.mean(null_rv) if len(null_rv) and np.mean(null_rv) > 0 else np.nan
    p_W = float((1 + np.sum(null_rv >= rv)) / (1 + len(null_rv))) if len(null_rv) else np.nan
    return {"q": q, "q_self": float(qs), "q_inf": float(q_inf), "q_lag1": float(q1), "M": float(M), "W": float(W),
            "p_W": p_W, "resvar": float(rv), "null_resvar_mean": float(np.mean(null_rv)) if len(null_rv) else None}


def day_field_remove_groups(Hfull, H1, H2, P, groups):
    """Per-group day field (post-hoc variant for multi-room periods): subtract each room's own day mean."""
    groups = np.asarray(groups)
    o1, o2, of = H1.copy(), H2.copy(), Hfull.copy()
    for gval in np.unique(groups):
        k = groups == gval
        a, b, c = day_field_remove(Hfull[:, k], H1[:, k], H2[:, k], P[:, k])
        o1[:, k], o2[:, k], of[:, k] = a, b, c
    return o1, o2, of


def day_field_remove(Hfull, H1, H2, P):
    """Subtract the day mean over present agents (computed on full-day states) from both halves."""
    Pm = P[..., None].astype(float)
    m = (Hfull * Pm).sum(1) / np.maximum(Pm.sum(1), 1)
    return H1 - m[:, None, :], H2 - m[:, None, :], Hfull - m[:, None, :]
