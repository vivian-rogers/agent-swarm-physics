"""H43 scheme: per-call table (the read-out clock) with kick counts by class, plus a write-event table.

Shared tables only (data/processed/shared/), non-holdout rows only (holdout_mask re-checked):
  call_windows            one row per model call; summary calls (CONSOLIDATE / STOP) dropped (they receive no items)
  context_ledger_items    (receiving call, message): which call first saw each kick
  period_units            matching units; 51g is split at NE43 (2026-08-21), which period_units predates
  work_commits            canonical, agent-authored, not automated, turn-backed commits (author time t)
  work_api_writes         successful API writes
Kick classes per call (new items read by that call):
  N   nudge naming the recipient (kind == nudge & ment)
  H   human message (any); Hm = human message naming the recipient
  A   agent message naming the recipient (@-mention)
No text is read or stored.

Output: data/processed/H43-kick-refractory-window/{calls.parquet, writes.parquet, _provenance.json}
Usage:  uv run python hypotheses/H43-kick-refractory-window/scheme/build.py
"""
from __future__ import annotations

import os

for _v in ("POLARS_MAX_THREADS", "OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "2")

import datetime as dt  # noqa: E402
import json  # noqa: E402
import sys  # noqa: E402
from pathlib import Path  # noqa: E402

import polars as pl  # noqa: E402

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "infra/shared"))
from common import REVISION, git_commit, holdout_mask  # noqa: E402

SH = ROOT / "data/processed/shared"
OUT = ROOT / "data/processed/H43-kick-refractory-window"
NE43_DATE = "2026-08-21"
KINDS = ["cu_action", "talk", "pause", "wait", "consolidate", "session_start", "session_stop", "search", "room_move",
         "request"]
GAPS = ["busy", "pause", "pause_early", "after_summary", "marker", "session_start", "long_prev", "first_of_day"]


def epoch(col: str) -> pl.Expr:
    return (pl.col(col).dt.epoch("us") / 1e6).alias(col)


def units_table(include_holdout: bool = False) -> pl.DataFrame:
    pu = pl.read_parquet(SH / "period_units.parquet")
    if not include_holdout:
        pu = pu.filter(~pl.col("holdout"))
    rows = []
    for r in pu.iter_rows(named=True):
        for d in r["days"]:
            uid = r["unit_id"]
            if uid == "51g":
                uid = "51g1" if d < NE43_DATE else "51g2"
            rows.append({"goal_no": r["goal_no"], "pt_date": d, "unit_id": uid,
                         "u_start": r["start"].timestamp(), "u_end": r["end"].timestamp()})
    return pl.DataFrame(rows)


def calls_frame(include_holdout: bool = False, goal_nos: list[int] | None = None) -> tuple[pl.DataFrame, int]:
    """Per-call table. include_holdout=True is used only by analysis/confirm.py behind its two flags."""
    cw = pl.scan_parquet(SH / "call_windows.parquet").filter(pl.col("ctx_mode").cast(pl.Utf8) != "summary")
    if not include_holdout:
        cw = cw.filter(~pl.col("holdout"))
    if goal_nos is not None:
        cw = cw.filter(pl.col("goal_no").is_in(goal_nos))
    cw = (cw.select("turn_id", "agent", "pt_date", "goal_no", pl.col("regime").cast(pl.Utf8), "kind", "talk",
                    pl.col("ctx_mode").cast(pl.Utf8), "gap_kind", "first_of_day", "start_conf", "t_call", "t_end", "t_log")
          .collect())
    if not include_holdout:
        hm = holdout_mask(cw["pt_date"].to_list(), cw["goal_no"].to_list())
        assert not any(hm), "holdout rows leaked into call_windows filter"
    cw = cw.with_columns(epoch("t_call"), epoch("t_end"), epoch("t_log"),
                         pl.col("kind").cast(pl.Utf8).replace_strict({k: i for i, k in enumerate(KINDS)}).cast(pl.Int8).alias("kind_c"),
                         pl.col("gap_kind").cast(pl.Utf8).replace_strict({k: i for i, k in enumerate(GAPS)}, default=-1).cast(pl.Int8).alias("gap_c"),
                         (pl.col("start_conf").cast(pl.Utf8) == "low").alias("low_conf"))
    it = (pl.scan_parquet(SH / "context_ledger_items.parquet")
          .select("turn_id", "kind", "ment")
          .filter(pl.col("turn_id").is_in(cw["turn_id"].implode()))
          .with_columns(pl.col("kind").cast(pl.Utf8))
          .group_by("turn_id")
          .agg(((pl.col("kind") == "nudge") & pl.col("ment")).sum().cast(pl.Int16).alias("nN"),
               (pl.col("kind") == "human").sum().cast(pl.Int16).alias("nH"),
               ((pl.col("kind") == "human") & pl.col("ment")).sum().cast(pl.Int16).alias("nHm"),
               ((pl.col("kind") == "agent") & pl.col("ment")).sum().cast(pl.Int16).alias("nA"),
               (pl.col("kind") == "agent").sum().cast(pl.Int16).alias("nAll"))
          .collect())
    cw = cw.join(it, on="turn_id", how="left").with_columns(
        [pl.col(c).fill_null(0) for c in ("nN", "nH", "nHm", "nA", "nAll")])
    un = units_table(include_holdout)
    cw = cw.join(un, on=["goal_no", "pt_date"], how="left")
    # days listed in two units (intra-day restarts): keep the unit whose [start, end) contains the call
    cw = (cw.with_columns(((pl.col("t_call") >= pl.col("u_start")) & (pl.col("t_call") < pl.col("u_end"))).alias("_in"))
          .sort("turn_id", "_in", descending=[False, True]).unique("turn_id", keep="first", maintain_order=True))
    n_nounit = cw.filter(pl.col("unit_id").is_null()).height
    calls = (cw.select("turn_id", pl.col("agent").cast(pl.Int8), "pt_date", "goal_no", "unit_id", "regime", "kind_c",
                       "talk", "ctx_mode", "gap_c", "first_of_day", "low_conf", "t_call", "t_end", "t_log",
                       "nN", "nH", "nHm", "nA", "nAll")
             .filter(pl.col("unit_id").is_not_null())
             .sort("agent", "pt_date", "t_call"))
    return calls, n_nounit


def writes_frame(include_holdout: bool = False) -> pl.DataFrame:
    wc = pl.scan_parquet(SH / "work_commits.parquet").filter(
        pl.col("canonical") & (pl.col("author_kind").cast(pl.Utf8) == "agent") & ~pl.col("automated")
        & pl.col("turn_backed") & pl.col("author_agent").is_not_null())
    wa = pl.scan_parquet(SH / "work_api_writes.parquet").filter(~pl.col("error").fill_null(False) & pl.col("agent").is_not_null())
    if not include_holdout:
        wc, wa = wc.filter(~pl.col("holdout")), wa.filter(~pl.col("holdout"))
    wc = wc.select(pl.col("author_agent").cast(pl.Int8).alias("agent"), "pt_date", "goal_no", epoch("t"),
                   pl.lit("commit").alias("src")).collect()
    wa = wa.select(pl.col("agent").cast(pl.Int8), "pt_date", "goal_no", epoch("t"), pl.lit("api").alias("src")).collect()
    writes = pl.concat([wc, wa]).sort("agent", "t")
    if not include_holdout:
        hm = holdout_mask(writes["pt_date"].to_list(), writes["goal_no"].to_list())
        writes = writes.filter(~pl.Series(hm))
    return writes


def build():
    OUT.mkdir(parents=True, exist_ok=True)
    calls, n_nounit = calls_frame(include_holdout=False)
    calls.write_parquet(OUT / "calls.parquet", compression="zstd")
    writes = writes_frame(include_holdout=False)
    writes.write_parquet(OUT / "writes.parquet", compression="zstd")

    prov_path = OUT / "_provenance.json"
    prov = json.loads(prov_path.read_text()) if prov_path.exists() else {}
    prov.update({
        "built_by": "hypotheses/H43-kick-refractory-window/scheme/build.py",
        "git_commit": git_commit(),
        "inputs": [{"source": "ai-village", "revision": REVISION,
                    "tables": ["shared/call_windows", "shared/context_ledger_items", "shared/period_units",
                               "shared/work_commits", "shared/work_api_writes", "shared/states_min (read by analysis)"]}],
        "params": {"summary_calls": "dropped", "classes": {"N": "nudge & ment", "H": "human", "Hm": "human & ment",
                                                            "A": "agent & ment"},
                   "ne43_split": NE43_DATE, "writes": "work_commits canonical agent non-automated turn_backed + "
                                                     "work_api_writes non-error", "holdout": "excluded"},
        "built_at": dt.datetime.now(dt.timezone.utc).isoformat(),
        "counts": {"calls": calls.height, "calls_without_unit_dropped": n_nounit, "writes": writes.height},
    })
    prov_path.write_text(json.dumps(prov, indent=1))
    print(f"calls {calls.height:,} (dropped without unit: {n_nounit}); writes {writes.height:,}")


if __name__ == "__main__":
    build()
