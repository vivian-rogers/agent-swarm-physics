"""H105 estimators: two-state goal spins, heterogeneous Curie-Weiss (RPA) fit, tilt prediction of the variance,
logit-shift slope, coupling change, transverse control. Same code on real and synthetic data.

A segment is a spin matrix S[t, i] in {0, 1, nan} (windows x agents; nan = agent not eligible in that window),
plus per-window day labels. Statement-level counts K[t, i] (on-goal statements) and Nst[t, i] (statements) feed P2.
"""
from __future__ import annotations

import os

for _v, _n in (("POLARS_MAX_THREADS", "2"), ("OMP_NUM_THREADS", "2"), ("OPENBLAS_NUM_THREADS", "2"),
               ("MKL_NUM_THREADS", "2"), ("VECLIB_MAXIMUM_THREADS", "2")):
    os.environ.setdefault(_v, _n)

from pathlib import Path  # noqa: E402

import numpy as np  # noqa: E402
import polars as pl  # noqa: E402
from scipy.optimize import brentq  # noqa: E402

ROOT = Path(__file__).resolve().parents[3]
DATA = ROOT / "data/processed/H105-two-state-goal-order"
MIN_STMT_WIN = 2
MIN_WINDOWS = 6
LN15 = np.log(1.5)


# ============================================================================================ loading
def load(design: str):
    st = pl.read_parquet(DATA / f"stmt_{design}.parquet")
    pr = np.load(DATA / f"proj_{design}.npz")
    thr = pl.read_parquet(DATA / "thresholds.parquet").filter(pl.col("design") == design)
    return st, pr, thr


def threshold(thr: pl.DataFrame, direction: str, model: str, variant: str, q: int = 95) -> float:
    return float(thr.filter((pl.col("dir") == direction) & (pl.col("model") == model) & (pl.col("variant") == variant))[f"q{q}"][0])


def spin_tables(st: pl.DataFrame, onflag: np.ndarray, seg: str, agents=None, rule: str = "tie"):
    """Window x agent matrices for one segment: S (majority spin, nan if < MIN_STMT_WIN statements), K, N, day labels."""
    d = st.with_columns(pl.Series("on", onflag.astype(np.int8))).filter(pl.col("seg") == seg)
    g = d.group_by("pt_date", "win30", "agent").agg(pl.len().alias("n"), pl.col("on").sum().alias("k"))
    wins = g.select("pt_date", "win30").unique().sort("pt_date", "win30")
    ags = sorted(g["agent"].unique().to_list()) if agents is None else list(agents)
    wi = {(r["pt_date"], r["win30"]): j for j, r in enumerate(wins.iter_rows(named=True))}
    ai = {a: j for j, a in enumerate(ags)}
    T, A = wins.height, len(ags)
    K = np.zeros((T, A)); Nn = np.zeros((T, A))
    for r in g.iter_rows(named=True):
        if r["agent"] in ai:
            j = wi[(r["pt_date"], r["win30"])]; K[j, ai[r["agent"]]] = r["k"]; Nn[j, ai[r["agent"]]] = r["n"]
    on = (K >= 0.5 * Nn) if rule == "tie" else (K > 0.5 * Nn)
    S = np.where(Nn >= MIN_STMT_WIN, on.astype(float), np.nan)
    return dict(S=S, K=K, N=Nn, days=wins["pt_date"].to_numpy(), agents=ags)


def common_agents(F, A, min_windows=MIN_WINDOWS):
    okF = {a for j, a in enumerate(F["agents"]) if np.isfinite(F["S"][:, j]).sum() >= min_windows}
    okA = {a for j, a in enumerate(A["agents"]) if np.isfinite(A["S"][:, j]).sum() >= min_windows}
    return sorted(okF & okA)


def restrict(T, agents):
    idx = [T["agents"].index(a) for a in agents]
    out = dict(T)
    out["S"], out["K"], out["N"], out["agents"] = T["S"][:, idx], T["K"][:, idx], T["N"][:, idx], list(agents)
    keep = np.isfinite(out["S"]).sum(1) >= max(3, int(np.ceil(len(agents) / 2)))
    for k in ("S", "K", "N", "days"):
        out[k] = out[k][keep]
    return out


# ============================================================================================ CW / RPA statistics
def seg_stats(S, p_i=None, day_demean=False, days=None):
    """Occupancy statistics of a spin matrix. p_i: agent rates (default: from S)."""
    pres = np.isfinite(S)
    Nt = pres.sum(1)
    if p_i is None:
        p_i = np.nanmean(S, 0)
    p_t = np.nanmean(S, 1)
    P = np.where(pres, p_i[None, :], np.nan)
    mu_t = np.nanmean(P, 1)
    dev = p_t - mu_t
    if day_demean and days is not None:
        for d in np.unique(days):
            m = days == d
            if m.sum() > 1:
                dev[m] = dev[m] - dev[m].mean()
    V = float(np.mean(dev ** 2))
    v_i = p_i * (1 - p_i)
    S_t = np.nansum(np.where(pres, v_i[None, :], np.nan), 1)
    Vind_t = S_t / Nt ** 2
    q_t = S_t / Nt
    Vind = float(np.mean(Vind_t))
    R = V / Vind if Vind > 0 else np.nan
    g = 1 - 1 / R if np.isfinite(R) and R > 0 else np.nan
    J = g / float(np.mean(q_t)) if np.isfinite(g) and np.mean(q_t) > 0 else np.nan
    return dict(p=float(np.mean(p_t)), V=V, Vind=Vind, R=R, g=g, J=J, q=float(np.mean(q_t)), T=int(len(p_t)),
                p_i=p_i, Nt=Nt, pres=pres)


def logit(p):
    return np.log(p / (1 - p))


def smooth_rates(S):
    k = np.nansum(S, 0); n = np.isfinite(S).sum(0)
    return (k + 0.5) / (n + 1)


def rpa_var(pres, p_i, J):
    """Predicted mean_t Var(p_t) under the heterogeneous RPA with coupling J, on a given presence pattern."""
    v_i = p_i * (1 - p_i)
    Nt = pres.sum(1)
    S_t = np.where(pres, v_i[None, :], 0).sum(1)
    q_t = S_t / Nt
    mu_t = np.where(pres, p_i[None, :], 0).sum(1) / Nt
    gain = 1 - J * q_t
    cap = mu_t * (1 - mu_t)
    V_t = np.where(gain > 0.05, S_t / (Nt ** 2 * np.maximum(gain, 0.05)), cap)
    V_t = np.minimum(V_t, cap)
    return float(np.mean(V_t)), bool(np.any(gain <= 0.05))


def tilt_prediction(F_S, A_S, J_F, day_demean=False, A_days=None):
    """Fit the uniform tilt lambda to A's mean occupancy, predict A's variance with J_F."""
    pF = smooth_rates(F_S)
    presA = np.isfinite(A_S)
    pA_obs = float(np.mean(np.nanmean(A_S, 1)))

    def mean_pred(lam):
        pp = 1 / (1 + np.exp(-(logit(pF) + lam)))
        return float(np.mean(np.where(presA, pp[None, :], 0).sum(1) / presA.sum(1))) - pA_obs

    try:
        lam = brentq(mean_pred, -15, 15)
    except ValueError:
        lam = np.nan
    if not np.isfinite(lam):
        return dict(lam=np.nan, V_pred=np.nan, crit=False, p_pred=None)
    pp = 1 / (1 + np.exp(-(logit(pF) + lam)))
    Jf = J_F if np.isfinite(J_F) else 0.0
    Vp, crit = rpa_var(presA, pp, max(Jf, 0.0) if Jf > 0 else Jf)
    return dict(lam=float(lam), V_pred=Vp, crit=crit, p_pred=pp)


def pair_core(F_S, A_S, day_demean=False, F_days=None, A_days=None):
    sF = seg_stats(F_S, day_demean=day_demean, days=F_days)
    sA = seg_stats(A_S, day_demean=day_demean, days=A_days)
    tp = tilt_prediction(F_S, A_S, sF["J"])
    rho = np.log(sA["V"] / tp["V_pred"]) if tp["V_pred"] and tp["V_pred"] > 0 and sA["V"] > 0 else np.nan
    # coupling-only version: observed p_i^A, J_F
    Vp2, _ = rpa_var(np.isfinite(A_S), sA["p_i"], max(sF["J"], 0) if np.isfinite(sF["J"]) else 0)
    rho2 = np.log(sA["V"] / Vp2) if Vp2 > 0 and sA["V"] > 0 else np.nan
    return dict(pF=sF["p"], pA=sA["p"], VF=sF["V"], VA=sA["V"], RF=sF["R"], RA=sA["R"], gF=sF["g"], gA=sA["g"],
                JF=sF["J"], JA=sA["J"], qF=sF["q"], qA=sA["q"], lam=tp["lam"], VA_pred=tp["V_pred"], crit=tp["crit"],
                rho=float(rho), rho_coupling=float(rho2), dg=sA["g"] - sF["g"] if np.isfinite(sA["g"]) and np.isfinite(sF["g"]) else np.nan,
                growth_obs=float(np.log(sA["V"] / sF["V"])) if sF["V"] > 0 and sA["V"] > 0 else np.nan,
                growth_pred=float(np.log(tp["V_pred"] / sF["V"])) if sF["V"] > 0 and tp["V_pred"] and tp["V_pred"] > 0 else np.nan,
                TF=sF["T"], TA=sA["T"])


def block_indices(days, rng, block=4):
    """Moving-block bootstrap of window indices within days."""
    out = []
    for d in np.unique(days):
        ix = np.flatnonzero(days == d)
        n = len(ix)
        if n <= block:
            out.append(ix[rng.integers(0, n, n)])
            continue
        nb = int(np.ceil(n / block))
        starts = rng.integers(0, n - block + 1, nb)
        out.append(np.concatenate([ix[s:s + block] for s in starts])[:n])
    # resample days too (with replacement) to propagate day-level variation
    return np.concatenate(out)


def boot_pair(F, A, n_boot=1000, seed=0, day_demean=False):
    rng = np.random.default_rng(seed)
    keys = ("rho", "dg", "rho_coupling", "gF", "gA", "pA", "pF", "growth_obs", "growth_pred")
    out = {k: np.full(n_boot, np.nan) for k in keys}
    for b in range(n_boot):
        iF = block_indices(F["days"], rng); iA = block_indices(A["days"], rng)
        try:
            r = pair_core(F["S"][iF], A["S"][iA], day_demean, F["days"][iF], A["days"][iA])
        except (ZeroDivisionError, ValueError, FloatingPointError):
            continue
        for k in keys:
            out[k][b] = r[k]
    return out


def p1_verdict(rho, lo, hi):
    if not np.isfinite(rho):
        return "untestable"
    if lo <= 0 <= hi and abs(rho) < LN15:
        return "supported"
    if (lo > 0 or hi < 0) and abs(rho) >= LN15:
        return "failed"
    return "inconclusive"


# ============================================================================================ P2: logit-shift slope
def logit_slope(F, A, n_boot=1000, seed=0):
    """IV slope of logit f_i^A on logit f_i^F (statement-level rates), instrument = odd/even windows of F."""
    def rates(K, N, rows=None):
        if rows is not None:
            K, N = K[rows], N[rows]
        return logit((K.sum(0) + 0.5) / (N.sum(0) + 1))

    odd = np.arange(F["K"].shape[0]) % 2 == 1
    LA = rates(A["K"], A["N"]); LO = rates(F["K"], F["N"], odd); LE = rates(F["K"], F["N"], ~odd)

    def iv(ix):
        a, o, e = LA[ix], LO[ix], LE[ix]
        den = np.cov(e, o)[0, 1]
        return np.cov(a, o)[0, 1] / den if den > 0 else np.nan

    n = len(LA)
    s = iv(np.arange(n))
    rng = np.random.default_rng(seed)
    bs = np.array([iv(rng.integers(0, n, n)) for _ in range(n_boot)])
    rel = np.corrcoef(LO, LE)[0, 1]
    return dict(s=float(s), lo=float(np.nanpercentile(bs, 5)), hi=float(np.nanpercentile(bs, 95)), n=n,
                rel_F=float(rel), sd_LF=float(np.std((LO + LE) / 2)))


def p2_verdict(s, lo, hi):
    if not np.isfinite(s):
        return "untestable"
    if lo <= 1 <= hi and lo > 0:
        return "supported"
    if hi < 1 and s < 0.5:
        return "failed"
    return "inconclusive"
