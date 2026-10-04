"""H19 analysis library: random-effects meta-regression across goal periods, LOPO predictive scoring, rivals.

Each period keeps its own estimate y_p with standard error s_p (from the method that produced it). The meta-
regression y_p ~ N(X_p b, s_p^2 + tau^2) (REML tau^2, GLS b, Knapp-Hartung-Sidik-Jonkman CIs with q floored at 1)
is the allowed exception (d): partial pooling of per-period parameters, never a model fitted to pooled raw data.
"""
from __future__ import annotations

import os
os.environ.setdefault("OMP_NUM_THREADS", "1"); os.environ.setdefault("VECLIB_MAXIMUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")

import numpy as np
from scipy import stats
from scipy.optimize import minimize_scalar

LOG2PI = np.log(2 * np.pi)


# ----------------------------------------------------------------------------- REML meta-regression
def _gls(y, X, v, return_A=False):
    w = 1.0 / v
    XtW = X.T * w
    A = XtW @ X
    try:
        Ai = np.linalg.inv(A)
    except np.linalg.LinAlgError:
        Ai = np.linalg.pinv(A)
    b = Ai @ (XtW @ y)
    return (b, Ai, A) if return_A else (b, Ai)


def _neg_reml(log_tau2, y, X, s2):
    v = s2 + np.exp(log_tau2)
    b, Ai, A = _gls(y, X, v, return_A=True)
    r = y - X @ b
    sign, logdetA = np.linalg.slogdet(A)
    return 0.5 * (np.sum(np.log(v)) + logdetA + np.sum(r * r / v))


def reml_fit(y, s, X) -> dict:
    y = np.asarray(y, float); s2 = np.asarray(s, float) ** 2; X = np.asarray(X, float)
    k, p = X.shape
    if k - p < 1:
        b, Ai = _gls(y, X, s2 + 1e-12)
        return {"b": b, "cov": Ai, "tau2": 0.0, "k": k, "p": p, "q": 1.0, "df": 1}
    # tau2 on a log grid then refine; tau2 -> 0 boundary handled by comparing with a tiny value
    lo, hi = np.log(1e-8), np.log(max(np.var(y) * 4, 1e-6))
    res = minimize_scalar(_neg_reml, bounds=(lo, hi), args=(y, X, s2), method="bounded", options={"xatol": 1e-4})
    tau2 = float(np.exp(res.x))
    if _neg_reml(lo, y, X, s2) <= res.fun:
        tau2 = 0.0
    v = s2 + tau2
    b, Ai = _gls(y, X, v)
    r = y - X @ b
    q = float(np.sum(r * r / v) / (k - p))
    return {"b": b, "cov": Ai, "tau2": tau2, "k": k, "p": p, "q": q, "df": k - p}


def coef_table(fit: dict, names: list[str], level=0.95) -> list[dict]:
    """Knapp-Hartung (HKSJ) intervals with q floored at 1 (conservative with few periods)."""
    qf = max(1.0, fit["q"])
    se = np.sqrt(np.diag(fit["cov"]) * qf)
    t = stats.t.ppf(0.5 + level / 2, fit["df"])
    out = []
    for i, nm in enumerate(names):
        b = float(fit["b"][i])
        p = float(2 * stats.t.sf(abs(b / se[i]), fit["df"])) if se[i] > 0 else np.nan
        out.append({"name": nm, "b": b, "se": float(se[i]), "lo": b - t * se[i], "hi": b + t * se[i], "p": p})
    return out


def predictive(fit: dict, Xnew, snew):
    m = np.asarray(Xnew, float) @ fit["b"]
    Xn = np.atleast_2d(Xnew)
    var_b = np.einsum("ij,jk,ik->i", Xn, fit["cov"] * max(1.0, fit["q"]), Xn)
    v = np.asarray(snew, float) ** 2 + fit["tau2"] + var_b
    return m, v


def reduce_cols(X, tol=1e-9):
    """Greedy full-rank column subset; returns kept cols, dropped cols and B with X[:, dropped] = X[:, kept] @ B."""
    kept = []
    for j in range(X.shape[1]):
        if np.abs(X[:, j]).sum() == 0:
            continue
        if np.linalg.matrix_rank(X[:, kept + [j]], tol=tol * max(1.0, np.abs(X).max())) > len(kept):
            kept.append(j)
    dropped = [j for j in range(X.shape[1]) if j not in kept]
    B = np.linalg.lstsq(X[:, kept], X[:, dropped], rcond=None)[0] if dropped else np.zeros((len(kept), 0))
    return kept, dropped, B


def lopo(y, s, X, groups=None) -> dict:
    """Leave-one-period-out: refit without period p, score its estimate (NaN where p needs a direction unseen in training)."""
    y = np.asarray(y, float); s = np.asarray(s, float); X = np.asarray(X, float)
    n = len(y)
    lpd = np.full(n, np.nan); mu = np.full(n, np.nan); var = np.full(n, np.nan)
    for i in range(n):
        keep = np.arange(n) != i
        Xi = X[keep]
        kept, dropped, B = reduce_cols(Xi)
        if keep.sum() - len(kept) < 1:
            continue
        if dropped and not np.allclose(X[i, kept] @ B, X[i, dropped], atol=1e-8):
            continue
        f = reml_fit(y[keep], s[keep], Xi[:, kept])
        m, v = predictive(f, X[i:i + 1, kept], s[i:i + 1])
        mu[i], var[i] = m[0], v[0]
        lpd[i] = -0.5 * (LOG2PI + np.log(v[0]) + (y[i] - m[0]) ** 2 / v[0])
    return {"lpd": lpd, "mu": mu, "var": var}


# ----------------------------------------------------------------------------- design matrices
def design(df_rows: list[dict], model: str, xname: str | None = None, extra: list[str] | None = None):
    """Rows are dicts with control columns. Models: 'const', 'x', 'regime', 'era', 'logN', 'regime+x', 'x+modeC'."""
    n = len(df_rows)
    cols, names = [np.ones(n)], ["intercept"]

    def add(v, nm):
        cols.append(np.asarray(v, float)); names.append(nm)

    if model in ("x", "regime+x", "x+modeC"):
        add([r[xname] for r in df_rows], xname)
    if model in ("regime", "regime+x"):
        regs = [r["regime"] for r in df_rows]
        for lvl in ("II", "III"):
            if lvl in regs:
                add([1.0 if g == lvl else 0.0 for g in regs], f"regime_{lvl}")
    if model == "era":
        add([r["date_mid"] / 100.0 for r in df_rows], "date_mid_per100d")
    if model == "logN":
        add([np.log(r["N_roster"]) for r in df_rows], "log_N_roster")
    if model == "x+modeC":
        add([1.0 if r["mode"] == "C" else 0.0 for r in df_rows], "mode_C")
    for e in extra or []:
        add([r[e] for r in df_rows], e)
    return np.column_stack(cols), names


def r2_het(tau2_0: float, tau2_x: float) -> float:
    if tau2_0 <= 0:
        return np.nan
    return float(max(0.0, 1.0 - tau2_x / tau2_0))


def elpd_diff(lpd_a, lpd_b) -> dict:
    a, b = np.asarray(lpd_a), np.asarray(lpd_b)
    ok = np.isfinite(a) & np.isfinite(b)
    d = a[ok] - b[ok]
    return {"delta": float(d.sum()), "se": float(np.sqrt(ok.sum() * d.var(ddof=1))) if ok.sum() > 1 else np.nan, "n": int(ok.sum())}


def spearman(a, b):
    a, b = np.asarray(a, float), np.asarray(b, float)
    ok = np.isfinite(a) & np.isfinite(b)
    if ok.sum() < 4:
        return np.nan, np.nan, int(ok.sum())
    r, p = stats.spearmanr(a[ok], b[ok])
    return float(r), float(p), int(ok.sum())


# ----------------------------------------------------------------------------- the decision procedure (P1)
def elpd_totals(per_method: dict, models=None) -> dict:
    """Sum LOPO lpd over methods, each method restricted to the periods every compared model can predict."""
    models = models or list(next(iter(per_method.values())).keys())
    tot = {m: 0.0 for m in models}
    for fm in per_method.values():
        L = np.array([fm[m]["lopo"]["lpd"] for m in models])
        ok = np.isfinite(L).all(0)
        for i, m in enumerate(models):
            tot[m] += float(L[i, ok].sum())
    return tot


MODELS = ("const", "x", "regime", "era", "logN", "regime+x")


def method_fits(rows: list[dict], xname: str, models=MODELS, do_lopo=True) -> dict:
    """rows: per-period dicts with y, s and controls for ONE method. Returns per-model fits + LOPO lpd."""
    y = np.array([r["y"] for r in rows]); s = np.array([r["s"] for r in rows])
    out = {}
    for m in models:
        X, names = design(rows, m, xname)
        keep, _, _ = reduce_cols(X)
        X, names = X[:, keep], [names[i] for i in keep]
        f = reml_fit(y, s, X)
        res = {"names": names, "fit": f, "coefs": coef_table(f, names)}
        if do_lopo:
            res["lopo"] = lopo(y, s, X)
        out[m] = res
    return out


def p1_decision(per_method: dict, primaries: tuple[str, str], xname: str, margin=2.0) -> dict:
    """per_method[m] = method_fits(...). Applies the card's P1 rule (written 2026-10-04 00:03 UTC)."""
    slope = {}
    for m, fm in per_method.items():
        c = [r for r in fm["x"]["coefs"] if r["name"] == xname][0]
        slope[m] = c
    a_prim = all(slope[m]["lo"] > 0 for m in primaries if m in slope)
    a_other = not any(slope[m]["hi"] < 0 for m in slope if m not in primaries)
    a = a_prim and a_other and all(m in slope for m in primaries)
    r2 = {m: r2_het(fm["const"]["fit"]["tau2"], fm["x"]["fit"]["tau2"]) for m, fm in per_method.items()}
    b = all(np.isfinite(r2[m]) and r2[m] >= 0.25 for m in primaries if m in r2)
    tot = elpd_totals(per_method)
    beats = {riv: tot["x"] - tot[riv] for riv in ("const", "regime", "era", "logN")}
    within = {}
    for m in primaries:
        c = [r for r in per_method[m]["regime+x"]["coefs"] if r["name"] == xname]
        within[m] = c[0] if c else None
    c_ok = all(v > margin for v in beats.values()) and all(within[m] is not None and within[m]["b"] > 0 for m in primaries)
    nconds = int(b) + int(c_ok)
    verdict = "supported" if (a and b and c_ok) else ("mixed" if a and nconds == 1 else "failed")
    return {"a_sign": a, "a_primaries_ci_excl_0": a_prim, "a_no_other_negative": a_other, "b_r2": b, "c_rivals": c_ok,
            "slopes": slope, "r2_het": r2, "elpd_total": tot, "elpd_x_minus_rival": beats, "within_regime_slope": within,
            "verdict": verdict}
