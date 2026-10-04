"""H36 round 1b: per-period estimates in the shared schema (infra/shared/estimates.py: write_estimates).

Replication rows (one per non-holdout goal period with a scored kickoff, both embedding models): the kickoff-window
maximum (days -1..+1) of the pre-registered alarm score Z_phys, of the content channel Z_cont and of the rival R1, and
the number of placebo days with their alarm count. Native rows: the window maxima at the four native targets
(NE39, NE40, NE43a/b, NE45), attached to the goal period that contains them. ci_kind none (single-day z-scores).

Usage: uv run python hypotheses/H36-reorganization-alarm/analysis/r1b_estimates.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import h36lib as L  # noqa: E402

sys.path.insert(0, str(L.ROOT / "infra/shared"))
import estimates as E  # noqa: E402

import numpy as np  # noqa: E402
import polars as pl  # noqa: E402

TAGS = {"bge_small": "fixed_bge_restate", "gte_modernbert": "fixed_gte_restate"}


def main():
    rows = []
    for model, tag in TAGS.items():
        d = L.OUT / "r1b" / tag
        et = pl.read_parquet(d / "event_table.parquet")
        res = json.loads((d / "results.json").read_text())
        meth = (f"round 1b: trailing robust z (10 active days, consistency-corrected) of surrogate-excess day statistics; "
                f"activity_bins_fixed + outages_fixed mask; content {model}, restatements removed")
        src = f"data/processed/H36-reorganization-alarm/r1b/{tag}/event_table.parquet"
        for r in et.filter(pl.col("cls") == "goal").iter_rows(named=True):
            g = int(r["ref"][1:])
            if r["n_scored"] == 0:
                continue
            pu = E.map_unit(g)
            for k, stat in (("Z_phys", "alarm_Zphys_kickoff_window_max"), ("Z_cont", "alarm_Zcont_kickoff_window_max"),
                            ("R1", "rival_R1_kickoff_window_max")):
                v = r[f"{k}_wmax"]
                if v is None or not np.isfinite(v):
                    continue
                rows.append({"period_unit": pu, "goal_no": g, "statistic": stat, "channel": "content" if k != "Z_phys" else "activity+content",
                             "estimate": float(v), "ci_lo": None, "ci_hi": None, "ci_kind": "none", "n": float(r["n_scored"]),
                             "n_kind": "scored days in window", "method": meth, "null": "trailing 10-day baseline; alarm at z >= 2.0",
                             "role": "replication", "source": src, "unit_local": f"G{g:02d}", "first_day": r["pt_date0"],
                             "notes": f"embedding {model}"})
            p = res["periods"].get(f"G{g:02d}")
            if p and p["placebo_n"]:
                rows.append({"period_unit": pu, "goal_no": g, "statistic": "alarm_Zphys_placebo_far", "channel": "activity+content",
                             "estimate": p["placebo_fa"] / p["placebo_n"], "ci_lo": None, "ci_hi": None, "ci_kind": "none",
                             "n": float(p["placebo_n"]), "n_kind": "placebo days", "method": meth,
                             "null": "placebo days >= 3 active days from every catalogued event", "role": "replication",
                             "source": src.replace("event_table.parquet", "results.json"), "unit_local": f"G{g:02d}",
                             "notes": f"embedding {model}"})
        nat = json.loads((d / "native.json").read_text())
        for t, rec in nat.items():
            if "note" in rec:
                continue
            for k in ("Z_phys", "Z_cont", "R1", "C3", "Z_act"):
                x = rec[k]
                vals = [v for v in (x["d-1"], x["d0"], x["d+1"]) if v is not None]
                if not vals:
                    continue
                rows.append({"period_unit": E.map_unit(rec["goal_no"]), "goal_no": rec["goal_no"],
                             "statistic": f"native_{t}_{k}_window_max", "channel": "content" if k in ("Z_cont", "R1", "C3") else "activity+content" if k == "Z_phys" else "activity",
                             "estimate": float(max(vals)), "ci_lo": None, "ci_hi": None, "ci_kind": "none", "n": 3.0,
                             "n_kind": "days in window", "method": meth, "null": "alarm at >= 2.0; blind dating vs candidate days",
                             "role": "native", "source": f"data/processed/H36-reorganization-alarm/r1b/{tag}/native.json",
                             "unit_local": t, "first_day": rec["day0"],
                             "notes": f"embedding {model}; percentile vs candidates {x['pct_vs_candidates']}"})
    out = E.write_estimates(rows, hypothesis="H36")
    print("wrote", out.height, "rows")


if __name__ == "__main__":
    main()
