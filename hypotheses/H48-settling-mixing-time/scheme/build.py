"""H48 scheme: read-out schedules (calls, reads, messages), statement clock and kickoff rosters per goal period.

  uv run python hypotheses/H48-settling-mixing-time/scheme/build.py [--periods 38,39] [--allow-holdout]

Writes data/processed/H48-settling-mixing-time/ (no text anywhere):
  calls.parquet     goal_no, turn_id, agent, a (active h since kickoff), room, n_agent (new agent items), talk, kind
  reads.parquet     goal_no, turn_id, reader, sender, a_read, a_msg, room  (agent messages posted at/after the kickoff)
  msgs.parquet      goal_no, sender, a, room                                (agent chat messages at/after the kickoff)
  stmts.parquet     goal_no, srow (row of embeddings/statements), agent, kind, a, room, pre_kick
  roster.parquet    goal_no, agent, on_day1, room0 (modal day-1 room), a_first (first call), first_day
  periods.parquet   goal_no, regime, n_days, T_h, hours_per_day, t0, t0_src, N_roster, rooms0
Holdout days are dropped with common.holdout_mask before anything is computed (--allow-holdout: confirm.py only).
"""
from __future__ import annotations

import argparse
import datetime as dt
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import h48common as hc  # noqa: E402

import numpy as np  # noqa: E402
import polars as pl  # noqa: E402


def build(periods: list[int], allow_holdout: bool = False, out: Path = hc.OUT):
    t_start = time.time()
    out.mkdir(parents=True, exist_ok=True)
    cal = hc.calendar(allow_holdout)
    keep_days = cal.select("pt_date", "goal_no").filter(pl.col("goal_no").is_in(periods))
    turns = (pl.scan_parquet(hc.SH / "context_ledger_turns.parquet")
             .filter(pl.col("goal_no").is_in(periods) & (pl.col("agent") != hc.CLAUDE_CODE))
             .select("turn_id", "agent", "pt_date", "goal_no", "t_call", "room", "n_agent", "kind", "talk")
             .collect())
    turns = turns.join(keep_days, on=["pt_date", "goal_no"], how="semi")
    chat = (pl.scan_parquet(hc.SH / "chat_core.parquet")
            .filter((pl.col("speaker_kind").cast(pl.String) == "agent") & (pl.col("agent") != hc.CLAUDE_CODE))
            .select("message_id", "t", "pt_date", "goal_no", "room", "agent").collect())
    st = pl.read_parquet(hc.ED / "statements.parquet").with_row_index("srow")
    st = st.filter(pl.col("goal_no").is_in(periods) & (pl.col("agent") != hc.CLAUDE_CODE))
    st = st.join(keep_days, on=["pt_date", "goal_no"], how="semi")
    items = (pl.scan_parquet(hc.SH / "context_ledger_items.parquet")
             .filter(pl.col("kind").cast(pl.String) == "agent")
             .select("turn_id", "message_id", "sender").collect())
    items = items.join(turns.select("turn_id"), on="turn_id", how="semi")

    C, R, M, S, RO, P = [], [], [], [], [], []
    for g in periods:
        try:
            days = hc.period_days(g, allow_holdout)
        except Exception:
            continue
        if days.height == 0:
            continue
        t0 = hc.kickoff_t0(g, allow_holdout)
        t0_src = "h54_kickoff" if hc.kickoff_times().get(g) == t0 else "first_window"
        tg = turns.filter(pl.col("goal_no") == g).sort("t_call")
        a = hc.active_hours_fast(tg["t_call"].dt.epoch("us").to_numpy(), tg["pt_date"].to_numpy(), g,
                                 allow_holdout, t0)
        tg = tg.with_columns(pl.Series("a", a, dtype=pl.Float64))
        tg = tg.filter(pl.col("t_call") >= t0)
        C.append(tg.select(pl.lit(g, pl.Int8).alias("goal_no"), "turn_id", "agent", pl.col("a").cast(pl.Float32),
                           "room", pl.col("n_agent").cast(pl.Int16), "talk", pl.col("kind").cast(pl.String)))
        # messages (agent chat at/after the kickoff, on non-holdout days of this period)
        cg = chat.filter((pl.col("goal_no") == g) & (pl.col("t") >= t0)).join(
            days.select("pt_date"), on="pt_date", how="semi").sort("t")
        am = hc.active_hours_fast(cg["t"].dt.epoch("us").to_numpy(), cg["pt_date"].to_numpy(), g, allow_holdout, t0)
        cg = cg.with_columns(pl.Series("a", am, dtype=pl.Float64))
        M.append(cg.select(pl.lit(g, pl.Int8).alias("goal_no"), pl.col("agent").alias("sender"),
                           pl.col("a").cast(pl.Float32), "room"))
        # reads: ledger items of this period's calls whose message was posted at/after the kickoff
        rg = (items.join(tg.select("turn_id", pl.col("agent").alias("reader"), pl.col("a").alias("a_read"), "room"),
                         on="turn_id", how="inner")
              .join(cg.select("message_id", pl.col("a").alias("a_msg"), pl.col("agent").alias("sender_chk")),
                    on="message_id", how="inner"))
        rg = rg.filter(pl.col("reader") != pl.col("sender"))
        R.append(rg.select(pl.lit(g, pl.Int8).alias("goal_no"), "turn_id", "reader", "sender",
                           pl.col("a_read").cast(pl.Float32), pl.col("a_msg").cast(pl.Float32), "room")
                 .sort("a_read"))
        # statements clock
        sg = st.filter(pl.col("goal_no") == g)
        asg = hc.active_hours_fast(sg["t"].dt.epoch("us").to_numpy(), sg["pt_date"].to_numpy(), g, allow_holdout, t0)
        S.append(sg.select(pl.lit(g, pl.Int8).alias("goal_no"), "srow", "agent", "kind", "room")
                 .with_columns(pl.Series("a", asg, dtype=pl.Float32), (sg["t"] < t0).alias("pre_kick")))
        # roster: agents with >= 1 call on the first active day; modal day-1 room; first call
        d1 = days["pt_date"][0]
        first = tg.group_by("agent").agg(pl.col("a").min().alias("a_first"), pl.col("turn_id").len().alias("n_calls"))
        day1 = (tg.filter(pl.col("pt_date") == d1).group_by("agent", "room").len()
                .sort(["agent", "len", "room"], descending=[False, True, False]).group_by("agent", maintain_order=True)
                .first().select("agent", pl.col("room").alias("room0")))
        fd = (tg.group_by("agent").agg(pl.col("pt_date").min().alias("first_day")))
        ro = first.join(day1, on="agent", how="left").join(fd, on="agent").with_columns(
            pl.col("room0").is_not_null().alias("on_day1"), pl.lit(g, pl.Int8).alias("goal_no"))
        RO.append(ro.select("goal_no", "agent", "on_day1", "room0", pl.col("a_first").cast(pl.Float32), "first_day",
                            "n_calls"))
        T_h = float(days["window_s"].sum()) / 3600.0
        rooms0 = ro.filter(pl.col("on_day1"))["room0"].value_counts()
        P.append(dict(goal_no=g, regime=hc.regime_of(g), n_days=days.height, T_h=T_h,
                      hours_per_day=hc.hours_per_day(g), t0=t0, t0_src=t0_src,
                      N_roster=int(ro["on_day1"].sum()),
                      rooms0=sorted(int(r) for r, n in zip(rooms0["room0"], rooms0["count"]) if n >= 3),
                      first_day=d1, last_day=days["pt_date"][-1]))
        print(f"#{g}: {tg.height} calls, {rg.height} reads, {cg.height} msgs, {sg.height} stmts, "
              f"N={P[-1]['N_roster']}, rooms={P[-1]['rooms0']}  ({time.time() - t_start:.0f}s)", flush=True)

    suffix = "_confirm" if allow_holdout else ""
    pl.concat(C).write_parquet(out / f"calls{suffix}.parquet", compression="zstd")
    pl.concat(R).write_parquet(out / f"reads{suffix}.parquet", compression="zstd")
    pl.concat(M).write_parquet(out / f"msgs{suffix}.parquet", compression="zstd")
    pl.concat(S).write_parquet(out / f"stmts{suffix}.parquet", compression="zstd")
    pl.concat(RO).write_parquet(out / f"roster{suffix}.parquet", compression="zstd")
    pl.DataFrame(P).write_parquet(out / f"periods{suffix}.parquet")
    prov = {
        "built_by": "hypotheses/H48-settling-mixing-time/scheme/build.py",
        "git_commit": hc.common.git_commit(),
        "inputs": [{"source": "ai-village", "revision": hc.common.REVISION,
                    "tables": ["shared/context_ledger_turns", "shared/context_ledger_items", "shared/chat_core",
                               "shared/calendar", "shared/embeddings/statements", "H54/kickoffs (read-only)"]}],
        "params": {"periods": periods, "allow_holdout": allow_holdout, "claude_code_excluded": hc.CLAUDE_CODE,
                   "kickoff": "H54 kickoffs.parquet t0 (room null), fallback first window start",
                   "reads": "context_ledger_items kind=agent, message posted at/after t0, reader != sender"},
        "built_at": dt.datetime.now(dt.timezone.utc).isoformat(),
    }
    pp = out / "_provenance.json"
    old = hc.load_json(pp) if pp.exists() else {}
    derived = old.get("derived", {})
    prov["derived"] = derived          # analysis steps append here (analysis/*.py)
    hc.save_json(pp, prov)
    print(f"done in {time.time() - t_start:.0f}s")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--periods", default=None)
    ap.add_argument("--allow-holdout", action="store_true")
    a = ap.parse_args()
    periods = [int(x) for x in a.periods.split(",")] if a.periods else hc.ALL_PERIODS
    build(periods, a.allow_holdout)


if __name__ == "__main__":
    main()
