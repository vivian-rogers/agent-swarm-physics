"""H112 statistics: Mantel-Haenszel risk ratios, mutual-leave excess, stick ratio, permutation null, DL pooling."""
from __future__ import annotations

import math

import numpy as np
import polars as pl

K_PRIMARY = 5


def pair_frame(pairs: pl.DataFrame, K: int = K_PRIMARY, unit: str = "") -> pl.DataFrame:
    """Uncensored pairs with outcome columns: any (>= 1 departs), both, di, dj, unaware, inflight, read."""
    if len(pairs) == 0:
        return pl.DataFrame()
    p = pairs.filter((pl.col(f"dep_i_{K}") >= 0) & (pl.col(f"dep_j_{K}") >= 0))
    return p.with_columns(
        pl.col(f"dep_i_{K}").cast(pl.Int8).alias("di"), pl.col(f"dep_j_{K}").cast(pl.Int8).alias("dj"),
        ((pl.col(f"dep_i_{K}") + pl.col(f"dep_j_{K}")) >= 1).cast(pl.Int8).alias("any"),
        ((pl.col(f"dep_i_{K}") + pl.col(f"dep_j_{K}")) == 2).cast(pl.Int8).alias("both"),
        (pl.col("cls") != "read").alias("unaware"), (pl.col("cls") == "inflight").alias("inflight"),
        (pl.col("cls") == "read").alias("read"), pl.lit(unit).alias("unit"))


def mh_rr(y: np.ndarray, x: np.ndarray, strata: np.ndarray) -> dict:
    """Mantel-Haenszel risk ratio of y (0/1) for x=True vs x=False; Greenland-Robins log-variance."""
    y = np.asarray(y, float); x = np.asarray(x, bool); strata = np.asarray(strata)
    num = den = 0.0; v = 0.0; R = S = 0.0
    n_used = 0
    for s in np.unique(strata):
        m = strata == s
        n1 = (x & m).sum(); n0 = (~x & m).sum()
        if n1 == 0 or n0 == 0:
            continue
        a = y[x & m].sum(); c = y[~x & m].sum(); N = n1 + n0
        num += a * n0 / N; den += c * n1 / N
        v += (n1 * n0 * (a + c) - a * c * N) / N ** 2
        n_used += N
    out = {"rr": float("nan"), "lo": float("nan"), "hi": float("nan"), "n": int(n_used)}
    if num > 0 and den > 0:
        rr = num / den
        se = math.sqrt(max(v, 0) / (num * den))
        out.update(rr=rr, lo=rr * math.exp(-1.96 * se), hi=rr * math.exp(1.96 * se), se_log=se)
    elif den > 0 and num == 0:
        out.update(rr=0.0)
    return out


def perm_p(y, x, strata, stat_obs: float, n: int = 2000, seed: int = 0) -> float:
    """One-sided permutation p (RR >= observed), labels shuffled within strata (time-shuffled null at matched lag)."""
    rng = np.random.default_rng(seed)
    y = np.asarray(y, float); x = np.asarray(x, bool); strata = np.asarray(strata)
    idx = [np.flatnonzero(strata == s) for s in np.unique(strata)]
    ge = 0; valid = 0
    for _ in range(n):
        xp = x.copy()
        for ii in idx:
            xp[ii] = x[rng.permutation(ii)]
        r = mh_rr(y, xp, strata)["rr"]
        if not np.isfinite(r):
            continue
        valid += 1
        ge += r >= stat_obs - 1e-12
    return float((1 + ge) / (1 + valid)) if valid else float("nan")


def mutual_excess(di: np.ndarray, dj: np.ndarray, clusters: np.ndarray, B: int = 500, seed: int = 0) -> dict:
    """M = P(both) / (P(i) P(j)); cluster bootstrap (e.g. by day)."""
    di = np.asarray(di, float); dj = np.asarray(dj, float)
    def M(a, b):
        pi, pj, pb = a.mean(), b.mean(), (a * b).mean()
        return pb / (pi * pj) if pi > 0 and pj > 0 else float("nan")
    est = M(di, dj)
    if len(di) < 5:
        return {"M": est, "lo": float("nan"), "hi": float("nan"), "n": int(len(di))}
    rng = np.random.default_rng(seed)
    cl = np.asarray(clusters); u = np.unique(cl); groups = [np.flatnonzero(cl == c) for c in u]
    bs = []
    for _ in range(B):
        ii = np.concatenate([groups[k] for k in rng.integers(0, len(u), len(u))])
        bs.append(M(di[ii], dj[ii]))
    bs = np.array(bs); bs = bs[np.isfinite(bs)]
    lo, hi = (np.percentile(bs, [2.5, 97.5]) if len(bs) > 20 else (float("nan"), float("nan")))
    return {"M": est, "lo": float(lo), "hi": float(hi), "n": int(len(di))}


def dl_pool(est, se) -> dict:
    est = np.asarray(est, float); se = np.asarray(se, float)
    ok = np.isfinite(est) & np.isfinite(se) & (se > 0)
    est, se = est[ok], se[ok]
    if len(est) == 0:
        return {"est": float("nan"), "lo": float("nan"), "hi": float("nan"), "k": 0, "tau2": float("nan")}
    w = 1 / se ** 2; mu = (w * est).sum() / w.sum()
    Q = (w * (est - mu) ** 2).sum(); df = len(est) - 1
    C = w.sum() - (w ** 2).sum() / w.sum()
    tau2 = max(0.0, (Q - df) / C) if C > 0 else 0.0
    ws = 1 / (se ** 2 + tau2); m = (ws * est).sum() / ws.sum(); s = math.sqrt(1 / ws.sum())
    return {"est": float(m), "lo": float(m - 1.96 * s), "hi": float(m + 1.96 * s), "k": int(len(est)), "tau2": float(tau2)}


def strata_of(df: pl.DataFrame, period_col: str = "unit") -> np.ndarray:
    return (df[period_col].cast(pl.String) + "|" + df["lag_bin"].cast(pl.String) + "|"
            + df["named"].cast(pl.String)).to_numpy()


def contrasts(pf: pl.DataFrame, n_perm: int = 2000, seed: int = 0) -> dict:
    """RR_U (unaware vs read), RR_F (in flight vs read; read + inflight rows only), per-class rates, M per class."""
    out = {"n_pairs": int(len(pf))}
    if len(pf) == 0:
        return out
    st = strata_of(pf)
    y = pf["any"].to_numpy()
    for cls in ("read", "silent", "inflight"):
        m = (pf["cls"] == cls).to_numpy()
        out[f"n_{cls}"] = int(m.sum())
        out[f"p_any_{cls}"] = float(y[m].mean()) if m.sum() else float("nan")
    u = pf["unaware"].to_numpy()
    out["rr_u"] = mh_rr(y, u, st)
    out["rr_u"]["p_perm"] = perm_p(y, u, st, out["rr_u"]["rr"], n_perm, seed) if np.isfinite(out["rr_u"]["rr"]) else float("nan")
    sub = pf.filter(pl.col("cls") != "silent")
    if len(sub) and sub["inflight"].sum() > 0:
        st2 = strata_of(sub)
        out["rr_f"] = mh_rr(sub["any"].to_numpy(), sub["inflight"].to_numpy(), st2)
    else:
        out["rr_f"] = {"rr": float("nan"), "lo": float("nan"), "hi": float("nan"), "n": int(len(sub))}
    days = pf["pt_date"].to_numpy()
    for lab, m in (("unaware", u), ("read", ~u)):
        out[f"M_{lab}"] = mutual_excess(pf["di"].to_numpy()[m], pf["dj"].to_numpy()[m], days[m], seed=seed)
    return out


def stick_ratio(pf: pl.DataFrame, solo: pl.DataFrame, K: int = K_PRIMARY) -> dict:
    """S = P(second mover departs | read) / P(departs | solo switch-in); MH over unit x named."""
    if len(pf) == 0 or len(solo) == 0:
        return {"rr": float("nan"), "lo": float("nan"), "hi": float("nan"), "n": 0}
    r = pf.filter(pl.col("read")).select(pl.col("dj").alias("y"), "unit", "named").with_columns(pl.lit(True).alias("x"))
    s = solo.filter(pl.col(f"dep_{K}") >= 0).select(pl.col(f"dep_{K}").cast(pl.Int8).alias("y"), "unit", "named") \
        .with_columns(pl.lit(False).alias("x"))
    d = pl.concat([r, s])
    st = (d["unit"].cast(pl.String) + "|" + d["named"].cast(pl.String)).to_numpy()
    return mh_rr(d["y"].to_numpy(), d["x"].to_numpy(), st)
