"""H25 round 1b: per-period estimates on the fixed activity table into the shared per_period_estimates table.
Replication: fixed-effect IVW mean of the daily dial per period (activity and talk, auto stall mask; activity with the
DQ8 trim), 90% CI from the widened SE. Content is unchanged by the fix and is not rewritten. Native: within-#51
Spearman(g, N) per channel (size-law test). NE43 / NE42 are transition designs (no single-period rows).
Usage: uv run python hypotheses/H25-criticality-dial/analysis/r1b_estimates.py
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

R = ROOT / "data/processed/H25-criticality-dial/r1b"
SRC = "data/processed/H25-criticality-dial/r1b/dial_period.parquet"
NSRC = "data/processed/H25-criticality-dial/r1b/native/native.json"
NOTE = "round 1b: activity_bins_fixed + shared outages_fixed"


def fin(x):
    return float(x) if x is not None and np.isfinite(x) else None


def main():
    per = pl.read_parquet(R / "dial_period.parquet")
    rows = []
    for (ch, v, stat, meth, null) in (
            ("activity", "auto", "loop_gain_g_daily_dial", "fixed-effect IVW mean of daily Curie-Weiss dials (30-min blocks, null-calibrated stall mask); SE x1.5", "per-day block shift (whole-day grid)"),
            ("talk", "auto", "loop_gain_g_daily_dial", "fixed-effect IVW mean of daily Curie-Weiss dials (30-min blocks, null-calibrated stall mask); SE x1.5", "per-day block shift (whole-day grid)"),
            ("activity", "trim", "loop_gain_g_daily_dial_trim", "fixed-effect IVW mean of daily dials, stall mask + all-present window applied before the null (DQ8); SE x1.5", "per-day block shift after trimming (DQ8)"),
            ("talk", "trim", "loop_gain_g_daily_dial_trim", "fixed-effect IVW mean of daily dials, stall mask + all-present window applied before the null (DQ8); SE x1.5", "per-day block shift after trimming (DQ8)")):
        x = per.filter((pl.col("channel") == ch) & (pl.col("variant") == v))
        for r in x.iter_rows(named=True):
            g = int(r["goal_no"]); lo, hi = E.ci_from_se(fin(r["fe"]), fin(r["se_fe"]), 0.90)
            rows.append({"period_unit": E.map_unit(g), "goal_no": g, "statistic": stat, "channel": ch, "estimate": fin(r["fe"]),
                         "ci_lo": lo, "ci_hi": hi, "ci_level": 0.90, "ci_kind": "se_z", "se": fin(r["se_fe"]), "n": float(r["k"]),
                         "n_kind": "days", "method": meth, "null": null, "role": "replication", "source": SRC, "status": "ok",
                         "notes": f"{NOTE}; random-effects mean {fin(r['re']):.3f}" if fin(r["re"]) is not None else NOTE})
    nat = json.loads((R / "native/native.json").read_text())["G51_size_law"]
    for ch in ("activity", "talk", "content"):
        x = nat[ch]
        rows.append({"period_unit": "G51", "goal_no": 51, "statistic": "spearman_g_vs_N_within_period", "channel": ch,
                     "estimate": x["spearman_g_N"], "n": float(x["n_days"]), "n_kind": "days", "ci_kind": "none",
                     "method": "Spearman of daily dial g vs daily dial population N inside #51 (non-holdout days)",
                     "null": f"LOO SSE constant rho-bar {x['loo_sse_const_rho']:.3f} vs constant g {x['loo_sse_const_g']:.3f}",
                     "role": "native", "source": NSRC, "status": "ok", "notes": NOTE + "; native size-law test (uninformative)"})
    old = E.read_estimates()
    if old.height:
        keep = old.filter(~((pl.col("hypothesis") == "H25") & pl.col("source").is_in([SRC, NSRC])))
        if keep.height != old.height:
            keep.write_parquet(E.PATH, compression="zstd")
    out = E.write_estimates(rows, hypothesis="H25")
    print(out.height, "rows;", out.group_by("statistic", "channel", "role").len().sort("statistic"))


if __name__ == "__main__":
    main()
