"""H12 round 1b: per-unit estimates (fixed activity table) into the shared per_period_estimates table.
Replication (scored units, H01's unit split; local ids where they do not match period_units): activity k and lambda_1 /
edge under the round-1 cross-day null and under the DQ8 null (trimmed + block-shift edge), talk lambda_1 / edge under
the DQ8 null. Native: #12 debates (PR on - off, unit 12a) and #26 vote windows (PR percentile, unit 26).
Usage: uv run python hypotheses/H12-groupthink-dimensional-collapse/analysis/r1b_estimates.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "infra/shared"))
import estimates as E  # noqa: E402
import numpy as np  # noqa: E402
import polars as pl  # noqa: E402

R = ROOT / "data/processed/H12-groupthink-dimensional-collapse/r1b"
SRC = "data/processed/H12-groupthink-dimensional-collapse/r1b/unit_table.parquet"
NSRC = "data/processed/H12-groupthink-dimensional-collapse/r1b/native/native.json"
NOTE = "round 1b: activity_bins_fixed"


def fin(x):
    return float(x) if x is not None and np.isfinite(x) else None


def unit_id(unit: str, g: int, pu: pl.DataFrame) -> tuple[str, str | None]:
    if unit == str(g):
        return E.map_unit(g), None
    return f"local:{unit}", unit


def main():
    ut = pl.read_parquet(R / "unit_table.parquet").filter(pl.col("scored"))
    units = pl.read_parquet(R / "units.parquet").select("unit", "n_days")
    ut = ut.join(units, on="unit", how="left", suffix="_u")
    rows = []
    for r in ut.iter_rows(named=True):
        g = int(r["goal_no"]); pu, loc = unit_id(r["unit"], g, None)
        base = {"period_unit": pu, "unit_local": loc, "goal_no": g, "role": "replication", "source": SRC, "status": "ok",
                "n": float(r["n_days"]), "n_kind": "days", "ci_kind": "none", "notes": NOTE}
        for stat, ch, col, meth, null in (
                ("collective_mode_count_k_cd", "activity", "k_cd", "eigenvalues of the equal-time activity correlation above the 95% cross-day surrogate edge (200)", "cross-day surrogate (whole-day grid)"),
                ("lambda1_over_crossday_edge", "activity", "l1_edge", "largest correlation eigenvalue / 95% cross-day surrogate edge", "cross-day surrogate (whole-day grid)"),
                ("collective_mode_count_k_trim", "activity", "k_trim", "eigenvalues above the 95% block-shift edge after trimming each day to the all-present window (DQ8)", "block shift on trimmed rows (DQ8)"),
                ("lambda1_over_trim_blockshift_edge", "activity", "l1_edge_trim", "largest correlation eigenvalue / 95% block-shift edge, trimmed rows (DQ8)", "block shift on trimmed rows (DQ8)"),
                ("lambda1_over_trim_blockshift_edge", "talk", "talk_l1_edge_trim", "largest talk-spin correlation eigenvalue / 95% block-shift edge, trimmed rows (DQ8)", "block shift on trimmed rows (DQ8)")):
            if r.get(col) is not None:
                rows.append({**base, "statistic": stat, "channel": ch, "estimate": fin(float(r[col])), "method": meth, "null": null})
    nat = json.loads((R / "native/native.json").read_text())
    a = nat["G12_motion"]["bge_h12"]
    rows.append({"period_unit": "12a", "goal_no": 12, "statistic": "pr_motion_on_minus_off_median", "channel": "content",
                 "estimate": a["median_diff"], "n": float(a["n_usable"]), "n_kind": "debates", "ci_kind": "none",
                 "method": "median over debates of PR(debate phase) - PR(verdict -> +20 min); rarefied n = 12, cap 4, 100 draws; bge regime-I whitened d = 32",
                 "null": f"paired one-sided Wilcoxon p = {a['wilcoxon_p_less']:.3f}", "role": "native", "source": NSRC, "status": "ok",
                 "notes": f"{NOTE}; gte median {nat['G12_motion']['gte_shared']['median_diff']:.2f}"})
    for k in ("E1", "E2"):
        b = nat["G26_votes"]["bge_h12"][k]
        rows.append({"period_unit": E.map_unit(26), "goal_no": 26, "statistic": f"pr_vote_window_percentile_{k}", "channel": "content",
                     "estimate": b["pct"], "n": float(nat["G26_votes"]["bge_h12"]["n_ref"]), "n_kind": "reference windows", "ci_kind": "none",
                     "method": "percentile of PR in the 30 min from the vote start among #26's other 30-min windows (PR30 estimator, n 30, cap 8)",
                     "null": "reference distribution of #26 windows", "role": "native", "source": NSRC, "status": "ok",
                     "notes": f"{NOTE}; {'contested approval vote + runoff (01-05)' if k == 'E1' else 'confirmatory re-election (01-09)'}; gte percentile {nat['G26_votes']['gte_shared'][k]['pct']:.2f}"})
    old = E.read_estimates()
    if old.height:
        keep = old.filter(~((pl.col("hypothesis") == "H12") & pl.col("source").is_in([SRC, NSRC])))
        if keep.height != old.height:
            keep.write_parquet(E.PATH, compression="zstd")
    out = E.write_estimates(rows, hypothesis="H12")
    print(out.height, "rows;", out.group_by("statistic", "channel", "role").len().sort("statistic"))


if __name__ == "__main__":
    main()
