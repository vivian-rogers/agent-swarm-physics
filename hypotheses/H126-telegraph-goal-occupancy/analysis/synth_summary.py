"""Summarize the H126 synthetic (units.parquet, segments.parquet) into synthetic/summary.json.
P1 rule (oracle form): a replicate is 'heavy' if dLL_held exceeds the 95th percentile of the W1 replicates of the same
unit and qmode AND max CV >= 2. P2: |rho_p| <= ln 1.2 (within), > ln 1.3 (off). P5: dLL(call - wall) > 0.
Usage: uv run python hypotheses/H126-telegraph-goal-occupancy/analysis/synth_summary.py
"""
from __future__ import annotations

import json
import math
from pathlib import Path

import polars as pl

D = Path(__file__).resolve().parents[3] / "data/processed/H126-telegraph-goal-occupancy/synthetic"


def main():
    u = pl.read_parquet(D / "units.parquet")
    q95 = u.filter(pl.col("world") == "W1").group_by("design", "qmode").agg(pl.col("dll4_held").quantile(0.95).alias("q95"))
    u = u.join(q95, on=["design", "qmode"]).with_columns(
        ((pl.col("dll4_held") > pl.col("q95")) & (pl.max_horizontal("cv_on", "cv_off") >= 2)).alias("heavy"),
        (pl.col("dll4_held") > pl.col("q95")).alias("exceed"),
        (pl.col("rho_p").abs() <= math.log(1.2)).alias("within20"),
        (pl.col("rho_p").abs() > math.log(1.3)).alias("off30"),
        (pl.col("dllw_held") > 0).alias("call_wins"),
        (pl.col("raw_on_med") / pl.col("tau_on_med")).alias("raw_over_latent"),
        (pl.col("tau_on_med") / pl.col("tau_on_true")).alias("tau_ratio"),
        (pl.col("p_dw") / pl.col("p_true")).alias("p_ratio"))
    agg = u.group_by("world", "qmode").agg(
        pl.len().alias("n"), pl.col("heavy").mean(), pl.col("exceed").mean(), pl.col("within20").mean(),
        pl.col("off30").mean(), pl.col("call_wins").mean(), pl.col("tau_ratio").median(), pl.col("p_ratio").median(),
        pl.col("raw_over_latent").median(), pl.col("q1").median(), pl.col("q0").median(),
        pl.max_horizontal("cv_on", "cv_off").median().alias("cv_max_med")).sort("world", "qmode")
    by_reg = u.with_columns(pl.col("design").is_in(["U38a", "U41"]).alias("regIII")).group_by("world", "qmode", "regIII").agg(
        pl.col("heavy").mean(), pl.col("within20").mean(), pl.col("tau_ratio").median(), pl.col("p_ratio").median(),
        pl.col("call_wins").mean()).sort("world", "qmode", "regIII")
    s = pl.read_parquet(D / "segments.parquet")
    sagg = s.group_by("world", "design").agg(pl.len().alias("n"), (pl.col("verdict") == "k_on").mean().alias("k_on"),
                                             (pl.col("verdict") == "k_off").mean().alias("k_off"),
                                             pl.col("dln_a").median(), pl.col("dln_b").median()).sort("world", "design")
    out = dict(units=agg.to_dicts(), units_by_regime=by_reg.to_dicts(), segments=sagg.to_dicts(),
               n_unit_rows=u.height, n_seg_rows=s.height)
    (D / "summary.json").write_text(json.dumps(out, indent=1, default=float))
    pl.Config.set_tbl_rows(80)
    pl.Config.set_tbl_width_chars(250)
    print(agg)
    print(by_reg)
    print(sagg)


if __name__ == "__main__":
    main()
