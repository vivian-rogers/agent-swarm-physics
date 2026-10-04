"""H64 estimators: cluster-robust antagonistic-pair counts against the calibrated agent-field null, and the
prize-gated DiD with fixed effects, cluster bootstrap and relation permutation. Used unchanged on synthetic and real
frames (analysis/synthetic.py, analysis/run.py)."""
from __future__ import annotations

import os

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")

import sys  # noqa: E402
from pathlib import Path  # noqa: E402

import numpy as np  # noqa: E402
from scipy.stats import t as tdist  # noqa: E402

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "infra/shared"))
from nulls import fit_ordinal, simulate_ordinal  # noqa: E402

# DQ2-like confusion matrix P(observed | true), rows true (-, 0, +), columns observed (-, 0, +). Noisier than H37's
# measured matrix (recall 0.56 / 0.73 / 0.89) because DQ2's stance kappa is 0.44 (card, N5).
CONF = np.array([[0.45, 0.35, 0.20], [0.10, 0.65, 0.25], [0.03, 0.15, 0.82]])


def reindex(*cols):
    """Map agent codes in the given arrays to 0..N-1 (shared index). Returns (arrays..., N, codes)."""
    codes = np.unique(np.concatenate([np.asarray(c) for c in cols]))
    m = {c: i for i, c in enumerate(codes)}
    return tuple(np.array([m[v] for v in c], dtype=np.int64) for c in cols) + (len(codes), codes)


def twoway_resid(spk, tgt, y, N, it: int = 30):
    y = np.asarray(y, float)
    a = np.zeros(N)
    b = np.zeros(N)
    mu = y.mean()
    ns = np.maximum(np.bincount(spk, None, N), 1)
    nt = np.maximum(np.bincount(tgt, None, N), 1)
    for _ in range(it):
        a = np.bincount(spk, y - mu - b[tgt], N) / ns
        b = np.bincount(tgt, y - mu - a[spk], N) / nt
    return y - mu - a[spk] - b[tgt]


def _bh_count(p: np.ndarray, q: float = 0.1) -> int:
    p = np.sort(p[np.isfinite(p)])
    m = len(p)
    if m == 0:
        return 0
    ok = p <= q * np.arange(1, m + 1) / m
    return int(np.flatnonzero(ok).max() + 1) if ok.any() else 0


def pair_tests(spk, tgt, y, block, N, robust: bool = True, q: float = 0.1, nmin: int = 5, gmin: int = 3):
    """Number of agent pairs (unordered, both directions pooled) whose residual stance is significantly negative.
    robust: cluster-robust SE with clusters = conversation blocks within the pair (>= gmin blocks, >= nmin replies);
    naive: iid replies (>= 3 replies), the H37 / RE-C2 test. Returns (count, n_tested)."""
    r = twoway_resid(spk, tgt, y, N)
    lo, hi = np.minimum(spk, tgt), np.maximum(spk, tgt)
    key = lo * N + hi
    if not robust:
        uk, inv, cnt = np.unique(key, return_inverse=True, return_counts=True)
        s = np.bincount(inv, r)
        s2 = np.bincount(inv, r * r)
        m = s / cnt
        var = np.where(cnt > 1, (s2 - cnt * m * m) / np.maximum(cnt - 1, 1), np.nan)
        ok = (cnt >= 3) & (var > 0)
        tt = m[ok] / np.sqrt(var[ok] / cnt[ok])
        p = tdist.cdf(tt, cnt[ok] - 1)
        return _bh_count(p, q), int(ok.sum())
    # cluster sums within pair
    pk = key * 1_000_003 + (np.asarray(block) % 1_000_003)
    upk, inv = np.unique(pk, return_inverse=True)
    S = np.bincount(inv, r)
    C = np.bincount(inv).astype(float)
    pair_of = upk // 1_000_003
    up, pinv = np.unique(pair_of, return_inverse=True)
    G = np.bincount(pinv).astype(float)
    n = np.bincount(pinv, C)
    m = np.bincount(pinv, S) / n
    dev = S - m[pinv] * C
    v = np.bincount(pinv, dev * dev) / (n * n) * G / np.maximum(G - 1, 1)
    ok = (G >= gmin) & (n >= nmin) & (v > 0)
    tt = m[ok] / np.sqrt(v[ok])
    p = tdist.cdf(tt, G[ok] - 1)
    return _bh_count(p, q), int(ok.sum())


def excess(spk, tgt, y, block, N, R: int = 200, rng=None):
    """Observed negative-pair counts (robust and naive) vs the calibrated agent-field null (ordered logit fitted to
    these hard labels, R simulations on the same reply structure, same tests)."""
    rng = np.random.default_rng(0) if rng is None else rng
    y = np.asarray(y)
    obs_r, n_r = pair_tests(spk, tgt, y, block, N, robust=True)
    obs_n, n_n = pair_tests(spk, tgt, y, block, N, robust=False)
    c, a, b, ok = fit_ordinal(spk, tgt, (y + 1).astype(int), N)
    nr = np.empty(R)
    nn = np.empty(R)
    for k in range(R):
        ys = simulate_ordinal(spk, tgt, c, a, b, rng)
        nr[k] = pair_tests(spk, tgt, ys, block, N, robust=True)[0]
        nn[k] = pair_tests(spk, tgt, ys, block, N, robust=False)[0]
    return {"n_neg_robust": obs_r, "n_tested_robust": n_r, "null_mean_robust": float(nr.mean()),
            "null_p95_robust": float(np.quantile(nr, 0.95)), "p_af_robust": float((1 + (nr >= obs_r).sum()) / (R + 1)),
            "E_robust": float(obs_r - nr.mean()),
            "n_neg_naive": obs_n, "n_tested_naive": n_n, "null_mean_naive": float(nn.mean()),
            "null_p95_naive": float(np.quantile(nn, 0.95)), "p_af_naive": float((1 + (nn >= obs_n).sum()) / (R + 1)),
            "E_naive": float(obs_n - nn.mean()), "fit_ok": ok, "R": R}


# ------------------------------------------------------------------------------------------------- DiD
def _dummies(codes: np.ndarray) -> np.ndarray:
    u, inv = np.unique(codes, return_inverse=True)
    if len(u) <= 1:
        return np.zeros((len(codes), 0))
    D = np.zeros((len(codes), len(u) - 1))
    m = inv > 0
    D[np.flatnonzero(m), inv[m] - 1] = 1.0
    return D


def did_fit(y, spk, tgt, win, R, O, heat: bool = False):
    """OLS y ~ 1 + speaker FE + target FE + window FE + g_open R*O + g_set R*(1-O) [+ phi O, when heat=True the window
    FE are coarser and O is identified]. Returns dict(g_open, g_set, delta[, phi])."""
    y = np.asarray(y, float)
    R = np.asarray(R, float)
    O = np.asarray(O, float)
    cols = [np.ones((len(y), 1)), _dummies(spk), _dummies(tgt), _dummies(win),
            (R * O)[:, None], (R * (1 - O))[:, None]]
    if heat:
        cols.append(O[:, None])
    X = np.hstack(cols)
    beta, *_ = np.linalg.lstsq(X, y, rcond=None)
    k = X.shape[1]
    j = k - (3 if heat else 2)
    out = {"g_open": float(beta[j]), "g_set": float(beta[j + 1])}
    out["delta"] = out["g_open"] - out["g_set"]
    if heat:
        out["phi"] = float(beta[j + 2])
    return out


def did(y, spk, tgt, win, R, O, cluster, B: int = 1000, rng=None, heat_unit=None):
    """Point estimates and cluster-bootstrap percentile CIs. heat_unit: coarser FE codes (e.g. debate) for phi."""
    rng = np.random.default_rng(1) if rng is None else rng
    y, spk, tgt, win, R, O, cluster = (np.asarray(v) for v in (y, spk, tgt, win, R, O, cluster))
    est = did_fit(y, spk, tgt, win, R, O)
    if heat_unit is not None:
        est["phi"] = did_fit(y, spk, tgt, np.asarray(heat_unit), R, O, heat=True)["phi"]
    uc, cinv = np.unique(cluster, return_inverse=True)
    idx_by = [np.flatnonzero(cinv == k) for k in range(len(uc))]
    boots = {k: [] for k in est}
    for _ in range(B):
        pick = rng.integers(0, len(uc), len(uc))
        ii = np.concatenate([idx_by[k] for k in pick])
        if R[ii].sum() == 0 or (R[ii] * O[ii]).sum() == 0 or (R[ii] * (1 - O[ii])).sum() == 0:
            continue
        e = did_fit(y[ii], spk[ii], tgt[ii], win[ii], R[ii], O[ii])
        if heat_unit is not None:
            e["phi"] = did_fit(y[ii], spk[ii], tgt[ii], np.asarray(heat_unit)[ii], R[ii], O[ii], heat=True)["phi"]
        for k in est:
            boots[k].append(e[k])
    ci = {k: (float(np.quantile(v, 0.025)), float(np.quantile(v, 0.975))) if len(v) > 20 else (np.nan, np.nan)
          for k, v in boots.items()}
    se = {k: float(np.std(v)) if len(v) > 20 else np.nan for k, v in boots.items()}
    return {"est": est, "ci": ci, "se": se, "n": int(len(y)), "n_rival_open": int((R * O).sum()),
            "n_rival_set": int((R * (1 - O)).sum()), "n_clusters": int(len(uc)), "B_ok": len(boots["g_open"])}


def decision(res, frac: float = 1 / 3) -> dict:
    """The card's gated-antagonism decision: open contrast CI below 0, settled contrast CI within +-frac*|g_open|,
    delta CI below 0."""
    go, gs, de = res["est"]["g_open"], res["ci"]["g_set"], res["ci"]["delta"]
    open_neg = res["ci"]["g_open"][1] < 0
    m = frac * abs(go)
    set_eq = (gs[0] > -m) and (gs[1] < m)
    delta_neg = de[1] < 0
    return {"open_neg": bool(open_neg), "set_equiv": bool(set_eq), "delta_neg": bool(delta_neg),
            "gated": bool(open_neg and set_eq and delta_neg)}


def perm_p(stat_obs: float, stats_null: np.ndarray, side: str = "less") -> float:
    s = np.asarray(stats_null, float)
    s = s[np.isfinite(s)]
    if side == "less":
        return float((1 + (s <= stat_obs).sum()) / (len(s) + 1))
    return float((1 + (s >= stat_obs).sum()) / (len(s) + 1))


# ------------------------------------------------------------------------------------------------- synthetic labels
def simulate_labels(spk, tgt, block, N, rng, sd_a=0.6, sd_b=0.6, sd_u=0.0, base=(0.09, 0.15), extra=None,
                    noise: bool = True, sd_pb: float = 0.0):
    """Ordered-logit latent with agent fields, block shocks and an optional extra latent term, cut points set so the
    noiseless marginal is about base = (P(-), P(0)); then label noise through CONF. Returns y in {-1, 0, 1}."""
    a = rng.normal(0, sd_a, N)
    b = rng.normal(0, sd_b, N)
    ub, binv = np.unique(block, return_inverse=True)
    u = rng.normal(0, sd_u, len(ub))[binv] if sd_u > 0 else 0.0
    if sd_pb > 0:  # pair x block shock: one exchange between two agents shares a sign (thread clustering)
        pk = (np.minimum(spk, tgt) * N + np.maximum(spk, tgt)) * 1_000_003 + (np.asarray(block) % 1_000_003)
        _, pinv = np.unique(pk, return_inverse=True)
        u = u + rng.normal(0, sd_pb, pinv.max() + 1)[pinv]
    lat = a[spk] + b[tgt] + u + rng.logistic(size=len(spk))
    if extra is not None:
        lat = lat + extra
    base_lat = a[spk] + b[tgt] + u + rng.logistic(size=len(spk))
    c1, c2 = np.quantile(base_lat, [base[0], base[0] + base[1]])
    yt = np.where(lat < c1, 0, np.where(lat < c2, 1, 2))
    if noise:
        cum = CONF.cumsum(1)[yt]
        r = rng.random(len(yt))[:, None]
        yo = (r > cum).sum(1)
    else:
        yo = yt
    return (yo - 1).astype(int)
