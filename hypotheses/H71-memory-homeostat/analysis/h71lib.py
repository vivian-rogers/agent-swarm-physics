"""H71 estimators: panel AR(1) on post-compression memory size, model comparison, decomposition, clock, Onsager.

All functions take polars frames from scheme/build.py (cycles.parquet / snapshots.parquet) and return plain dicts.
Pairs (n-1 -> n) are used only when both cycles are in the same period (fits never cross a period boundary).
"""
from __future__ import annotations

import numpy as np
import polars as pl

RNG = np.random.default_rng(20261004)
MIN_PAIRS_AGENT = 15


# ---------------------------------------------------------------------------------------------- pairs
def pairs(cyc: pl.DataFrame) -> pl.DataFrame:
    """Consecutive compression cycles of one agent inside one period: x0 = x+_{n-1}, x1 = x+_n, y1 = peak before n."""
    c = cyc.sort("agent", "t")
    return (c.filter(pl.col("xplus_prev").is_not_null() & (pl.col("period_prev") == pl.col("period")))
            .select("agent", "period", "regime", "ctype", "t", "dt_s", "n_app",
                    pl.col("xplus_prev").alias("x0"), pl.col("xplus").alias("x1"), pl.col("ypeak").alias("y1")))


def _demean(p: pl.DataFrame) -> pl.DataFrame:
    """Agent means mu_i over all x+ values of the agent in the period (x0 and x1 pooled)."""
    mu = (pl.concat([p.select("agent", pl.col("x0").alias("x")), p.select("agent", pl.col("x1").alias("x"))])
          .group_by("agent").agg(pl.col("x").mean().alias("mu")))
    return p.join(mu, on="agent").with_columns((pl.col("x0") - pl.col("mu")).alias("d0"),
                                               (pl.col("x1") - pl.col("mu")).alias("d1"))


def phi_pooled(p: pl.DataFrame) -> float:
    q = _demean(p)
    den = float((q["d0"] ** 2).sum())
    return float((q["d0"] * q["d1"]).sum() / den) if den > 0 else float("nan")


def phi_hpj(p: pl.DataFrame) -> float:
    """Half-panel jackknife (Dhaene & Jochmans 2015): removes the O(1/T) Nickell bias of the within estimator."""
    full = phi_pooled(p)
    q = p.sort("agent", "t").with_columns(pl.int_range(pl.len()).over("agent").alias("k"),
                                          pl.len().over("agent").alias("T"))
    h1 = q.filter(pl.col("k") < pl.col("T") // 2)
    h2 = q.filter(pl.col("k") >= pl.col("T") // 2)
    if h1.height < 4 or h2.height < 4:
        return full
    return 2 * full - 0.5 * (phi_pooled(h1) + phi_pooled(h2))


def boot_agents(p: pl.DataFrame, fn, B: int = 500, rng=RNG) -> tuple[float, float, float]:
    """Cluster bootstrap over agents (agents resampled with replacement, relabelled)."""
    est = fn(p)
    ags = p["agent"].unique().to_list()
    if len(ags) < 2:
        return est, float("nan"), float("nan")
    parts = {a: p.filter(pl.col("agent") == a) for a in ags}
    vals = []
    for _ in range(B):
        pick = rng.choice(len(ags), size=len(ags), replace=True)
        fr = [parts[ags[j]].with_columns(pl.lit(int(k)).cast(pl.Int32).alias("agent")) for k, j in enumerate(pick)]
        v = fn(pl.concat(fr))
        if np.isfinite(v):
            vals.append(v)
    lo, hi = (np.percentile(vals, [2.5, 97.5]) if vals else (np.nan, np.nan))
    return est, float(lo), float(hi)


def ar2(p_cyc: pl.DataFrame) -> float:
    """AR(2) coefficient on the agent-demeaned x+ series (triples inside one period)."""
    c = p_cyc.sort("agent", "t").with_columns(
        pl.col("xplus").shift(1).over(["agent", "period"]).alias("l1"),
        pl.col("xplus").shift(2).over(["agent", "period"]).alias("l2")).drop_nulls(["l1", "l2"])
    if c.height < 10:
        return float("nan")
    mu = c.group_by("agent").agg(pl.col("xplus").mean().alias("mu"))
    c = c.join(mu, on="agent")
    y = (c["xplus"] - c["mu"]).to_numpy()
    X = np.column_stack([(c["l1"] - c["mu"]).to_numpy(), (c["l2"] - c["mu"]).to_numpy()])
    beta, *_ = np.linalg.lstsq(X, y, rcond=None)
    return float(beta[1])


def ar2_stat(p: pl.DataFrame) -> float:
    """AR(2) coefficient from a pairs frame rebuilt into series (for bootstrap)."""
    s = p.select("agent", "t", pl.col("x1").alias("xplus"), "period")
    return ar2(s)


# ---------------------------------------------------------------------------------------------- per agent
def per_agent(p: pl.DataFrame, min_pairs: int = MIN_PAIRS_AGENT) -> pl.DataFrame:
    rows = []
    for a, g in p.group_by("agent"):
        if g.height < min_pairs:
            continue
        ph = phi_pooled(g)
        T = g.height
        se = float(np.sqrt(max(1 - ph ** 2, 1e-3) / T))
        rows.append({"agent": int(a[0]), "phi": ph, "phi_hpj": phi_hpj(g), "se": se, "T": T,
                     "mu": float(np.mean(np.concatenate([g["x0"].to_numpy(), g["x1"].to_numpy()])))})
    return pl.DataFrame(rows) if rows else pl.DataFrame(schema={"agent": pl.Int64, "phi": pl.Float64,
                                                                "phi_hpj": pl.Float64, "se": pl.Float64,
                                                                "T": pl.Int64, "mu": pl.Float64})


def dl_tau(est: np.ndarray, se: np.ndarray) -> tuple[float, float, float]:
    """DerSimonian-Laird: pooled mean, its SE, and between-unit SD tau."""
    w = 1 / se ** 2
    m = np.sum(w * est) / np.sum(w)
    Q = np.sum(w * (est - m) ** 2)
    k = len(est)
    c = np.sum(w) - np.sum(w ** 2) / np.sum(w)
    tau2 = max(0.0, (Q - (k - 1)) / c) if c > 0 else 0.0
    ws = 1 / (se ** 2 + tau2)
    ms = np.sum(ws * est) / np.sum(ws)
    return float(ms), float(np.sqrt(1 / np.sum(ws))), float(np.sqrt(tau2))


# ---------------------------------------------------------------------------------------------- model comparison
def oos(cyc: pl.DataFrame, frac: float = 0.7, min_n: int = 20) -> pl.DataFrame:
    """Per agent and period: one-step MSE on the last 30% of its x+ series for RW, deadbeat, AR(1), AR(2)."""
    rows = []
    for (a, per), g in cyc.sort("t").group_by(["agent", "period"], maintain_order=True):
        x = g["xplus"].to_numpy()
        n = len(x)
        if n < min_n:
            continue
        k = int(np.floor(frac * n))
        tr, te = x[:k], x[k:]
        mu = tr.mean()
        d = tr - mu
        phi = float(np.sum(d[1:] * d[:-1]) / np.sum(d[:-1] ** 2)) if np.sum(d[:-1] ** 2) > 0 else 0.0
        X2 = np.column_stack([d[1:-1], d[:-2]])
        b2 = np.linalg.lstsq(X2, d[2:], rcond=None)[0] if len(d) > 4 else np.array([phi, 0.0])
        prev = x[k - 1:n - 1]
        prev2 = x[k - 2:n - 2]
        e_rw = te - prev
        e_db = te - mu
        e_ar = te - (mu + phi * (prev - mu))
        e_ar2 = te - (mu + b2[0] * (prev - mu) + b2[1] * (prev2 - mu))
        rows.append({"agent": int(a), "period": per, "n_test": len(te), "mse_rw": float(np.mean(e_rw ** 2)),
                     "mse_db": float(np.mean(e_db ** 2)), "mse_ar1": float(np.mean(e_ar ** 2)),
                     "mse_ar2": float(np.mean(e_ar2 ** 2)), "phi_train": phi})
    return pl.DataFrame(rows)


# ---------------------------------------------------------------------------------------------- mixed series
def mixed_phi(snaps: pl.DataFrame, period: str | None = None) -> float:
    """H09-style AR(1) on all snapshots (append + compress) in time order, agent-demeaned within period."""
    s = snaps.filter(pl.col("phase") != "same")
    if period is not None:
        s = s.filter(pl.col("period") == period)
    s = s.sort("agent", "t").with_columns(pl.col("lx").shift(1).over(["agent", "period"]).alias("l1")).drop_nulls("l1")
    if s.height < 10:
        return float("nan")
    mu = s.group_by("agent").agg(pl.col("lx").mean().alias("mu"))
    s = s.join(mu, on="agent")
    d1 = (s["lx"] - s["mu"]).to_numpy()
    d0 = (s["l1"] - s["mu"]).to_numpy()
    return float(np.sum(d0 * d1) / np.sum(d0 ** 2))


# ---------------------------------------------------------------------------------------------- decomposition
def decomposition(p: pl.DataFrame) -> dict:
    """b: within-agent slope of x+_n on the peak y_n; c: slope of the growth Delta_n = y_n - x+_{n-1} on x+_{n-1}."""
    q = p.with_columns((pl.col("y1") - pl.col("x0")).alias("grow"))
    m = q.group_by("agent").agg(pl.col("x0").mean().alias("m0"), pl.col("x1").mean().alias("m1"),
                                pl.col("y1").mean().alias("my"), pl.col("grow").mean().alias("mg"))
    q = q.join(m, on="agent")
    y = (q["y1"] - q["my"]).to_numpy()
    x1 = (q["x1"] - q["m1"]).to_numpy()
    x0 = (q["x0"] - q["m0"]).to_numpy()
    g = (q["grow"] - q["mg"]).to_numpy()
    b = float(np.sum(y * x1) / np.sum(y * y)) if np.sum(y * y) > 0 else float("nan")
    c = float(np.sum(x0 * g) / np.sum(x0 * x0)) if np.sum(x0 * x0) > 0 else float("nan")
    return {"b": b, "c": c, "b1c": b * (1 + c)}


# ---------------------------------------------------------------------------------------------- clock
def clock_slope(p: pl.DataFrame) -> dict:
    """phi+ in terciles of the cycle's wall-clock length dt, and the slope of phi on mean log dt."""
    q = p.filter(pl.col("dt_s") > 0).with_columns(pl.col("dt_s").log().alias("ldt"))
    if q.height < 30:
        return {"slope": float("nan")}
    qs = np.quantile(q["ldt"].to_numpy(), [1 / 3, 2 / 3])
    out, xs, ys = {}, [], []
    q = _demean(q)
    for k, (lo, hi) in enumerate([(-np.inf, qs[0]), (qs[0], qs[1]), (qs[1], np.inf)]):
        g = q.filter((pl.col("ldt") > lo) & (pl.col("ldt") <= hi))
        den = float((g["d0"] ** 2).sum())
        ph = float((g["d0"] * g["d1"]).sum() / den) if den > 0 else float("nan")
        out[f"phi_t{k + 1}"] = ph
        out[f"dt_med_t{k + 1}_s"] = float(np.exp(g["ldt"].median()))
        xs.append(float(g["ldt"].mean()))
        ys.append(ph)
    out["slope"] = float(np.polyfit(xs, ys, 1)[0]) if all(np.isfinite(ys)) else float("nan")
    return out


def clock_stat(p: pl.DataFrame) -> float:
    return clock_slope(p)["slope"]


def phi_by_type(p: pl.DataFrame, col: str = "ctype") -> dict:
    """phi+ restricted to pairs whose compression n is of a given type (forced / voluntary), common agent means."""
    q = _demean(p)
    out = {}
    for k, g in q.group_by(col):
        den = float((g["d0"] ** 2).sum())
        out[str(k[0])] = float((g["d0"] * g["d1"]).sum() / den) if den > 0 else float("nan")
    return out


def phi_forced_minus_vol(p: pl.DataFrame) -> float:
    d = phi_by_type(p)
    return d.get("forced", np.nan) - d.get("voluntary", np.nan)


def phi_forced(p: pl.DataFrame) -> float:
    return phi_by_type(p).get("forced", np.nan)


def phi_vol(p: pl.DataFrame) -> float:
    return phi_by_type(p).get("voluntary", np.nan)


# ---------------------------------------------------------------------------------------------- simulator (axis F)
def simulate_cycles(skel: pl.DataFrame, phi_b: float, c: float, s_grow: float = 0.15, s_comp: float = 0.15,
                    rng=RNG, wall_k: float | None = None) -> tuple[pl.DataFrame, pl.DataFrame]:
    """Two-phase sawtooth on a real cycle skeleton (agent, period, t, n_app per cycle).

    growth over a cycle Delta = d + c (x - mu) + xi, split over n_app appends; compression x' = mu + b (y - mu - d) + zeta,
    so that phi = b (1 + c). Returns (cycles, snapshots) in the scheme's schemas (subset of columns)."""
    cyc_rows, snap_rows = [], []
    for (a, per), g in skel.sort("t").group_by(["agent", "period"], maintain_order=True):
        mu = rng.normal(10.0, 0.5)
        d = abs(rng.normal(0.5, 0.15))
        b = phi_b / (1 + c) if (1 + c) != 0 else phi_b
        x = mu + rng.normal(0, 0.2)
        ts = g["t"].to_list()
        napps = g["n_app"].to_list()
        regime = g["regime"][0] if "regime" in g.columns else "III"
        ctypes = g["ctype"].to_list() if "ctype" in g.columns else ["forced"] * len(ts)
        dts = g["dt_s"].to_list() if "dt_s" in g.columns else [600.0] * len(ts)
        xprev, perprev = None, None
        for j, t in enumerate(ts):
            k = max(int(napps[j]), 0)
            if wall_k is not None:  # continuous-time relaxation: phi = exp(-k dt) per cycle
                dtj = dts[j] if (dts[j] is not None and np.isfinite(dts[j])) else 600.0
                b = float(np.exp(-wall_k * dtj)) / (1 + c)
            grow = d + c * (x - mu) + rng.normal(0, s_grow)
            y = x + grow
            # append snapshots: cumulative path toward y (k of them; the last equals y)
            for i in range(k):
                snap_rows.append({"agent": int(a), "t": t - np.timedelta64(int(60 * (k - i)), "s"), "period": per,
                                  "phase": "append", "lx": x + grow * (i + 1) / k})
            y_obs = y if k > 0 else x  # no append snapshot: the observed peak is the previous trough
            xn = mu + b * (y - mu - d) + rng.normal(0, s_comp)
            snap_rows.append({"agent": int(a), "t": t, "period": per, "phase": "compress", "lx": xn})
            cyc_rows.append({"agent": int(a), "t": t, "period": per, "regime": regime, "ctype": ctypes[j],
                             "xplus": xn, "ypeak": y_obs, "xplus_prev": xprev, "period_prev": perprev,
                             "dt_s": dts[j], "n_app": k})
            xprev, perprev = xn, per
            x = xn
    cyc = pl.DataFrame(cyc_rows, infer_schema_length=None)
    snaps = pl.DataFrame(snap_rows, infer_schema_length=None).sort("agent", "t")
    return cyc, snaps


# ---------------------------------------------------------------------------------------------- fast agent bootstrap
def _stats(x0: np.ndarray, x1: np.ndarray) -> tuple[float, float]:
    mu = np.concatenate([x0, x1]).mean()
    d0, d1 = x0 - mu, x1 - mu
    return float(np.sum(d0 * d1)), float(np.sum(d0 * d0))


def agent_stats(p: pl.DataFrame) -> np.ndarray:
    """Per agent: (S01, S00) for the full series and for each half (rows: agents; cols: 6)."""
    rows = []
    for _, g in p.sort("agent", "t").group_by("agent", maintain_order=True):
        x0, x1 = g["x0"].to_numpy(), g["x1"].to_numpy()
        h = len(x0) // 2
        f = _stats(x0, x1)
        a = _stats(x0[:h], x1[:h]) if h >= 2 else (0.0, 0.0)
        b = _stats(x0[h:], x1[h:]) if len(x0) - h >= 2 else (0.0, 0.0)
        rows.append([*f, *a, *b])
    return np.array(rows, dtype=float)


def hpj_from_stats(S: np.ndarray) -> float:
    full = S[:, 0].sum() / S[:, 1].sum()
    h1 = S[:, 2].sum() / S[:, 3].sum() if S[:, 3].sum() > 0 else full
    h2 = S[:, 4].sum() / S[:, 5].sum() if S[:, 5].sum() > 0 else full
    return float(2 * full - 0.5 * (h1 + h2))


def boot_hpj(p: pl.DataFrame, B: int = 1000, rng=RNG) -> tuple[float, float, float]:
    """phi+ (half-panel jackknife) with an agent cluster bootstrap, vectorised over agent sufficient statistics."""
    S = agent_stats(p)
    if len(S) == 0:
        return float("nan"), float("nan"), float("nan")
    est = hpj_from_stats(S)
    if len(S) < 2:
        return est, float("nan"), float("nan")
    idx = rng.integers(0, len(S), size=(B, len(S)))
    vals = np.array([hpj_from_stats(S[i]) for i in idx])
    vals = vals[np.isfinite(vals)]
    return est, float(np.percentile(vals, 2.5)), float(np.percentile(vals, 97.5))


# ---------------------------------------------------------------------------------------------- all-statistics fast bootstrap
STAT_NAMES = ("phi_hpj", "ar2", "b", "c", "clock_slope", "phi_forced", "phi_vol", "f_minus_v")


def agent_suff(p: pl.DataFrame, cuts: np.ndarray | None = None) -> tuple[np.ndarray, dict]:
    """Per-agent sufficient statistics for every bootstrapped statistic (one row per agent).

    Columns: [hpj 6] [ar2: Sxx(2x2) 4, Sxy 2] [b: Syx1, Syy] [c: Sx0g, Sx0x0] [clock: 3 x (S01, S00, sum ldt, n)]
             [type: forced (S01, S00), voluntary (S01, S00)]"""
    q = p.filter(pl.col("dt_s").is_not_null()).with_columns(
        pl.col("dt_s").clip(lower_bound=1).log().alias("ldt"), (pl.col("y1") - pl.col("x0")).alias("grow"))
    if cuts is None:
        cuts = np.quantile(q["ldt"].to_numpy(), [1 / 3, 2 / 3]) if q.height > 30 else np.array([0.0, 0.0])
    rows = []
    for _, g in q.sort("agent", "t").group_by("agent", maintain_order=True):
        x0, x1, y1 = g["x0"].to_numpy(), g["x1"].to_numpy(), g["y1"].to_numpy()
        gr, ldt = g["grow"].to_numpy(), g["ldt"].to_numpy()
        ct = g["ctype"].to_list()
        h = len(x0) // 2
        r = list(_stats(x0, x1))
        r += list(_stats(x0[:h], x1[:h])) if h >= 2 else [0.0, 0.0]
        r += list(_stats(x0[h:], x1[h:])) if len(x0) - h >= 2 else [0.0, 0.0]
        mu = np.concatenate([x0, x1]).mean()
        d0, d1 = x0 - mu, x1 - mu
        # AR(2): triples from consecutive pairs (x0[k] = x1[k-1] when consecutive)
        if len(d0) >= 3:
            Y, L1, L2 = d1[1:], d0[1:], d0[:-1]
            r += [np.sum(L1 * L1), np.sum(L1 * L2), np.sum(L2 * L1), np.sum(L2 * L2), np.sum(L1 * Y), np.sum(L2 * Y)]
        else:
            r += [0.0] * 6
        yc, x1c, x0c, gc = y1 - y1.mean(), x1 - x1.mean(), x0 - x0.mean(), gr - gr.mean()
        r += [np.sum(yc * x1c), np.sum(yc * yc), np.sum(x0c * gc), np.sum(x0c * x0c)]
        for lo, hi in ((-np.inf, cuts[0]), (cuts[0], cuts[1]), (cuts[1], np.inf)):
            m = (ldt > lo) & (ldt <= hi)
            r += [np.sum(d0[m] * d1[m]), np.sum(d0[m] ** 2), np.sum(ldt[m]), float(m.sum())]
        for t in ("forced", "voluntary"):
            m = np.array([c == t for c in ct])
            r += [np.sum(d0[m] * d1[m]), np.sum(d0[m] ** 2)]
        rows.append(r)
    return np.array(rows, dtype=float), {"cuts": cuts}


def stats_from_suff(S: np.ndarray) -> dict:
    s = S.sum(0)
    out = {}
    full = s[0] / s[1] if s[1] > 0 else np.nan
    h1 = s[2] / s[3] if s[3] > 0 else full
    h2 = s[4] / s[5] if s[5] > 0 else full
    out["phi_hpj"] = 2 * full - 0.5 * (h1 + h2)
    A = np.array([[s[6], s[7]], [s[8], s[9]]])
    try:
        out["ar2"] = float(np.linalg.solve(A, s[10:12])[1])
    except np.linalg.LinAlgError:
        out["ar2"] = np.nan
    out["b"] = s[12] / s[13] if s[13] > 0 else np.nan
    out["c"] = s[14] / s[15] if s[15] > 0 else np.nan
    xs, ys = [], []
    for k in range(3):
        b0 = 16 + 4 * k
        if s[b0 + 3] > 0 and s[b0 + 1] > 0:
            ys.append(s[b0] / s[b0 + 1])
            xs.append(s[b0 + 2] / s[b0 + 3])
    out["clock_slope"] = float(np.polyfit(xs, ys, 1)[0]) if len(xs) == 3 else np.nan
    out["phi_forced"] = s[28] / s[29] if s[29] > 0 else np.nan
    out["phi_vol"] = s[30] / s[31] if s[31] > 0 else np.nan
    out["f_minus_v"] = out["phi_forced"] - out["phi_vol"]
    return out


def boot_all(p: pl.DataFrame, B: int = 1000, rng=RNG) -> dict:
    """Point estimates and agent-cluster percentile CIs for every statistic in STAT_NAMES."""
    S, meta = agent_suff(p)
    est = stats_from_suff(S)
    if len(S) < 2:
        return {k: {"est": float(est[k]), "lo": np.nan, "hi": np.nan} for k in STAT_NAMES}
    idx = rng.integers(0, len(S), size=(B, len(S)))
    draws = [stats_from_suff(S[i]) for i in idx]
    out = {}
    for k in STAT_NAMES:
        v = np.array([d[k] for d in draws], dtype=float)
        v = v[np.isfinite(v)]
        out[k] = {"est": float(est[k]), "lo": float(np.percentile(v, 2.5)) if len(v) > 10 else np.nan,
                  "hi": float(np.percentile(v, 97.5)) if len(v) > 10 else np.nan}
    out["_cuts_ldt"] = meta["cuts"].tolist()
    return out
