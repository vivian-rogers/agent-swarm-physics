"""H34 statistics: GW-NB cascade-size law, fits, bootstraps, jitter-null test, dose-response hazard ratios."""
from __future__ import annotations

import math

import numpy as np
from scipy import optimize, special, stats

K_INF = 1e4  # dispersion treated as Poisson (Borel) above this


# ------------------------------------------------------------------------------------------- size laws
def nb_gw_logpmf(s, R, k):
    """Total progeny of a GW tree with NB(mean R, dispersion k) offspring (Lloyd-Smith 2005); Borel as k -> inf."""
    s = np.asarray(s, dtype=float)
    R = max(float(R), 1e-12)
    if k >= K_INF:
        return -R * s + (s - 1) * np.log(R * s) - special.gammaln(s + 1)
    return (special.gammaln(k * s + s - 1) - special.gammaln(k * s) - special.gammaln(s + 1)
            + (s - 1) * np.log(R / k) - (k * s + s - 1) * np.log1p(R / k))


def nb_gw_pmf_trunc(R, k, smax):
    s = np.arange(1, smax + 1)
    lp = nb_gw_logpmf(s, R, k)
    lp = np.where(np.isfinite(lp), lp, -np.inf)
    p = np.exp(lp - lp.max())
    return p / p.sum()


def borel_cutoff(R):
    """s_c with P(s) ~ s^-3/2 exp(-s/s_c) for the Borel law (R < 1)."""
    R = min(max(R, 1e-9), 1 - 1e-12)
    return 1.0 / (R - 1.0 - math.log(R))


# ------------------------------------------------------------------------------------------- offspring fits
def fit_offspring(off: np.ndarray) -> dict:
    """R = mean offspring; k = NB dispersion MLE (K_INF when not overdispersed)."""
    off = np.asarray(off, dtype=float)
    n = len(off)
    if n == 0:
        return dict(R=np.nan, k=np.nan, n=0)
    R = off.mean()
    v = off.var(ddof=1) if n > 1 else 0.0
    if R <= 0 or v <= R * 1.0001:
        return dict(R=R, k=K_INF, n=n, var=v)

    def nll(lk):
        k = math.exp(lk)
        return -np.sum(special.gammaln(off + k) - special.gammaln(k) - special.gammaln(off + 1)
                       + k * np.log(k / (k + R)) + off * np.log(R / (k + R)))
    r = optimize.minimize_scalar(nll, bounds=(-7, math.log(K_INF)), method="bounded")
    return dict(R=R, k=float(math.exp(r.x)), n=n, var=v)


def size_mle(sizes: np.ndarray, smax: int, k: float | None = None) -> dict:
    """R (and k if None) from tree sizes alone, GW-NB truncated at smax."""
    sizes = np.asarray(sizes, dtype=int)
    cnt = np.bincount(sizes, minlength=smax + 1)[1:smax + 1]

    def nll(th):
        R = 1 / (1 + math.exp(-th[0])) * 0.999
        kk = k if k is not None else math.exp(th[1])
        p = nb_gw_pmf_trunc(R, kk, smax)
        return -np.sum(cnt * np.log(np.maximum(p, 1e-300)))
    if k is not None:
        r = optimize.minimize_scalar(lambda x: nll([x]), bounds=(-8, 8), method="bounded")
        R = 1 / (1 + math.exp(-r.x)) * 0.999
        return dict(R=R, k=k, nll=float(r.fun))
    best = None
    for k0 in (0.3, 1.0, 5.0):
        r = optimize.minimize(nll, x0=[0.0, math.log(k0)], method="Nelder-Mead", options=dict(xatol=1e-4, fatol=1e-6))
        if best is None or r.fun < best.fun:
            best = r
    return dict(R=1 / (1 + math.exp(-best.x[0])) * 0.999, k=float(math.exp(best.x[1])), nll=float(best.fun))


# ------------------------------------------------------------------------------------------- power-law fits
def _pl_logp(tau, sc, smax):
    s = np.arange(1, smax + 1, dtype=float)
    lw = -tau * np.log(s) - (s / sc if np.isfinite(sc) else 0.0)
    return lw - special.logsumexp(lw)


def powerlaw_fits(sizes: np.ndarray, smax: int) -> dict:
    """Discrete power law with exponential cutoff and pure power law on 1..smax; LR test (cutoff vs none)."""
    sizes = np.asarray(sizes, dtype=int)
    cnt = np.bincount(sizes, minlength=smax + 1)[1:smax + 1]

    def nll_c(th):
        return -np.sum(cnt * _pl_logp(th[0], math.exp(th[1]), smax))

    def nll_p(tau):
        return -np.sum(cnt * _pl_logp(tau, np.inf, smax))
    rp = optimize.minimize_scalar(nll_p, bounds=(0.01, 12), method="bounded")
    best = None
    for x0 in ([1.5, 0.0], [1.5, 2.0], [0.5, 0.5], [2.5, 3.0]):
        r = optimize.minimize(nll_c, x0=x0, method="Nelder-Mead", options=dict(xatol=1e-5, fatol=1e-7, maxiter=4000))
        if best is None or r.fun < best.fun:
            best = r
    tau_c, sc = float(best.x[0]), float(math.exp(best.x[1]))
    if best.fun > rp.fun:  # cutoff -> infinity limit
        tau_c, sc = float(rp.x), np.inf
    nllc = min(best.fun, rp.fun)
    lr = 2 * (rp.fun - nllc)
    # fixed tau = 1.5 with cutoff, and pure 1.5
    r15 = optimize.minimize_scalar(lambda x: nll_c([1.5, x]), bounds=(-5, 12), method="bounded")
    # profile CI on tau (cutoff model)
    def prof_at(tv):
        r = optimize.minimize_scalar(lambda x: nll_c([tv, x]), bounds=(-5, 12), method="bounded")
        return min(r.fun, nll_p(tv))
    taus = np.linspace(max(-3.0, tau_c - 4), tau_c + 4, 81)
    prof = np.array([prof_at(tv) for tv in taus])
    ok = prof - nllc <= 1.92
    if ok.sum() <= 3 and ok.any():   # refine around the optimum
        step = taus[1] - taus[0]
        taus = np.linspace(taus[ok].min() - step, taus[ok].max() + step, 61)
        prof = np.array([prof_at(tv) for tv in taus])
        ok = prof - nllc <= 1.92
    return dict(tau_app=float(rp.x), nll_pure=float(rp.fun), tau=tau_c, s_c=sc, nll_cut=float(nllc),
                lr_cut_vs_pure=float(lr), p_cut=float(stats.chi2.sf(lr, 1)) if lr > 0 else 1.0,
                tau_lo=float(taus[ok].min()) if ok.any() else np.nan, tau_hi=float(taus[ok].max()) if ok.any() else np.nan,
                nll_15cut=float(r15.fun), s_c_15=float(math.exp(r15.x)),
                nll_15pure=float(nll_p(1.5)),
                lr_15pure_vs_cut=float(2 * (nll_p(1.5) - nllc)))


# ------------------------------------------------------------------------------------------- finite-N GW (depletion)
def fngw_sim(R0, k, N, M=20000, seed=0):
    """Finite-population GW: each node of a generation has NB(k, mean R0*S/(N-1)) offspring, S = susceptibles left.
    Returns tree sizes (M,). Generation-synchronous; offspring capped at S."""
    rng = np.random.default_rng(seed)
    size = np.ones(M, dtype=np.int64)
    act = np.ones(M, dtype=np.int64)
    Sx = np.full(M, N - 1, dtype=np.int64)
    for _ in range(N + 1):
        live = (act > 0) & (Sx > 0)
        if not live.any():
            break
        mu = R0 * Sx[live] / max(N - 1, 1) * act[live]
        if k >= K_INF:
            o = rng.poisson(mu)
        else:
            shape = k * act[live]
            o = rng.negative_binomial(shape, shape / (shape + np.maximum(mu, 1e-12)))
        o = np.minimum(o, Sx[live])
        a2 = np.zeros(M, dtype=np.int64)
        a2[live] = o
        size += a2
        Sx -= a2
        act = a2
    return size


def fngw_calibrate(R_hat, k, N, M=8000, seed=0):
    """R0 such that the FN-GW mean tree size equals 1/(1-R_hat) (the forest identity)."""
    target = 1.0 / max(1e-9, 1.0 - R_hat)
    if target >= N:
        return np.inf
    lo, hi = 0.0, 1.0
    while fngw_sim(hi, k, N, M, seed).mean() < target and hi < 64:
        hi *= 2
    for _ in range(22):
        mid = 0.5 * (lo + hi)
        if fngw_sim(mid, k, N, M, seed).mean() < target:
            lo = mid
        else:
            hi = mid
    return 0.5 * (lo + hi)


def fngw_pmf(R_hat, k, N, M=40000, seed=1):
    R0 = fngw_calibrate(R_hat, k, N, seed=seed)
    if not np.isfinite(R0):
        p = np.zeros(N)
        p[-1] = 1
        return p, R0
    sz = fngw_sim(R0, k, N, M, seed + 7)
    return np.bincount(sz, minlength=N + 1)[1:N + 1] / M, R0


def predict_tail_fngw(R, k, N, n_trees, boot_Rk=None, B=1000, n_param=25, seed=0, thresholds=(2, 3, 5)):
    """As predict_tail, with the finite-N GW law (calibrated to the observed mean size)."""
    rng = np.random.default_rng(seed)
    p, R0 = fngw_pmf(R, k, N, seed=seed)
    cdf_ge = {x: float(p[x - 1:].sum()) for x in thresholds}
    pmfs = [p]
    if boot_Rk is not None and len(boot_Rk):
        for i in rng.integers(0, len(boot_Rk), n_param):
            pmfs.append(fngw_pmf(boot_Rk[i][0], boot_Rk[i][1], N, M=8000, seed=seed + 11 + int(i))[0])
    draws = {x: [] for x in thresholds}
    for b in range(B):
        pb = pmfs[rng.integers(len(pmfs))]
        c = rng.multinomial(n_trees, pb / pb.sum())
        for x in thresholds:
            draws[x].append(c[x - 1:].sum() / n_trees)
    band = {x: (float(np.percentile(draws[x], 5)), float(np.percentile(draws[x], 95))) for x in thresholds}
    return cdf_ge, band, R0


# ------------------------------------------------------------------------------------------- bootstraps
def cluster_boot_ratio(num: np.ndarray, den: np.ndarray, B=1000, seed=0):
    """Ratio of sums with resampling of clusters (rows = clusters)."""
    rng = np.random.default_rng(seed)
    n = len(num)
    if n == 0 or den.sum() == 0:
        return np.nan, np.nan, np.nan
    est = num.sum() / den.sum()
    idx = rng.integers(0, n, size=(B, n))
    bs = num[idx].sum(1) / np.maximum(den[idx].sum(1), 1e-12)
    return float(est), float(np.percentile(bs, 2.5)), float(np.percentile(bs, 97.5))


def predict_tail(R, k, smax, n_trees, boot_Rk=None, B=2000, seed=0, thresholds=(2, 3, 5)):
    """GW-NB predicted P(s >= x) with a 90% band from parameter uncertainty + multinomial sampling of n_trees."""
    rng = np.random.default_rng(seed)
    p = nb_gw_pmf_trunc(R, k, smax)
    cdf_ge = {x: float(p[x - 1:].sum()) for x in thresholds}
    draws = {x: [] for x in thresholds}
    for b in range(B):
        if boot_Rk is not None and len(boot_Rk):
            Rb, kb = boot_Rk[rng.integers(len(boot_Rk))]
            pb = nb_gw_pmf_trunc(Rb, kb, smax)
        else:
            pb = p
        c = rng.multinomial(n_trees, pb)
        for x in thresholds:
            draws[x].append(c[x - 1:].sum() / n_trees)
    band = {x: (float(np.percentile(draws[x], 5)), float(np.percentile(draws[x], 95))) for x in thresholds}
    return cdf_ge, band


# ------------------------------------------------------------------------------------------- jitter-null test
def jitter_test(obs: np.ndarray, pnull: np.ndarray, cluster: np.ndarray, B=2000, seed=0):
    """Excess of observed exposed fraction over the jitter null; idea-cluster bootstrap CI and one-sided p."""
    rng = np.random.default_rng(seed)
    obs = np.asarray(obs, float)
    pnull = np.asarray(pnull, float)
    if len(obs) == 0:
        return dict(n=0)
    _, inv = np.unique(cluster, return_inverse=True)
    C = inv.max() + 1
    so = np.bincount(inv, weights=obs, minlength=C)
    sp = np.bincount(inv, weights=pnull, minlength=C)
    nn = np.bincount(inv, minlength=C).astype(float)
    ex = (so.sum() - sp.sum()) / nn.sum()
    idx = rng.integers(0, C, size=(B, C))
    bs = (so[idx].sum(1) - sp[idx].sum(1)) / nn[idx].sum(1)
    se = bs.std(ddof=1)
    # Poisson-binomial null (independent adopters), for reference
    mu, var = pnull.sum(), (pnull * (1 - pnull)).sum()
    z_pb = (obs.sum() - mu) / math.sqrt(var) if var > 0 else np.nan
    return dict(n=int(len(obs)), obs_frac=float(obs.mean()), null_frac=float(pnull.mean()), excess=float(ex),
                lo=float(np.percentile(bs, 2.5)), hi=float(np.percentile(bs, 97.5)),
                p_boot=float(stats.norm.sf(ex / se)) if se > 0 else (0.0 if ex > 0 else 1.0),
                p_pb=float(stats.norm.sf(z_pb)) if np.isfinite(z_pb) else np.nan)


# ------------------------------------------------------------------------------------------- dose response
def mh_rate_ratio(a1, t1, a0, t0):
    """Mantel-Haenszel rate ratio over strata: events a, at-risk turns t at exposure 1 vs 0."""
    T = t1 + t0
    m = T > 0
    num = np.sum(a1[m] * t0[m] / T[m])
    den = np.sum(a0[m] * t1[m] / T[m])
    return num / den if den > 0 else np.nan


def rate_ratio_cond(a1, t1, a0, t0):
    """Stratified rate ratio by conditional (binomial) likelihood: in each stratum, given n = a0 + a1 events,
    a1 ~ Bin(n, psi t1 / (psi t1 + t0)). Returns (psi_hat, lo, hi) with a profile 95% CI (inf if unbounded)."""
    a1, t1, a0, t0 = (np.asarray(x, float) for x in (a1, t1, a0, t0))
    m = ((a0 + a1) > 0) & (t0 > 0) & (t1 > 0)
    a1, t1, a0, t0 = a1[m], t1[m], a0[m], t0[m]
    if len(a1) == 0 or (a1.sum() == 0 and a0.sum() == 0):
        return np.nan, np.nan, np.nan

    def ll(lp):
        lt1 = lp + np.log(t1)
        lt0 = np.log(t0)
        den = np.logaddexp(lt1, lt0)
        return np.sum(a1 * (lt1 - den) + a0 * (lt0 - den))
    grid = np.linspace(-9, 9, 721)
    L = np.array([ll(g) for g in grid])
    j = int(np.argmax(L))
    r = optimize.minimize_scalar(lambda x: -ll(x), bounds=(grid[max(j - 1, 0)], grid[min(j + 1, len(grid) - 1)]), method="bounded")
    lmax = -r.fun
    ok = L >= lmax - 1.92
    lo = grid[ok].min()
    hi = grid[ok].max()
    psi = math.exp(r.x)
    return (psi if r.x < 8.9 else np.inf, math.exp(lo) if lo > -8.9 else 0.0, math.exp(hi) if hi < 8.9 else np.inf)


def dose_response(ar, B=500, seed=0, kcol="krbin"):
    """Adoption hazard per at-risk talk turn by k (0, 1, 2, 3+).
    hr10: k>=1 vs k=0 (first exposure vs none), idea-stratified conditional MLE with profile CI. The first source
          becomes visible independently of the at-risk agent, so stratifying by idea is valid here.
    hr21, hr32: pooled ratios with idea-cluster bootstrap CIs. Stratifying by idea is biased for k>=2 (a second
          source exists only after an adoption at k=1: outcome-dependent exposure); pooling is biased upward by
          idea heterogeneity (salient ideas get more sources), so pooled hr21 <= 2.5 is conservative evidence
          against complex contagion."""
    import polars as pl
    if ar.height == 0:
        return {}
    w = ar.group_by("idea", kcol).agg(pl.col("turns").sum(), pl.col("adopts").sum())
    ideas = np.unique(w["idea"].to_numpy())
    pos = {int(x): i for i, x in enumerate(ideas)}
    T = np.zeros((len(ideas), 4))
    A = np.zeros((len(ideas), 4))
    for r in w.iter_rows(named=True):
        T[pos[r["idea"]], r[kcol]] += r["turns"]
        A[pos[r["idea"]], r[kcol]] += r["adopts"]

    def pooled(Ti, Ai):
        h = Ai.sum(0) / np.maximum(Ti.sum(0), 1)
        return h, (h[2] / h[1] if h[1] > 0 else np.nan), (h[3] / h[2] if h[2] > 0 else np.nan)
    h, r21, r32 = pooled(T, A)
    rng = np.random.default_rng(seed)
    bs = []
    for _ in range(B):
        ii = rng.integers(0, len(ideas), len(ideas))
        bs.append(pooled(T[ii], A[ii])[1:])
    bs = np.array(bs, dtype=float)

    def ci(col):
        v = bs[:, col]
        v = v[np.isfinite(v)]
        return (float(np.percentile(v, 2.5)), float(np.percentile(v, 97.5))) if len(v) > 20 else (np.nan, np.nan)
    a1 = A[:, 1:].sum(1)
    t1 = T[:, 1:].sum(1)
    hr10, lo10, hi10 = rate_ratio_cond(a1, t1, A[:, 0], T[:, 0])
    return dict(h=[float(x) for x in h], turns=[float(x) for x in T.sum(0)], adopts=[float(x) for x in A.sum(0)],
                hr21=float(r21), hr21_ci=ci(0), hr32=float(r32), hr32_ci=ci(1),
                hr10=float(hr10), hr10_ci=(float(lo10), float(hi10)),
                hr10_pooled=float((a1.sum() / max(t1.sum(), 1)) / (A[:, 0].sum() / T[:, 0].sum())) if A[:, 0].sum() > 0 else np.inf,
                n_ideas=int(len(ideas)), n_k0_adopts=float(A[:, 0].sum()))
