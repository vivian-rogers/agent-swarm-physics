"""H04 round 1b: the round-1 design (explore.run_suite, unchanged) re-run on the corrected activity table only.

  uv run python hypotheses/H04-reversible-forcing/analysis/r1b_r1design.py

Separates the effect of the DQ8 event-drop fix from the design fixes in r1b.py: same isolation rule, same targets (all
valid mentions), same strata, same FD / Onsager / mean-field code, but activity from activity_bins_fixed.parquet.
Writes data/processed/H04-reversible-forcing/r1b/explore_kernels_fixedbins.json (round-1 files are not touched).
Hawkes n is not re-run: it uses chat_core talk events, not activity_bins, so the event-drop bug does not reach it.
"""
from __future__ import annotations

import os

for _v in ("POLARS_MAX_THREADS", "OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ[_v] = "2"
os.environ["H04_ACTIVITY_TABLE"] = "activity_bins_fixed.parquet"

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import explore as X  # noqa: E402

if __name__ == "__main__":
    assert X.ACTIVITY_TABLE == "activity_bins_fixed.parquet"
    out = X.OUT / "r1b"
    out.mkdir(parents=True, exist_ok=True)
    cal = X.calendar()
    suites = X.suite_days(cal)
    res = {k: X.run_suite(k, v) for k, v in suites.items() if len(v) >= 3}
    for v in res.values():
        v["activity_table"] = X.ACTIVITY_TABLE
    X.jdump(res, out / "explore_kernels_fixedbins.json")
    print("done")


def kickoffs():
    """P4 (goal-kickoff step response) on the corrected table: explore.kickoff_suite unchanged."""
    out = X.OUT / "r1b"
    cal = X.calendar()
    suites = X.suite_days(cal)
    ko = {k: X.kickoff_suite(k, v) for k, v in suites.items() if k in ("I", "II", "III") and len(v) >= 3}
    X.jdump(ko, out / "explore_kickoff_fixedbins.json")
    print({k: v.get("same_hours", {}).get("first60") for k, v in ko.items()})
