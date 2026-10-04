"""Stance v2.1 label-noise null (NG): the labeller's confusion built into nulls for `disagree_validated_agent`.

Round 1c of H22, H55 and H64 (2026-10-04). Identical copies live in each hypothesis's analysis/ folder because new
code must not import across hypothesis folders (STANDARDS §8); the suggested home is infra/shared/stance_noise.py.

Sensor: D = disagree_validated_agent (stance2 == disagree, confidence >= 0.6, parent by an agent or human), validated
precision pi 0.61-0.67 [lower bound 0.54], recall r ~ 0.6 (DQ10, stance_v2.md, Amendment 2).

Null generator (card round-1c pre-registrations):
  truth   D*_e ~ Bernoulli(sigmoid(eta0_e + delta + u_block + beta * x_e))
          eta0 = two-way (or more-way) logistic fixed effects fitted to the OBSERVED flags; delta shifts the mean so that
          E[sum D*] = pi * sum(D_obs) / r (the implied true count); u_block ~ N(0, sigma_u^2) per conversation block;
          beta * x_e is a planted effect (synthetic validation only; 0 under the null).
  observe D_e ~ Bernoulli(r * D*_e + f_e * (1 - D*_e)), with a DIFFERENTIAL false-positive rate
          f_e = fbar * g_e / mean(g),   g_e = sum_k phi_k * p_k(e) / (1 - p_disagree(e))   (k != disagree)
          phi_k = confirm2 false flags whose reference class is k / population hard-class count of k
          fbar  = (1 - pi) * Dbar / (1 - pi * Dbar / r)   (the implied mean false-positive rate)
  pi ~ U[0.54, 0.80], r ~ U[0.50, 0.75], sigma_u ~ {0, 0.5, 1} drawn per replicate unless fixed.
Corrected contrast: T* = (T - T_f) / (r - fbar), T_f = the same linear contrast computed on f_e.
"""
from __future__ import annotations

import os

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "VECLIB_MAXIMUM_THREADS", "POLARS_MAX_THREADS"):
    os.environ.setdefault(_v, "2")

import sys  # noqa: E402
from pathlib import Path  # noqa: E402

import numpy as np  # noqa: E402
import polars as pl  # noqa: E402
from scipy import optimize  # noqa: E402

ROOT = Path(__file__).resolve().parents[3]
SH = ROOT / "data/processed/shared"
sys.path.insert(0, str(ROOT / "infra/shared"))
from common import holdout_mask  # noqa: E402

PI_RANGE = (0.54, 0.80)
R_RANGE = (0.50, 0.75)
PI_POINT, R_POINT = 0.64, 0.61
SIGMA_U = (0.0, 0.5, 1.0)
CLASSES = ["agree", "disagree", "correct", "decline", "coordinate", "ask", "acknowledge", "inform"]
# confirm2 (stance_v2.md, Amendment 2 result): Jev's 28 false `disagree` calls by reference class
FALSE_FLAGS = {"inform": 11, "correct": 10, "coordinate": 3, "agree": 2, "acknowledge": 1, "ask": 1, "decline": 0}
V2_COLS = ["B_message_id", "A_message_id", "b_agent", "a_kind", "a_agent", "room", "pt_date", "goal_no", "regime",
           "p_reply", "stance2", "stance2_conf", "s2_soft", "disagree_validated", "disagree_validated_agent", "holdout"] + \
          [f"p_{k}" for k in CLASSES]


def load_v2(columns=None) -> pl.DataFrame:
    """reply_stance_v2 (non-holdout by construction), with holdout_mask re-applied."""
    cols = sorted(set(V2_COLS if columns is None else list(columns) + ["pt_date", "goal_no", "holdout"]))
    d = pl.read_parquet(SH / "reply_stance_v2.parquet", columns=cols)
    d = d.filter(~pl.col("holdout"))
    hm = holdout_mask(d["pt_date"].to_list(), d["goal_no"].to_list())
    d = d.filter(~pl.Series(hm))
    assert d["holdout"].sum() == 0
    return d


_PHI = None


def phi() -> dict:
    """False-flag propensity per reference class: confirm2 false flags / population hard-class count (all non-holdout
    labelled pairs; a shared ruler, not a per-period quantity). Scale is irrelevant (f_e is renormalized)."""
    global _PHI
    if _PHI is None:
        d = pl.read_parquet(SH / "reply_stance_v2.parquet", columns=["stance2", "labelled"]).filter(pl.col("labelled"))
        cnt = dict(d["stance2"].cast(pl.String).value_counts().iter_rows())
        _PHI = {k: FALSE_FLAGS[k] / max(cnt.get(k, 1), 1) for k in FALSE_FLAGS}
    return _PHI


def fp_profile(df: pl.DataFrame) -> np.ndarray:
    """g_e = sum_k phi_k * p_k / (1 - p_disagree): the reply's propensity to be falsely flagged (unnormalized)."""
    ph = phi()
    den = np.maximum(1 - df["p_disagree"].fill_null(0).to_numpy().astype(float), 1e-6)
    g = np.zeros(df.height)
    for k, v in ph.items():
        g += v * df[f"p_{k}"].fill_null(0).to_numpy().astype(float) / den
    return np.maximum(g, 1e-9)


def implied_fpr(dbar: float, pi: float, r: float) -> float:
    return float(np.clip((1 - pi) * dbar / max(1 - pi * dbar / r, 1e-6), 0, 0.5))


# --------------------------------------------------------------------------------------------- estimators
def twoway_resid(spk, tgt, y, N=None, it: int = 50):
    """y minus additive speaker and target means (alternating projections)."""
    y = np.asarray(y, float)
    N = int(max(spk.max(), tgt.max()) + 1) if N is None else N
    a, b = np.zeros(N), np.zeros(N)
    mu = y.mean()
    ns = np.maximum(np.bincount(spk, None, N), 1)
    nt = np.maximum(np.bincount(tgt, None, N), 1)
    for _ in range(it):
        a = np.bincount(spk, y - mu - b[tgt], N) / ns
        b = np.bincount(tgt, y - mu - a[spk], N) / nt
    return y - mu - a[spk] - b[tgt]


def demean_multi(v, groups, it: int = 50):
    """v minus additive fixed effects for every code array in groups (alternating projections)."""
    r = np.asarray(v, float).copy()
    r = r - r.mean()
    inv = [np.unique(g, return_inverse=True)[1] for g in groups]
    for _ in range(it):
        for g in inv:
            n = g.max() + 1
            r -= (np.bincount(g, r, n) / np.maximum(np.bincount(g, None, n), 1))[g]
    return r


def fit_logit_fe(groups, y, ridge: float = 1.0, x=None):
    """Additive logistic fixed effects (ridge on the effects, not the intercept). Returns the linear predictor eta.
    groups: list of integer code arrays. x: optional extra covariate columns (n x p), unpenalized."""
    y = np.asarray(y, float)
    n = len(y)
    inv = [np.unique(g, return_inverse=True)[1] for g in groups]
    sizes = [g.max() + 1 for g in inv]
    off = np.cumsum([0] + sizes)
    P = 0 if x is None else x.shape[1]
    m0 = np.clip(y.mean(), 1e-4, 1 - 1e-4)

    def f(th):
        mu, fe, bx = th[0], th[1:1 + off[-1]], th[1 + off[-1]:]
        eta = np.full(n, mu)
        for k, g in enumerate(inv):
            eta += fe[off[k]:off[k + 1]][g]
        if P:
            eta += x @ bx
        p = 1 / (1 + np.exp(-eta))
        ll = np.sum(y * eta - np.logaddexp(0, eta))
        r = p - y
        grad = [r.sum()]
        for k, g in enumerate(inv):
            grad.append(np.bincount(g, r, sizes[k]) + ridge * fe[off[k]:off[k + 1]])
        if P:
            grad.append(x.T @ r)
        return -ll + 0.5 * ridge * np.sum(fe ** 2), np.concatenate([np.atleast_1d(v) for v in grad])

    th0 = np.zeros(1 + off[-1] + P)
    th0[0] = np.log(m0 / (1 - m0))
    res = optimize.minimize(f, th0, jac=True, method="L-BFGS-B", options={"maxiter": 500})
    th = res.x
    eta = np.full(n, th[0])
    for k, g in enumerate(inv):
        eta += th[1 + off[k]:1 + off[k + 1]][g]
    if P:
        eta += x @ th[1 + off[-1]:]
    return eta


def _shift(eta, target_mean, u=0.0):
    lo, hi = -15.0, 15.0
    for _ in range(40):
        mid = 0.5 * (lo + hi)
        m = np.mean(1 / (1 + np.exp(-(eta + mid + u))))
        lo, hi = (mid, hi) if m < target_mean else (lo, mid)
    return 0.5 * (lo + hi)


class NoiseNull:
    """Draws observed flags under the label-noise null (or with a planted effect) on a fixed reply structure."""

    def __init__(self, groups, y_obs, g, block=None, ridge: float = 1.0, eta0=None):
        self.y = np.asarray(y_obs, float)
        self.g = np.asarray(g, float)
        self.n = len(self.y)
        self.dbar = float(self.y.mean())
        self.eta0 = fit_logit_fe(groups, self.y, ridge=ridge) if eta0 is None else eta0
        self.binv = None if block is None else np.unique(block, return_inverse=True)[1]

    def draw(self, rng, beta: float = 0.0, x=None, pi=None, r=None, sigma_u=None, return_truth: bool = False):
        pi = rng.uniform(*PI_RANGE) if pi is None else pi
        r = rng.uniform(*R_RANGE) if r is None else r
        su = SIGMA_U[rng.integers(len(SIGMA_U))] if sigma_u is None else sigma_u
        u = rng.normal(0, su, self.binv.max() + 1)[self.binv] if (self.binv is not None and su > 0) else 0.0
        target = min(pi * max(self.dbar, 1e-6) / r, 0.5)
        lin = self.eta0 + u + (beta * x if (x is not None and beta != 0) else 0.0)
        # shift so that the TRUE mean matches the implied true rate (a planted effect keeps its own excess)
        base = self.eta0 + u
        delta = _shift(base, target)
        pt = 1 / (1 + np.exp(-(lin + delta)))
        dstar = rng.random(self.n) < pt
        fbar = implied_fpr(self.dbar, pi, r)
        f = np.clip(fbar * self.g / self.g.mean(), 0, 0.5)
        obs = np.where(dstar, rng.random(self.n) < r, rng.random(self.n) < f).astype(float)
        return (obs, dstar, dict(pi=pi, r=r, sigma_u=su, fbar=fbar)) if return_truth else obs

    def f_expected(self, pi=PI_POINT, r=R_POINT):
        fbar = implied_fpr(self.dbar, pi, r)
        return np.clip(fbar * self.g / self.g.mean(), 0, 0.5), fbar


def p_greater(obs, null):
    null = np.asarray(null, float)
    null = null[np.isfinite(null)]
    return float((1 + np.sum(null >= obs)) / (1 + len(null))) if np.isfinite(obs) else float("nan")


def p_less(obs, null):
    null = np.asarray(null, float)
    null = null[np.isfinite(null)]
    return float((1 + np.sum(null <= obs)) / (1 + len(null))) if np.isfinite(obs) else float("nan")


def dl_random_effects(est, se):
    """DerSimonian-Laird random-effects mean of per-unit estimates."""
    from scipy import stats
    est, se = np.asarray(est, float), np.asarray(se, float)
    ok = np.isfinite(est) & np.isfinite(se) & (se > 0)
    est, se = est[ok], se[ok]
    if len(est) == 0:
        return {"k": 0}
    w = 1 / se ** 2
    mf = np.sum(w * est) / np.sum(w)
    Q = float(np.sum(w * (est - mf) ** 2))
    tau2 = max(0.0, (Q - (len(est) - 1)) / (np.sum(w) - np.sum(w ** 2) / np.sum(w))) if len(est) > 1 else 0.0
    ws = 1 / (se ** 2 + tau2)
    mu = float(np.sum(ws * est) / np.sum(ws))
    sem = float(np.sqrt(1 / np.sum(ws)))
    return {"k": int(len(est)), "mu": mu, "se": sem, "lo": mu - 1.96 * sem, "hi": mu + 1.96 * sem,
            "z": mu / sem, "p_two": float(2 * stats.norm.sf(abs(mu / sem))), "tau2": float(tau2), "Q": Q}
