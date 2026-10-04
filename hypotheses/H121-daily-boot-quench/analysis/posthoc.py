"""H121 POST HOC analysis (labelled; written 2026-10-04 after the first real-data pass, see card "Post hoc").

The registered single-exponential fit is unstable because the real boot curve has two parts: a fast first-call
spike (one to a few calls) and a slow, day-scale talk excess. This script separates them with ratio estimators
(Known issues: prefer ratio estimators for decay times).

  plateau   m_plat = mean m(k) over k in [20, 60] (agent-day weighted)
  fast      e(k) = m(k) - m_plat;  r1 = e(1)/e(0), r2 = e(2)/e(0);  tau_fast = -1/ln r1 (0 if r1 <= 0)
            tau_fast2 = -2/ln r2 (consistency of one exponential within the fast part)
            K_fast = tau_fast / tau_pred (HH form, tau_pred from the unit's rho_self and g_lag; agent-day weighted)
  slow      S = [mean m(k), k in [20, 240]] / m_ss - 1, with m_ss the registered steady-state talk rate
Pools: per regime and per period (curves pooled over the units' agent-days), cluster bootstrap over unit-days (B = 400).
Natives: NE14, NE43, NE42 with the same estimators. Collapse proxy: odd vs even unit-days, kickoff vs other days.

    uv run python hypotheses/H121-daily-boot-quench/analysis/posthoc.py
"""
from __future__ import annotations

import os

for _v in ("POLARS_MAX_THREADS", "OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ.setdefault(_v, "2")

import json  # noqa: E402
import math  # noqa: E402
import sys  # noqa: E402
from pathlib import Path  # noqa: E402

import numpy as np  # noqa: E402
import polars as pl  # noqa: E402

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

ROOT = HERE.parents[2]
D = ROOT / "data/processed/H121-daily-boot-quench"
RES = D / "results"
B = 400


def frame(units: list[str], U: pl.DataFrame) -> pl.DataFrame:
    parts = []
    for j, u in enumerate(units):
        r = U.filter(pl.col("unit_id") == u).to_dicts()[0]
        d = (pl.read_parquet(D / "calls" / f"{u}.parquet", columns=["agent", "day", "k", "Y", "ss", "kickoff_day"])
             .filter(pl.col("k") <= 240)
             .with_columns((pl.col("day").cast(pl.Int32) + 1000 * j).alias("uday"),
                           pl.lit(r["tau_pred"]).alias("tau_pred")))
        parts.append(d)
    return pl.concat(parts)


def ss_rate(units, U):
    """Registered steady-state talk rate, agent-day weighted over units (from each unit's ss calls)."""
    num = den = 0.0
    for u in units:
        d = pl.read_parquet(D / "calls" / f"{u}.parquet", columns=["Y", "ss"]).filter(pl.col("ss"))
        num += float(d["Y"].sum()); den += d.height
    return num / den if den else np.nan


def stats(df: pl.DataFrame, m_ss: float) -> dict:
    g = df.group_by("k").agg(pl.col("Y").mean().alias("m"), pl.len().alias("n")).sort("k")
    m = dict(zip(g["k"].to_list(), g["m"].to_list()))
    n = dict(zip(g["k"].to_list(), g["n"].to_list()))
    pl_k = [k for k in range(20, 61) if k in m]
    m_plat = float(np.average([m[k] for k in pl_k], weights=[n[k] for k in pl_k])) if pl_k else np.nan
    e = [m.get(k, np.nan) - m_plat for k in range(4)]
    r1 = e[1] / e[0] if e[0] > 0 else np.nan
    r2 = e[2] / e[0] if e[0] > 0 else np.nan
    tf = (-1 / math.log(r1) if 0 < r1 < 1 else (0.0 if r1 <= 0 else np.inf)) if np.isfinite(r1) else np.nan
    tf2 = (-2 / math.log(r2) if 0 < r2 < 1 else (0.0 if r2 <= 0 else np.inf)) if np.isfinite(r2) else np.nan
    slow_k = [k for k in range(20, 241) if k in m]
    slow = float(np.average([m[k] for k in slow_k], weights=[n[k] for k in slow_k])) / m_ss - 1 if slow_k else np.nan
    tp = float(df.filter(pl.col("k") == 0)["tau_pred"].mean())
    return {"m0": m.get(0, np.nan), "m1": m.get(1, np.nan), "m2": m.get(2, np.nan), "m_plat": m_plat, "e0": e[0], "r1": r1,
            "r2": r2, "tau_fast": tf, "tau_fast2": tf2, "slow_excess": slow, "tau_pred": tp,
            "K_fast": tf / tp if np.isfinite(tf) else np.nan, "n_agentdays": int(df.filter(pl.col("k") == 0).height)}


def boot(df: pl.DataFrame, m_ss: float, seed: int = 0) -> dict:
    est = stats(df, m_ss)
    days = np.sort(df["uday"].unique().to_numpy())
    rng = np.random.default_rng(seed)
    parts = {d: df.filter(pl.col("uday") == d) for d in days}
    draws = {k: [] for k in ("tau_fast", "K_fast", "slow_excess", "r1", "e0")}
    for _ in range(B):
        pick = rng.choice(days, len(days), replace=True)
        s = stats(pl.concat([parts[d] for d in pick]), m_ss)
        for k in draws:
            draws[k].append(s[k])
    for k, v in draws.items():
        v = np.array(v, float)
        v = v[np.isfinite(v)]
        est[f"{k}_lo"], est[f"{k}_hi"] = (float(np.percentile(v, 2.5)), float(np.percentile(v, 97.5))) if len(v) > 20 else (np.nan, np.nan)
    return est


def main():
    U = pl.read_parquet(RES / "units.parquet").filter(pl.col("ok"))
    out = {"regimes": {}, "periods": {}, "natives": {}, "collapse_proxy": {}}
    for reg in ("I", "II", "III"):
        us = U.filter(pl.col("regime") == reg)["unit_id"].to_list()
        df = frame(us, U)
        mss = ss_rate(us, U)
        out["regimes"][reg] = boot(df, mss, 1) | {"m_ss": mss, "n_units": len(us)}
        # collapse proxy: odd vs even unit-days; kickoff vs other days
        days = np.sort(df["uday"].unique().to_numpy())
        cp = {}
        for nm, sub in (("odd", df.filter(pl.col("uday").is_in(days[0::2]))), ("even", df.filter(pl.col("uday").is_in(days[1::2]))),
                        ("kickoff", df.filter(pl.col("kickoff_day"))), ("other", df.filter(~pl.col("kickoff_day")))):
            if sub.height:
                cp[nm] = boot(sub, mss, 2)
        out["collapse_proxy"][reg] = cp
        print(reg, {k: round(v, 3) if isinstance(v, float) else v for k, v in out["regimes"][reg].items()}, flush=True)
    for (g,), s in U.group_by(["goal_no"], maintain_order=True):
        us = s["unit_id"].to_list()
        df = frame(us, U)
        out["periods"][int(g)] = boot(df, ss_rate(us, U), 3)
    nat = {"NE14": {"II": ["35", "36a"], "III": ["36b", "36c"]}, "NE42": {"39": ["39"], "40": ["40"], "41": ["41"]}}
    for ne, sides in nat.items():
        out["natives"][ne] = {nm: boot(frame(us, U), ss_rate(us, U), 4) for nm, us in sides.items()}
    # NE43: 51f vs first 5 days of 51g
    g = pl.read_parquet(D / "calls" / "51g.parquet")
    first5 = sorted(g["pt_date"].unique().to_list())[:5]
    f5 = frame(["51g"], U).join(g.select("day", "pt_date").unique(), on="day").filter(pl.col("pt_date").is_in(first5)).drop("pt_date")
    out["natives"]["NE43"] = {"before": boot(frame(["51f"], U), ss_rate(["51f"], U), 5),
                              "after": boot(f5, ss_rate(["51g"], U), 5)}
    (RES / "posthoc.json").write_text(json.dumps(out, indent=1, default=float))
    print(json.dumps({k: out[k] for k in ("natives", "collapse_proxy")}, indent=1, default=lambda x: round(float(x), 3))[:6000])


if __name__ == "__main__":
    main()
