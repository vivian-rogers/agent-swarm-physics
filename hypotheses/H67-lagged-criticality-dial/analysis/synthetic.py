"""H67 synthetic validation (axis F), run before any real-data estimate.

Talk is simulated on the real call grids (call times, latencies, rooms, classes, all-present windows) of four
non-holdout units, with a shared OU rate field (tau 5 min, sigma 0.5) and a day-start edge in every arm:
  coupling worlds  g_true in {0.15, 0.30, 0.60}: read-out-gated (hop 1) talk response J = g / r_bar per read message
  null world       g_true = 0
  burst world      g_true = 0 plus room-wide 3-min conversation bursts (x4, one per 20 min)
For each run: g_lag (main variant, matched-lag placebo), the uncorrected naive gain, and the equal-time dial on the
same trimmed data. Output: data/processed/H67-lagged-criticality-dial/synthetic/runs.parquet + summary.json.

    uv run python hypotheses/H67-lagged-criticality-dial/analysis/synthetic.py [--reps 8] [--workers 4]
"""
from __future__ import annotations

import argparse
import json
from concurrent.futures import ProcessPoolExecutor

import numpy as np
import polars as pl

import h67lib as L

UNITS = ["27", "40", "41", "51e"]
WORLDS = [("null", 0.0, False), ("burst", 0.0, True), ("g015", 0.15, False), ("g030", 0.30, False),
          ("g060", 0.60, False)]


def design_rbar(c, m):
    d = L.counts(c, L.decision_times(m, c))
    rows = L._rows(d, True)
    win = rows.group_by("day").agg(pl.col("ap_lo").first(), pl.col("ap_hi").first())
    n = m.join(win, on="day").filter((pl.col("t") >= pl.col("ap_lo")) & (pl.col("t") <= pl.col("ap_hi"))).height
    return float(rows["R_all"].sum()) / max(n, 1)


def job(args):
    unit, world, g, burst, rep, rbar = args
    c = pl.read_parquet(L.OUT / "units" / f"{unit}.parquet")
    rng = np.random.default_rng(1000 * rep + hash((unit, world)) % 997)
    sim, m = L.simulate(c, g, rbar, rng, burst=burst)
    d = L.all_counts(sim, m)
    r = L.fit(d, m, "dm", True, B=100, seed=rep)
    rp = L.fit(d, m, "main", True, B=100, seed=rep)
    rn = L.fit(d, m, "naive", True, B=0, seed=rep)
    eq = L.equal_time(d, B=0)
    J = g / max(rbar, 1e-9)
    out = {"unit": unit, "world": world, "g_true_nominal": g, "rep": rep, "J_true": J}
    if r.get("ok"):
        out.update({k: r.get(k, np.nan) for k in ("g", "g_lo", "g_hi", "J1", "J1_lo", "J1_hi", "rbar", "mbar", "g3")})
        out["g_true"] = J * r["rbar"] * r["mbar"]
    if rp.get("ok"):
        out.update({"g_pm": rp["g"], "g_pm_lo": rp.get("g_lo", np.nan), "g_pm_hi": rp.get("g_hi", np.nan)})
    out["g_naive"] = rn.get("g", np.nan)
    out["g_eq"] = eq.get("g_eq", np.nan)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--reps", type=int, default=8)
    ap.add_argument("--workers", type=int, default=4)
    a = ap.parse_args()
    rb = {}
    for u in UNITS:
        c = pl.read_parquet(L.OUT / "units" / f"{u}.parquet")
        m = pl.read_parquet(L.OUT / "msgs" / f"{u}.parquet")
        rb[u] = design_rbar(c, m)
    print("design r_bar:", rb, flush=True)
    jobs = [(u, w, g, b, k, rb[u]) for u in UNITS for (w, g, b) in WORLDS for k in range(a.reps)]
    with ProcessPoolExecutor(a.workers) as ex:
        res = list(ex.map(job, jobs))
    df = pl.DataFrame(res)
    od = L.OUT / "synthetic"
    od.mkdir(parents=True, exist_ok=True)
    df.write_parquet(od / "runs.parquet")
    summ = {"design_rbar": rb}
    for w, g, b in WORLDS:
        s = df.filter(pl.col("world") == w)
        if g > 0:
            rel = ((s["g"] - s["g_true"]) / s["g_true"])
            cover = ((s["g_lo"] <= s["g_true"]) & (s["g_hi"] >= s["g_true"])).mean()
            summ[w] = {"median_rel_err": float(rel.median()), "rel_err_by_unit": s.with_columns(rel.alias("re"))
                       .group_by("unit").agg(pl.col("re").median()).sort("unit").to_dicts(),
                       "coverage": float(cover), "g_eq_over_true": float((s["g_eq"] / s["g_true"]).median()),
                       "g_eq_over_true_regIII": float((s.filter(pl.col("unit") != "27")["g_eq"]
                                                       / s.filter(pl.col("unit") != "27")["g_true"]).median()),
                       "g_naive_over_true": float((s["g_naive"] / s["g_true"]).median()),
                       "median_g": float(s["g"].median()), "median_g_true": float(s["g_true"].median()),
                       "pm_median_rel_err": float(((s["g_pm"] - s["g_true"]) / s["g_true"]).median())}
        else:
            summ[w] = {"median_g": float(s["g"].median()), "abs_med_g": float(s["g"].abs().median()),
                       "median_g_pm": float(s["g_pm"].median()),
                       "pm_ci_excl0_share": float(((s["g_pm_lo"] > 0) | (s["g_pm_hi"] < 0)).mean()),
                       "ci_excl0_share": float(((s["g_lo"] > 0) | (s["g_hi"] < 0)).mean()),
                       "median_g_naive": float(s["g_naive"].median()), "median_g_eq": float(s["g_eq"].median()),
                       "J1_within_ci_share": float(((s["J1_lo"] <= 0) & (s["J1_hi"] >= 0)).mean())}
    (od / "summary.json").write_text(json.dumps(summ, indent=1))
    print(json.dumps(summ, indent=1))


if __name__ == "__main__":
    main()
