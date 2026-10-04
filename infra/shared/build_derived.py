"""Phase 0, step 2: derived tables from the scans (polars, multithreaded).

Outputs (data/processed/shared/):
  calendar.parquet        one row per PT day with agent activity: empirical active window, gap before,
                          goal, regime, documented hours, holdout flag, active-time offset
  rooms_timeline.parquet  per agent: intervals in a room (from room-tagged agent events)
  exposure.parquet        per chat message x agent in the room at that time (excluding the speaker):
                          lag until that agent's next action (when it could next have seen it)
  activity_bins.parquet   agent x 1-minute bin of active time: counts and a coarse state code
  kicks.parquet           outside impulses: human / automated messages, goal kickoffs, roster changes, NEs

Usage: uv run python infra/shared/build_derived.py
"""
from __future__ import annotations

import datetime as dt
import re
import sys
import time
from pathlib import Path

import polars as pl

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import OUT, ROOT, load_goals, load_holdout, write_provenance

HOURS = [("2025-05-23", "2025-07-18", 2), ("2025-07-18", "2025-08-18", 3), ("2025-08-18", "2026-06-07", 4),
         ("2026-06-07", "2026-06-15", 8), ("2026-06-15", "2026-06-29", 4), ("2026-06-29", "2027-01-01", 8)]

STATE = {"absent": 0, "silent": 1, "idle": 2, "act": 3, "talk": 4}


def documented_hours(d: str):
    for s, e, h in HOURS:
        if s <= d < e:
            return h
    return None


def build_calendar(ev: pl.DataFrame) -> pl.DataFrame:
    ag = ev.filter(pl.col("actor_kind") == "agent")
    cal = (ag.group_by("pt_date").agg(pl.col("t").min().alias("win_start"), pl.col("t").max().alias("win_end"),
                                       pl.len().alias("n_agent_events"),
                                       pl.col("goal_no").mode().first().alias("goal_no"),
                                       pl.col("regime").mode().first().alias("regime"))
           .sort("pt_date")
           .with_columns(((pl.col("win_end") - pl.col("win_start")).dt.total_seconds()).alias("window_s"),
                         ((pl.col("win_start") - pl.col("win_end").shift(1)).dt.total_seconds()).alias("gap_before_s")))
    cal = cal.with_columns(pl.col("window_s").cum_sum().shift(1, fill_value=0).alias("active_offset_s"),
                           pl.col("pt_date").map_elements(documented_hours, return_dtype=pl.Int8).alias("documented_hours"),
                           pl.col("pt_date").str.to_date().dt.weekday().alias("weekday"))
    h = load_holdout()
    held = set(h["goal_periods_held_out"])
    wins = [(w["start"], w["end"]) for w in h["ne_windows"]]
    cal = cal.with_columns(pl.struct("pt_date", "goal_no").map_elements(
        lambda r: (r["goal_no"] in held) or any(s <= r["pt_date"] < e for s, e in wins),
        return_dtype=pl.Boolean).alias("holdout"))
    return cal


def build_rooms_timeline(ev: pl.DataFrame) -> pl.DataFrame:
    x = (ev.filter(pl.col("agent").is_not_null() & pl.col("room").is_not_null() & (pl.col("actor_kind") == "agent"))
         .select("agent", "t", "room").sort("agent", "t"))
    x = x.with_columns((pl.col("room") != pl.col("room").shift(1).over("agent")).fill_null(True).alias("chg"))
    x = x.with_columns(pl.col("chg").cum_sum().over("agent").alias("run"))
    iv = (x.group_by("agent", "run").agg(pl.col("room").first(), pl.col("t").min().alias("t_start"),
                                         pl.col("t").max().alias("t_last"))
          .sort("agent", "t_start")
          .with_columns(pl.col("t_start").shift(-1).over("agent").alias("t_end")))
    return iv.select("agent", "room", "t_start", "t_last", "t_end")


def build_exposure(chat: pl.DataFrame, ev: pl.DataFrame, roster: pl.DataFrame, rooms_tl: pl.DataFrame) -> pl.DataFrame:
    msgs = chat.with_row_index("msg").select("msg", "t", "room", pl.col("agent").alias("speaker"))
    agents = roster.filter(~pl.col("claude_code")).select("agent", "joined", "left")
    pieces = []
    room_ev = rooms_tl.select("agent", pl.col("t_start").alias("t_room"), pl.col("room").alias("agent_room"))
    acts = (ev.filter((pl.col("actor_kind") == "agent") & pl.col("agent").is_not_null())
            .select("agent", pl.col("t").alias("t_next")).sort("t_next"))
    for a, joined, left in agents.iter_rows():
        m = msgs.with_columns(pl.lit(a, dtype=pl.Int8).alias("agent")).sort("t")
        m = m.filter(pl.col("t").dt.date() >= dt.date.fromisoformat(joined))
        if left:
            m = m.filter(pl.col("t").dt.date() < dt.date.fromisoformat(left))
        if m.is_empty():
            continue
        m = m.join_asof(room_ev.filter(pl.col("agent") == a).sort("t_room"), left_on="t", right_on="t_room",
                        strategy="backward", by="agent")
        m = m.filter((pl.col("agent_room") == pl.col("room")) & (pl.col("speaker").is_null() | (pl.col("speaker") != a)))
        m = m.join_asof(acts.filter(pl.col("agent") == a), left_on="t", right_on="t_next", strategy="forward", by="agent")
        pieces.append(m.select("msg", "agent", ((pl.col("t_next") - pl.col("t")).dt.total_seconds()).cast(pl.Float32).alias("lag_s")))
    return pl.concat(pieces).sort("msg", "agent")


def build_activity_bins(ev: pl.DataFrame, acts: pl.DataFrame, cal: pl.DataFrame, roster: pl.DataFrame) -> pl.DataFrame:
    win = cal.select("pt_date", "win_start", "active_offset_s")

    def binned(df, tcol="t"):
        return (df.with_columns(pl.col(tcol).dt.convert_time_zone("America/Los_Angeles").dt.date().cast(pl.Utf8).alias("pt_date"))
                .join(win, on="pt_date")
                .with_columns(((pl.col(tcol) - pl.col("win_start")).dt.total_seconds() // 60).cast(pl.Int32).alias("minute"),
                              ((pl.col("active_offset_s") + (pl.col(tcol) - pl.col("win_start")).dt.total_seconds()) // 60)
                              .cast(pl.Int32).alias("active_min")))

    e = binned(ev.filter((pl.col("actor_kind") == "agent") & pl.col("agent").is_not_null()))
    e = e.with_columns(
        (pl.col("action_type") == "AGENT_TALK").cast(pl.Int16).alias("talk"),
        pl.col("action_type").is_in(["WAIT", "PAUSE"]).cast(pl.Int16).alias("idle"),
        (pl.col("action_type") == "CONSOLIDATE").cast(pl.Int16).alias("consolidate"),
        (~pl.col("action_type").is_in(["AGENT_TALK", "WAIT", "PAUSE", "CONSOLIDATE"])).cast(pl.Int16).alias("other_event"))
    # Join key is (pt_date, minute, agent); active_min comes from the grid only. Computing it per event as
    # (offset + dt)//60 disagreed with the grid's offset//60 + minute whenever offset%60 + seconds >= 60, which
    # silently dropped ~half of all events (found by DQ8, 2026-10-04; see infra/README Known issues).
    e = e.group_by("pt_date", "minute", "agent").agg(
        pl.col("talk").sum(), pl.col("idle").sum(), pl.col("consolidate").sum(), pl.col("other_event").sum())
    # PAUSE declares a duration; the agent is idle until min(t + seconds, its next event)
    ag = ev.filter((pl.col("actor_kind") == "agent") & pl.col("agent").is_not_null()).select("agent", "t", "action_type", "pause_s").sort("agent", "t")
    ag = ag.with_columns(pl.col("t").shift(-1).over("agent").alias("t_next"))
    pz = ag.filter((pl.col("action_type") == "PAUSE") & pl.col("pause_s").is_not_null())
    pz = pz.with_columns(pl.min_horizontal(pl.col("t") + pl.duration(seconds=pl.col("pause_s")), pl.col("t_next")).alias("t_end"))
    pz = binned(pz.select("agent", "t", "t_end"))
    pz = pz.with_columns((pl.col("minute") + ((pl.col("t_end") - pl.col("t")).dt.total_seconds() // 60).cast(pl.Int32)).alias("m_end"))
    pz = (pz.with_columns(pl.int_ranges(pl.col("minute"), pl.col("m_end") + 1).alias("mm")).explode("mm")
          .with_columns(pl.col("mm").alias("minute"))
          .group_by("pt_date", "minute", "agent").agg(pl.len().cast(pl.Int16).alias("paused")))
    c = binned(acts.filter(pl.col("agent").is_not_null()).select("t", "agent"))
    c = c.group_by("pt_date", "minute", "agent").agg(pl.len().cast(pl.Int16).alias("turns"))
    # dense grid: every minute of every day's window x every agent on the roster that day
    grid = (cal.select("pt_date", "window_s", "active_offset_s")
            .with_columns(pl.int_ranges(0, (pl.col("window_s") // 60 + 1).cast(pl.Int32)).alias("minute"))
            .explode("minute")
            .with_columns(((pl.col("active_offset_s") // 60) + pl.col("minute")).cast(pl.Int32).alias("active_min"))
            .select("pt_date", "minute", "active_min"))
    ros = roster.filter(~pl.col("claude_code")).select("agent", "joined", "left")
    grid = grid.join(ros, how="cross").filter(
        (pl.col("pt_date") >= pl.col("joined")) & (pl.col("left").is_null() | (pl.col("pt_date") < pl.col("left")))
    ).drop("joined", "left")
    key = ["pt_date", "minute", "agent"]
    out = (grid.join(e, on=key, how="left")
           .join(c, on=key, how="left")
           .join(pz, on=key, how="left")
           .with_columns(*[pl.col(k).fill_null(0).cast(pl.Int16) for k in ("talk", "idle", "consolidate", "other_event", "turns", "paused")]))
    out = out.with_columns(
        pl.when(pl.col("talk") > 0).then(STATE["talk"])
        .when((pl.col("turns") > 0) | (pl.col("other_event") > 0) | (pl.col("consolidate") > 0)).then(STATE["act"])
        .when((pl.col("idle") > 0) | (pl.col("paused") > 0)).then(STATE["idle"])
        .otherwise(STATE["silent"]).cast(pl.Int8).alias("state"))
    return out.sort("active_min", "agent")


def parse_ne_dates() -> list[tuple[str, str]]:
    out = []
    for line in (ROOT / "hypotheses/natural-experiments.md").read_text().splitlines():
        m = re.match(r"\|\s*(NE\d+)\s*\|\s*([^|]+)\|", line)
        if m:
            d = re.search(r"\d{4}-\d{2}-\d{2}", m.group(2))
            if d:
                out.append((m.group(1), d.group(0)))
    return out


def label_automated(chat: pl.DataFrame, ev: pl.DataFrame) -> pl.DataFrame:
    """chat_messages has no speaker name; USER_TALK events carry it. 'automated' = the nudger/bot."""
    auto = ev.filter(pl.col("actor_kind") == "automated").select("message_id").unique().with_columns(pl.lit(True).alias("auto"))
    return (chat.join(auto, on="message_id", how="left")
            .with_columns(pl.when(pl.col("auto")).then(pl.lit("automated")).otherwise(pl.col("speaker_kind").cast(pl.Utf8))
                          .cast(pl.Categorical).alias("speaker_kind")).drop("auto"))


def build_kicks(chat: pl.DataFrame, roster: pl.DataFrame) -> pl.DataFrame:
    msg = (chat.filter(pl.col("speaker_kind") != "agent")
           .select("t", pl.when(pl.col("speaker_kind") == "automated").then(pl.lit("automated_message"))
                   .otherwise(pl.lit("human_message")).alias("kind"), pl.col("room"), pl.lit(None, dtype=pl.Int8).alias("agent"),
                   pl.col("human").alias("ref")))
    goals = pl.DataFrame([{"t": g["start"], "kind": "goal_kickoff", "room": None, "agent": None, "ref": f"#{g['goal_no']}"}
                          for g in load_goals()]).with_columns(pl.col("room").cast(pl.Int8), pl.col("agent").cast(pl.Int8),
                                                               pl.col("ref").cast(pl.Utf8))
    rj = []
    for a, j, l in roster.select("agent", "joined", "left").iter_rows():
        rj.append({"t": dt.datetime.fromisoformat(j + "T17:00:00+00:00"), "kind": "roster_join", "room": None, "agent": a, "ref": None})
        if l:
            rj.append({"t": dt.datetime.fromisoformat(l + "T17:00:00+00:00"), "kind": "roster_leave", "room": None, "agent": a, "ref": None})
    ne = [{"t": dt.datetime.fromisoformat(d + "T17:00:00+00:00"), "kind": "natural_experiment", "room": None, "agent": None, "ref": i}
          for i, d in parse_ne_dates()]
    extra = pl.DataFrame(rj + ne).with_columns(pl.col("room").cast(pl.Int8), pl.col("agent").cast(pl.Int8),
                                                pl.col("ref").cast(pl.Utf8), pl.col("t").dt.cast_time_unit("us"))
    goals = goals.with_columns(pl.col("t").dt.cast_time_unit("us"))
    msg = msg.with_columns(pl.col("t").dt.cast_time_unit("us"))
    return pl.concat([msg, goals, extra], how="vertical_relaxed").sort("t")


if __name__ == "__main__":
    t0 = time.time()
    ev = pl.read_parquet(OUT / "events_core.parquet")
    chat = label_automated(pl.read_parquet(OUT / "chat_core.parquet"), pl.read_parquet(OUT / "events_core.parquet"))
    chat.write_parquet(OUT / "chat_core.parquet", compression="zstd")
    acts = pl.read_parquet(OUT / "actions.parquet", columns=["t", "agent"])
    roster = pl.read_parquet(OUT / "roster.parquet")
    cal = build_calendar(ev); cal.write_parquet(OUT / "calendar.parquet", compression="zstd")
    print("calendar", cal.height, "days", f"{time.time()-t0:.0f}s", flush=True)
    rtl = build_rooms_timeline(ev); rtl.write_parquet(OUT / "rooms_timeline.parquet", compression="zstd")
    print("rooms_timeline", rtl.height, f"{time.time()-t0:.0f}s", flush=True)
    exp = build_exposure(chat, ev, roster, rtl); exp.write_parquet(OUT / "exposure.parquet", compression="zstd")
    print("exposure", exp.height, f"{time.time()-t0:.0f}s", flush=True)
    bins = build_activity_bins(ev, acts, cal, roster); bins.write_parquet(OUT / "activity_bins.parquet", compression="zstd")
    print("activity_bins", bins.height, f"{time.time()-t0:.0f}s", flush=True)
    k = build_kicks(chat, roster); k.write_parquet(OUT / "kicks.parquet", compression="zstd")
    print("kicks", k.height, f"{time.time()-t0:.0f}s", flush=True)
    write_provenance("build_derived", ["(shared scans)"],
                     {"active_window": "first..last agent event per PT day", "bins": "1 min of active time",
                      "state": STATE, "exposure": "room-based rule; lag = time to recipient's next action"})
