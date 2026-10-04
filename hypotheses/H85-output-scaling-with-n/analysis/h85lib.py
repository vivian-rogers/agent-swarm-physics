"""H85 library: unit-level allometric fits ln(Y/T) = alpha_regime [+ delta_mode] + beta ln N with goal-cluster CIs.

Used by synthetic.py, replication.py, natives.py and confirm.py. No imports from other hypotheses.
"""
from __future__ import annotations

import os

for _v in ("POLARS_MAX_THREADS", "OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "2")
from pathlib import Path  # noqa: E402

import numpy as np  # noqa: E402

ROOT = Path(__file__).resolve().parents[3]
DATA = ROOT / "data/processed/H85-output-scaling-with-n"
BETA_D = 0.66          # H18 mention-based dilution exponent on ledger k (RE-V1)
F_PARENT = {"I": 0.37, "II": 0.48, "III": 0.54}   # documented DQ2 parent fractions (reply_threading.md)


def design(lnN, regime=None, extra=None):
    """Columns: ln N, regime dummies (full set, no global intercept), optional extra covariates."""
    cols, names = [np.asarray(lnN, float)], ["lnN"]
    if regime is None:
        cols.append(np.ones(len(lnN))); names.append("const")
    else:
        reg = np.asarray(regime)
        for r in sorted(set(reg)):
            cols.append((reg == r).astype(float)); names.append(f"reg_{r}")
    if extra is not None:
        for k, v in extra.items():
            cols.append(np.asarray(v, float)); names.append(k)
    return np.column_stack(cols), names


def ols(X, y, w=None):
    if w is not None:
        sw = np.sqrt(np.asarray(w, float))
        X, y = X * sw[:, None], y * sw
    keep = np.abs(X).sum(0) > 0
    b = np.full(X.shape[1], np.nan)
    b[keep] = np.linalg.lstsq(X[:, keep], y, rcond=None)[0]
    return b


def cr1_se(X, y, b, cluster):
    """Cluster-robust (CR1) SE of the coefficients."""
    keep = ~np.isnan(b)
    Xk, bk = X[:, keep], b[keep]
    e = y - Xk @ bk
    XtX_inv = np.linalg.pinv(Xk.T @ Xk)
    cl = np.asarray(cluster)
    G = len(set(cl))
    meat = np.zeros((Xk.shape[1], Xk.shape[1]))
    for g in set(cl):
        s = Xk[cl == g].T @ e[cl == g]
        meat += np.outer(s, s)
    n, k = Xk.shape
    adj = G / max(G - 1, 1) * (n - 1) / max(n - k, 1)
    V = adj * XtX_inv @ meat @ XtX_inv
    se = np.full(len(b), np.nan)
    se[keep] = np.sqrt(np.clip(np.diag(V), 0, None))
    return se


def fit_beta(y, lnN, regime, cluster, extra=None, w=None, B=2000, rng=None, coef="lnN", unit_boot=False):
    """Point estimate, goal-cluster bootstrap percentile CI (primary), CR1 SE, optional unit bootstrap CI."""
    rng = rng or np.random.default_rng(20261004)
    y, lnN = np.asarray(y, float), np.asarray(lnN, float)
    reg = None if regime is None else np.asarray(regime)
    X, names = design(lnN, reg, extra)
    j = names.index(coef)
    b = ols(X, y, w)
    se = cr1_se(X, y, b, cluster)
    cl = np.asarray(cluster)
    groups = sorted(set(cl))
    idx_by = {g: np.where(cl == g)[0] for g in groups}
    boots = np.empty(B)
    for i in range(B):
        pick = rng.choice(len(groups), len(groups), replace=True)
        ii = np.concatenate([idx_by[groups[p]] for p in pick])
        bb = ols(X[ii], y[ii], None if w is None else np.asarray(w)[ii])
        boots[i] = bb[j]
    boots = boots[np.isfinite(boots)]
    out = {"beta": float(b[j]), "ci_lo": float(np.quantile(boots, 0.025)), "ci_hi": float(np.quantile(boots, 0.975)),
           "se_boot": float(boots.std(ddof=1)), "se_cr1": float(se[j]), "n_units": int(len(y)), "n_goals": len(groups),
           "coefs": {n: float(v) for n, v in zip(names, b)}}
    if unit_boot:
        ub = np.empty(B)
        for i in range(B):
            ii = rng.integers(0, len(y), len(y))
            ub[i] = ols(X[ii], y[ii], None if w is None else np.asarray(w)[ii])[j]
        ub = ub[np.isfinite(ub)]
        out["ci_unit"] = [float(np.quantile(ub, 0.025)), float(np.quantile(ub, 0.975))]
    return out


def boot_pairs(y1, y2, lnN, regime, cluster, B=2000, rng=None):
    """Joint goal-cluster bootstrap of beta(y1) and beta(y2) on the same units; returns the difference's CI."""
    rng = rng or np.random.default_rng(20261005)
    X, names = design(lnN, regime)
    j = names.index("lnN")
    cl = np.asarray(cluster)
    groups = sorted(set(cl))
    idx_by = {g: np.where(cl == g)[0] for g in groups}
    d0 = ols(X, np.asarray(y1))[j] - ols(X, np.asarray(y2))[j]
    ds = np.empty(B)
    for i in range(B):
        ii = np.concatenate([idx_by[groups[p]] for p in rng.choice(len(groups), len(groups), replace=True)])
        ds[i] = ols(X[ii], np.asarray(y1)[ii])[j] - ols(X[ii], np.asarray(y2)[ii])[j]
    ds = ds[np.isfinite(ds)]
    return {"diff": float(d0), "ci_lo": float(np.quantile(ds, 0.025)), "ci_hi": float(np.quantile(ds, 0.975)),
            "p_le0": float((ds <= 0).mean())}


def budget_factor(f: float) -> float:
    """Elasticity factor of P(parent) = 1 - exp(-lambda) in lambda, at parent fraction f."""
    lam = -np.log(1 - f)
    return float(lam * (1 - f) / f)
