"""H15 estimators, shared by synthetic.py (axis F) and run_scrambles.py (real data).

Panel convention: for one viability V, `u` is the same-day-differenced residual (V minus the leave-one-out mean of
the other agents that day), z-scored by the unit's residual SD. For one agent and one unit, x is an array over the
unit's active days (NaN where the agent has no value).

Counterfactuals for an event at index i0 (post window given as offsets from i0):
  ar1   mu + r_s (x[i0-1] - mu)       pre-registered AR form (r_s = pooled lag-s autocorrelation)
  kal   mu + rho^s E[h_{i0-1} | pre]   AR(1)+noise state space, Kalman-filtered over the pre window
  did   mean(pre)                      plain difference-in-differences (same-day differencing is already in u)
  naive same as did but on the undifferenced z(V)  (computed by the caller with a different panel)
"""
from __future__ import annotations

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scheme"))
import h15common  # noqa: E402,F401  (sets thread caps before numpy)

import numpy as np  # noqa: E402
import polars as pl  # noqa: E402

PRE = 5
METHODS = ("kal", "ar1", "did")


# ----------------------------------------------------------------------------- panel
def residual_panel(ad: pl.DataFrame, V: str, min_agents: int = 3) -> pl.DataFrame:
    """u = V - leave-one-out same-day mean, z-scored within unit. Also zV = V z-scored within unit (no differencing)."""
    d = ad.filter(pl.col(V).is_not_null() & pl.col(V).is_finite()).select("pt_date", "agent", "unit", "regime", V)
    d = d.with_columns(pl.col(V).sum().over("pt_date").alias("_s"), pl.len().over("pt_date").alias("_n"))
    d = d.filter(pl.col("_n") >= min_agents)
    d = d.with_columns((pl.col(V) - (pl.col("_s") - pl.col(V)) / (pl.col("_n") - 1)).alias("u_raw"))
    d = d.with_columns(((pl.col("u_raw") - pl.col("u_raw").mean().over("unit")) / pl.col("u_raw").std().over("unit"))
                       .alias("u"),
                       ((pl.col(V) - pl.col(V).mean().over("unit")) / pl.col(V).std().over("unit")).alias("zV"))
    return d.select("pt_date", "agent", "unit", "regime", "u", "zV").with_columns(
        pl.col("u").fill_nan(None), pl.col("zV").fill_nan(None))


class Panel:
    """Arrays per (agent, unit) over the unit's active days."""

    def __init__(self, rp: pl.DataFrame, unit_days: dict[str, list[str]], col: str = "u"):
        self.unit_days = unit_days
        self.day_idx = {u: {d: i for i, d in enumerate(ds)} for u, ds in unit_days.items()}
        self.x: dict[tuple[int, str], np.ndarray] = {}
        self.regime_of = {}
        for (a, u), g in rp.group_by(["agent", "unit"]):
            if u not in unit_days:
                continue
            arr = np.full(len(unit_days[u]), np.nan)
            for d, val in zip(g["pt_date"].to_list(), g[col].to_list()):
                if val is not None and d in self.day_idx[u]:
                    arr[self.day_idx[u][d]] = val
            self.x[(int(a), u)] = arr
            self.regime_of[u] = g["regime"][0]

    def get(self, a, u):
        return self.x.get((int(a), u))


def autocov_params(panel: Panel, units: list[str], exclude: dict | None = None, maxlag: int = 3):
    """Pooled (within agent-unit, demeaned) autocovariances -> AR(1)+noise params and empirical r_s."""
    sums = np.zeros(maxlag + 1)
    cnts = np.zeros(maxlag + 1)
    for (a, u), x in panel.x.items():
        if u not in units:
            continue
        y = x.copy()
        if exclude:
            for i in exclude.get((a, u), []):
                y[max(0, i):i + 3] = np.nan
        m = np.nanmean(y) if np.isfinite(y).sum() >= 4 else np.nan
        if not np.isfinite(m):
            continue
        y = y - m
        for k in range(maxlag + 1):
            p = y[k:] * y[:len(y) - k]
            ok = np.isfinite(p)
            sums[k] += p[ok].sum()
            cnts[k] += ok.sum()
    g = sums / np.maximum(cnts, 1)
    r = g / g[0]
    # AR(1)+noise: g1 = rho*Sh, g2 = rho^2*Sh  (Sh = stationary var of h)
    if g[1] > 1e-9 and g[2] > 0:
        rho = float(np.clip(g[2] / g[1], 0.0, 0.95))
        sh = float(g[1] / rho) if rho > 1e-6 else 0.0
    else:
        rho, sh = max(float(r[1]), 0.0), max(float(g[1]), 0.0)
    sh = min(sh, g[0] * 0.999)
    se = float(max(g[0] - sh, 1e-6))
    return {"rho": rho, "var_h": sh, "var_e": se, "r": [float(v) for v in r], "g": [float(v) for v in g],
            "n_pairs_lag1": int(cnts[1])}


def kalman_level(y: np.ndarray, rho: float, var_h: float, var_e: float) -> float:
    """E[h_last | y] for h AR(1) (stationary var var_h) observed with noise var_e; y already demeaned (NaN ok)."""
    q = var_h * (1 - rho ** 2)
    h, P = 0.0, var_h
    first = True
    for v in y:
        if not first:
            h, P = rho * h, rho ** 2 * P + q
        first = False
        if np.isfinite(v):
            K = P / (P + var_e)
            h, P = h + K * (v - h), (1 - K) * P
    return h


def event_delta(x: np.ndarray, i0: int, post_offsets: list[int], mu: float, prm: dict, pre: int = PRE):
    """ΔV for each method plus pre-trend slope. Returns None if the windows are not usable."""
    lo = i0 - pre
    if lo < 0:
        prew = x[max(0, lo):i0]
    else:
        prew = x[lo:i0]
    post_idx = [i0 + k for k in post_offsets if 0 <= i0 + k < len(x)]
    postv = np.array([x[i] for i in post_idx]) if post_idx else np.array([])
    if np.isfinite(prew).sum() < 2 or np.isfinite(postv).sum() < 1 or not np.isfinite(mu) or i0 < 1:
        return None
    last = x[i0 - 1]
    out = {}
    steps = np.array([k + 1 for k in post_offsets if 0 <= i0 + k < len(x)])  # steps ahead of day i0-1
    ok = np.isfinite(postv)
    # kal
    hl = kalman_level(prew - mu, prm["rho"], prm["var_h"], prm["var_e"])
    out["kal"] = float(np.mean(postv[ok] - mu - (prm["rho"] ** steps[ok]) * hl))
    # ar1 (last pre value; if missing, fall back to the Kalman level)
    r = prm["r"]
    rs = np.array([r[min(s, len(r) - 1)] for s in steps])
    base = (last - mu) if np.isfinite(last) else hl
    out["ar1"] = float(np.mean(postv[ok] - mu - rs[ok] * base))
    out["did"] = float(np.nanmean(postv) - np.nanmean(prew))
    t = np.arange(len(prew))
    okp = np.isfinite(prew)
    out["pretrend"] = float(np.polyfit(t[okp], prew[okp], 1)[0]) if okp.sum() >= 3 else float("nan")
    out["n_post"] = int(ok.sum())
    return out


def agent_mu(x: np.ndarray, event_idx: list[int], width: int = 3) -> float:
    y = x.copy()
    for i in event_idx:
        y[max(0, i):i + width] = np.nan
    return float(np.nanmean(y)) if np.isfinite(y).sum() >= 4 else float("nan")


def placebo_deltas(x: np.ndarray, event_idx: list[int], post_offsets: list[int], prm: dict, guard: int = 3,
                   pre: int = PRE):
    out = []
    mu = agent_mu(x, event_idx)
    for j in range(1, len(x)):
        if any(abs(j - i) <= guard for i in event_idx):
            continue
        r = event_delta(x, j, post_offsets, mu, prm, pre)
        if r is not None:
            out.append(r)
    return out


def unit_placebo_pool(panel: "Panel", unit: str, events_by_agent: dict, post_offsets: list[int], prm: dict,
                      cache: dict | None = None, guard: int = 3):
    """Placebo deltas pooled over ALL agents of a unit (each agent's own mu; windows near its events excluded).

    Amendment (2026-10-03, after the synthetic run, before real data): the same-agent-only pool has ~10-30
    correlated days per event, so the pool mean's own sampling error is not in the null SD and the period test
    over-rejects. The unit-wide pool keeps 'same unit, matched estimator' and makes the null calibrated."""
    key = (unit, tuple(post_offsets))
    if cache is not None and key in cache:
        return cache[key]
    pool = []
    for (a, u), x in panel.x.items():
        if u != unit:
            continue
        pool += placebo_deltas(x, events_by_agent.get((a, u), []), post_offsets, prm, guard)
    if cache is not None:
        cache[key] = pool
    return pool


def period_test(ev_vals: list[float], null_lists: list[list[float]], ndraw: int = 2000, rng=None):
    """Mean of event values vs. draws of one placebo per event. Returns mean, null mean/sd, z, p (two-sided)."""
    rng = rng or np.random.default_rng(0)
    keep = [(v, np.asarray(n, float)) for v, n in zip(ev_vals, null_lists)]
    keep = [(v, n[np.isfinite(n)]) for v, n in keep if np.isfinite(v)]
    keep = [(v, n) for v, n in keep if len(n) >= 3]
    if not keep:
        return None
    M = float(np.mean([v for v, _ in keep]))
    draws = np.zeros(ndraw)
    for v, n in keep:
        draws += n[rng.integers(0, len(n), ndraw)]
    draws /= len(keep)
    sd = float(draws.std(ddof=1)) if ndraw > 1 else float("nan")
    z = (M - draws.mean()) / sd if sd > 0 else float("nan")
    p = float((np.abs(draws - draws.mean()) >= abs(M - draws.mean())).mean())
    return {"n": len(keep), "mean": M, "null_mean": float(draws.mean()), "null_sd": sd, "z": float(z), "p": p,
            "effect": M - float(draws.mean())}


def dl_meta(effects: list[float], ses: list[float]):
    """DerSimonian-Laird random-effects meta-analysis."""
    e = np.asarray(effects, float)
    s = np.asarray(ses, float)
    ok = np.isfinite(e) & np.isfinite(s) & (s > 0)
    e, s = e[ok], s[ok]
    if len(e) == 0:
        return None
    w = 1 / s ** 2
    fe = float((w * e).sum() / w.sum())
    Q = float((w * (e - fe) ** 2).sum())
    k = len(e)
    tau2 = max(0.0, (Q - (k - 1)) / (w.sum() - (w ** 2).sum() / w.sum())) if k > 1 else 0.0
    wr = 1 / (s ** 2 + tau2)
    mu = float((wr * e).sum() / wr.sum())
    se = float(math.sqrt(1 / wr.sum()))
    return {"k": k, "mu": mu, "se": se, "z": mu / se, "lo": mu - 1.96 * se, "hi": mu + 1.96 * se, "tau2": tau2,
            "Q": Q, "fe": fe}


def hockey_vs_linear(dose: np.ndarray, y: np.ndarray, grid=None):
    """Linear y = a + b d vs hockey-stick y = a + b max(0, d - d*); Gaussian AIC. Returns dict."""
    dose, y = np.asarray(dose, float), np.asarray(y, float)
    ok = np.isfinite(dose) & np.isfinite(y)
    dose, y = dose[ok], y[ok]
    n = len(y)
    if n < 5:
        return None
    grid = grid if grid is not None else np.linspace(0.5, 0.95, 46)

    def fit(X):
        beta, *_ = np.linalg.lstsq(X, y, rcond=None)
        rss = float(((y - X @ beta) ** 2).sum())
        return beta, rss

    bl, rl = fit(np.c_[np.ones(n), dose])
    aic_l = n * math.log(rl / n + 1e-12) + 2 * 3
    best = None
    for ds in grid:
        h = np.maximum(0, dose - ds)
        if h.std() == 0:
            continue
        b, r = fit(np.c_[np.ones(n), h])
        if best is None or r < best[2]:
            best = (ds, b, r)
    if best is None:
        return {"n": n, "slope_lin": float(bl[1]), "aic_lin": aic_l}
    aic_h = n * math.log(best[2] / n + 1e-12) + 2 * 4
    return {"n": n, "slope_lin": float(bl[1]), "int_lin": float(bl[0]), "aic_lin": aic_l, "aic_hockey": aic_h,
            "dstar": float(best[0]), "slope_hockey": float(best[1][1]), "dAIC_lin_minus_hockey": aic_l - aic_h}


def cluster_boot_diff(a_vals, a_cl, b_vals, b_cl, nboot=500, rng=None):
    """Mean(a) - mean(b) with a cluster bootstrap (clusters resampled within each group)."""
    rng = rng or np.random.default_rng(0)
    a_vals, b_vals = np.asarray(a_vals, float), np.asarray(b_vals, float)
    a_cl, b_cl = np.asarray(a_cl), np.asarray(b_cl)

    def groups(v, c):
        ok = np.isfinite(v)
        v, c = v[ok], c[ok]
        u, inv = np.unique(c, return_inverse=True)
        sums = np.bincount(inv, weights=v, minlength=len(u))
        cnts = np.bincount(inv, minlength=len(u)).astype(float)
        return sums, cnts

    sa, ca = groups(a_vals, a_cl)
    sb, cb = groups(b_vals, b_cl)
    if len(sa) < 3 or len(sb) < 3:
        return None
    est = sa.sum() / ca.sum() - sb.sum() / cb.sum()
    bs = np.empty(nboot)
    for i in range(nboot):
        ia = rng.integers(0, len(sa), len(sa))
        ib = rng.integers(0, len(sb), len(sb))
        bs[i] = sa[ia].sum() / ca[ia].sum() - sb[ib].sum() / cb[ib].sum()
    return {"est": float(est), "lo": float(np.percentile(bs, 2.5)), "hi": float(np.percentile(bs, 97.5)),
            "se": float(bs.std(ddof=1)), "n_a": int(ca.sum()), "n_b": int(cb.sum()),
            "clusters_a": int(len(sa)), "clusters_b": int(len(sb))}


def spearman(x, y):
    x, y = np.asarray(x, float), np.asarray(y, float)
    ok = np.isfinite(x) & np.isfinite(y)
    if ok.sum() < 5:
        return float("nan"), 0
    rx = np.argsort(np.argsort(x[ok]))
    ry = np.argsort(np.argsort(y[ok]))
    return float(np.corrcoef(rx, ry)[0, 1]), int(ok.sum())
