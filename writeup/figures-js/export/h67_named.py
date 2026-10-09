"""H67 named vs other reads (Fig. fig:named): regime-III read-out loop gain g per unit, with the part carried by reads
that name the reader, and the 95% CI of g.

    uv run python writeup/figures-js/export/h67_named.py

Same rows as writeup/papers/thermodynamics/figs/make_card_cols.py:h67_named (the old h67_named_col.pdf): H67 results/units.parquet,
ok units of regime III, sorted by goal period and unit. Reserved periods are excluded by the card's build (asserted).
g is the one-kernel read-out gain (the paper's number: median 0.13 over 25 units); g_named and g_unnamed come from the
card's two-kernel fit and need not add up to g exactly (in 3 units g_unnamed < 0).
"""
from __future__ import annotations

import importlib.util

import polars as pl

from common import ROOT, write

spec = importlib.util.spec_from_file_location("shared_common", ROOT / "infra/shared/common.py")
sc = importlib.util.module_from_spec(spec); spec.loader.exec_module(sc)

SRC = ROOT / "data/processed/H67-lagged-criticality-dial/results/units.parquet"


def main():
    held = set(sc.load_holdout()["goal_periods_held_out"])
    u = pl.read_parquet(SRC)
    u = u.filter(pl.col("ok").fill_null(False) & (pl.col("regime") == "III")).sort("goal_no", "unit_id")
    assert not set(u["goal_no"].to_list()) & held
    med = float(u["g"].median())
    share = float((u["g_named"] / u["g"]).median())
    assert u.height == 25 and round(med, 2) == 0.13, (u.height, med)       # paper: 25 units, median 0.13
    assert float(u["g_hi"].max()) < 0.40 and round(float(u["g"].min()), 2) == 0.00 and round(float(u["g"].max()), 2) == 0.29
    units = [dict(unit=r["unit_id"], goal=r["goal_no"], g=r["g"], lo=r["g_lo"], hi=r["g_hi"], named=r["g_named"],
                  unnamed=r["g_unnamed"]) for r in u.iter_rows(named=True)]
    print(f"{u.height} units, median g {med:.4f}, median named share {share:.2f}, max hi {u['g_hi'].max():.3f}")
    write("h67_named", dict(units=units, median=med, named_share_median=share),
          "writeup/figures-js/export/h67_named.py", ["data/processed/H67-lagged-criticality-dial/results/units.parquet"],
          dict(regime="III", filter="ok"))


if __name__ == "__main__":
    main()
