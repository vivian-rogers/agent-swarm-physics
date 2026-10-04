"""Fixed-effect binary GLMs (logit, cloglog) and OLS with a day-block bootstrap, in plain numpy.

Written for H72 (two-clock escape hazard at idle gates) and H60 (nudge response surface); usable by any discrete-time
hazard on call or gate rows. The environment has no statsmodels, so these are small, tested Fisher-scoring fits.

  design(cov, names, agent)            -> X, names (intercept + covariates + agent dummies, first agent dropped)
  fit_binary(X, y, link="logit")       -> dict(beta, cov, ll, converged)
  fit_ols(X, y)                        -> dict(beta, cov, rss)
  loglik_binary(X, y, beta, link)      -> per-row log-likelihood
  block_resample(day_codes, rng)       -> row index of a day-block bootstrap draw
  interleaved_folds(day_codes, k)      -> fold id per row (days sorted, assigned round-robin)

Tests: `uv run python infra/shared/hazard_fe.py --test` (or `--verify`) recovers planted coefficients on simulated data.
"""
from __future__ import annotations

import numpy as np

EPS = 1e-12


def design(cov: np.ndarray, names: list[str], agent: np.ndarray | None = None):
    """Intercept + covariates + agent dummies (first agent level dropped)."""
    n = cov.shape[0]
    cols = [np.ones((n, 1)), cov]
    nm = ["const"] + list(names)
    if agent is not None:
        lev = np.unique(agent)
        if len(lev) > 1:
            D = (agent[:, None] == lev[None, 1:]).astype(float)
            cols.append(D)
            nm += [f"agent_{int(a)}" for a in lev[1:]]
    return np.hstack(cols), nm


def _mu(eta, link):
    if link == "logit":
        mu = 1.0 / (1.0 + np.exp(-eta))
        dmu = mu * (1 - mu)
    elif link == "cloglog":
        e = np.exp(np.clip(eta, -30, 30))
        mu = 1.0 - np.exp(-e)
        dmu = e * np.exp(-e)
    else:
        raise ValueError(link)
    return np.clip(mu, 1e-10, 1 - 1e-10), np.maximum(dmu, 1e-12)


def loglik_binary(X, y, beta, link="logit"):
    mu, _ = _mu(X @ beta, link)
    return y * np.log(mu) + (1 - y) * np.log(1 - mu)


def fit_binary(X, y, link="logit", beta0=None, maxit=60, tol=1e-8, ridge=1e-6, w=None):
    """Fisher scoring; tiny ridge on non-intercept terms for stability. Returns beta, cov (inverse information)."""
    n, p = X.shape
    w = np.ones(n) if w is None else w
    beta = np.zeros(p) if beta0 is None else beta0.copy()
    if beta0 is None:
        ybar = np.clip(np.average(y, weights=w), 1e-3, 1 - 1e-3)
        beta[0] = np.log(ybar / (1 - ybar)) if link == "logit" else np.log(-np.log(1 - ybar))
    R = np.full(p, ridge)
    R[0] = 0.0
    conv = False
    ll_old = -np.inf
    for _ in range(maxit):
        eta = X @ beta
        mu, dmu = _mu(eta, link)
        W = w * dmu ** 2 / (mu * (1 - mu))
        grad = X.T @ (w * (y - mu) * dmu / (mu * (1 - mu))) - R * beta
        H = (X * W[:, None]).T @ X + np.diag(R)
        try:
            step = np.linalg.solve(H, grad)
        except np.linalg.LinAlgError:
            step = np.linalg.lstsq(H, grad, rcond=None)[0]
        # step halving on the log-likelihood
        t = 1.0
        for _h in range(20):
            bn = beta + t * step
            ll = float(np.sum(w * loglik_binary(X, y, bn, link))) - 0.5 * float(np.sum(R * bn ** 2))
            if ll >= ll_old - 1e-9:
                break
            t /= 2
        beta = bn
        if abs(ll - ll_old) < tol * (1 + abs(ll)) and np.max(np.abs(t * step)) < 1e-6:
            conv = True
            ll_old = ll
            break
        ll_old = ll
    eta = X @ beta
    mu, dmu = _mu(eta, link)
    W = w * dmu ** 2 / (mu * (1 - mu))
    H = (X * W[:, None]).T @ X + np.diag(R)
    try:
        cov = np.linalg.inv(H)
    except np.linalg.LinAlgError:
        cov = np.linalg.pinv(H)
    return {"beta": beta, "cov": cov, "ll": float(np.sum(w * loglik_binary(X, y, beta, link))), "converged": conv}


def fit_ols(X, y, w=None):
    w = np.ones(len(y)) if w is None else w
    Xw = X * w[:, None]
    XtX = Xw.T @ X + np.diag(np.r_[0.0, np.full(X.shape[1] - 1, 1e-8)])
    beta = np.linalg.solve(XtX, Xw.T @ y)
    r = y - X @ beta
    dof = max(len(y) - X.shape[1], 1)
    s2 = float(np.sum(w * r ** 2) / dof)
    cov = s2 * np.linalg.inv(XtX)
    return {"beta": beta, "cov": cov, "rss": float(np.sum(w * r ** 2)), "s2": s2}


def block_resample(day_codes: np.ndarray, rng: np.random.Generator, rows_by_day: list | None = None):
    """Rows of a day-block bootstrap draw (days drawn with replacement; all rows of a drawn day kept)."""
    if rows_by_day is None:
        rows_by_day = rows_per_day(day_codes)
    k = len(rows_by_day)
    pick = rng.integers(0, k, size=k)
    return np.concatenate([rows_by_day[i] for i in pick])


def rows_per_day(day_codes: np.ndarray) -> list:
    order = np.argsort(day_codes, kind="stable")
    dc = day_codes[order]
    cuts = np.flatnonzero(np.diff(dc)) + 1
    return np.split(order, cuts)


def interleaved_folds(day_codes: np.ndarray, k: int = 5) -> np.ndarray:
    days = np.unique(day_codes)
    f = {d: i % k for i, d in enumerate(np.sort(days))}
    return np.array([f[d] for d in day_codes])


def _test():
    rng = np.random.default_rng(1)
    n = 20000
    agent = rng.integers(0, 20, n)
    x1 = rng.normal(size=n)
    x2 = 0.6 * x1 + rng.normal(size=n)
    alpha = rng.normal(0, 0.5, 20)
    for link, b in (("logit", (-0.5, 0.3)), ("cloglog", (-0.4, 0.2))):
        eta = -1 + alpha[agent] + b[0] * x1 + b[1] * x2
        mu, _ = _mu(eta, link)
        y = (rng.random(n) < mu).astype(float)
        X, nm = design(np.c_[x1, x2], ["x1", "x2"], agent)
        f = fit_binary(X, y, link=link)
        se = np.sqrt(np.diag(f["cov"]))
        print(link, f["converged"], np.round(f["beta"][1:3], 3), np.round(se[1:3], 3), "truth", b)
        assert abs(f["beta"][1] - b[0]) < 4 * se[1] and abs(f["beta"][2] - b[1]) < 4 * se[2]
    y = 2 + alpha[agent] + 0.5 * x1 - 0.2 * x2 + rng.normal(size=n)
    X, nm = design(np.c_[x1, x2], ["x1", "x2"], agent)
    f = fit_ols(X, y)
    print("ols", np.round(f["beta"][1:3], 3))
    assert abs(f["beta"][1] - 0.5) < 0.05
    print("ok")


if __name__ == "__main__":
    import sys
    if "--test" in sys.argv or "--verify" in sys.argv:   # --verify: the build_all name for this self-check
        _test()
