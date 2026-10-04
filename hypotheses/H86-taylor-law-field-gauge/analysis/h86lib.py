"""H86 library: Taylor fits and the shared-field coefficient on per-agent bin counts.

Count model: y_it ~ Poisson(mu_i xi_t zeta_it); V_i = mu_i + [c_x + s_i(1 + c_x)] mu_i^2; Cov_ij = c_x mu_i mu_j.
Statistics on one cell set (cells = (pt_date, bin); agents in columns; NaN = agent absent that day):
  c_T, a   OLS of the Fano factor F_i = V_i/mu_i on mu_i across agents (V = a mu + c_T mu^2)
  b        OLS slope of ln V_i on ln mu_i across agents (b_ad: across agent-days with >= 4 bins)
  c_x      sum_{i<j} n_ij Cov_ij / sum_{i<j} n_ij mu_i mu_j over common cells (pair-specific means)
  c_xw     the same on counts demeaned within agent-day, normalized by agent-day means (within-day field)
  phi      c_x * sum_i mu_i^2 / sum_i (V_i - mu_i): shared share of the super-Poisson variance
Null: circular shift of each agent's series within each day (trimmed grid only), for c_xw.
No imports from other hypotheses.
"""
from __future__ import annotations

import os

for _v in ("POLARS_MAX_THREADS", "OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "2")
from pathlib import Path  # noqa: E402

import numpy as np  # noqa: E402
import polars as pl  # noqa: E402

ROOT = Path(__file__).resolve().parents[3]
DATA = ROOT / "data/processed/H86-taylor-law-field-gauge"
MIN_CELLS, MIN_AGENTS = 8, 4


def matrix(df: pl.DataFrame, channel: str):
    """Cells x agents array (NaN where the agent is absent), cell day labels, agent ids."""
    piv = df.pivot(on="agent", index=["pt_date", "bin"], values=channel, aggregate_function="sum").sort("pt_date", "bin")
    agents = [c for c in piv.columns if c not in ("pt_date", "bin")]
    Y = piv.select(agents).to_numpy().astype(float)
    return Y, piv["pt_date"].to_numpy(), np.array([int(a) for a in agents])


def _pair_sums(Y, P):
    Y0 = np.where(P, Y, 0.0)
    Pf = P.astype(float)
    n = Pf.T @ Pf
    s = Y0.T @ Pf          # s[i, j] = sum of y_i over cells where i and j present
    p = Y0.T @ Y0
    return n, s, p


def c_cross(Y, P=None):
    P = ~np.isnan(Y) if P is None else P
    n, s, p = _pair_sums(Y, P)
    iu = np.triu_indices(Y.shape[1], 1)
    nn = n[iu]
    ok = nn > 1
    if not ok.any():
        return np.nan
    mi, mj = s[iu][ok] / nn[ok], s.T[iu][ok] / nn[ok]
    cov = p[iu][ok] / nn[ok] - mi * mj
    den = (nn[ok] * mi * mj).sum()
    return float((nn[ok] * cov).sum() / den) if den > 0 else np.nan


def c_cross_within(Y, days):
    """Within-day shared coefficient: deviations from agent-day means, normalized by agent-day mean products."""
    P = ~np.isnan(Y)
    D = np.zeros_like(Y)
    Mb = np.zeros_like(Y)
    for d in np.unique(days):
        r = days == d
        sub = Y[r]
        with np.errstate(invalid="ignore", divide="ignore"):
            mu = np.nanmean(sub, 0)
        pres = P[r].any(0)
        D[np.ix_(r, pres)] = sub[:, pres] - mu[pres]
        Mb[np.ix_(r, pres)] = mu[pres]
    D[~P] = 0.0
    Mb[~P] = 0.0
    iu = np.triu_indices(Y.shape[1], 1)
    num = (D.T @ D)[iu].sum()
    den = (Mb.T @ Mb)[iu].sum()
    return float(num / den) if den > 0 else np.nan


def taylor(Y, days=None, min_cells=MIN_CELLS, ad=True):
    """Per-agent mu, V over its cells; c_T, a, b, phi; b_ad over agent-days."""
    P = ~np.isnan(Y)
    ncell = P.sum(0)
    keep = ncell >= min_cells
    with np.errstate(invalid="ignore", divide="ignore"):
        mu = np.nanmean(Y, 0)
        V = np.nanvar(Y, 0, ddof=1)
    keep &= (mu > 0) & np.isfinite(V)
    out = {"n_agents": int(keep.sum()), "mu_med": float(np.median(mu[keep])) if keep.any() else np.nan}
    if keep.sum() < MIN_AGENTS:
        return out | {"c_T": np.nan, "a": np.nan, "b": np.nan, "phi": np.nan, "c_x": np.nan}
    m, v = mu[keep], V[keep]
    F = v / m
    X = np.column_stack([np.ones_like(m), m])
    a, cT = np.linalg.lstsq(X, F, rcond=None)[0]
    pos = v > 0
    b = np.polyfit(np.log(m[pos]), np.log(v[pos]), 1)[0] if pos.sum() >= MIN_AGENTS else np.nan
    cx = c_cross(Y[:, keep])
    exc = (v - m).sum()
    phi = cx * (m ** 2).sum() / exc if exc > 0 and np.isfinite(cx) else np.nan
    out |= {"c_T": float(cT), "a": float(a), "b": float(b), "phi": float(phi), "c_x": cx,
            "fano_med": float(np.median(F))}
    if days is not None and ad:
        mus, vs = [], []
        for d in np.unique(days):
            r = days == d
            sub = Y[r][:, keep]
            for k in range(sub.shape[1]):
                x = sub[:, k]
                x = x[~np.isnan(x)]
                if len(x) >= 4 and x.mean() > 0 and x.var(ddof=1) > 0:
                    mus.append(x.mean()); vs.append(x.var(ddof=1))
        out["b_ad"] = float(np.polyfit(np.log(mus), np.log(vs), 1)[0]) if len(mus) >= 8 else np.nan
    if days is not None:
        out["c_xw"] = c_cross_within(Y[:, keep], days)
    return out


def shift_null(Y, days, rng, n_surr=49):
    """Within-day circular shift per agent (trimmed grids only): null distribution of c_xw."""
    vals = np.empty(n_surr)
    ud = np.unique(days)
    rows = {d: np.where(days == d)[0] for d in ud}
    for s in range(n_surr):
        Z = Y.copy()
        for d in ud:
            r = rows[d]
            if len(r) < 2:
                continue
            for k in range(Y.shape[1]):
                col = Y[r, k]
                if np.isnan(col).all():
                    continue
                Z[r, k] = np.roll(col, rng.integers(1, len(r)))
        vals[s] = c_cross_within(Z, days)
    return vals


def boot(Y, days, rng, B=200, keys=("c_T", "b", "c_x", "c_xw", "phi")):
    """Day bootstrap (>= 3 days) or 1-hour block bootstrap within days (bins of 15 min: 4 per block)."""
    ud = np.unique(days)
    if len(ud) >= 3:
        blocks = {d: np.where(days == d)[0] for d in ud}
        labels = list(ud)
    else:
        idx = np.arange(len(days))
        lab = np.array([f"{d}:{i // 4}" for i, d in zip(idx, days)])
        blocks = {lb: np.where(lab == lb)[0] for lb in np.unique(lab)}
        labels = list(blocks)
    res = {k: [] for k in keys}
    for _ in range(B):
        pick = rng.choice(len(labels), len(labels), replace=True)
        ii, dd = [], []
        for j, p in enumerate(pick):
            r = blocks[labels[p]]
            ii.append(r)
            dd.append(np.array([f"{days[r[0]]}#{j}"] * len(r)))   # duplicated days stay separate days
        ii = np.concatenate(ii)
        st = taylor(Y[ii], np.concatenate(dd), ad=False)
        for k in keys:
            res[k].append(st.get(k, np.nan))
    ci = {}
    for k, v in res.items():
        v = np.asarray(v, float)
        v = v[np.isfinite(v)]
        ci[k] = (float(np.quantile(v, 0.025)), float(np.quantile(v, 0.975))) if len(v) > 20 else (np.nan, np.nan)
    return ci
