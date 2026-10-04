"""H63 synthetic validation (axis F), run before any real-data statistic. Four worlds (work-led, co-burst, link-led,
null) at village counts (N = 12, 5 days of 4 or 8 h, 15 projects, ~20 events); 25 runs each. For each run: OR_S
(bursts vs matched non-burst clusters), the ordering share (first S before first link), and the hazard contrasts
dS = h_S - h_S' and dL = kappa - kappa'. Output: data/processed/H63-bursts-start-with-work/synthetic/.

    uv run python hypotheses/H63-bursts-start-with-work/analysis/synthetic.py [--runs 25] [--workers 4]
"""
from __future__ import annotations

import argparse
import json
from concurrent.futures import ProcessPoolExecutor

import numpy as np
import polars as pl

import h63lib as L

WORLDS = ["work", "burst", "link", "null"]


def one(args):
    world, k = args
    rng = np.random.default_rng(7919 * k + WORLDS.index(world))
    P = L.simulate(world, rng, base_rate=1 / 36000.0)
    arr = L.arrivals(P, trim=True)
    cl = L.clusters(arr, L.arrivals(P, trim=False))
    out = {"world": world, "run": k, "n_arrivals": arr.height}
    if cl.height:
        pre = L.precedence(P, cl)
        tb = L.table(pre, "S_pre")
        o = L.mh_or([tb])
        out.update({"n_bursts": int(pre.filter(pl.col("quiet") & (pl.col("n_agents") >= 3)).height),
                    "n_controls": int(pre.filter(pl.col("quiet") & (pl.col("n_agents") < 3)).height),
                    "OR_S": o["or"], "OR_S_lo": o["lo"], "OR_S_hi": o["hi"]})
        both = pre.filter(pl.col("quiet") & (pl.col("n_agents") >= 3) & pl.col("first_S").is_not_nan()
                          & pl.col("first_L").is_not_nan())
        out["n_both"] = both.height
        out["order_S_first"] = float((both["first_S"] < both["first_L"]).mean()) if both.height else np.nan
        ol = L.mh_or([L.table(pre, "L_pre")])
        out["OR_L"] = ol["or"]
    D, uni = L.risk_panel(P, trim=True)
    if D is not None:
        h = L.hazard(D, B=20, seed=k)
        for key in ("dS", "dS_lo", "dS_hi", "dL", "dL_lo", "dL_hi", "S", "S_lead", "L", "L_lead", "S_minus_R"):
            out[key] = h.get(key, np.nan)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--runs", type=int, default=25)
    ap.add_argument("--workers", type=int, default=4)
    a = ap.parse_args()
    jobs = [(w, k) for w in WORLDS for k in range(a.runs)]
    with ProcessPoolExecutor(a.workers) as ex:
        res = list(ex.map(one, jobs))
    df = pl.DataFrame(res, infer_schema_length=None)
    od = L.OUT / "synthetic"
    od.mkdir(parents=True, exist_ok=True)
    df.write_parquet(od / "runs.parquet")
    summ = {}
    for w in WORLDS:
        s = df.filter(pl.col("world") == w)
        p1 = (s["OR_S"] >= 2) & (s["OR_S_lo"] > 1)
        p3 = s["dS_lo"] > 0
        summ[w] = {"runs": s.height, "median_bursts": float(s["n_bursts"].median()),
                   "median_controls": float(s["n_controls"].median()),
                   "median_OR_S": float(s["OR_S"].median()), "P1_pass": float(p1.fill_null(False).mean()),
                   "P3_pass": float(p3.fill_null(False).mean()),
                   "P1_and_P3": float((p1 & p3).fill_null(False).mean()),
                   "median_dS": float(s["dS"].median()), "median_dL": float(s["dL"].median()),
                   "dL_pos_sig": float((s["dL_lo"] > 0).fill_null(False).mean()),
                   "dL_neg_or0": float((s["dL"] <= 0).fill_null(False).mean()),
                   "median_order_S_first": float(s["order_S_first"].median()),
                   "median_OR_L": float(s["OR_L"].median())}
    (od / "summary.json").write_text(json.dumps(summ, indent=1))
    print(json.dumps(summ, indent=1))


if __name__ == "__main__":
    main()
