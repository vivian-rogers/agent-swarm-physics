"""Label-noise model for the DQ10 validated conflict flag (round 1c, 2026-10-04).

Identical copy in hypotheses/H21-debate-antiferromagnet/analysis/labelnoise.py and
hypotheses/H37-stance-spins/analysis/labelnoise.py (two users; proposed for infra/shared/).

The flag f (reply_stance_v2.disagree_validated_agent: Jev v2.1 'disagree' with confidence >= 0.6) is a noisy reading of
true disagreement d on the merits:
    P(f = 1 | d = 1) = R   (recall / sensitivity)
    P(f = 1 | d = 0) = phi (false-positive rate per non-disagreement reply)
so P(f = 1) = phi + (R - phi) * pi, pi = P(d = 1).

DQ10 (infra/data-quality/stance_v2.md, confirm2 sheet): precision (PPV) 0.67 [0.54, 0.80] for disagree_validated,
0.61 without replies to automated messages; reweighted recall 0.61. Population flag rate (agent parents) q = 0.0106.
phi follows from (q, PPV, R): pi_pop = q PPV / R ; phi = q (1 - PPV) / (1 - pi_pop).

Functions
  draws(K, rng, ctx)            K draws of (PPV, R, phi); ctx 'pop' (validated population noise) or 'g12' (#12 stratum:
                                10/10 flagged pairs correct on two DQ10 sheets -> PPV ~ Beta(11, 1), R ~ 0.9)
  observe(d, R, phi, rng)       flags from true labels (phi scalar or per-row)
  rogan_gladen(r, R, phi)       corrected true rate from an observed rate
  fit(y, spk, tgt, X, N, R, phi)  noise-aware logistic with speaker and target fields (L2 lam on fields) and fixed
                                effects X (true-scale log-odds); returns dict(mu, a, b, beta, ok)
  simulate(spk, tgt, X, par, R, phi, rng)  true labels from a fitted model, then flags
  stress_phi(phi, groups, share)  per-row false-positive rate proportional to each group's share of Jev correct+inform
"""
from __future__ import annotations

import numpy as np
from scipy.optimize import minimize

Q_POP = 0.0106            # flag rate over agent-parent pairs in reply_stance_v2 (59,291 pairs)
PPV_MEAN, PPV_SD = 0.64, 0.065
R_MEAN, R_SD = 0.60, 0.08
G12_PPV_AB = (11.0, 1.0)  # #12 stratum: 10/10 flagged correct (fresh 3/3, confirm2 7/7)
G12_R_MEAN, G12_R_SD = 0.90, 0.07


def beta_ab(m: float, s: float) -> tuple[float, float]:
    k = m * (1 - m) / s ** 2 - 1
    return m * k, (1 - m) * k


def phi_from(q: float, ppv: float, R: float) -> float:
    pi = min(q * ppv / R, 0.99)
    return q * (1 - ppv) / (1 - pi)


def draws(K: int, rng: np.random.Generator, ctx: str = "pop", q: float = Q_POP) -> np.ndarray:
    """(K, 3) array of (PPV, R, phi)."""
    if ctx == "pop":
        ppv = rng.beta(*beta_ab(PPV_MEAN, PPV_SD), K)
        R = rng.beta(*beta_ab(R_MEAN, R_SD), K)
    elif ctx == "g12":
        ppv = rng.beta(*G12_PPV_AB, K)
        R = rng.beta(*beta_ab(G12_R_MEAN, G12_R_SD), K)
    else:
        raise ValueError(ctx)
    phi = np.array([phi_from(q, p, r) for p, r in zip(ppv, R)])
    return np.column_stack([ppv, R, phi])


def observe(d: np.ndarray, R: float, phi, rng: np.random.Generator) -> np.ndarray:
    d = np.asarray(d, bool)
    u = rng.random(len(d))
    return np.where(d, u < R, u < phi).astype(float)


def rogan_gladen(r, R, phi):
    return np.clip((np.asarray(r, float) - phi) / (R - phi), 0.0, 1.0)


def _sig(x):
    return 1.0 / (1.0 + np.exp(-x))


def fit(y, spk, tgt, X, N, R, phi, lam: float = 0.1, lam_beta: float = 0.01, mu0: float | None = None):
    """Noise-aware logistic: P(f=1) = phi + (R - phi) sigmoid(mu + a[spk] + b[tgt] + X beta).
    y: 0/1 flags; spk, tgt: int codes < N; X: (n, k) or None; phi: scalar or per-row. Bounds +-12 keep it finite when a
    group's observed rate is below phi."""
    y = np.asarray(y, float)
    n = len(y)
    X = np.zeros((n, 0)) if X is None else np.asarray(X, float).reshape(n, -1)
    k = X.shape[1]
    phi = np.broadcast_to(np.asarray(phi, float), (n,))
    Rm = R - phi
    if mu0 is None:
        r = np.clip((y.mean() - phi.mean()) / max(R - phi.mean(), 1e-6), 1e-3, 0.9)
        mu0 = np.log(r / (1 - r))

    def nll(th):
        mu = th[0]; a = th[1:N + 1]; b = th[N + 1:2 * N + 1]; be = th[2 * N + 1:]
        eta = mu + a[spk] + b[tgt] + X @ be
        s = _sig(eta)
        P = np.clip(phi + Rm * s, 1e-12, 1 - 1e-12)
        ll = y * np.log(P) + (1 - y) * np.log(1 - P)
        g = (y / P - (1 - y) / (1 - P)) * Rm * s * (1 - s)
        f = -ll.sum() + lam * (a @ a + b @ b) + lam_beta * (be @ be)
        grad = -np.r_[g.sum(), np.bincount(spk, g, N), np.bincount(tgt, g, N), X.T @ g]
        grad[1:2 * N + 1] += 2 * lam * th[1:2 * N + 1]
        grad[2 * N + 1:] += 2 * lam_beta * be
        return f, grad
    th0 = np.r_[mu0, np.zeros(2 * N + k)]
    res = minimize(nll, th0, jac=True, method="L-BFGS-B", bounds=[(-12, 12)] * len(th0))
    th = res.x
    return {"mu": th[0], "a": th[1:N + 1], "b": th[N + 1:2 * N + 1], "beta": th[2 * N + 1:], "ok": bool(res.success),
            "nll": float(res.fun)}


def true_prob(spk, tgt, X, par):
    n = len(spk)
    X = np.zeros((n, 0)) if X is None else np.asarray(X, float).reshape(n, -1)
    beta = par["beta"] if len(par["beta"]) == X.shape[1] else np.zeros(X.shape[1])
    return _sig(par["mu"] + par["a"][spk] + par["b"][tgt] + X @ beta)


def simulate(spk, tgt, X, par, R, phi, rng):
    pi = true_prob(spk, tgt, X, par)
    d = rng.random(len(pi)) < pi
    return observe(d, R, phi, rng)


def stress_phi(phi: float, group: np.ndarray, ci_share: np.ndarray) -> np.ndarray:
    """Per-row phi proportional to the row's group share of Jev correct+inform (shares computed by the caller over
    rows whose Jev class is not 'disagree'), normalized so the row-mean of phi stays phi."""
    group = np.asarray(group)
    w = np.asarray(ci_share, float)[group]
    return phi * w / w.mean() if w.mean() > 0 else np.full(len(group), phi)


def pval(obs, null, side="greater"):
    null = np.asarray(null, float)
    null = null[np.isfinite(null)]
    if not np.isfinite(obs) or len(null) == 0:
        return float("nan")
    if side == "greater":
        return float((1 + np.sum(null >= obs - 1e-12)) / (1 + len(null)))
    return float((1 + np.sum(null <= obs + 1e-12)) / (1 + len(null)))
