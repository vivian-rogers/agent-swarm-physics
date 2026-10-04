"""H68 estimators: per-agent dilution exponents (cloglog uptake model) and population mixture tests.

Uptake model (H18 M_pow with an agent index):  P(r = 1) = 1 - exp(-exp(a_g + log n - beta * log k + gamma * m + ...))
with group propensities a_g (agent-day) ridge-penalized toward a free mean a0 (sigma = 1.5, as H18).
Fitted by penalized Newton (exact Hessian). All code is H68's own (no imports from other hypothesis folders).
"""
from __future__ import annotations

import math

import numpy as np
from scipy import optimize, stats

SIGMA = 1.5
ETA_LO, ETA_HI = -30.0, 6.0


# ============================================================================ cloglog with group effects
def _terms(eta, y):
    """log-lik, d/deta, -d2/deta2 for the cloglog Bernoulli."""
    eta = np.clip(eta, ETA_LO, ETA_HI)
    mu = np.exp(eta)
    em1 = np.expm1(mu)
    ll = np.where(y, np.log(-np.expm1(-mu)), -mu)
    g1 = mu / em1  # y = 1 gradient
    g = np.where(y, g1, -mu)
    # y = 1 curvature: mu * (e^mu - 1 - mu e^mu) / (e^mu - 1)^2  (negative); stable form
    with np.errstate(over="ignore", invalid="ignore"):
        c1 = mu * (em1 - mu * (em1 + 1.0)) / (em1 * em1)
    c1 = np.where(np.isfinite(c1), c1, 0.0)
    w = np.where(y, -c1, mu)
    return ll, g, np.maximum(w, 1e-12)


def fit_cll(y, X, offset, groups, sigma=SIGMA, max_iter=60, tol=1e-8, start=None):
    """Penalized Newton fit. y bool (n,), X (n, p) covariates, offset (n,), groups int (n,) in 0..G-1.

    Parameters: a_g (G), a0, b (p). Penalty sum_g (a_g - a0)^2 / (2 sigma^2).
    Returns dict(b, se, a, a0, ll (unpenalized), pll, converged, cov_b).
    """
    y = np.asarray(y, dtype=bool)
    X = np.asarray(X, dtype=float).reshape(len(y), -1)
    off = np.asarray(offset, dtype=float)
    gr = np.asarray(groups, dtype=np.int64)
    G = int(gr.max()) + 1
    p = X.shape[1]
    lam = 1.0 / sigma ** 2
    rate = max(y.mean(), 1e-4)
    a = np.full(G, math.log(-math.log(1 - min(rate, 0.9))) - float(np.mean(off)))
    a0 = float(a[0])
    b = np.zeros(p) if start is None else np.asarray(start, dtype=float).copy()

    def pll_of(a, a0, b):
        eta = a[gr] + off + X @ b
        ll, _, _ = _terms(eta, y)
        return ll.sum() - 0.5 * lam * np.sum((a - a0) ** 2), ll.sum()

    cur, _ = pll_of(a, a0, b)
    conv = False
    for _ in range(max_iter):
        eta = a[gr] + off + X @ b
        _, g, w = _terms(eta, y)
        # gradient
        ga = np.bincount(gr, weights=g, minlength=G) - lam * (a - a0)
        ga0 = lam * np.sum(a - a0)
        gb = X.T @ g
        # negative Hessian
        K = G + 1 + p
        H = np.zeros((K, K))
        H[np.arange(G), np.arange(G)] = np.bincount(gr, weights=w, minlength=G) + lam
        H[:G, G] = H[G, :G] = -lam
        H[G, G] = lam * G
        WX = X * w[:, None]
        cross = np.zeros((G, p))
        for j in range(p):
            cross[:, j] = np.bincount(gr, weights=WX[:, j], minlength=G)
        H[:G, G + 1:] = cross
        H[G + 1:, :G] = cross.T
        H[G + 1:, G + 1:] = X.T @ WX
        grad = np.concatenate([ga, [ga0], gb])
        try:
            step = np.linalg.solve(H, grad)
        except np.linalg.LinAlgError:
            step = np.linalg.lstsq(H, grad, rcond=None)[0]
        t = 1.0
        while t > 1e-4:
            na, na0, nb = a + t * step[:G], a0 + t * step[G], b + t * step[G + 1:]
            new, _ = pll_of(na, na0, nb)
            if new >= cur - 1e-10:
                break
            t *= 0.5
        a, a0, b = na, na0, nb
        dif = new - cur
        cur = new
        if abs(dif) < tol and np.max(np.abs(t * step)) < 1e-5:
            conv = True
            break
    # final Hessian for SEs
    eta = a[gr] + off + X @ b
    _, g, w = _terms(eta, y)
    K = G + 1 + p
    H = np.zeros((K, K))
    H[np.arange(G), np.arange(G)] = np.bincount(gr, weights=w, minlength=G) + lam
    H[:G, G] = H[G, :G] = -lam
    H[G, G] = lam * G
    WX = X * w[:, None]
    cross = np.zeros((G, p))
    for j in range(p):
        cross[:, j] = np.bincount(gr, weights=WX[:, j], minlength=G)
    H[:G, G + 1:] = cross
    H[G + 1:, :G] = cross.T
    H[G + 1:, G + 1:] = X.T @ WX
    try:
        cov = np.linalg.inv(H)
    except np.linalg.LinAlgError:
        cov = np.linalg.pinv(H)
    cb = cov[G + 1:, G + 1:]
    pll, ll = pll_of(a, a0, b)
    return dict(b=b, se=np.sqrt(np.maximum(np.diag(cb), 0)), cov_b=cb, a=a, a0=a0, ll=ll, pll=pll, converged=conv)


def design(df, engaged=False):
    """Covariates for the uptake model: [-log k, mention (, engaged)]; offset log n."""
    cols = [-df["logk"].to_numpy(), df["ment"].to_numpy().astype(float)]
    if engaged:
        cols.append(df["engaged"].to_numpy().astype(float))
    return np.column_stack(cols), np.log(df["n"].to_numpy().astype(float))


def agent_fit(df, resp="resp", engaged=False):
    """Per-agent exponent with day propensities. df: one agent's units (polars)."""
    X, off = design(df, engaged)
    y = df[resp].to_numpy()
    r = fit_cll(y, X, off, df["day"].to_numpy())
    return dict(beta=float(r["b"][0]), se=float(r["se"][0]), gamma=float(r["b"][1]), ll=float(r["ll"]),
                converged=bool(r["converged"]), n=int(len(y)), n_resp=int(y.sum()))


def eligible(df, resp="resp", min_units=150, min_resp=15, min_sd=0.3):
    """Eligibility for a per-agent fit: units, responses and within-agent-day spread of log k."""
    if df.height < min_units or int(df[resp].sum()) < min_resp:
        return False
    lk = df["logk"].to_numpy()
    dd = df["day"].to_numpy()
    m = np.bincount(dd, weights=lk) / np.maximum(np.bincount(dd), 1)
    sd = float(np.sqrt(np.mean((lk - m[dd]) ** 2)))
    return sd >= min_sd


# ============================================================================ population layer
def _npdf_log(x, m, v):
    return -0.5 * (np.log(2 * np.pi * v) + (x - m) ** 2 / v)


def fit_U(b, s):
    """Heteroscedastic random effects b_i ~ N(mu, tau^2 + s_i^2). Returns mu, tau, ll (profile over tau)."""
    b, s = np.asarray(b, float), np.asarray(s, float)
    s2 = s ** 2

    def prof(lt):
        v = np.exp(2 * lt) + s2
        mu = np.sum(b / v) / np.sum(1 / v)
        return -np.sum(_npdf_log(b, mu, v)), mu
    r = optimize.minimize_scalar(lambda lt: prof(lt)[0], bounds=(np.log(1e-4), np.log(3.0)), method="bounded",
                                 options=dict(xatol=1e-6))
    lt = r.x
    f0, mu0 = prof(np.log(1e-4))
    if f0 <= r.fun:
        lt, mu, f = np.log(1e-4), mu0, f0
    else:
        f, mu = prof(lt)
    tau = float(np.exp(lt))
    if tau < 2e-4:
        tau = 0.0
    return dict(mu=float(mu), tau=tau, ll=float(-f))


def tau_profile_ci(b, s, level=0.95):
    b, s = np.asarray(b, float), np.asarray(s, float)
    full = fit_U(b, s)
    crit = stats.chi2.ppf(level, 1) / 2

    def prof(tau):
        v = tau ** 2 + s ** 2
        mu = np.sum(b / v) / np.sum(1 / v)
        return np.sum(_npdf_log(b, mu, v))
    grid = np.linspace(0, 1.5, 601)
    pl_ = np.array([prof(t) for t in grid])
    ok = grid[pl_ >= full["ll"] - crit]
    return float(ok.min()), float(ok.max())


def _m2_nll_grad(par, b, s2):
    m1, m2, lt, lp = par
    e2 = np.exp(2 * lt)
    v = e2 + s2
    pi = 1 / (1 + np.exp(-lp))
    pi = min(max(pi, 1e-9), 1 - 1e-9)
    d1, d2 = b - m1, b - m2
    base = -0.5 * np.log(2 * np.pi * v)
    l1 = np.log(pi) + base - 0.5 * d1 ** 2 / v
    l2 = np.log(1 - pi) + base - 0.5 * d2 ** 2 / v
    ll = np.logaddexp(l1, l2)
    r1 = np.exp(l1 - ll)
    r2 = 1 - r1
    g_m1 = np.sum(r1 * d1 / v)
    g_m2 = np.sum(r2 * d2 / v)
    dl1 = -0.5 / v + 0.5 * d1 ** 2 / v ** 2
    dl2 = -0.5 / v + 0.5 * d2 ** 2 / v ** 2
    g_lt = np.sum((r1 * dl1 + r2 * dl2) * 2 * e2)
    g_lp = np.sum(r1 - pi)
    return -np.sum(ll), -np.array([g_m1, g_m2, g_lt, g_lp])


def fit_M2(b, s, starts=8, rng=None):
    """Two Gaussians, common tau, free means and weight: b_i ~ pi N(m1, tau^2+s^2) + (1-pi) N(m2, tau^2+s^2)."""
    b, s = np.asarray(b, float), np.asarray(s, float)
    s2 = s ** 2
    rng = np.random.default_rng(0) if rng is None else rng
    qs = np.quantile(b, [0.1, 0.25, 0.5, 0.75, 0.9])
    inits = [(qs[0], qs[4]), (qs[1], qs[3]), (0.0, 1.0), (qs[0], qs[2]), (qs[2], qs[4])]
    best = None
    bnds = [(-5, 5), (-5, 5), (np.log(1e-4), np.log(3.0)), (-8, 8)]
    for i in range(starts):
        if i < len(inits):
            m1, m2 = inits[i]
        else:
            m1, m2 = np.sort(rng.choice(b, 2, replace=False))
        for lt0 in (np.log(0.05), np.log(0.25)):
            r = optimize.minimize(_m2_nll_grad, [m1, m2, lt0, 0.0], args=(b, s2), jac=True, method="L-BFGS-B",
                                  bounds=bnds)
            if best is None or r.fun < best.fun:
                best = r
    m1, m2, lt, lp = best.x
    pi = 1 / (1 + np.exp(-lp))
    if m1 > m2:
        m1, m2, pi = m2, m1, 1 - pi
    v = np.exp(2 * lt) + s2
    pi = min(max(pi, 1e-9), 1 - 1e-9)
    l1 = np.log(pi) + _npdf_log(b, m1, v)
    l2 = np.log(1 - pi) + _npdf_log(b, m2, v)
    post_hi = np.exp(l2 - np.logaddexp(l1, l2))
    return dict(m_lo=float(m1), m_hi=float(m2), tau=float(np.exp(lt)), pi_lo=float(pi), ll=float(-best.fun),
                n_hi=int(np.sum(post_hi >= 0.5)), n_lo=int(np.sum(post_hi < 0.5)), post_hi=post_hi)


def fit_H68(b, s, tau_max=0.15):
    """H68 literal: modes fixed at 0 and 1, common tau_w <= tau_max, free weight."""
    b, s = np.asarray(b, float), np.asarray(s, float)

    def nll(par):
        tw, lp = par
        tw = min(abs(tw), tau_max)
        v = tw ** 2 + s ** 2
        pi = min(max(1 / (1 + np.exp(-lp)), 1e-9), 1 - 1e-9)
        return -np.sum(np.logaddexp(np.log(pi) + _npdf_log(b, 1.0, v), np.log(1 - pi) + _npdf_log(b, 0.0, v)))
    best = None
    for tw0 in (0.02, 0.08, 0.14):
        for lp0 in (-1.0, 0.0, 1.0):
            r = optimize.minimize(nll, [tw0, lp0], method="Nelder-Mead", options=dict(maxiter=3000))
            if best is None or r.fun < best.fun:
                best = r
    tw, lp = best.x
    return dict(tau_w=float(min(abs(tw), tau_max)), pi_thin=float(1 / (1 + np.exp(-lp))), ll=float(-best.fun))


def mixture_test(b, s, B=200, seed=0):
    """LR = 2(ll_M2 - ll_U); parametric bootstrap p under the fitted U."""
    b, s = np.asarray(b, float), np.asarray(s, float)
    rng = np.random.default_rng(seed)
    U = fit_U(b, s)
    M = fit_M2(b, s, rng=rng)
    lr = max(0.0, 2 * (M["ll"] - U["ll"]))
    null = []
    for _ in range(B):
        bb = U["mu"] + rng.normal(0, np.sqrt(U["tau"] ** 2 + s ** 2))
        u = fit_U(bb, s)
        m = fit_M2(bb, s, starts=3, rng=rng)
        null.append(max(0.0, 2 * (m["ll"] - u["ll"])))
    null = np.array(null)
    p = (1 + np.sum(null >= lr - 1e-9)) / (B + 1)
    H = fit_H68(b, s)
    return dict(U=U, M2={k: v for k, v in M.items() if k != "post_hi"}, H68=H, lr=lr, p=float(p),
                dll_H68_U=float(H["ll"] - U["ll"]), post_hi=M["post_hi"].tolist())


def p1_pass(mt, alpha=0.05):
    m = mt["M2"]
    return bool(mt["p"] < alpha and 0.7 <= m["m_hi"] <= 1.3 and -0.3 <= m["m_lo"] <= 0.3 and m["n_hi"] >= 2
                and m["n_lo"] >= 2)


# ============================================================================ family and trait
def lab_share(df, n_perm=2000, seed=0, tau2=None):
    """Weighted share of deconvolved between-agent variance explained by lab, with period fixed effects.

    df: polars with columns agent, period, lab, beta, se. Permutation: agent -> lab map permuted (agents whole)."""
    rng = np.random.default_rng(seed)
    per = np.unique(df["period"].to_numpy(), return_inverse=True)[1]
    tau2 = 0.0 if tau2 is None else tau2
    se = df["se"].to_numpy()
    w = 1.0 / (se ** 2 + tau2)
    y = df["beta"].to_numpy()
    agents = df["agent"].to_numpy()
    labs = df["lab"].to_numpy()
    ua = np.unique(agents)
    amap = dict(zip(agents.tolist(), labs.tolist()))
    labs_of_agent = np.array([amap[a] for a in ua.tolist()])
    P = np.eye(per.max() + 1)[per]
    sw = np.sqrt(w)

    def rss(codes=None):
        Xd = P if codes is None else np.hstack([P, np.eye(codes.max() + 1)[codes][:, 1:]])
        coef = np.linalg.lstsq(Xd * sw[:, None], y * sw, rcond=None)[0]
        r = y - Xd @ coef
        return float(np.sum(w * r ** 2))
    rss0 = rss()
    lab_codes = np.unique(labs, return_inverse=True)[1]
    expl = rss0 - rss(lab_codes)
    samp = float(np.sum(w * se ** 2)) * (1 - (per.max() + 1) / len(y))
    true_tot = max(rss0 - samp, 1e-12)
    eta2 = min(expl / true_tot, 1.0)
    null = []
    aidx = np.searchsorted(ua, agents)
    for _ in range(n_perm):
        perm_labs = rng.permutation(labs_of_agent)[aidx]
        null.append(rss0 - rss(np.unique(perm_labs, return_inverse=True)[1]))
    null = np.array(null)
    p = (1 + np.sum(null >= expl - 1e-12)) / (n_perm + 1)
    return dict(eta2=float(eta2), eta2_raw=float(expl / rss0), p=float(p), n_agent_periods=int(len(y)),
                n_agents=int(len(ua)), n_labs=int(len(set(labs_of_agent.tolist()))))


def trait_icc(df, n_boot=1000, seed=0):
    """Agent random effect vs agent x period: beta_ip = mu_p + a_i + e_ip + noise(se). Method of moments.

    var(a) = mean over agents with >= 2 periods of the mean cross-product of centered estimates across their periods;
    total true variance = mean centered square - mean se^2. ICC = var(a) / total. Bootstrap over agents."""
    import polars as pl
    d = df.with_columns((pl.col("beta") - pl.col("beta").mean().over("period")).alias("c"))
    rng = np.random.default_rng(seed)
    groups = {int(a): (g["c"].to_numpy(), g["se"].to_numpy()) for (a,), g in d.group_by(["agent"])}
    keys = sorted(groups)
    multi = [a for a in keys if len(groups[a][0]) >= 2]

    def est(agent_list):
        cps, sq, se2 = [], [], []
        for a in agent_list:
            c, s = groups[a]
            sq.extend(c ** 2)
            se2.extend(s ** 2)
            if len(c) >= 2:
                cps.append((np.sum(c) ** 2 - np.sum(c ** 2)) / (len(c) * (len(c) - 1)))
        va = float(np.mean(cps)) if cps else float("nan")
        tot = float(np.mean(sq) - np.mean(se2))
        return va, tot
    va, tot = est(keys)
    icc = va / tot if tot > 0 else float("nan")
    bs = []
    for _ in range(n_boot):
        v, t = est(list(rng.choice(keys, len(keys), replace=True)))
        if t > 0 and np.isfinite(v):
            bs.append(v / t)
    lo, hi = (np.percentile(bs, [2.5, 97.5]) if bs else (np.nan, np.nan))
    return dict(var_agent=va, var_true_total=tot, icc=float(icc), ci=[float(lo), float(hi)], n_agents_multi=len(multi),
                n_agents=len(keys))


def thread_concentration(df, resp="resp", min_resp_day=3):
    """Mean normalized Herfindahl of addressed senders per agent-day (pending scored senders as the support)."""
    out = []
    for (day,), g in df.group_by(["day"]):
        S = g["sender"].n_unique()
        r = g.filter(g[resp])
        if S < 2 or r.height < min_resp_day:
            continue
        c = r.group_by("sender").len()["len"].to_numpy().astype(float)
        H = np.sum((c / c.sum()) ** 2)
        out.append(((H - 1 / S) / (1 - 1 / S), r.height))
    if not out:
        return float("nan"), 0
    v = np.array(out)
    return float(np.average(v[:, 0], weights=v[:, 1])), int(len(out))


def floor_vs_pow(df, resp="resp", rhos=(0.0, 0.005, 0.01, 0.02, 0.05, 0.1, 0.2, 0.5, 1.0, 3.0, 10.0)):
    """Per-agent shape: M_pow (k^-beta) vs M_floor (1/k + rho), both one shape parameter."""
    y = df[resp].to_numpy()
    gr = df["day"].to_numpy()
    k = np.exp(df["logk"].to_numpy())
    m = df["ment"].to_numpy().astype(float)
    off_n = np.log(df["n"].to_numpy().astype(float))
    best = None
    for rho in rhos:
        r = fit_cll(y, m[:, None], off_n + np.log(1.0 / k + rho), gr)
        if best is None or r["ll"] > best[1]:
            best = (rho, r["ll"])
    X, off = design(df)
    rp = fit_cll(y, X, off, gr)
    return dict(rho=best[0], ll_floor=best[1], ll_pow=float(rp["ll"]), dll_floor_pow=float(best[1] - rp["ll"]))
