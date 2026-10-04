"""H71 scheme: phase-labelled memory snapshots and compression cycles (non-holdout by default).

Usage:
    uv run python hypotheses/H71-memory-homeostat/scheme/build.py            # exploratory build (holdout masked)
The confirmatory script calls build(held=True, days=[...]) explicitly on held-out days; nothing else may.

Outputs (data/processed/H71-memory-homeostat/): snapshots.parquet, cycles.parquet, _provenance.json.
No memory text is read: only memory_stats (sizes and hashed-line diffs).
"""
from __future__ import annotations

import os

for _v in ("POLARS_MAX_THREADS", "OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ.setdefault(_v, "4")

import datetime as dt  # noqa: E402
import json  # noqa: E402
import sys  # noqa: E402
from pathlib import Path  # noqa: E402

import polars as pl  # noqa: E402

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "infra/shared"))
from common import REVISION, git_commit, holdout_mask  # noqa: E402

SH = ROOT / "data/processed/shared"
OUT = ROOT / "data/processed/H71-memory-homeostat"
# memory-relevant step changes inside goal periods (PT dates where a new sub-period starts)
SPLITS = {12: ("2025-09-05", "NE04"), 36: ("2026-03-24", "NE14")}
SPLIT2 = {36: ("2026-03-26", "NE16")}


def subperiod(goal_no: int, d: str) -> str:
    """Goal period label with memory-relevant splits: G12a/G12b (NE04), G36a/G36b/G36c (NE14, NE16)."""
    base = f"G{goal_no:02d}"
    if goal_no in SPLITS:
        s, _ = SPLITS[goal_no]
        if d < s:
            return base + "a"
        if goal_no in SPLIT2 and d >= SPLIT2[goal_no][0]:
            return base + "c"
        return base + "b"
    return base


def build(held: bool = False, days: list[str] | None = None, out: Path = OUT) -> dict:
    m = pl.read_parquet(SH / "memory_stats.parquet").sort("agent", "t")
    m = m.with_columns(pl.col("t").dt.convert_time_zone("America/Los_Angeles").dt.strftime("%Y-%m-%d")
                       .alias("pt_date"))
    cal = pl.read_parquet(SH / "calendar.parquet", columns=["pt_date", "goal_no", "regime", "holdout"])
    m = m.join(cal.with_columns(pl.col("regime").cast(pl.Utf8)), on="pt_date", how="inner")
    hm = pl.Series(holdout_mask(m["pt_date"].to_list(), m["goal_no"].fill_null(-1).to_list()))
    if not held:
        m = m.filter(~hm & ~pl.col("holdout"))
        assert not m["holdout"].any()
    else:
        assert days is not None, "confirmatory builds must pass held-out days explicitly"
        m = m.filter(pl.col("pt_date").is_in(days))
    m = m.filter(pl.col("goal_no") > 0)
    # phase labels
    m = m.with_columns(
        pl.when(pl.col("lines_removed") > 0).then(pl.lit("compress"))
        .when(pl.col("lines_added") > 0).then(pl.lit("append")).otherwise(pl.lit("same")).alias("phase"),
        pl.col("n_chars").cast(pl.Float64).clip(lower_bound=1.0).log().alias("lx"))
    m = m.with_columns(pl.struct("goal_no", "pt_date").map_elements(
        lambda r: subperiod(r["goal_no"], r["pt_date"]), return_dtype=pl.Utf8).alias("period"))
    # cycle types from the ledger: the reset call following a compress snapshot (regime III)
    led = (pl.read_parquet(SH / "context_ledger_turns.parquet",
                           columns=["agent", "t_call", "reset_forced", "reset_consol", "first_of_day", "holdout"])
           .filter(pl.col("reset_consol")).select("agent", pl.col("t_call").alias("t_reset"), "reset_forced")
           .sort("t_reset"))
    m = m.sort("t").join_asof(led, left_on="t", right_on="t_reset", by="agent", strategy="forward",
                              tolerance="10m", check_sortedness=False)
    m = m.with_columns(
        pl.when(pl.col("regime") != "III").then(pl.lit("session"))
        .when(pl.col("t_reset").is_null()).then(pl.lit("unmatched"))
        .when(pl.col("reset_forced")).then(pl.lit("forced")).otherwise(pl.lit("voluntary")).alias("ctype"))
    m = m.sort("agent", "t")
    snaps = m.select("agent", "t", "pt_date", "goal_no", "regime", "period", "phase", "lx", "n_chars", "n_lines",
                     "lines_kept", "lines_added", "lines_removed", "jaccard_prev", "ctype")
    # cycles: one row per compress snapshot; peak = the snapshot just before it (same agent)
    s = snaps.filter(pl.col("phase") != "same").with_columns(
        pl.col("lx").shift(1).over("agent").alias("lx_prev"),
        pl.col("t").shift(1).over("agent").alias("t_prev"),
        pl.col("phase").shift(1).over("agent").alias("phase_prev"))
    # appends since the previous compression
    s = s.with_columns((pl.col("phase") == "compress").cast(pl.Int32).cum_sum().over("agent").alias("cyc"))
    nap = (s.filter(pl.col("phase") == "append").group_by("agent", "cyc")
           .agg(pl.len().alias("n_app"), pl.col("lines_added").sum().alias("lines_app")))
    c = s.filter(pl.col("phase") == "compress").with_columns((pl.col("cyc") - 1).alias("cyc_prev_key"))
    c = c.join(nap.rename({"cyc": "cyc_prev_key"}), on=["agent", "cyc_prev_key"], how="left")
    c = c.with_columns(pl.col("n_app").fill_null(0), pl.col("lines_app").fill_null(0))
    c = c.with_columns(
        pl.col("lx").alias("xplus"),
        pl.col("lx_prev").alias("ypeak"),
        pl.col("t").shift(1).over("agent").alias("t_prevc"),
        pl.col("lx").shift(1).over("agent").alias("xplus_prev"),
        pl.col("period").shift(1).over("agent").alias("period_prev"),
    ).with_columns(((pl.col("t") - pl.col("t_prevc")).dt.total_seconds()).alias("dt_s"))
    cycles = c.select("agent", "t", "pt_date", "goal_no", "regime", "period", "ctype", "xplus", "ypeak", "xplus_prev",
                      "period_prev", "dt_s", "n_app", "lines_app", "lines_added", "lines_removed", "lines_kept",
                      "n_chars", "jaccard_prev")
    out.mkdir(parents=True, exist_ok=True)
    tag = "" if not held else "_confirm"
    snaps.write_parquet(out / f"snapshots{tag}.parquet", compression="zstd")
    cycles.write_parquet(out / f"cycles{tag}.parquet", compression="zstd")
    prov = {"built_by": "hypotheses/H71-memory-homeostat/scheme/build.py", "git_commit": git_commit(),
            "inputs": [{"source": "ai-village", "revision": REVISION,
                        "tables": ["memory_stats", "context_ledger_turns", "calendar"]}],
            "params": {"phase": "compress if lines_removed>0; append if lines_added>0 & lines_removed==0",
                       "cycle_type": "first reset_consol call within 10 min after the compress snapshot (regime III)",
                       "splits": {"NE04": "2025-09-05 (G12a|G12b)", "NE14": "2026-03-24 (G36a|G36b)",
                                  "NE16": "2026-03-26 (G36b|G36c)"},
                       "holdout": "masked (holdout_mask + calendar.holdout)" if not held else "CONFIRMATORY"},
            "built_at": dt.datetime.now(dt.timezone.utc).isoformat()}
    (out / ("_provenance.json" if not held else "_provenance_confirm.json")).write_text(json.dumps(prov, indent=1))
    return {"snapshots": snaps.height, "cycles": cycles.height}


if __name__ == "__main__":
    print(build())
