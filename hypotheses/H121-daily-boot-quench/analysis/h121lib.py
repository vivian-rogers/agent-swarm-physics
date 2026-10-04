"""H121 estimators: boot curve m(k), exponential fits, single-agent call memory rho_self, predictions, collapse,
late-booter contrast, wall-clock variant, random-effects pooling, and the call-grid simulator (axis F).

All inputs are frames with the columns written by scheme/build.py (agent, day, pt_date, k, Y, mins, block, ss, cls,
boot_lag_min, dt_prev, kickoff_day, n_ad). Nothing here reads held-out data.
"""
from __future__ import annotations

import math
import warnings

import numpy as np
import polars as pl
from scipy.optimize import curve_fit

warnings.filterwarnings("ignore", category=RuntimeWarning)


# ------------------------------------------------------------------ curves
def curve_arrays(df: pl.DataFrame, K: int):
    """m(k), n(k) for k = 0..K (equal weight per agent-day: each contributes one Y per k)."""
    d = df.filter(pl.col("k") <= K).group_by("k").agg(pl.col("Y").sum().alias("s"), pl.len().alias("n")).sort("k")
    k = d["k"].to_numpy()
    n = np.zeros(K + 1)
    s = np.zeros(K + 1)
    n[k] = d["n"].to_numpy()
    s[k] = d["s"].to_numpy()
    return np.arange(K + 1), s, n


def _exp1(k, minf, A, tau):
    return minf + A * np.exp(-k / tau)


def _exp2(k, minf, A1, t1, A2, t2):
    return minf + A1 * np.exp(-k / t1) + A2 * np.exp(-k / t2)


def fit_exp1(k, m, w, K: int):
    """WLS fit of m = minf + A exp(-k/tau); several starting taus, best weighted SSE. Returns dict."""
    ok = w > 0
    k, m, w = k[ok], m[ok], w[ok]
    if len(k) < 6:
        return None
    sig = 1 / np.sqrt(w)
    tail = m[k >= 0.6 * k.max()] if np.any(k >= 0.6 * k.max()) else m[-5:]
    m0 = float(np.average(tail, weights=w[k >= 0.6 * k.max()] if np.any(k >= 0.6 * k.max()) else None))
    best = None
    lo_t, hi_t = 0.2, 5.0 * K
    for t0 in (0.5, 2.0, 8.0, 30.0, 100.0, min(300.0, hi_t * 0.5)):
        try:
            p, _ = curve_fit(_exp1, k, m, p0=[m0, m[0] - m0 if abs(m[0] - m0) > 1e-3 else 0.05, t0], sigma=sig,
                             bounds=([-1, -2, lo_t], [2, 2, hi_t]), maxfev=4000)
        except Exception:
            continue
        sse = float(np.sum(w * (m - _exp1(k, *p)) ** 2))
        if best is None or sse < best[1]:
            best = (p, sse)
    if best is None:
        return None
    p, sse = best
    return {"minf": float(p[0]), "A": float(p[1]), "tau": float(p[2]), "sse": sse, "dof": len(k) - 3,
            "at_bound": bool(p[2] <= lo_t * 1.01 or p[2] >= hi_t * 0.99)}


def fit_exp2(k, m, w, K: int):
    ok = w > 0
    k, m, w = k[ok], m[ok], w[ok]
    if len(k) < 10:
        return None
    sig = 1 / np.sqrt(w)
    m0 = float(np.mean(m[k >= 0.6 * k.max()]))
    best = None
    for t1, t2 in ((0.5, 10.0), (1.0, 30.0), (2.0, 100.0), (5.0, 200.0), (0.5, 50.0)):
        try:
            p, _ = curve_fit(_exp2, k, m, p0=[m0, (m[0] - m0) / 2, t1, (m[0] - m0) / 2, t2], sigma=sig,
                             bounds=([-1, -2, 0.2, -2, 0.2], [2, 2, 5 * K, 2, 5 * K]), maxfev=6000)
        except Exception:
            continue
        sse = float(np.sum(w * (m - _exp2(k, *p)) ** 2))
        if best is None or sse < best[1]:
            best = (p, sse)
    return None if best is None else {"p": best[0], "sse": best[1]}


def curve_fit_df(df: pl.DataFrame, K: int):
    k, s, n = curve_arrays(df, K)
    m = np.where(n > 0, s / np.maximum(n, 1), np.nan)
    return fit_exp1(k, np.nan_to_num(m), n, K)


# ------------------------------------------------------------------ rho_self
def rho_self(df: pl.DataFrame) -> float:
    """Lag-1 autocorrelation of an agent's talk across consecutive receiving calls, steady-state calls only,
    centred per (agent, day, 30-min block); pairs need consecutive k, both steady state, same block."""
    d = (df.filter(pl.col("ss"))
         .with_columns((pl.col("Y") - pl.col("Y").mean().over("agent", "day", "block")).alias("x"))
         .sort("agent", "day", "k"))
    x = d["x"].to_numpy().astype(float)
    a = d["agent"].to_numpy()
    dy = d["day"].to_numpy()
    b = d["block"].to_numpy()
    k = d["k"].to_numpy()
    if len(x) < 50:
        return float("nan")
    same = (a[1:] == a[:-1]) & (dy[1:] == dy[:-1]) & (b[1:] == b[:-1]) & (k[1:] == k[:-1] + 1)
    num = float(np.sum(x[1:][same] * x[:-1][same]))
    den = float(np.sum(x ** 2))
    return num / den if den > 0 else float("nan")


def tau0_of(rho: float, floor: bool = True) -> float:
    if not np.isfinite(rho):
        return float("nan")
    if rho <= 0:
        return 1.0 if floor else float("nan")
    t = -1.0 / math.log(min(rho, 0.999999))
    return max(1.0, t) if floor else t


def tau_pred_hh(rho: float, g: float, floor: bool = True) -> float:
    g = min(max(g, -0.5), 0.99)
    return tau0_of(rho, floor) / (1.0 - g)


def tau_pred_ar(rho: float, g: float) -> float:
    lam = (rho if np.isfinite(rho) else 0.0) + g
    if lam >= 1:
        return float("inf")
    if lam <= 0:
        return 1.0
    return max(1.0, -1.0 / math.log(lam))


# ------------------------------------------------------------------ bootstrap over days
def resample(df: pl.DataFrame, rng, by_day: bool):
    if by_day:
        days = np.sort(df["day"].unique().to_numpy())
        pick = rng.choice(days, size=len(days), replace=True)
        parts = [df.filter(pl.col("day") == d).with_columns(pl.lit(j, dtype=pl.Int32).alias("rep"))
                 for j, d in enumerate(pick)]
        out = pl.concat(parts)
        return out.with_columns((pl.col("rep") * 1000 + pl.col("day")).cast(pl.Int32).alias("day"))
    ad = df.select("agent", "day").unique().sort("agent", "day")
    pick = rng.integers(0, ad.height, ad.height)
    sel = ad[pick].with_columns(pl.int_range(pl.len()).cast(pl.Int32).alias("rep"))
    out = df.join(sel, on=["agent", "day"], how="inner")
    return out.with_columns((pl.col("rep") * 1000 + pl.col("day").cast(pl.Int32)).alias("day"))


def unit_estimate(df: pl.DataFrame, K: int, g: float, g_se: float, B: int = 200, seed: int = 0,
                  min_days_cluster: int = 4) -> dict:
    """Point estimates and day-cluster bootstrap for tau_boot, rho_self, predictions, K."""
    rng = np.random.default_rng(seed)
    f = curve_fit_df(df, K)
    r = rho_self(df)
    if f is None:
        return {"ok": False}
    by_day = df["day"].n_unique() >= min_days_cluster
    tp = tau_pred_hh(r, g)
    ta = tau_pred_ar(r, g)
    taus, rhos, Ks, Kas, tps = [], [], [], [], []
    for _ in range(B):
        d = resample(df, rng, by_day)
        fb = curve_fit_df(d, K)
        rb = rho_self(d)
        if fb is None or not np.isfinite(rb):
            continue
        gb = g + (g_se if np.isfinite(g_se) else 0.0) * rng.standard_normal()
        taus.append(fb["tau"]); rhos.append(rb)
        tpb = tau_pred_hh(rb, gb); tps.append(tpb)
        Ks.append(fb["tau"] / tpb)
        tab = tau_pred_ar(rb, gb)
        Kas.append(fb["tau"] / tab if np.isfinite(tab) else np.nan)
    q = lambda a: (float(np.nanpercentile(a, 2.5)), float(np.nanpercentile(a, 97.5))) if len(a) > 10 else (np.nan, np.nan)  # noqa: E731
    out = {"ok": True, "tau": f["tau"], "minf": f["minf"], "A": f["A"], "at_bound": f["at_bound"],
           "chi2_dof": f["sse"] / max(f["dof"], 1), "rho": r, "tau0": tau0_of(r), "tau0_unfloored": tau0_of(r, False),
           "tau_pred": tp, "tau_pred_ar": ta, "K": f["tau"] / tp,
           "K_ar": f["tau"] / ta if np.isfinite(ta) else np.nan, "boot_by_day": by_day, "n_boot": len(taus)}
    out["tau_lo"], out["tau_hi"] = q(taus)
    out["rho_lo"], out["rho_hi"] = q(rhos)
    out["K_lo"], out["K_hi"] = q(Ks)
    out["K_ar_lo"], out["K_ar_hi"] = q(Kas)
    out["tau_pred_lo"], out["tau_pred_hi"] = q(tps)
    out["ln_tau_se"] = float(np.nanstd(np.log(taus))) if len(taus) > 10 else np.nan
    out["ln_K_se"] = float(np.nanstd(np.log(np.array(Ks)[np.array(Ks) > 0]))) if len(Ks) > 10 else np.nan
    return out


# ------------------------------------------------------------------ one exponential (CV over days)
def one_exp_cv(df: pl.DataFrame, K: int, seed: int = 0) -> dict:
    days = np.sort(df["day"].unique().to_numpy())
    if len(days) >= 2:
        halves = [df.filter(pl.col("day").is_in(days[0::2])), df.filter(pl.col("day").is_in(days[1::2]))]
    else:
        ad = df.select("agent").unique().sort("agent")["agent"].to_numpy().copy()
        rng = np.random.default_rng(seed)
        rng.shuffle(ad)
        h = ad[: len(ad) // 2]
        halves = [df.filter(pl.col("agent").is_in(h)), df.filter(~pl.col("agent").is_in(h))]
    sse1 = sse2 = 0.0
    for a, b in ((0, 1), (1, 0)):
        k, s, n = curve_arrays(halves[a], K)
        m = np.where(n > 0, s / np.maximum(n, 1), 0)
        kb, sb, nb = curve_arrays(halves[b], K)
        mb = np.where(nb > 0, sb / np.maximum(nb, 1), 0)
        f1 = fit_exp1(k, m, n, K)
        f2 = fit_exp2(k, m, n, K)
        if f1 is None or f2 is None:
            return {"cv_gain": np.nan}
        p1 = _exp1(kb, f1["minf"], f1["A"], f1["tau"])
        p2 = _exp2(kb, *f2["p"])
        sse1 += float(np.sum(nb * (mb - p1) ** 2))
        sse2 += float(np.sum(nb * (mb - p2) ** 2))
    return {"cv_gain": 1 - sse2 / sse1 if sse1 > 0 else np.nan, "cv_sse1": sse1, "cv_sse2": sse2}


# ------------------------------------------------------------------ per-day fits (collapse)
def log_bins(K: int):
    edges = sorted(set([0, 1, 2, 3, 4, 5] + [int(round(x)) for x in np.geomspace(6, K + 1, 18)]))
    edges = [e for e in edges if e <= K + 1]
    if edges[-1] != K + 1:
        edges.append(K + 1)
    return np.array(edges)


def binned_curve(df: pl.DataFrame, K: int):
    edges = log_bins(K)
    d = df.filter(pl.col("k") <= K).select("k", "Y")
    k = d["k"].to_numpy()
    y = d["Y"].to_numpy().astype(float)
    idx = np.searchsorted(edges, k, side="right") - 1
    nb = len(edges) - 1
    n = np.bincount(idx, minlength=nb).astype(float)
    s = np.bincount(idx, weights=y, minlength=nb)
    kc = np.bincount(idx, weights=k.astype(float), minlength=nb)
    kc = np.where(n > 0, kc / np.maximum(n, 1), 0)
    m = np.where(n > 0, s / np.maximum(n, 1), 0)
    return kc, m, n


def day_fit(df_day: pl.DataFrame, K: int, B: int, rng) -> dict:
    kc, m, n = binned_curve(df_day, K)
    f = fit_exp1(kc, m, n, K)
    if f is None:
        return {"tau": np.nan}
    agents = df_day["agent"].unique().to_numpy()
    taus = []
    for _ in range(B):
        pick = rng.choice(agents, size=len(agents), replace=True)
        d = pl.concat([df_day.filter(pl.col("agent") == a) for a in pick])
        kc2, m2, n2 = binned_curve(d, K)
        fb = fit_exp1(kc2, m2, n2, K)
        if fb is not None:
            taus.append(fb["tau"])
    lo, hi = (np.percentile(taus, 2.5), np.percentile(taus, 97.5)) if len(taus) >= 20 else (np.nan, np.nan)
    return {"tau": f["tau"], "tau_lo": float(lo), "tau_hi": float(hi), "A": f["A"], "minf": f["minf"],
            "resolved": bool(np.isfinite(lo) and lo > 0 and hi / lo < 4), "n_agents": len(agents)}


def i_squared(ln_t: np.ndarray, se: np.ndarray) -> float:
    ok = np.isfinite(ln_t) & np.isfinite(se) & (se > 0)
    if ok.sum() < 2:
        return np.nan
    w = 1 / se[ok] ** 2
    mu = np.sum(w * ln_t[ok]) / np.sum(w)
    Q = float(np.sum(w * (ln_t[ok] - mu) ** 2))
    dfree = ok.sum() - 1
    return max(0.0, (Q - dfree) / Q) if Q > 0 else 0.0


# ------------------------------------------------------------------ wall-clock variant
def wall_fit(df: pl.DataFrame, max_min: float):
    d = df.filter(pl.col("mins") <= max_min).with_columns(pl.col("mins").floor().cast(pl.Int32).alias("mb"))
    g = d.group_by("mb").agg(pl.col("Y").sum().alias("s"), pl.len().alias("n")).sort("mb")
    K = int(max_min)
    k = np.arange(K + 1)
    n = np.zeros(K + 1)
    s = np.zeros(K + 1)
    n[g["mb"].to_numpy()] = g["n"].to_numpy()
    s[g["mb"].to_numpy()] = g["s"].to_numpy()
    m = np.where(n > 0, s / np.maximum(n, 1), 0)
    return fit_exp1(k, m, n, K)


# ------------------------------------------------------------------ random effects
def re_pool(est: np.ndarray, se: np.ndarray):
    """DerSimonian-Laird random-effects mean of est (e.g. ln tau) with SEs; returns (mu, se_mu, tau2)."""
    ok = np.isfinite(est) & np.isfinite(se) & (se > 0)
    est, se = est[ok], se[ok]
    if len(est) == 0:
        return (np.nan, np.nan, np.nan)
    if len(est) == 1:
        return (float(est[0]), float(se[0]), 0.0)
    w = 1 / se ** 2
    mu_f = np.sum(w * est) / np.sum(w)
    Q = np.sum(w * (est - mu_f) ** 2)
    c = np.sum(w) - np.sum(w ** 2) / np.sum(w)
    t2 = max(0.0, (Q - (len(est) - 1)) / c) if c > 0 else 0.0
    wr = 1 / (se ** 2 + t2)
    mu = np.sum(wr * est) / np.sum(wr)
    return (float(mu), float(np.sqrt(1 / np.sum(wr))), float(t2))


# ------------------------------------------------------------------ simulator on real call grids (axis F)
def simulate_unit(df: pl.DataFrame, rng, rho: float, g: float, b: float = 0.2, F_amp: float = 0.0,
                  F_tau=30.0, start_talk: bool = True) -> pl.DataFrame:
    """Replace Y on the real grid by a linear per-call update:
       p_ik = b + rho (Y_i,k-1 - b) + J (R_ik - b n_ik) + F_amp exp(-k / F_tau[day]),
    R_ik = other agents' talk calls since i's previous call (one shared room), n_ik = other agents' calls in that
    window, J = g / (N_day - 1). Y_i,-1 = 1 (every agent starts in the talking state) if start_talk.
    F_tau may be a scalar or a dict day -> tau (heterogeneous days)."""
    out_y = np.zeros(df.height, dtype=np.int8)
    d = df.with_columns(pl.int_range(pl.len()).alias("_row"),
                        (pl.col("boot_lag_min") + pl.col("mins")).alias("_t"))
    for (day,), dd in d.group_by(["day"], maintain_order=True):
        dd = dd.sort("_t", "agent", "k")
        t = dd["_t"].to_numpy()
        a = dd["agent"].to_numpy().astype(int)
        k = dd["k"].to_numpy()
        rows = dd["_row"].to_numpy()
        agents = np.unique(a)
        N = len(agents)
        J = g / max(N - 1, 1)
        ftau = F_tau[day] if isinstance(F_tau, dict) else F_tau
        cum_calls = np.zeros(len(t) + 1)
        cum_talk = np.zeros(len(t) + 1)
        last_pos = {}
        prev_y = {ag: (1 if start_talk else 0) for ag in agents}
        for j in range(len(t)):
            ag = a[j]
            if ag in last_pos:      # calls strictly between ag's previous call and this one are other agents'
                p0 = last_pos[ag] + 1
                n_win = cum_calls[j] - cum_calls[p0]
                r_win = cum_talk[j] - cum_talk[p0]
            else:
                n_win = r_win = 0.0
            p = b + rho * (prev_y[ag] - b) + J * (r_win - b * n_win) + F_amp * math.exp(-k[j] / ftau)
            p = min(max(p, 0.0), 1.0)
            y = 1 if rng.random() < p else 0
            out_y[rows[j]] = y
            prev_y[ag] = y
            cum_calls[j + 1] = cum_calls[j] + 1
            cum_talk[j + 1] = cum_talk[j] + y
            last_pos[ag] = j
    return df.with_columns(pl.Series("Y", out_y))
