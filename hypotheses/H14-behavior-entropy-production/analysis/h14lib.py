"""H14 library: entropy production of categorical state sequences (single agent and collective).

Estimators (nats per transition):
  ep_plugin      plug-in pair-KL  sum_{a!=b} p_ab ln(n_ab / n_ba) over pairs with both counts > 0
  ep_chi2        chi-square bias-corrected plug-in (1/n) sum_{a<b} [(n_ab - n_ba)^2 / (n_ab + n_ba) - 1]
                 (iid-transition correction; biased negative under flicker, like H05's iid pair version)
  ep_newton      cross-fitted Newton-step AIK bound on antisymmetrized transition indicators (H05 ep_gauss_crossfit,
                 day folds): the primary estimator
  ep_ml          held-out exact AIK dual (H05 ep_heldout)
  ep_order2      cross-fitted Newton bound on antisymmetrized 3-block indicators, divided by 2 (per transition)
Nulls:
  db_surrogates  detailed-balance surrogate: reversible chain with the same symmetric pair counts, simulated with the
                 real day lengths and day-start states
  crossday       cross-day surrogate for the collective grid (each agent's day replaced by another of its days)
Currents: net flux and triangle cycle affinities.
Collective observables on a common grid: single, mean-field (MF) and pairwise (PW) antisymmetric observables.
Kinetic Potts simulator with exact EP (parallel updates).

H05's estimator module is imported, not copied. No project data is read here except by load_state_table.
"""
from __future__ import annotations

import os

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "VECLIB_MAXIMUM_THREADS", "POLARS_MAX_THREADS"):
    os.environ.setdefault(_v, "2")

import itertools
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "hypotheses/H05-rooms-cut/analysis"))
from ep import ep_gauss_crossfit, ep_heldout  # noqa: E402  (H05's validated estimators)


# ============================================================================ sequences
def transitions(seq: np.ndarray, day: np.ndarray, order: np.ndarray | None = None):
    """Consecutive pairs within a day. For grids, `order` (bin index) must also step by exactly 1.

    seq, day, order: rows sorted by (day, order). Returns prev, next, day_of_transition."""
    ok = day[1:] == day[:-1]
    if order is not None:
        ok &= (order[1:] - order[:-1]) == 1
    return seq[:-1][ok], seq[1:][ok], day[1:][ok]


def triples(seq, day, order=None):
    ok = (day[2:] == day[1:-1]) & (day[1:-1] == day[:-2])
    if order is not None:
        ok &= ((order[2:] - order[1:-1]) == 1) & ((order[1:-1] - order[:-2]) == 1)
    return seq[:-2][ok], seq[1:-1][ok], seq[2:][ok], day[2:][ok]


def counts(prev, nxt, q):
    C = np.zeros((q, q))
    np.add.at(C, (prev, nxt), 1)
    return C


def pair_list(q):
    return [(a, b) for a in range(q) for b in range(a + 1, q)]


def g_trans(prev, nxt, q, drop_empty=True):
    """Antisymmetrized transition indicators g_ab = 1[a->b] - 1[b->a], a<b. (T, q(q-1)/2)."""
    code = prev.astype(np.int64) * q + nxt.astype(np.int64)
    P = pair_list(q)
    G = np.zeros((len(prev), len(P)))
    for k, (a, b) in enumerate(P):
        G[:, k] = (code == a * q + b).astype(np.float64) - (code == b * q + a)
    if drop_empty:
        G = G[:, np.any(G != 0, axis=0)]
    return G


def g_triples(x0, x1, x2, q, drop_empty=True):
    """Antisymmetrized 3-block indicators 1[(a,b,c)] - 1[(c,b,a)] for non-palindromic triples, canonical a < c."""
    code = (x0.astype(np.int64) * q + x1) * q + x2
    cols = []
    for a in range(q):
        for c in range(a + 1, q):
            for b in range(q):
                f = (a * q + b) * q + c
                r = (c * q + b) * q + a
                cols.append((code == f).astype(np.float64) - (code == r))
    G = np.stack(cols, 1) if cols else np.zeros((len(x0), 0))
    if drop_empty:
        G = G[:, np.any(G != 0, axis=0)]
    return G


# ============================================================================ estimators
def ep_plugin(prev, nxt, q):
    C = counts(prev, nxt, q)
    n = C.sum()
    if n == 0:
        return np.nan
    m = (C > 0) & (C.T > 0)
    np.fill_diagonal(m, False)
    return float((C[m] / n * np.log(C[m] / C.T[m])).sum())


def ep_chi2(prev, nxt, q):
    C = counts(prev, nxt, q)
    n = C.sum()
    if n == 0:
        return np.nan
    s = 0.0
    for a, b in pair_list(q):
        t = C[a, b] + C[b, a]
        if t > 0:
            s += (C[a, b] - C[b, a]) ** 2 / t - 1.0
    return float(s / n)


def _k(days):
    return int(min(5, len(np.unique(days))))


def newton(G, days):
    """Cross-fitted Newton bound (nats per row) with day folds; NaN if < 2 days or no columns."""
    if G.shape[1] == 0 or len(np.unique(days)) < 2:
        return np.nan
    return float(ep_gauss_crossfit(G, days, k=_k(days))["sigma"])


def ep_newton(prev, nxt, d, q):
    return newton(g_trans(prev, nxt, q), d)


def day_folds(d, k=None):
    days = np.unique(d)
    k = min(5, len(days)) if k is None else k
    fold_of = {dd: i % k for i, dd in enumerate(days)}
    return np.array([fold_of[x] for x in d]), k


def ep_cfx(prev, nxt, d, q, alpha=0.5):
    """Cross-fitted exact AIK dual for transition indicators. On training days the optimal parameters are the
    smoothed log-ratios Theta_ab = ln((n_ab + alpha) / (n_ba + alpha)) (exact optimum: theta_ab = ln p_ab / p_ba,
    Z = 1, value = pair-KL). The dual is evaluated on held-out days: f = <Theta[x, y]> - ln <exp(-Theta[x, y])>.
    A valid held-out lower bound on the pair-KL (biased low by the noise in Theta); NaN if < 2 days."""
    if len(np.unique(d)) < 2 or len(prev) == 0:
        return np.nan
    f, k = day_folds(d)
    vals, ws = [], []
    for qq in range(k):
        tr, te = f != qq, f == qq
        if te.sum() == 0 or tr.sum() == 0:
            continue
        C = counts(prev[tr], nxt[tr], q)
        Th = np.log((C + alpha) / (C.T + alpha))
        z = Th[prev[te], nxt[te]]
        vals.append(z.mean() - np.log(np.mean(np.exp(-z))))
        ws.append(te.sum())
    return float(np.average(vals, weights=ws)) if vals else np.nan


def ep_tur(newton_value):
    """TUR form of the Newton quadratic, ln(1 + Sigma_N): a valid (looser) bound at any asymmetry."""
    return float(np.log1p(max(newton_value, 0.0))) if np.isfinite(newton_value) else np.nan


def ep_ml(prev, nxt, d, q):
    G = g_trans(prev, nxt, q)
    if G.shape[1] == 0 or len(np.unique(d)) < 2:
        return np.nan
    return float(ep_heldout(G, d, k=_k(d), return_theta=False)["sigma"])


def ep_order2(seq, day, q, order=None):
    x0, x1, x2, d = triples(seq, day, order)
    if len(x0) < 10:
        return np.nan
    return 0.5 * newton(g_triples(x0, x1, x2, q), d)


def ep_cfx3(seq, day, q, order=None, alpha=0.5):
    """Order-2 analogue of ep_cfx: cross-fitted exact dual on 3-block indicators, Theta_abc = ln((n_abc + a) /
    (n_cba + a)), evaluated on held-out days, divided by 2 (per transition). Exceeds ep_cfx when the sequence has
    memory beyond order 1 that carries irreversibility (Roldan-Parrondo hierarchy)."""
    x0, x1, x2, d = triples(seq, day, order)
    if len(x0) < 10 or len(np.unique(d)) < 2:
        return np.nan
    f, k = day_folds(d)
    vals, ws = [], []
    for qq in range(k):
        tr, te = f != qq, f == qq
        if te.sum() == 0 or tr.sum() == 0:
            continue
        C = np.zeros((q, q, q))
        np.add.at(C, (x0[tr], x1[tr], x2[tr]), 1)
        Th = np.log((C + alpha) / (C.transpose(2, 1, 0) + alpha))
        z = Th[x0[te], x1[te], x2[te]]
        vals.append(z.mean() - np.log(np.mean(np.exp(-z))))
        ws.append(te.sum())
    return 0.5 * float(np.average(vals, weights=ws)) if vals else np.nan


def newton_subsets(G, days, subsets, k=None, ridge=1e-3):
    """H05's cross-fitted Newton bound (ep_gauss_crossfit) for several column subsets of G, sharing one
    covariance and one set of fold means. Same formula: K_S + ridge * tr(K_S)/d_S * I; sigma = 2 mean_{a!=b}
    gbar_a' K_S^-1 gbar_b over day folds. Returns {name: sigma}."""
    G = np.asarray(G, dtype=np.float64)
    days = np.asarray(days)
    if len(np.unique(days)) < 2:
        return {nm: np.nan for nm in subsets}
    u = np.unique(days)
    kk = int(min(5, len(u))) if k is None else k
    fold_of = {dd: i % kk for i, dd in enumerate(u)}
    f = np.array([fold_of[x] for x in days])
    K = np.cov(G, rowvar=False).reshape(G.shape[1], G.shape[1])
    means = np.array([G[f == qq].mean(0) for qq in range(kk) if (f == qq).any()])
    out = {}
    for nm, cols in subsets.items():
        cols = np.asarray(cols)
        if len(cols) == 0:
            out[nm] = np.nan
            continue
        Ks = K[np.ix_(cols, cols)]
        Ks = Ks + ridge * np.trace(Ks) / len(Ks) * np.eye(len(Ks))
        Ms = means[:, cols]
        W = np.linalg.solve(Ks, Ms.T).T
        M = Ms @ W.T
        m = len(Ms)
        out[nm] = float(2 * (M.sum() - np.trace(M)) / (m * (m - 1)))
    return out


def heldout_loglik(seq, day, q, orders=(0, 1, 2), alpha=0.5):
    """Day-blocked held-out log-likelihood per transition of order-k Markov chains (additive smoothing).
    All orders are scored on the same targets (positions with >= 2 predecessors in the day)."""
    days = np.unique(day)
    k = min(5, len(days))
    if k < 2:
        return {o: np.nan for o in orders}
    fold = {dd: i % k for i, dd in enumerate(days)}
    f = np.array([fold[dd] for dd in day])
    ok = np.zeros(len(seq), bool)
    ok[2:] = (day[2:] == day[1:-1]) & (day[1:-1] == day[:-2])
    tgt = np.flatnonzero(ok)
    ctx = {0: np.zeros(len(tgt), np.int64), 1: seq[tgt - 1].astype(np.int64),
           2: seq[tgt - 2].astype(np.int64) * q + seq[tgt - 1]}
    y = seq[tgt].astype(np.int64)
    out = {}
    for o in orders:
        nctx = q ** o
        ll = 0.0
        for qq in range(k):
            tr, te = f[tgt] != qq, f[tgt] == qq
            C = np.zeros((nctx, q))
            np.add.at(C, (ctx[o][tr], y[tr]), 1)
            P = (C + alpha) / (C + alpha).sum(1, keepdims=True)
            ll += np.log(P[ctx[o][te], y[te]]).sum()
        out[o] = float(ll / len(tgt)) if len(tgt) else np.nan
    return out


# ============================================================================ detailed-balance surrogate
def db_matrix(prev, nxt, q):
    C = counts(prev, nxt, q)
    S = (C + C.T) / 2.0
    rs = S.sum(1)
    P = np.where(rs[:, None] > 0, S / np.where(rs[:, None] > 0, rs[:, None], 1), np.eye(q))
    return P


def simulate_days(P, starts, lengths, R, rng):
    """Simulate R copies of a Markov chain for each day: returns (seqs (R, sum L), day labels (sum L,))."""
    cP = np.cumsum(P, 1)
    cP[:, -1] = 1.0 + 1e-12
    out, dl = [], []
    for di, (s0, L) in enumerate(zip(starts, lengths)):
        X = np.empty((R, L), dtype=np.int8)
        X[:, 0] = s0
        U = rng.random((R, L))
        for t in range(1, L):
            X[:, t] = (U[:, t, None] > cP[X[:, t - 1]]).sum(1)
        out.append(X)
        dl.append(np.full(L, di))
    return np.concatenate(out, 1), np.concatenate(dl)


def day_structure(seq, day):
    """Day starts and lengths of a sequence (rows sorted by day)."""
    u, idx, cnt = np.unique(day, return_index=True, return_counts=True)
    order = np.argsort(idx)
    return seq[idx[order]], cnt[order], u[order]


def db_null(seq, day, q, R, rng, stats=("newton", "plugin"), lump=None):
    """Statistics of R detailed-balance surrogates. lump: optional array mapping states -> lumped states, for
    affinity nulls on the lumped chain (returns also 'counts_lumped' per surrogate)."""
    p, n_, _ = transitions(seq, day)
    P = db_matrix(p, n_, q)
    s0, L, _ = day_structure(seq, day)
    X, dl = simulate_days(P, s0, L, R, rng)
    res = {s: np.empty(R) for s in stats}
    lumped = []
    for r in range(R):
        pp, nn, dd = transitions(X[r], dl)
        if "newton" in stats:
            res["newton"][r] = ep_newton(pp, nn, dd, q)
        if "plugin" in stats:
            res["plugin"][r] = ep_plugin(pp, nn, q)
        if "chi2" in stats:
            res["chi2"][r] = ep_chi2(pp, nn, q)
        if "cfx" in stats:
            res["cfx"][r] = ep_cfx(pp, nn, dd, q)
        if lump is not None:
            ql = int(lump.max()) + 1
            lumped.append(counts(lump[pp], lump[nn], ql))
    if lump is not None:
        res["counts_lumped"] = np.stack(lumped)
    return res


# ============================================================================ currents
def triangles(q):
    return list(itertools.combinations(range(q), 3))


def cycle_affinity(C, a, b, c, alpha=0.5):
    """ln of forward/backward products around a -> b -> c -> a."""
    Ca = C + alpha
    return float(np.log(Ca[a, b] * Ca[b, c] * Ca[c, a] / (Ca[a, c] * Ca[c, b] * Ca[b, a])))


def cycle_current(C, a, b, c):
    """Mean net flux per transition around a -> b -> c -> a."""
    n = C.sum()
    F = (C - C.T) / max(n, 1)
    return float((F[a, b] + F[b, c] + F[c, a]) / 3.0)


def flux(C):
    n = C.sum()
    return (C - C.T) / max(n, 1)


def ep_decomposition(C):
    """Plug-in EP contribution of each unordered pair: (p_ab - p_ba) ln(n_ab / n_ba) (pairs with both > 0)."""
    n = C.sum()
    q = len(C)
    out = np.zeros((q, q))
    for a, b in pair_list(q):
        if C[a, b] > 0 and C[b, a] > 0:
            out[a, b] = out[b, a] = (C[a, b] - C[b, a]) / n * np.log(C[a, b] / C[b, a])
    return out


# ============================================================================ family statistics
def eta2(v, lab):
    v = np.asarray(v, float)
    lab = np.asarray(lab)
    m = v.mean()
    sst = ((v - m) ** 2).sum()
    if sst == 0:
        return 0.0
    ssb = sum(((lab == g).sum()) * (v[lab == g].mean() - m) ** 2 for g in np.unique(lab))
    return float(ssb / sst)


def perm_eta2(v, lab, n_perm, rng):
    obs = eta2(v, lab)
    null = np.array([eta2(v, rng.permutation(lab)) for _ in range(n_perm)])
    return obs, float((1 + (null >= obs - 1e-12).sum()) / (n_perm + 1)), float(null.mean())


def perm_diff(v, lab, a, b, n_perm, rng):
    v = np.asarray(v, float)
    lab = np.asarray(lab)
    sel = (lab == a) | (lab == b)
    if (lab == a).sum() < 1 or (lab == b).sum() < 1:
        return np.nan, np.nan, np.nan
    vv, ll = v[sel], lab[sel]
    obs = vv[ll == a].mean() - vv[ll == b].mean()
    null = np.empty(n_perm)
    for i in range(n_perm):
        p = rng.permutation(ll)
        null[i] = vv[p == a].mean() - vv[p == b].mean()
    p2 = float((1 + (np.abs(null) >= abs(obs) - 1e-12).sum()) / (n_perm + 1))
    p1 = float((1 + (null >= obs - 1e-12).sum()) / (n_perm + 1))
    return float(obs), p2, p1


# ============================================================================ collective observables (grid)
def collective_blocks(Xp, Xn, q, work, chat, which=("single", "mf", "pw")):
    """Observables on a common grid. Xp, Xn: (T, N) int states at t and t+1.

    single: per agent antisymmetrized transition indicators (empty columns dropped);
    mf:     g_i^{ab} = 1[x_i'=a] m_{-i}^b - 1[x_i=a] m_{-i}^{b'}, a, b in {work, chat};
    pw:     g_ij^c = s_i^c' s_j^c - s_i^c s_j^c', s^c = +-1 indicator of c in {work, chat}, i < j."""
    T, N = Xp.shape
    work = np.asarray(work)
    out = {}
    if "single" in which:
        out["single"] = np.hstack([g_trans(Xp[:, i], Xn[:, i], q) for i in range(N)])
    ind_p = {"work": np.isin(Xp, work).astype(np.float64), "chat": (Xp == chat).astype(np.float64)}
    ind_n = {"work": np.isin(Xn, work).astype(np.float64), "chat": (Xn == chat).astype(np.float64)}
    if "mf" in which:
        cols = []
        for a in ("work", "chat"):
            for b in ("work", "chat"):
                mp = (ind_p[b].sum(1, keepdims=True) - ind_p[b]) / max(N - 1, 1)
                mn = (ind_n[b].sum(1, keepdims=True) - ind_n[b]) / max(N - 1, 1)
                cols.append(ind_n[a] * mp - ind_p[a] * mn)
        G = np.hstack(cols)
        out["mf"] = G[:, np.any(G != 0, axis=0)]
    if "pw" in which:
        i, j = np.triu_indices(N, k=1)
        cols = []
        for c in ("work", "chat"):
            sp, sn = 2 * ind_p[c] - 1, 2 * ind_n[c] - 1
            cols.append(sn[:, i] * sp[:, j] - sp[:, i] * sn[:, j])
        G = np.hstack(cols)
        out["pw"] = G[:, np.any(G != 0, axis=0)]
    return out


def collective_ep(Xp, Xn, d, q, work, chat, which=("mf", "pw")):
    """Sigma_1 (single observables), Sigma_{1+w} and Delta_w = Sigma_{1+w} - Sigma_1 for w in which, plus each
    collective block alone. Newton cross-fit (H05 formula) with one shared covariance (newton_subsets)."""
    B = collective_blocks(Xp, Xn, q, work, chat, which=("single",) + tuple(which))
    blocks = [("single", B["single"])] + [(w, B[w]) for w in which]
    G = np.hstack([b for _, b in blocks])
    idx, o = {}, 0
    for nm, b in blocks:
        idx[nm] = np.arange(o, o + b.shape[1])
        o += b.shape[1]
    subsets = {"sigma1": idx["single"]}
    for w in which:
        subsets[f"sigma1_{w}"] = np.r_[idx["single"], idx[w]]
        subsets[f"sigma_{w}_alone"] = idx[w]
    r = newton_subsets(G, d, subsets)
    res = {"sigma1": r["sigma1"], "d_single": int(len(idx["single"]))}
    for w in which:
        res[f"sigma1_{w}"] = r[f"sigma1_{w}"]
        res[f"delta_{w}"] = r[f"sigma1_{w}"] - r["sigma1"]
        res[f"sigma_{w}_alone"] = r[f"sigma_{w}_alone"]
        res[f"d_{w}"] = int(len(idx[w]))
    return res


def crossday_surrogate(X, rng):
    """X: (n_days, L+1, N) aligned minute arrays. Each agent's days permuted independently (derangement)."""
    nd, _, N = X.shape
    Y = np.empty_like(X)
    for a in range(N):
        for _ in range(100):
            perm = rng.permutation(nd)
            if nd < 2 or not np.any(perm == np.arange(nd)):
                break
        Y[:, :, a] = X[perm, :, a]
    return Y


def circshift_surrogate(X, rng):
    nd, L1, N = X.shape
    Y = np.empty_like(X)
    for dd in range(nd):
        for a in range(N):
            Y[dd, :, a] = np.roll(X[dd, :, a], rng.integers(L1))
    return Y


def stack_aligned(X):
    """(n_days, L+1, N) -> Xp, Xn, d (transitions within days)."""
    nd, L1, N = X.shape
    Xp = X[:, :-1].reshape(-1, N)
    Xn = X[:, 1:].reshape(-1, N)
    d = np.repeat(np.arange(nd), L1 - 1)
    return Xp, Xn, d


# ============================================================================ kinetic Potts
def _potts_logits(H0, K, Jz, xp):
    """logit[r, i, a] = H0[i,a] + K[i,a,x_i] + sum_j Jz[i,j,a,x_j] for a batch of configurations xp (R, N)."""
    N, q = H0.shape
    oh = np.eye(q)[xp]                                   # (R, N, q)
    self_t = np.einsum("iab,rib->ria", K, oh)
    cross_t = np.einsum("ijab,rjb->ria", Jz, oh)
    return H0[None] + self_t + cross_t


def simulate_potts(H0, K, J, n_days, L, rng, burn=300, h_t=None, restart=None, x0=None):
    """Parallel kinetic Potts. H0 (N,q); K (N,q,q) self-kernel K[i,a,b]: effect of own state b on next state a;
    J (N,N,q,q) J[i,j,a,b]: effect of agent j in state b on agent i's next state a (diag ignored).
    h_t: optional (L, q) common time-of-day field. restart: None = continue the chain across days (with burn
    before day 0); 'cold' = each day restarts from x0 (or state 0). Returns X (n_days*L, N) int8, day labels."""
    N, q = H0.shape
    Jz = J.copy()
    Jz[np.arange(N), np.arange(N)] = 0.0
    x = rng.integers(q, size=N) if x0 is None else np.array(x0)
    X = np.empty((n_days * L, N), dtype=np.int8)

    def step(x, t=None):
        logit = _potts_logits(H0, K, Jz, x[None])[0]
        if h_t is not None and t is not None:
            logit = logit + h_t[t]
        p = np.exp(logit - logit.max(1, keepdims=True))
        p /= p.sum(1, keepdims=True)
        u = rng.random(N)
        return (u[:, None] > np.cumsum(p, 1)).sum(1).clip(0, q - 1)

    if restart is None:
        for _ in range(burn):
            x = step(x)
    for dd in range(n_days):
        if restart == "cold":
            x = np.zeros(N, int) if x0 is None else np.array(x0)
        for t in range(L):
            x = step(x, t)
            X[dd * L + t] = x
    return X, np.repeat(np.arange(n_days), L)


def potts_logp(H0, K, J, Xp, Xn):
    """log P(x' | x) summed over agents, for each row (no time field)."""
    N, q = H0.shape
    Jz = J.copy()
    Jz[np.arange(N), np.arange(N)] = 0.0
    T = len(Xp)
    out = np.zeros(T)
    for t0 in range(0, T, 4096):
        xp = Xp[t0:t0 + 4096].astype(int)
        xn = Xn[t0:t0 + 4096].astype(int)
        logit = _potts_logits(H0, K, Jz, xp)
        mx = logit.max(2, keepdims=True)
        lse = np.log(np.exp(logit - mx).sum(2)) + mx[:, :, 0]
        lp = np.take_along_axis(logit, xn[:, :, None], 2)[:, :, 0] - lse
        out[t0:t0 + 4096] = lp.sum(1)
    return out


def potts_exact_ep(H0, K, J, X, day):
    """Exact stationary EP per step: mean of ln P(x'|x) - ln P(x|x') over consecutive within-day pairs."""
    ok = day[1:] == day[:-1]
    Xp, Xn = X[:-1][ok], X[1:][ok]
    return float(np.mean(potts_logp(H0, K, J, Xp, Xn) - potts_logp(H0, K, J, Xn, Xp)))


# ============================================================================ generic state tables
def load_state_table(path_or_df, agent_col="agent", state_col="state", time_col="t", day_col=None, bin_col=None,
                     state_names=None):
    """Normalize any categorical state table to (agent, pt_date, order, state code) plus the state-name list.

    Event tables: give time_col (UTC datetime); order = rank within (agent, day); transitions between consecutive
    records. Grid tables (e.g. Jev labels per 5-min window): give bin_col (int window index) and day_col;
    transitions only between bins that differ by exactly 1."""
    import polars as pl
    df = pl.read_parquet(path_or_df) if isinstance(path_or_df, (str, Path)) else path_or_df
    if day_col is None:
        df = df.with_columns(pl.col(time_col).dt.convert_time_zone("America/Los_Angeles").dt.date().cast(pl.Utf8).alias("pt_date"))
        day_col = "pt_date"
    df = df.filter(pl.col(state_col).is_not_null())
    names = state_names or sorted(df[state_col].cast(pl.Utf8).unique().to_list())
    code = {s: i for i, s in enumerate(names)}
    df = df.with_columns(pl.col(state_col).cast(pl.Utf8).replace_strict(code, return_dtype=pl.Int8).alias("state"),
                         pl.col(agent_col).cast(pl.Int16).alias("agent"), pl.col(day_col).cast(pl.Utf8).alias("pt_date"))
    if bin_col is not None:
        df = df.with_columns(pl.col(bin_col).cast(pl.Int64).alias("order"), pl.lit(True).alias("grid"))
    else:
        df = df.sort("agent", time_col).with_columns(
            pl.col(time_col).rank("ordinal").over(["agent", "pt_date"]).cast(pl.Int64).alias("order"), pl.lit(False).alias("grid"))
    return df.select("agent", "pt_date", "order", "state", "grid").sort("agent", "pt_date", "order"), names
