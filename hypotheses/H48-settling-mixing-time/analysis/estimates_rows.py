"""H48 per-period estimates in the shared per_period_estimates schema, written to H48's own data folder
(data/processed/H48-settling-mixing-time/estimates_H48.parquet). Merging into the shared table is the coordinator's
step (`infra/shared/estimates.py: write_estimates`), outside H48's edit scope.

  uv run python hypotheses/H48-settling-mixing-time/analysis/estimates_rows.py"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import h48lib as L  # noqa: E402,F401
from h48lib import hc  # noqa: E402

import polars as pl  # noqa: E402

sys.path.insert(0, str(hc.ROOT / "infra/shared"))
import estimates as E  # noqa: E402


def main():
    S = pl.read_parquet(hc.OUT / "settling_period.parquet")
    X = pl.read_parquet(hc.OUT / "readout_period.parquet")
    rows = []
    for g in hc.REPLICATION:
        unit = E.map_unit(g)
        role = "native" if g in (38, 51) else "replication"
        for model in ("bge_small", "gte_modernbert"):
            s = S.filter((pl.col("goal_no") == g) & (pl.col("model") == model) & (pl.col("estimator") == "S1"))
            if s.height and s["tau"][0] is not None:
                r = s.row(0, named=True)
                rows.append(dict(hypothesis="H48", period_unit=unit, goal_no=g, statistic="tau_settle_S1_active_h",
                                 channel=f"content_{model}", estimate=float(r["tau"]), ci_lo=None, ci_hi=None,
                                 n=float(r["n"] or 0), n_kind="active-hour bins", method="kickoff-excess plateau fit (1-h bins)",
                                 null="constant across periods (LOPO)", role=role, ci_kind="none",
                                 status="detected" if r["detected"] else "not_detected",
                                 source="data/processed/H48-settling-mixing-time/settling_period.parquet"))
        x = X.filter(pl.col("goal_no") == g).row(0, named=True)
        for stat, col, meth in (("readout_coverage_T90_k1_active_h", "k1_room_T90", "ledger reads, room-reachable pairs"),
                                ("readout_coverage_T90_k5_active_h", "k5_room_T90", "ledger reads, room-reachable pairs, depth 5"),
                                ("readout_bulk_mixing_time_active_h", "tmix_batch_bulk", "batch read-out chain, median-start TV 1/4"),
                                ("reading_turn_rate_per_active_h", "u", "median over kickoff roster, days 1-2"),
                                ("lambda2_wsym_min_block_per_active_h", "l2_sym_min", "ledger-read graph, min over room blocks")):
            rows.append(dict(hypothesis="H48", period_unit=unit, goal_no=g, statistic=stat, channel="readout",
                             estimate=float(x[col]) if x[col] is not None else None, ci_lo=None, ci_hi=None,
                             n=float(x["N"]), n_kind="agents", method=meth, null="none (predictor)", role=role,
                             ci_kind="none", source="data/processed/H48-settling-mixing-time/readout_period.parquet"))
    df = E.complete(E._frame(rows))
    probs = E.validate(df)
    df.write_parquet(hc.OUT / "estimates_H48.parquet")
    print(df.height, "rows;", "validation:", probs or "ok")


if __name__ == "__main__":
    main()
