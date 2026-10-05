"""H13 round 2: write per_period_estimates rows (ladder, read-out family contrast, talk, enculturation).

Usage: uv run python hypotheses/H13-family-fields/analysis/r2_write.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import polars as pl

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scheme"))
import r2lib as R  # noqa: E402
import build as B  # noqa: E402
import estimates as E  # noqa: E402

LEVEL_DESC = {"W1": "within-agent map, core14 (genre-controlled)", "W2": "within-agent map, S20 (genre-controlled)",
              "W3": "within-agent map, S20 + FW50 (genre-controlled)", "Wf": "within-agent map, FW50 (genre-controlled)",
              "P3": "pooled map, S20 + FW50 (genre-controlled); biased down under style-only null",
              "S-a'": "within-agent map, raw S20 (round-1 S-a')"}


def unit_base(u):
    a, b = B.UNITS[u][3], B.UNITS[u][4]
    g = B.UNITS[u][1]
    pu = E.map_unit(g, a, b) or f"local:{u}"
    return {"period_unit": pu, "goal_no": g, "unit_local": u, "first_day": a, "last_day": b, "role": "replication",
            "status": "round 2", "post_hoc": False}


def main():
    rows = []
    lad = json.loads((R.R2 / "ladder.json").read_text())
    src = "data/processed/H13-family-fields/r2/ladder.json"
    for model, ch in (("bge", "content:bge_small"), ("gte", "content:gte_modernbert")):
        for u, v in lad["units"][model].items():
            for lv in (["W1", "W2", "W3", "Wf", "P3", "S-a'"] if model == "bge" else ["W3"]):
                t = v[lv]
                lo, hi = E.ci_from_se(t["T"], t["se"])
                rows.append({**unit_base(u), "statistic": f"family_field_T_{lv.replace(chr(39), 'p')}", "channel": ch,
                             "estimate": t["T"], "se": t["se"], "ci_lo": lo, "ci_hi": hi, "ci_kind": "jackknife_z",
                             "n": v["N"], "n_kind": "agents", "method": f"T_field after style residualization: {LEVEL_DESC[lv]}",
                             "null": "lab-label permutation", "source": src, "notes": f"p={t['p']:.4f}; round 2 graded ladder"})
    ro = json.loads((R.R2 / "readout.json").read_text())
    src = "data/processed/H13-family-fields/r2/readout.json"
    for u, v in ro["units"].items():
        if v["eligible"]:
            for k, stat in (("same", "readout_J1_same_lab"), ("cross", "readout_J1_cross_lab"), ("delta_adj", "readout_family_delta_adj"),
                            ("all", "readout_J1_all")):
                t = v["bge_white32"][k]
                rows.append({**unit_base(u), "statistic": stat, "channel": "content:bge_small", "estimate": t["est"], "se": t["se"],
                             "ci_lo": t["lo"], "ci_hi": t["hi"], "ci_kind": "percentile", "n": v["n_h1"], "n_kind": "hop-1 rows (age < 60 s)",
                             "method": "matched-age hop-1 minus hop-0 content jump (H50 estimator); same vs cross lab, named-stratified",
                             "null": "in-flight (hop-0) placebo at matched age; 1-h block bootstrap", "source": src,
                             "notes": "round 2 R2-C"})
        t = v["talk"]["delta_adj"]
        rows.append({**unit_base(u), "statistic": "readout_talk_family_delta_adj", "channel": "talk", "estimate": t["est"],
                     "se": t["se"], "ci_lo": t["lo"], "ci_hi": t["hi"], "ci_kind": "percentile", "n": v["talk"]["n_calls"],
                     "n_kind": "calls", "method": "LPM talk ~ items read at the call (same/cross lab x named), agent-day FE; named-stratified beta_same - beta_cross",
                     "null": "zero; 1-h block bootstrap", "source": src, "notes": "round 2 R2-C"})
    enc = json.loads((R.R2 / "encult.json").read_text())
    src = "data/processed/H13-family-fields/r2/encult.json"
    pu = pl.read_parquet(R.SH / "period_units.parquet")
    ro_ = pl.read_parquet(R.SH / "roster.parquet", columns=["agent", "joined"])
    joined = dict(zip(ro_["agent"].to_list(), ro_["joined"].to_list()))
    for p in enc["bge_white32"]["per_joiner"]:
        J = joined[p["agent"]]
        hit = pu.filter((pl.col("first_day") <= J) & (pl.col("last_day") >= J) & (pl.col("goal_no") == p["goal_no"]))
        unit = hit["unit_id"][0] if hit.height else f"G{p['goal_no']:02d}"
        a = [x for x in p["a"] if x is not None]
        slope = float(np.polyfit(np.arange(len(a)), a, 1)[0]) if len(a) >= 3 else None
        base = {"period_unit": unit, "goal_no": p["goal_no"], "unit_local": f"joiner-{p['agent']}", "role": "native",
                "status": "round 2", "post_hoc": False, "source": src, "ci_kind": "none", "n_kind": "joiner statements, day 1",
                "n": p["n_stmt"][0], "null": "own-lab relabelling (pooled over joiners)", "channel": "content:bge_small"}
        rows.append({**base, "statistic": "newcomer_lab_alignment_day1", "estimate": p["a"][0],
                     "method": "a(1) = cos(v - m_d, h_own) - mean cos(v - m_d, h_other), 5-statement means, 20 draws",
                     "notes": "round 2 R2-B; per joiner"})
        if slope is not None:
            rows.append({**base, "statistic": "newcomer_lab_alignment_slope", "estimate": slope, "n": len(a), "n_kind": "joiner days",
                         "method": "OLS slope of a(d) over joiner days d = 1..6", "notes": "round 2 R2-B; per joiner"})
    w = E.write_estimates(rows, hypothesis="H13", replace_keys=("statistic", "channel", "method", "role", "source", "unit_local"))
    print("rows", w.height)


if __name__ == "__main__":
    main()
