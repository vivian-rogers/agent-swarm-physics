"""H67 dial (Fig. dial): per goal period, read-out loop gain g (95% CI) against the equal-time talk dial g_eq.

    uv run python writeup/figures-js/export/h67_dial.py

Same input and selection as writeup/papers/thermodynamics/figs/make_card_cols.py (h67_dial; the old h67_dial_col.pdf):
data/processed/H67-lagged-criticality-dial/results/periods.parquet, every row, regime from the card. Reserved periods are
excluded by the card's build; asserted here against hypotheses/holdout.json.
"""
from __future__ import annotations

import importlib.util

import polars as pl

from common import ROOT, write

_spec = importlib.util.spec_from_file_location("shared_common", ROOT / "infra/shared/common.py")
SC = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(SC)


def main():
    P = pl.read_parquet(ROOT / "data/processed/H67-lagged-criticality-dial/results/periods.parquet")
    held = set(SC.load_holdout()["goal_periods_held_out"])
    assert not set(P["goal_no"].to_list()) & held, "reserved period in H67 periods"
    rows = [dict(goal=r["goal_no"], regime=r["regime"], g=r["g"], lo=r["g_lo"], hi=r["g_hi"], geq=r["g_eq"])
            for r in P.sort("regime", "goal_no").iter_rows(named=True)]
    print(P.group_by("regime").agg(pl.len(), pl.col("g").median(), pl.col("g_eq").median()).sort("regime").to_dicts())
    write("h67_dial", dict(periods=rows), "writeup/figures-js/export/h67_dial.py",
          ["data/processed/H67-lagged-criticality-dial/results/periods.parquet"])


if __name__ == "__main__":
    main()
