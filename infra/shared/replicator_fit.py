"""Estimators for repos-as-replicators (H77, H78), on the tables from replicator_hosts.py.

  poisson_order   growth order p:  R_jb ~ Poisson(C_free_jb * exp(a + p log n_jb [+ repo FE]))   (H78 primary, v3, v5, v6)
  clogit_order    choice form:     P(recruit picks j) = n_j^p / sum_k n_k^p                       (H78 v4)
  lab_order       cross-lab order: R ~ C_free_lab * exp(a + p_x log n_cross + g log(1 + n_same)) (H78 v7)
  depart_order    uncopying order q: departs ~ C_host * exp(a + (q - 1) log n)                    (H77)
  sigma_star      top repo, plateau, sigma* = ln[(J+ + 1/2)/(J- + 1/2)]                           (H77)
  resolution      selection-resolution bound s >= exp(-sigma*) on extinct rivals, permutation null (H77 D3)
  mathis_step     share of hosts on kickoff-named repos: single step vs 4.5-h exponential ramp      (A0)
  re_pool         DerSimonian-Laird random-effects pooling of unit estimates (exception (d))
Quasi-Poisson standard errors (Pearson dispersion, floored at 1).
"""
from __future__ import annotations

import math

import numpy as np
import polars as pl


# ============================================================================================ GLM
def _poisson_fit(y, X, off, max_iter=60):
    """Newton-Raphson Poisson MLE with offset. Returns beta, cov (quasi), dispersion, converged."""
    y = np.asarray(y, float)
    X = np.asarray(X, float)
    off = np.asarray(off, float)
    beta = np.zeros(X.shape[1])
    beta[0] = math.log(max(y.sum(), 0.5) / np.exp(off).sum())
    ok = False
    for _ in range(max_iter):
        eta = np.clip(off + X @ beta, -50, 50)
        mu = np.exp(eta)
        g = X.T @ (y - mu)
        H = X.T @ (X * mu[:, None]) + 1e-9 * np.eye(X.shape[1])
        try:
            step = np.linalg.solve(H, g)
        except np.linalg.LinAlgError:
            break
        # damped step
        lam = 1.0
        ll0 = np.sum(y * eta - mu)
        while lam > 1e-4:
            b1 = beta + lam * step
            e1 = np.clip(off + X @ b1, -50, 50)
            if np.sum(y * e1 - np.exp(e1)) >= ll0 - 1e-10:
                break
            lam /= 2
        beta = beta + lam * step
        if np.max(np.abs(lam * step)) < 1e-8:
            ok = True
            break
    eta = np.clip(off + X @ beta, -50, 50)
    mu = np.exp(eta)
    H = X.T @ (X * mu[:, None]) + 1e-9 * np.eye(X.shape[1])
    dof = max(len(y) - X.shape[1], 1)
    disp = max(float(np.sum((y - mu) ** 2 / np.maximum(mu, 1e-12)) / dof), 1.0)
    try:
        cov = np.linalg.inv(H) * disp
    except np.linalg.LinAlgError:
        cov = np.full((X.shape[1], X.shape[1]), np.nan)
    return beta, cov, disp, ok


def _result(est, se, n_events, n_rows, extra=None):
    out = {"est": float(est), "se": float(se), "lo": float(est - 1.96 * se), "hi": float(est + 1.96 * se),
           "n_events": int(n_events), "n_rows": int(n_rows)}
    if extra:
        out.update(extra)
    return out


def testable_order(df: pl.DataFrame, R: str, n: str = "n", min_events: int = 15) -> bool:
    d = df.filter(pl.col(n) >= 1)
    return d[R].sum() >= min_events and d.filter(pl.col(R) > 0)[n].n_unique() >= 2


def poisson_order(bins: pl.DataFrame, R: str = "R_ff", n: str = "n", offset: str = "C_free", fe: bool = False,
                  exclude_named: set | None = None) -> dict | None:
    d = bins.filter((pl.col(n) >= 1) & (pl.col(offset) > 0))
    if exclude_named:
        d = d.filter(~pl.col("repo").is_in(list(exclude_named)))
    if d.height == 0 or d[R].sum() == 0:
        return None
    y = d[R].to_numpy()
    x = np.log(d[n].to_numpy().astype(float))
    off = np.log(d[offset].to_numpy().astype(float))
    if fe:
        reps = d["repo"].to_list()
        # keep repos with >= 1 event; repos with none have FE -> -inf and carry no information about p
        keep_r = set(d.filter(pl.col(R) > 0)["repo"].to_list())
        m = np.array([r in keep_r for r in reps])
        if m.sum() < 3 or len(keep_r) < 1:
            return None
        y, x, off = y[m], x[m], off[m]
        reps = [r for r, k in zip(reps, m) if k]
        lv = sorted(set(reps))
        D = np.zeros((len(y), len(lv)))
        ix = {r: i for i, r in enumerate(lv)}
        for i, r in enumerate(reps):
            D[i, ix[r]] = 1
        if np.ptp(x) == 0:
            return None
        X = np.column_stack([D, x])
        beta, cov, disp, ok = _poisson_fit(y, X, off)
        # the first column is not an intercept here; fine for Newton
        return _result(beta[-1], math.sqrt(max(cov[-1, -1], 0)), y.sum(), len(y), {"disp": disp, "conv": ok})
    if np.ptp(x) == 0:
        return None
    X = np.column_stack([np.ones_like(x), x])
    beta, cov, disp, ok = _poisson_fit(y, X, off)
    return _result(beta[1], math.sqrt(max(cov[1, 1], 0)), y.sum(), len(y), {"disp": disp, "conv": ok, "log_c": beta[0]})


def clogit_order(cs: pl.DataFrame) -> dict | None:
    if cs.height == 0:
        return None
    from scipy.optimize import minimize_scalar
    g = cs.group_by("eid", maintain_order=True).agg(pl.col("n"), pl.col("chosen"))
    sets = [(np.log(np.array(nn, float)), np.array(ch)) for nn, ch in zip(g["n"].to_list(), g["chosen"].to_list())]
    sets = [(l, c) for l, c in sets if c.sum() == 1 and np.ptp(l) > 0]
    if len(sets) < 5:
        return None

    def nll(p):
        s = 0.0
        for l, c in sets:
            u = p * l
            s -= u[c][0] - (np.log(np.sum(np.exp(u - u.max()))) + u.max())
        return s

    r = minimize_scalar(nll, bounds=(-3, 5), method="bounded")
    p = r.x
    h = 1e-3
    d2 = (nll(p + h) - 2 * nll(p) + nll(p - h)) / h ** 2
    se = 1 / math.sqrt(d2) if d2 > 0 else float("nan")
    return _result(p, se, len(sets), len(sets))


def lab_order(lt: pl.DataFrame) -> dict | None:
    d = lt.filter((pl.col("n_cross") >= 1) & (pl.col("C_free_lab") > 0))
    if d.height == 0 or d["R"].sum() < 5:
        return None
    y = d["R"].to_numpy()
    x1 = np.log(d["n_cross"].to_numpy().astype(float))
    x2 = np.log1p(d["n_same"].to_numpy().astype(float))
    if np.ptp(x1) == 0:
        return None
    X = np.column_stack([np.ones_like(x1), x1, x2])
    beta, cov, disp, ok = _poisson_fit(y, X, np.log(d["C_free_lab"].to_numpy().astype(float)))
    return _result(beta[1], math.sqrt(max(cov[1, 1], 0)), y.sum(), len(y), {"g_same": float(beta[2]), "conv": ok})


def depart_order(bins: pl.DataFrame) -> dict | None:
    d = bins.filter((pl.col("n") >= 1) & (pl.col("C_host") > 0))
    if d.height == 0 or d["departs"].sum() == 0:
        return None
    x = np.log(d["n"].to_numpy().astype(float))
    if np.ptp(x) == 0:
        return None
    X = np.column_stack([np.ones_like(x), x])
    beta, cov, disp, ok = _poisson_fit(d["departs"].to_numpy(), X, np.log(d["C_host"].to_numpy().astype(float)))
    return _result(beta[1] + 1, math.sqrt(max(cov[1, 1], 0)), d["departs"].sum(), d.height, {"conv": ok})


# ============================================================================================ sigma*, resolution
def dense_n(bins: pl.DataFrame) -> tuple[np.ndarray, list, dict]:
    """Matrix n[repo, bin] over all bins of the table (missing = 0). Returns (N, bin list, repo index)."""
    bl = sorted(bins["bin"].unique().to_list())
    bix = {b: i for i, b in enumerate(bl)}
    rl = sorted(bins["repo"].unique().to_list())
    rix = {r: i for i, r in enumerate(rl)}
    N = np.zeros((len(rl), len(bl)))
    for r, b, n in bins.select("repo", "bin", "n").iter_rows():
        N[rix[r], bix[b]] = n
    return N, bl, rix


def all_bins(bins: pl.DataFrame, cb_bins: list) -> pl.DataFrame:
    return bins


def top_repo(bins: pl.DataFrame, n_bins_total: int) -> str | None:
    s = bins.group_by("repo").agg(pl.col("n").sum()).sort("n", descending=True)
    return s["repo"][0] if s.height else None


def sigma_star(bins: pl.DataFrame, all_bin_ids: list, top: str | None = None, R: str = "R_all", unit: str | None = None,
               min_flux: int = 8) -> dict | None:
    """Top repo T (largest call-clock mean n), plateau = bins after n_T first reaches ceil(0.8 max) with n_T >= 0.5 max.
    J+ = recruits into T, J- = switch-outs, D = expiries/leaves, on the plateau (optionally restricted to one unit)."""
    if top is None:
        top = top_repo(bins, len(all_bin_ids))
    if top is None:
        return None
    t = bins.filter(pl.col("repo") == top).select("bin", "unit", "n", R, "departs", "expires")
    full = pl.DataFrame({"bin": all_bin_ids}).join(t, on="bin", how="left").sort("bin")
    nn = full["n"].fill_null(0).to_numpy()
    if nn.max() < 1:
        return None
    mx = nn.max()
    first = int(np.argmax(nn >= math.ceil(0.8 * mx)))
    plat = np.zeros(len(nn), bool)
    plat[first:] = nn[first:] >= 0.5 * mx
    full = full.with_columns(pl.Series("plat", plat))
    p = full.filter(pl.col("plat"))
    if unit is not None:
        p = p.filter(pl.col("unit") == unit)
    jp = int(p[R].fill_null(0).sum())
    jm = int(p["departs"].fill_null(0).sum())
    dd = int(p["expires"].fill_null(0).sum())
    s = math.log((jp + 0.5) / (jm + 0.5))
    se = math.sqrt(1 / (jp + 0.5) + 1 / (jm + 0.5))
    return {"top": top, "est": s, "se": se, "lo": s - 1.96 * se, "hi": s + 1.96 * se, "J_plus": jp, "J_minus": jm, "D": dd,
            "plateau_bins": int(p.height), "n_max": int(mx), "testable": (jp + jm) >= min_flux,
            "sigma_all": math.log((jp + 0.5) / (jm + dd + 0.5))}


def fitness(bins: pl.DataFrame, R: str = "R_ff", nmax: int = 2) -> pl.DataFrame:
    d = bins.filter((pl.col("n") >= 1) & (pl.col("n") <= nmax))
    return (d.group_by("repo").agg(pl.col(R).sum().alias("rec"), (pl.col("n") * pl.col("C_free")).sum().alias("expo"))
            .with_columns((1000 * pl.col("rec") / pl.col("expo")).alias("f")))


def resolution(bins: pl.DataFrame, all_bin_ids: list, sig: dict, R: str = "R_ff", n_perm: int = 999, seed: int = 0) -> dict:
    top = sig["top"]
    N, bl, rix = dense_n(bins)
    tail = max(1, int(round(0.2 * len(all_bin_ids))))
    # n matrix over all bins
    allix = {b: i for i, b in enumerate(all_bin_ids)}
    M = np.zeros((len(rix), len(all_bin_ids)))
    for r, i in rix.items():
        for j, b in enumerate(bl):
            M[i, allix[b]] = N[i, j]
    top_alive = M[rix[top], -1] >= 1
    F = fitness(bins, R)
    f = dict(zip(F["repo"].to_list(), F["f"].to_list()))
    rec = dict(zip(F["repo"].to_list(), F["rec"].to_list()))
    fT = f.get(top)
    if fT is None or not np.isfinite(fT) or fT <= 0:
        F3 = fitness(bins, R, nmax=3)
        fT = dict(zip(F3["repo"].to_list(), F3["f"].to_list())).get(top)
    if fT is None or not np.isfinite(fT) or fT <= 0:
        F9 = fitness(bins, R, nmax=999)
        fT = dict(zip(F9["repo"].to_list(), F9["f"].to_list())).get(top)
    testable = [r for r in rix if r != top and rec.get(r, 0) >= 1]
    extinct = {r: bool(M[rix[r]].max() >= 1 and M[rix[r], -tail:].max() == 0) for r in testable}
    # frustrated herds: reached >= 3 hosts, then extinct
    frustrated = [r for r in rix if r != top and M[rix[r]].max() >= 3 and M[rix[r], -tail:].max() == 0]
    thr = math.exp(-sig["est"])
    out = {"fT": fT, "n_testable": len(testable), "n_extinct": int(sum(extinct.values())), "threshold_s": thr,
           "top_alive": bool(top_alive), "n_frustrated": len(frustrated)}
    if not fT or not top_alive:
        out.update({"frac": None, "p_perm": None})
        return out
    s = {r: 1 - f[r] / fT for r in testable}
    ex = [r for r in testable if extinct[r]]
    if not ex:
        out.update({"frac": None, "p_perm": None, "surv_below": None})
        return out
    obs = float(np.mean([s[r] >= thr for r in ex]))
    vals = np.array([f[r] for r in testable])
    rng = np.random.default_rng(seed)
    exm = np.array([extinct[r] for r in testable])
    cnt = 0
    for _ in range(n_perm):
        pv = rng.permutation(vals)
        fr = np.mean((1 - pv[exm] / fT) >= thr)
        cnt += fr >= obs
    surv = [r for r in testable if not extinct[r]]
    out.update({"frac": obs, "p_perm": (cnt + 1) / (n_perm + 1),
                "surv_below": float(np.mean([s[r] < thr for r in surv])) if surv else None,
                "s_extinct": [round(s[r], 3) for r in ex]})
    return out


# ============================================================================================ Mathis A0
def mathis_step(bins: pl.DataFrame, named: set, t_active_h: dict, min_hosts: int = 2, tau_h: float = 4.5,
                n_surr: int = 200) -> dict | None:
    """m(b) = share of hosts on kickoff-named repos. Step (one change point) vs exponential ramp with tau fixed."""
    g = bins.group_by("bin").agg(pl.col("n").sum().alias("tot"),
                                 pl.col("n").filter(pl.col("repo").is_in(list(named))).sum().alias("nm"),
                                 pl.col("births").sum().alias("births"), pl.col("C").first())
    g = g.filter(pl.col("tot") >= min_hosts).sort("bin")
    if g.height < 8 or not named:
        return None
    m = (g["nm"] / g["tot"]).to_numpy()
    t = np.array([t_active_h[b] for b in g["bin"].to_list()])
    n = len(m)
    x = np.exp(-(t - t[0]) / tau_h)
    X = np.column_stack([np.ones(n), x])

    def dbic(y):
        c1 = np.cumsum(y)
        c2 = np.cumsum(y ** 2)
        ks = np.arange(3, n - 2)
        s1, q1 = c1[ks - 1], c2[ks - 1]
        s2, q2 = c1[-1] - s1, c2[-1] - q1
        sse = (q1 - s1 ** 2 / ks) + (q2 - s2 ** 2 / (n - ks))
        j = int(np.argmin(sse))
        cf, *_ = np.linalg.lstsq(X, y, rcond=None)
        sr = float(np.sum((y - X @ cf) ** 2))
        bs = n * math.log(max(sse[j], 1e-12) / n) + 3 * math.log(n)
        br = n * math.log(max(sr, 1e-12) / n) + 2 * math.log(n)
        return br - bs, int(ks[j]), cf

    d_obs, k, coef = dbic(m)
    # A2 (post hoc) calibrated null: the ramp fit plus AR(1) residuals with the observed lag-1 autocorrelation
    resid = m - X @ coef
    phi = float(np.corrcoef(resid[:-1], resid[1:])[0, 1]) if n > 3 and resid.std() > 0 else 0.0
    phi = min(max(phi, 0.0), 0.995)
    sd = resid.std() * math.sqrt(max(1 - phi ** 2, 1e-6))
    rng = np.random.default_rng(7)
    ds = []
    for _ in range(n_surr):
        e = np.empty(n)
        e[0] = rng.normal(0, resid.std())
        z = rng.normal(0, sd, n)
        for i in range(1, n):
            e[i] = phi * e[i - 1] + z[i]
        ds.append(dbic(X @ coef + e)[0])
    ds = np.array(ds)
    br = (g["births"] / g["C"] * 1000).to_numpy()
    lo, hi = max(0, k - 1), min(n, k + 2)
    peak = br[lo:hi].max()
    return {"dBIC": d_obs, "step": d_obs >= 6, "ramp_preferred": d_obs <= -2, "ar1_phi": phi,
            "p_surrogate": float((np.sum(ds >= d_obs) + 1) / (len(ds) + 1)), "dBIC_surr_q95": float(np.quantile(ds, 0.95)),
            "step_calibrated": bool(np.mean(ds >= d_obs) < 0.05),
            "k_bin": int(g["bin"][k]), "t_step_h": float(t[k] - t[0]), "m_before": float(m[:k].mean()),
            "m_after": float(m[k:].mean()), "birth_peak_ratio_median": float(peak / np.median(br)) if np.median(br) > 0 else None,
            "birth_peak_ratio_mean": float(peak / br.mean()) if br.mean() > 0 else None, "n_bins": n,
            "I_bits_mean": float(np.mean([_mi(mm) for mm in m]))}


def _mi(m):
    """I(label; named) bits for a bin, when label is a deterministic function of repo: H(named) = binary entropy of m."""
    if m <= 0 or m >= 1:
        return 0.0
    return float(-(m * math.log2(m) + (1 - m) * math.log2(1 - m)))


# ============================================================================================ pooling
def re_pool(est: list, se: list) -> dict | None:
    e = np.array([x for x, s in zip(est, se) if s is not None and np.isfinite(s) and s > 0])
    s = np.array([s for x, s in zip(est, se) if s is not None and np.isfinite(s) and s > 0])
    if len(e) == 0:
        return None
    if len(e) == 1:
        return {"est": float(e[0]), "se": float(s[0]), "lo": float(e[0] - 1.96 * s[0]), "hi": float(e[0] + 1.96 * s[0]),
                "tau2": 0.0, "k": 1}
    w = 1 / s ** 2
    mf = np.sum(w * e) / np.sum(w)
    Q = np.sum(w * (e - mf) ** 2)
    c = np.sum(w) - np.sum(w ** 2) / np.sum(w)
    tau2 = max(0.0, (Q - (len(e) - 1)) / c) if c > 0 else 0.0
    wr = 1 / (s ** 2 + tau2)
    m = np.sum(wr * e) / np.sum(wr)
    se_m = math.sqrt(1 / np.sum(wr))
    return {"est": float(m), "se": se_m, "lo": float(m - 1.96 * se_m), "hi": float(m + 1.96 * se_m), "tau2": float(tau2),
            "k": int(len(e))}


# ============================================================================================ period wrappers
def period_order(bins: pl.DataFrame, R: str = "R_ff", n: str = "n", offset: str = "C_free", fe: bool = False,
                 min_unit: int = 5, exclude: set | None = None) -> dict:
    """Per-unit growth order where a unit has >= min_unit events and >= 2 distinct n; random-effects pooled period value
    (exception (d)). Also the single period fit with unit intercepts absent (reported, not the primary)."""
    units = {}
    for (u,), g in bins.group_by(["unit"], maintain_order=True):
        d = g.filter(pl.col(n) >= 1)
        if exclude:
            d = d.filter(~pl.col("repo").is_in(list(exclude)))
        if d[R].sum() >= min_unit and d.filter(pl.col(R) > 0)[n].n_unique() >= 2:
            r = poisson_order(d, R=R, n=n, offset=offset, fe=fe)
            if r is not None and np.isfinite(r["se"]) and r["se"] > 0:
                units[u] = r
    pooled = re_pool([v["est"] for v in units.values()], [v["se"] for v in units.values()]) if units else None
    whole = poisson_order(bins, R=R, n=n, offset=offset, fe=fe, exclude_named=exclude)
    d = bins.filter(pl.col(n) >= 1)
    if exclude:
        d = d.filter(~pl.col("repo").is_in(list(exclude)))
    test = testable_order(d, R, n)
    return {"units": units, "pooled": pooled, "whole": whole, "testable": bool(test), "n_events": int(d[R].sum())}
