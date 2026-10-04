"""H99 round-2 scheme: per non-holdout period unit, the receiving-call skeleton, agent messages (rooms, names), kick
receipts and exogenous kick times needed for the call-clock tests (R1, R2, R4) and the scheduler-removal stack.
Codes only (no text). Round 1's outputs are untouched (they live in grids/, content/, kicks/).

Output data/processed/H99-glauber-fluctuation-relaxation/r2/:
  calls/<unit>.parquet  one row per receiving call (ctx_mode != summary): turn_id, agent, day, t (t_call), tf (t_first),
                        room, is_chat, is_wake, talk, active (kind in cu_action/talk/search/room_move/request), E_h, E_n,
                        trim (DQ8 call-based all-present window: agents with >= 20 receiving calls that day), ap_lo,
                        ap_hi, minute (floor((t_call - calendar.win_start)/60)), mf (minute of t_first)
  msgs/<unit>.parquet   agent chat messages: t, day, room, agent, minute, named (list of agent codes, mentions_roster),
                        n_readers (ledger receipts by agent recipients)
  kicks/<unit>.parquet  kick receipts (kicks_receipts, same day, receiving call in the unit): msg, kind, agent,
                        is_primary, is_named, turn_id, t_call
  exo/<unit>.parquet    exogenous kick times (kicks_classified: human_message, nudge, pause_resume, goal_kickoff): t, day,
                        kind, room
  unit_meta.parquet, _provenance.json
Times are float seconds since 2025-01-01 UTC. Holdout asserted twice (calendar.holdout and common.holdout_mask).
Usage: uv run python hypotheses/H99-glauber-fluctuation-relaxation/scheme/build_r2.py [--units 38a,51g]
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import sys
from pathlib import Path

import numpy as np
import polars as pl

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "infra/shared"))
from common import git_commit, holdout_mask  # noqa: E402

SH = ROOT / "data/processed/shared"
OUT = ROOT / "data/processed/H99-glauber-fluctuation-relaxation/r2"
EPOCH = dt.datetime(2025, 1, 1, tzinfo=dt.timezone.utc)
WAKE = {"pause", "pause_early", "first_of_day", "after_summary", "session_start", "marker"}
ACTIVE = {"cu_action", "talk", "search", "room_move", "request"}
MIN_CALLS_PRESENT = 20


def secs(col: str, alias: str | None = None) -> pl.Expr:
    return ((pl.col(col) - pl.lit(EPOCH)).dt.total_microseconds() / 1e6).alias(alias or col)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--units", default="")
    a = ap.parse_args()
    cal = pl.read_parquet(SH / "calendar.parquet")
    calh = dict(zip(cal["pt_date"].to_list(), cal["holdout"].fill_null(False).to_list()))
    ws = dict(zip(cal["pt_date"].to_list(), ((cal["win_start"] - EPOCH).dt.total_microseconds() / 1e6).to_list()))
    pu = pl.read_parquet(SH / "period_units.parquet").filter(~pl.col("holdout"))
    if a.units:
        pu = pu.filter(pl.col("unit_id").is_in(a.units.split(",")))
    cw = (pl.scan_parquet(SH / "call_windows.parquet").filter(~pl.col("holdout") & (pl.col("ctx_mode") != "summary"))
          .select("turn_id", "agent", "pt_date", "goal_no", "kind", "talk", "ctx_mode", "t_call", "t_first", "gap_kind")
          .collect())
    lt = (pl.scan_parquet(SH / "context_ledger_turns.parquet").filter(~pl.col("holdout"))
          .select("turn_id", "room", "n_human", "n_nudge").collect())
    cc = (pl.scan_parquet(SH / "chat_core.parquet").filter(pl.col("speaker_kind") == "agent")
          .select("message_id", "t", "pt_date", "goal_no", "room", "agent").collect())
    mc = pl.read_parquet(SH / "chat_mentions_clean.parquet", columns=["message_id", "mentions_roster"])
    cc = cc.join(mc, on="message_id", how="left")
    items = (pl.scan_parquet(SH / "context_ledger_items.parquet").filter(pl.col("kind") == "agent")
             .select("turn_id", "message_id").collect())
    kr = (pl.scan_parquet(SH / "kicks_receipts.parquet").filter(~pl.col("holdout") & pl.col("same_day"))
          .select("msg", "kind", "agent", "is_primary", "is_named", "turn_id", "t_call").collect())
    kc = (pl.read_parquet(SH / "kicks_classified.parquet", columns=["t", "kind", "room", "pt_date", "goal_no", "holdout"])
          .filter(~pl.col("holdout").fill_null(False)
                  & pl.col("kind").cast(pl.String).is_in(["human_message", "nudge", "pause_resume", "goal_kickoff"])))
    for sub in ("calls", "msgs", "kicks", "exo"):
        (OUT / sub).mkdir(parents=True, exist_ok=True)
    meta = []
    for u in pu.sort("goal_no", "seq").iter_rows(named=True):
        uid, g = u["unit_id"], u["goal_no"]
        days = [d for d in u["days"] if not calh.get(d, False)]
        assert not any(holdout_mask(days, [g] * len(days))), uid
        assert not cal.filter(pl.col("pt_date").is_in(days) & pl.col("holdout")).height, uid
        dmap = {d: k for k, d in enumerate(sorted(days))}
        s, e = u["start"], u["end"]
        c = (cw.filter(pl.col("pt_date").is_in(days) & (pl.col("goal_no") == g) & (pl.col("t_call") >= s)
                       & (pl.col("t_call") < e))
             .join(lt, on="turn_id", how="left"))
        if c.height == 0:
            continue
        c = (c.with_columns(secs("t_call", "t"), secs("t_first", "tf"),
                            pl.col("pt_date").replace_strict(dmap, return_dtype=pl.Int16).alias("day"),
                            pl.col("pt_date").replace_strict(ws, return_dtype=pl.Float64).alias("ws"),
                            (pl.col("ctx_mode") == "chat").cast(pl.Int8).alias("is_chat"),
                            pl.col("gap_kind").cast(pl.String).is_in(list(WAKE)).cast(pl.Int8).alias("is_wake"),
                            pl.col("kind").cast(pl.String).is_in(list(ACTIVE)).alias("active"),
                            pl.col("n_human").fill_null(0).alias("E_h"), pl.col("n_nudge").fill_null(0).alias("E_n"))
             .sort("agent", "day", "t", "turn_id"))
        pres = (c.group_by("day", "agent").agg(pl.len().alias("n"), pl.col("t").min().alias("f"), pl.col("t").max().alias("l"))
                .filter(pl.col("n") >= MIN_CALLS_PRESENT)
                .group_by("day").agg(pl.col("f").max().alias("ap_lo"), pl.col("l").min().alias("ap_hi"),
                                     pl.col("agent").alias("present")))
        c = c.join(pres.select("day", "ap_lo", "ap_hi"), on="day", how="left")
        pmap = {r["day"]: set(r["present"]) for r in pres.iter_rows(named=True)}
        c = c.with_columns(
            ((pl.col("t") >= pl.col("ap_lo")) & (pl.col("t") <= pl.col("ap_hi"))).fill_null(False).alias("trim"),
            ((pl.col("t") - pl.col("ws")) // 60).cast(pl.Int32).alias("minute"),
            ((pl.col("tf") - pl.col("ws")) // 60).cast(pl.Int32).alias("mf"))
        c = c.with_columns(pl.struct("day", "agent").map_elements(lambda r: r["agent"] in pmap.get(r["day"], set()),
                                                                  return_dtype=pl.Boolean).alias("present"))
        c = c.with_columns(pl.col("trim") & pl.col("present"))
        calls = c.select("turn_id", "agent", "day", "t", "tf", "room", "is_chat", "is_wake", "talk", "active", "E_h",
                         "E_n", "trim", "ap_lo", "ap_hi", "minute", "mf")
        calls.write_parquet(OUT / "calls" / f"{uid}.parquet", compression="zstd")
        m = (cc.filter(pl.col("pt_date").is_in(days) & (pl.col("goal_no") == g) & (pl.col("t") >= s) & (pl.col("t") < e))
             .with_columns(secs("t"), pl.col("pt_date").replace_strict(dmap, return_dtype=pl.Int16).alias("day"),
                           pl.col("pt_date").replace_strict(ws, return_dtype=pl.Float64).alias("ws")))
        nr = (items.join(calls.select("turn_id"), on="turn_id", how="semi").group_by("message_id")
              .agg(pl.len().alias("n_readers")))
        m = (m.join(nr, on="message_id", how="left")
             .with_columns(pl.col("n_readers").fill_null(0), ((pl.col("t") - pl.col("ws")) // 60).cast(pl.Int32).alias("minute"),
                           pl.col("mentions_roster").fill_null([]).alias("named"))
             .select("t", "day", "room", "agent", "minute", "named", "n_readers").sort("t"))
        m.write_parquet(OUT / "msgs" / f"{uid}.parquet", compression="zstd")
        k = (kr.join(calls.select("turn_id", "agent"), on=["turn_id", "agent"], how="semi")
             .with_columns(secs("t_call")).with_columns(pl.col("kind").cast(pl.String)))
        k.write_parquet(OUT / "kicks" / f"{uid}.parquet", compression="zstd")
        x = (kc.filter(pl.col("pt_date").is_in(days) & (pl.col("goal_no") == g))
             .with_columns(secs("t"), pl.col("pt_date").replace_strict(dmap, return_dtype=pl.Int16).alias("day"),
                           pl.col("kind").cast(pl.String))
             .select("t", "day", "kind", "room"))
        x.write_parquet(OUT / "exo" / f"{uid}.parquet", compression="zstd")
        tr = calls.filter(pl.col("trim"))
        mt = m.filter(pl.col("n_readers") > 0)
        meta.append({"unit_id": uid, "goal_no": g, "regime": u["regime"], "n_days": len(days), "days": sorted(days),
                     "n_calls": calls.height, "n_calls_trim": tr.height, "n_agents_trim": tr["agent"].n_unique(),
                     "n_talk_trim": int(tr["talk"].sum()), "n_msgs": m.height,
                     "r_bar": float(mt["n_readers"].mean()) if mt.height else float("nan"),
                     "rooms_trim": tr["room"].drop_nulls().n_unique(),
                     "n_kick_receipts": k.height})
        print(uid, calls.height, tr.height, flush=True)
    md = pl.DataFrame(meta)
    if a.units and (OUT / "unit_meta.parquet").exists():
        old = pl.read_parquet(OUT / "unit_meta.parquet").filter(~pl.col("unit_id").is_in(md["unit_id"]))
        md = pl.concat([old, md], how="diagonal_relaxed")
    md.sort("goal_no", "unit_id").write_parquet(OUT / "unit_meta.parquet")
    prov = {"built_by": "hypotheses/H99-glauber-fluctuation-relaxation/scheme/build_r2.py", "git_commit": git_commit(),
            "inputs": [{"source": "ai-village", "revision": "shared tables (DQ1 context ledger)",
                        "tables": ["call_windows", "context_ledger_turns", "context_ledger_items", "chat_core",
                                   "chat_mentions_clean", "kicks_receipts", "kicks_classified", "calendar", "period_units"]}],
            "params": {"min_calls_present": MIN_CALLS_PRESENT, "wake_gap_kinds": sorted(WAKE), "active_kinds": sorted(ACTIVE),
                       "epoch": EPOCH.isoformat(), "holdout": "excluded, asserted twice"},
            "built_at": dt.datetime.now(dt.timezone.utc).isoformat()}
    (OUT / "_provenance.json").write_text(json.dumps(prov, indent=1))


if __name__ == "__main__":
    main()
