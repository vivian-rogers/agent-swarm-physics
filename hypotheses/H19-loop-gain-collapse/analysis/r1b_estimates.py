"""H19 round 1b: per-period equal-time gains into the shared table (infra/shared/estimates.py: write_estimates).
One row per goal period x version (raw / DQ8 trim / H38-conditioned) x spin (activity / talk), windows combined by
inverse-variance weighting (r1b/estimates.parquet), CI from the day-bootstrap SE; plus the #51 per-unit gains of the
native N-sweep test. Supersedes the backfilled round-1 rows (buggy activity_bins).
Usage: uv run python hypotheses/H19-loop-gain-collapse/analysis/r1b_estimates.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import polars as pl

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "infra/shared"))
import estimates as E  # noqa: E402

D = ROOT / "data/processed/H19-loop-gain-collapse/r1b"
NOTE = "round 1b (2026-10-04): activity_bins_fixed + outages_fixed; supersedes the backfilled round-1 row (buggy activity_bins)"
VERS = {"": ("raw", "whole-day grid (pre-registered E1/E2)"),
        "_trim": ("trim", "all-present window, explained joint silences removed (DQ8)"),
        "_scaf": ("scaf", "H38 agent-state conditioning (mask_scaffold)")}


def main():
    est = pl.read_parquet(D / "estimates.parquet")
    rows = []
    for spin in ("active", "talk"):
        for sfx, (v, desc) in VERS.items():
            m = f"H19.geq_{spin}{sfx}"
            for r in est.filter(pl.col("method") == m).iter_rows(named=True):
                lo, hi = E.ci_from_se(r["value"], r["se"], 0.95)
                rows.append({"period_unit": E.map_unit(r["goal_no"]), "goal_no": r["goal_no"], "statistic": "loop_gain_g_eq",
                             "channel": "activity" if spin == "active" else "talk", "estimate": r["value"], "se": r["se"],
                             "ci_lo": lo, "ci_hi": hi, "ci_level": 0.95, "ci_kind": "se_z", "n": r["n_days"], "n_kind": "days",
                             "method": f"Curie-Weiss 1 - 1/VR in 30-min blocks (H02 rules), {desc}; day-bootstrap SE; chunks combined by inverse variance",
                             "null": None, "role": "replication", "status": "ok", "source": str((D / "estimates.parquet").relative_to(ROOT)),
                             "notes": f"{NOTE}; version {v}"})
    g = json.loads((D / "native_g51.json").read_text())
    for u, rec in g["units"].items():
        r = rec.get("active|trim")
        if not r or r.get("se") is None or not (r["se"] == r["se"]):
            continue
        lo, hi = E.ci_from_se(r["g"], r["se"], 0.95)
        rows.append({"period_unit": u, "goal_no": 51, "statistic": "loop_gain_g_eq", "channel": "activity", "estimate": r["g"],
                     "se": r["se"], "ci_lo": lo, "ci_hi": hi, "ci_level": 0.95, "ci_kind": "se_z", "n": rec["N"], "n_kind": "agents",
                     "method": "Curie-Weiss 1 - 1/VR, one window per shared unit, all-present window + stall mask (DQ8); day-bootstrap SE",
                     "null": None, "role": "native", "status": "ok", "source": str((D / "native_g51.json").relative_to(ROOT)),
                     "notes": f"{NOTE}; #51 N-sweep native test (N51-b failed: slope +0.025 per agent)"})
    out = E.write_estimates(rows, hypothesis="H19")
    print(out.height, "rows written")


if __name__ == "__main__":
    main()
