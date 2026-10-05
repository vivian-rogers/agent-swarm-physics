"""H42 round 2 scheme: call sequences with rooms and next-call fields, and agent ledger items with named / thread flags.

Round-1 tables (G<NN>/calls, talk, items, ...) are not touched. Per non-reserved period unit, writes
data/processed/H42-readout-hawkes-kernel/round2/G<NN>/:

  calls.parquet  unit_id, day, agent, turn_id, t_call, t_first, t_end (s since the realization start, as round 1),
                 recv (ctx_mode != summary), talk, kind, ctx_mode, gap_kind, wake, start_conf, room,
                 t_next, kind_next, ctx_next (next call of the same agent-day, summary calls included)
  items.parquet  unit_id, day, recipient, turn_id (receiving call), s, sender (-1 = human/automated), kind, message_id,
                 ment (ledger), named (mentions_roster contains the recipient), reply_to_rec (DQ2 parent by the
                 recipient), engaged (the recipient named, or DQ2-replied to, the sender in the 30 min before s, same
                 PT day), thread = reply_to_rec | engaged, cold = named & ~thread

Unit days, windows and the call-to-realization rule are round 1's (scheme/build.py: realizations). Reserved data are
excluded and asserted twice (period_units/calendar flag and infra/shared/common.py: holdout_mask). No text is read.

Usage: uv run python hypotheses/H42-readout-hawkes-kernel/scheme/build_r2.py [--period G38]
"""
from __future__ import annotations

import datetime as dt
import importlib.util
import json
import os
import sys
from pathlib import Path

os.environ.setdefault("POLARS_MAX_THREADS", "2")
import polars as pl  # noqa: E402

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "infra/shared"))
from common import REVISION, holdout_mask  # noqa: E402

_spec = importlib.util.spec_from_file_location("h42_build_r1", HERE / "build.py")
B1 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(B1)

SH = ROOT / "data/processed/shared"
OUT = ROOT / "data/processed/H42-readout-hawkes-kernel/round2"
ENGAGE_S = 1800.0


def secs(col: str) -> pl.Expr:
    return ((pl.col(col) - pl.col("t0")).dt.total_microseconds() / 1e6).alias(col)


def build(goals=None):
    R = B1.realizations()
    if goals:
        R = R.filter(pl.col("goal_no").is_in(goals))
    dates = R["pt_date"].unique().to_list()
    hm = holdout_mask(R["pt_date"].to_list(), R["goal_no"].to_list())
    assert not any(hm), "reserved day in a round-2 unit"
    cw = (pl.scan_parquet(SH / "call_windows.parquet").filter(pl.col("pt_date").is_in(dates) & ~pl.col("holdout"))
          .select("turn_id", "agent", "pt_date", "goal_no", "kind", "talk", "ctx_mode", "t_call", "t_first", "t_end",
                  "gap_kind", "start_conf").collect())
    lt = (pl.scan_parquet(SH / "context_ledger_turns.parquet").filter(pl.col("pt_date").is_in(dates))
          .select("turn_id", "room").collect())
    cw = cw.join(lt, on="turn_id", how="left")
    cc = (pl.scan_parquet(SH / "chat_core.parquet").filter(pl.col("pt_date").is_in(dates))
          .select("message_id", "t", "pt_date", "speaker_kind", "agent").collect())
    men = pl.read_parquet(SH / "chat_mentions_clean.parquet", columns=["message_id", "mentions_roster"])
    cc = cc.join(men, on="message_id", how="left")
    par = (pl.scan_parquet(SH / "reply_pairs.parquet").filter(pl.col("parent"))
           .select(pl.col("B_message_id").alias("message_id"), pl.col("a_agent").alias("par_agent")).collect())
    cc = cc.join(par, on="message_id", how="left")
    it = (pl.scan_parquet(SH / "context_ledger_items.parquet").filter(pl.col("turn_id").is_in(cw["turn_id"].implode()))
          .select("turn_id", "message_id", "sender", "kind", "ment").collect())
    # engagement events: agent i posted at t' a message naming j, or with a DQ2 parent by j
    ag = cc.filter(pl.col("speaker_kind") == "agent")
    e1 = ag.select(pl.col("agent").alias("recipient"), "pt_date", pl.col("t").alias("te"),
                   pl.col("mentions_roster").alias("j")).explode("j").drop_nulls("j")
    e2 = ag.select(pl.col("agent").alias("recipient"), "pt_date", pl.col("t").alias("te"),
                   pl.col("par_agent").alias("j")).drop_nulls("j")
    eng = (pl.concat([e1, e2.cast(e1.schema)]).filter(pl.col("j") != pl.col("recipient"))
           .rename({"j": "sender"}).unique().sort("te"))
    for g in sorted(R["goal_no"].unique().to_list()):
        Rg = R.filter(pl.col("goal_no") == g)
        key = Rg.select("unit_id", "day", "pt_date", "t0", "t1")
        c = (cw.filter(pl.col("goal_no") == g).join(key, on="pt_date")
             .filter((pl.col("t_first") >= pl.col("t0")) & (pl.col("t_first") <= pl.col("t1"))))
        c = (c.sort("unit_id", "day", "agent", "t_call", "turn_id")
             .with_columns((pl.col("ctx_mode") != "summary").alias("recv"),
                           pl.col("gap_kind").cast(pl.String).is_in(B1.WAKE_GAPS).alias("wake"),
                           pl.col("t_call").shift(-1).over("unit_id", "day", "agent").alias("t_next"),
                           pl.col("kind").cast(pl.String).shift(-1).over("unit_id", "day", "agent").alias("kind_next"),
                           pl.col("ctx_mode").cast(pl.String).shift(-1).over("unit_id", "day", "agent").alias("ctx_next"))
             .with_columns(*[secs(x) for x in ("t_call", "t_first", "t_end", "t_next")]))
        calls = c.select("unit_id", "day", "agent", "turn_id", "t_call", "t_first", "t_end", "recv", "talk",
                         pl.col("kind").cast(pl.String), pl.col("ctx_mode").cast(pl.String),
                         pl.col("gap_kind").cast(pl.String), "wake", pl.col("start_conf").cast(pl.String), "room",
                         "t_next", "kind_next", "ctx_next")
        cm = c.filter(pl.col("recv")).select("turn_id", "unit_id", "day", "pt_date", "t0",
                                             pl.col("agent").alias("recipient"))
        ii = (it.join(cm, on="turn_id")
              .join(cc.select("message_id", pl.col("t").alias("s_abs"), "mentions_roster", "par_agent"),
                    on="message_id", how="left")
              .with_columns(pl.col("sender").fill_null(-1)).drop_nulls("s_abs"))
        ii = ii.with_columns(
            pl.col("mentions_roster").list.contains(pl.col("recipient")).fill_null(False).alias("named"),
            (pl.col("par_agent") == pl.col("recipient")).fill_null(False).alias("reply_to_rec"))
        ii = ii.sort("s_abs").join_asof(eng.select("recipient", "sender", "pt_date", "te"), left_on="s_abs",
                                        right_on="te", by=["recipient", "sender", "pt_date"], strategy="backward",
                                        tolerance=dt.timedelta(seconds=ENGAGE_S), allow_exact_matches=False)
        ii = (ii.with_columns(pl.col("te").is_not_null().alias("engaged"))
              .with_columns((pl.col("reply_to_rec") | pl.col("engaged")).alias("thread"))
              .with_columns((pl.col("named") & ~pl.col("thread")).alias("cold"),
                            ((pl.col("s_abs") - pl.col("t0")).dt.total_microseconds() / 1e6).alias("s"))
              .select("unit_id", "day", "recipient", "turn_id", "s", "sender", pl.col("kind").cast(pl.String),
                      "message_id", "ment", "named", "reply_to_rec", "engaged", "thread", "cold")
              .sort("unit_id", "day", "recipient", "s"))
        out = OUT / f"G{g:02d}"
        out.mkdir(parents=True, exist_ok=True)
        calls.write_parquet(out / "calls.parquet", compression="zstd")
        ii.write_parquet(out / "items.parquet", compression="zstd")
        a = ii.filter(pl.col("kind") == "agent")
        print(f"G{g:02d}: {len(calls)} calls, {len(ii)} items; agent items {len(a)}, named {a['named'].sum()}, "
              f"cold {a['cold'].sum()}, thread {a['thread'].sum()}", flush=True)
    prov = {"built_by": "hypotheses/H42-readout-hawkes-kernel/scheme/build_r2.py", "git_commit": B1.git_commit(),
            "inputs": [{"source": "ai-village", "revision": REVISION,
                        "tables": ["shared/call_windows", "shared/context_ledger_turns", "shared/context_ledger_items",
                                   "shared/chat_core", "shared/chat_mentions_clean", "shared/reply_pairs",
                                   "shared/calendar", "shared/period_units"]}],
            "params": {"engage_s": ENGAGE_S, "named": "mentions_roster contains recipient",
                       "thread": "DQ2 parent by recipient, or recipient named / DQ2-replied to sender in prior 30 min",
                       "holdout": "excluded (asserted twice)"},
            "built_at": dt.datetime.now(dt.timezone.utc).isoformat()}
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "_provenance.json").write_text(json.dumps(prov, indent=1))


if __name__ == "__main__":
    goals = None
    if "--period" in sys.argv:
        goals = [int(x.strip().lstrip("Gg#")) for x in sys.argv[sys.argv.index("--period") + 1].split(",")]
    build(goals)
