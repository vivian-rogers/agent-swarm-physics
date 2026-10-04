"""H60 replication: cross-fitted policy values on G51 (nudger-on days) and G38; counts for the small periods.

Usage: uv run python hypotheses/H60-index-nudge-policy/analysis/run_period.py
Writes data/processed/H60-index-nudge-policy/G<NN>/results.json.
"""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

import numpy as np
import polars as pl

sys.path.insert(0, str(Path(__file__).resolve().parent))
import h60lib as L  # noqa: E402

ELIGIBLE = (51, 38)
COUNT_ONLY = (37, 41, 44)
BOOT = {"calls30": 200, "sus": 100, "any": 100}


def verdict(r):
    ci_l = r["ci"]["index/logged"]
    ci_o = r["ci"]["index/once_early"]
    rl = r["ratios"]["index/logged"]
    ro = r["ratios"]["index/once_early"]
    if rl >= 2.3 and ci_l[0] > 1 and ro > 1 and ci_o[0] > 1:
        return "supported"
    if (ci_l[0] <= 1 <= ci_l[1]) or rl < 1.5:
        return "failed"
    return "mixed"


def one(df, per):
    out = {"period": f"G{per:02d}", "days": df["pt_date"].n_unique(), "agents": df["agent"].n_unique()}
    for oc in ("calls30", "sus", "any"):
        t0 = time.time()
        P = L.prep(df, oc)
        cf = L.crossfit(P)
        D = L.boot_crossfit(P, BOOT[oc], seed=per)
        vals = {p: float(cf[p]) for p in L.POL}
        rat = L.ratios(cf)
        cis = {}
        for num, den in (("index", "logged"), ("index", "once_early"), ("index_once", "logged"),
                         ("index", "index_ak"), ("random", "logged"), ("once_early", "logged"),
                         ("index_once", "once_early")):
            cis[f"{num}/{den}"] = L.ratio_ci(D, num, den)
        val_ci = {p: [float(np.nanpercentile(D[:, i], 2.5)), float(np.nanpercentile(D[:, i], 97.5))]
                  for i, p in enumerate(L.POL)}
        het = L.heterogeneity(P, B=BOOT[oc], seed=per + 1)
        r = {"n_gates": P["n"], "n_nudged": int(P["M"].sum()), "mean_y": float(P["y"].mean()),
             "values": vals, "values_ci": val_ci, "ratios": rat, "ci": cis, "het": het,
             "dV_logged": vals["logged"] - vals["random"], "dV_index": vals["index"] - vals["random"],
             "halves": cf["halves"], "n_boot": int(len(D)), "runtime_s": round(time.time() - t0, 1)}
        r["verdict"] = verdict(r)
        out[oc] = r
        print(out["period"], oc, r["verdict"], {k: round(v, 3) for k, v in vals.items()},
              {k: round(v, 2) for k, v in rat.items()}, {k: [round(x, 2) for x in v] for k, v in cis.items()},
              "het p", round(het["p"], 3), r["runtime_s"], flush=True)
    return out


def main():
    g = pl.read_parquet(L.OUT / "gates.parquet")
    for per in ELIGIBLE:
        df = g.filter((pl.col("goal_no") == per) & pl.col("nudger_on"))
        r = one(df, per)
        od = L.OUT / f"G{per:02d}"
        od.mkdir(parents=True, exist_ok=True)
        (od / "results.json").write_text(json.dumps(r, indent=1, default=float))
    for per in COUNT_ONLY:
        df = g.filter((pl.col("goal_no") == per) & pl.col("a_sus").is_not_null())
        r = {"period": f"G{per:02d}", "verdict": "descriptive (not eligible)", "n_gates": df.height,
             "n_nudged": int(df["nudged"].sum()), "days": df["pt_date"].n_unique()}
        od = L.OUT / f"G{per:02d}"
        od.mkdir(parents=True, exist_ok=True)
        (od / "results.json").write_text(json.dumps(r, indent=1))


if __name__ == "__main__":
    main()
