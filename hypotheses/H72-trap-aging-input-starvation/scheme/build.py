"""H72 scheme: eligible idle gates (shared table) and Jev blocked-spell windows (native N2).

Outputs in data/processed/H72-trap-aging-input-starvation/:
  gates.parquet        shared idle gates (infra/shared/idle_gates.py) for goal periods with >= MIN_GATES gates
  blocked.parquet      G51 and G27 Jev v3.1 windows in blocked spells (p_blocked >= 0.5 runs), with the directed and
                       novel starvation clocks at the window start and the reads inside the window
  _provenance.json
Holdout: the shared gate table already excludes held-out days; both outputs are re-checked with holdout_mask.
Usage: uv run python hypotheses/H72-trap-aging-input-starvation/scheme/build.py
"""
from __future__ import annotations

import os

for _v in ("POLARS_MAX_THREADS", "OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "4")

import datetime as dt
import json
import sys
from pathlib import Path

import numpy as np
import polars as pl

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "infra/shared"))
from common import REVISION, git_commit, holdout_mask  # noqa: E402
import idle_gates as IG  # noqa: E402

SH = ROOT / "data/processed/shared"
OUT = ROOT / "data/processed/H72-trap-aging-input-starvation"
MIN_GATES = 200
BLOCK_P = 0.5
NATIVE_BLOCK_PERIODS = (51, 27)


def assert_no_holdout(df: pl.DataFrame):
    hm = holdout_mask(df["pt_date"].to_list(), df["goal_no"].to_list())
    assert not any(hm), "holdout rows present"


def eligible_gates() -> pl.DataFrame:
    g = pl.read_parquet(SH / "idle_gates/idle_gates.parquet")
    n = g.group_by("goal_no").len()
    keep = n.filter(pl.col("len") >= MIN_GATES)["goal_no"]
    g = g.filter(pl.col("goal_no").is_in(keep))
    assert_no_holdout(g)
    return g


def read_times() -> pl.DataFrame:
    """Per call (all non-summary calls): t_call and whether it read novel / directed items."""
    cw = IG.load_calls()
    ic = IG.item_counts(cw)
    cw = cw.join(ic, on="turn_id", how="left").with_columns(pl.col("n_novel").fill_null(0), pl.col("n_dir").fill_null(0))
    return cw.select("agent", "pt_date", "goal_no", "t_call", "n_novel", "n_dir")


def blocked_windows() -> pl.DataFrame:
    bs = (pl.scan_parquet(SH / "behavior_states_v3.parquet")
          .filter(pl.col("goal_no").is_in(NATIVE_BLOCK_PERIODS) & ~pl.col("holdout"))
          .select("pt_date", "agent", "w", "t0", "t1", "goal_no", "labeled", "in_span", "p_blocked", "n_seen",
                  "n_seen_mentioning")
          .collect().sort("agent", "pt_date", "w"))
    assert_no_holdout(bs)
    ok = pl.col("labeled") & pl.col("in_span") & pl.col("p_blocked").is_not_null()
    bs = bs.with_columns((ok & (pl.col("p_blocked") >= BLOCK_P)).alias("blk"), ok.alias("ok"))
    ad = ["agent", "pt_date"]
    # spells: consecutive windows (w increments by 1) with blk
    bs = bs.with_columns(((pl.col("blk") != pl.col("blk").shift(1).over(ad)) |
                          (pl.col("w") != pl.col("w").shift(1).over(ad) + 1)).fill_null(True).cast(pl.Int32)
                         .cum_sum().over(ad).alias("spell"))
    bs = bs.with_columns(pl.int_range(1, pl.len() + 1).over(ad + ["spell"]).alias("j"),
                         pl.col("blk").shift(-1).over(ad).alias("blk_next"),
                         pl.col("ok").shift(-1).over(ad).alias("ok_next"),
                         (pl.col("w").shift(-1).over(ad) == pl.col("w") + 1).alias("adj_next"))
    b = bs.filter(pl.col("blk"))
    # escape at the next window: next window labelled, adjacent and not blocked; censored otherwise
    b = b.with_columns(pl.when(pl.col("adj_next").fill_null(False) & pl.col("ok_next").fill_null(False))
                       .then(~pl.col("blk_next").fill_null(False)).otherwise(None).alias("y_leave"))
    # clocks at the window start from call reads (same agent-day, strictly before t0)
    rt = read_times().filter(pl.col("goal_no").is_in(NATIVE_BLOCK_PERIODS))
    out = []
    for v, col in (("dir", "n_dir"), ("novel", "n_novel")):
        r = rt.filter(pl.col(col) > 0).select("agent", "pt_date", pl.col("t_call").alias(f"t_last_{v}")).sort(f"t_last_{v}")
        out.append(r)
    b = b.sort("t0")
    for v, r in zip(("dir", "novel"), out):
        b = b.join_asof(r, left_on="t0", right_on=f"t_last_{v}", by=["agent", "pt_date"], strategy="backward",
                        allow_exact_matches=False)
    first = rt.group_by("agent", "pt_date").agg(pl.col("t_call").min().alias("t_first_call"))
    b = b.join(first, on=["agent", "pt_date"], how="left")
    # reads inside the window [t0, t1)
    rt2 = rt.with_columns(pl.col("t_call").alias("tc"))
    win_reads = (b.select("agent", "pt_date", "w", "t0", "t1")
                 .join(rt2.select("agent", "pt_date", "tc", "n_dir", "n_novel"), on=["agent", "pt_date"], how="inner")
                 .filter((pl.col("tc") >= pl.col("t0")) & (pl.col("tc") < pl.col("t1")))
                 .group_by("agent", "pt_date", "w").agg(pl.col("n_dir").sum().alias("win_dir"),
                                                        pl.col("n_novel").sum().alias("win_novel"),
                                                        pl.len().alias("win_calls")))
    b = b.join(win_reads, on=["agent", "pt_date", "w"], how="left").with_columns(
        pl.col("win_dir").fill_null(0), pl.col("win_novel").fill_null(0), pl.col("win_calls").fill_null(0))
    sec = lambda a, c: (pl.col(a) - pl.col(c)).dt.total_microseconds().cast(pl.Float64) / 1e6  # noqa: E731
    b = b.with_columns(sec("t0", "t_last_dir").alias("s_dir"), sec("t0", "t_last_novel").alias("s_novel"),
                       sec("t0", "t_first_call").alias("s_lc"))
    return b.select("goal_no", "pt_date", "agent", "w", "t0", "spell", "j", "p_blocked", "y_leave", "s_dir", "s_novel",
                    "s_lc", "win_dir", "win_novel", "win_calls", "n_seen", "n_seen_mentioning").sort("agent", "pt_date", "w")


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    g = eligible_gates()
    g.write_parquet(OUT / "gates.parquet", compression="zstd")
    b = blocked_windows()
    b.write_parquet(OUT / "blocked.parquet", compression="zstd")
    prov = {"built_by": "hypotheses/H72-trap-aging-input-starvation/scheme/build.py", "git_commit": git_commit(),
            "inputs": [{"source": "ai-village", "revision": REVISION,
                        "tables": ["idle_gates (infra/shared/idle_gates.py)", "behavior_states_v3", "call_windows",
                                   "context_ledger_items"]}],
            "params": {"min_gates": MIN_GATES, "block_p": BLOCK_P, "native_block_periods": NATIVE_BLOCK_PERIODS},
            "rows": {"gates": g.height, "blocked": b.height},
            "built_at": dt.datetime.now(dt.UTC).isoformat()}
    (OUT / "_provenance.json").write_text(json.dumps(prov, indent=1))
    print("gates", g.height, "periods", g["goal_no"].n_unique(), "blocked windows", b.height)


if __name__ == "__main__":
    main()
