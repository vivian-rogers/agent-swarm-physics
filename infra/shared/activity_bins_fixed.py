"""Corrected `activity_bins` sidecar (found by DQ8, 2026-10-04): activity_bins.parquet silently drops events.

Bug (infra/shared/build_derived.py: build_activity_bins). Event and action rows are binned with
    active_min = (active_offset_s + (t - win_start)) // 60
but the dense grid uses
    active_min = active_offset_s // 60 + minute,      minute = (t - win_start) // 60
and the two are joined on (pt_date, minute, active_min, agent). With a = active_offset_s mod 60 and b the event's
second within its minute, the keys differ whenever a + b >= 60, so every such event is dropped by the left join.
On a day, the share of events lost is ~ a / 60: talk counts per day correlate with a at r = -0.99 (turns -0.999);
305 of 389 days keep < 80% of their AGENT_TALK events, the median day keeps about half, and days with a = 59 s keep
1-2%. Every event-derived column (talk, idle, consolidate, other_event, turns, paused) and therefore `state` is
affected, and so is everything built from `state` (outages / stall_minutes / reasons via outages.py, and
hypothesis spins built from activity_bins: H02, H05, H12, H13, H19, H22, H25, H26, H30, H33, H36, H38, ...).
The dropping is random within a day (it depends only on the event's second), so it thins activity at a
day-specific rate: rates and co-activation are understated and vary from day to day for no behavioral reason.

Fix: identical code, but events are joined to the grid on (pt_date, minute, agent) and active_min is taken from the
grid. --verify: 170,870 / 170,870 roster-agent talk events recovered (the other 2,623 AGENT_TALK events are the
Claude Code agent's, excluded from the grid by design); median per-day turn recovery 1.000 (old table: 0.53). Output: data/processed/shared/activity_bins_fixed.parquet, same schema and row set as activity_bins.parquet.
Rebuild of the original belongs to DQ7 (the coordinator merges); until then use this sidecar.

Usage: uv run python infra/shared/activity_bins_fixed.py            (build, ~1 min)
       uv run python infra/shared/activity_bins_fixed.py --verify   (per-day talk/turn recovery vs events/actions)
Library: build(ev, acts, cal, roster) -> DataFrame (same signature as build_derived.build_activity_bins).
"""
from __future__ import annotations

import os

for _v, _n in (("POLARS_MAX_THREADS", "2"), ("OMP_NUM_THREADS", "2"), ("OPENBLAS_NUM_THREADS", "2"),
               ("MKL_NUM_THREADS", "2"), ("VECLIB_MAXIMUM_THREADS", "2")):
    os.environ.setdefault(_v, _n)

import sys  # noqa: E402
import time  # noqa: E402
from pathlib import Path  # noqa: E402

import polars as pl  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import OUT, write_provenance  # noqa: E402

STATE = {"absent": 0, "silent": 1, "idle": 2, "act": 3, "talk": 4}  # = build_derived.STATE


def build(ev: pl.DataFrame, acts: pl.DataFrame, cal: pl.DataFrame, roster: pl.DataFrame) -> pl.DataFrame:
    win = cal.select("pt_date", "win_start", "active_offset_s")

    def binned(df, tcol="t"):
        return (df.with_columns(pl.col(tcol).dt.convert_time_zone("America/Los_Angeles").dt.date().cast(pl.Utf8).alias("pt_date"))
                .join(win, on="pt_date")
                .with_columns(((pl.col(tcol) - pl.col("win_start")).dt.total_seconds() // 60).cast(pl.Int32).alias("minute")))

    e = binned(ev.filter((pl.col("actor_kind") == "agent") & pl.col("agent").is_not_null()))
    e = e.with_columns(
        (pl.col("action_type") == "AGENT_TALK").cast(pl.Int16).alias("talk"),
        pl.col("action_type").is_in(["WAIT", "PAUSE"]).cast(pl.Int16).alias("idle"),
        (pl.col("action_type") == "CONSOLIDATE").cast(pl.Int16).alias("consolidate"),
        (~pl.col("action_type").is_in(["AGENT_TALK", "WAIT", "PAUSE", "CONSOLIDATE"])).cast(pl.Int16).alias("other_event"))
    e = e.group_by("pt_date", "minute", "agent").agg(
        pl.col("talk").sum(), pl.col("idle").sum(), pl.col("consolidate").sum(), pl.col("other_event").sum())
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
    out = (grid.join(e, on=key, how="left").join(c, on=key, how="left").join(pz, on=key, how="left")
           .with_columns(*[pl.col(k).fill_null(0).cast(pl.Int16) for k in ("talk", "idle", "consolidate", "other_event", "turns", "paused")]))
    out = out.with_columns(
        pl.when(pl.col("talk") > 0).then(STATE["talk"])
        .when((pl.col("turns") > 0) | (pl.col("other_event") > 0) | (pl.col("consolidate") > 0)).then(STATE["act"])
        .when((pl.col("idle") > 0) | (pl.col("paused") > 0)).then(STATE["idle"])
        .otherwise(STATE["silent"]).cast(pl.Int8).alias("state"))
    return out.with_columns(pl.col("minute").cast(pl.Int64)).sort("active_min", "agent")


def load_inputs():
    ev = pl.read_parquet(OUT / "events_core.parquet", columns=["t", "actor_kind", "agent", "action_type", "pause_s"])
    acts = pl.read_parquet(OUT / "actions.parquet", columns=["t", "agent"])
    cal = pl.read_parquet(OUT / "calendar.parquet")
    roster = pl.read_parquet(OUT / "roster.parquet")
    return ev, acts, cal, roster


def verify(path: Path = OUT / "activity_bins_fixed.parquet") -> pl.DataFrame:
    """Per day: talk events and turns recovered by the old and fixed tables vs events_core / actions."""
    ev, acts, cal, _ = load_inputs()
    tz = "America/Los_Angeles"
    talk = (ev.filter((pl.col("action_type") == "AGENT_TALK") & (pl.col("actor_kind") == "agent") & pl.col("agent").is_not_null())
            .with_columns(pl.col("t").dt.convert_time_zone(tz).dt.date().cast(pl.Utf8).alias("pt_date"))
            .group_by("pt_date").agg(pl.len().alias("n_talk_events")))
    turns = (acts.filter(pl.col("agent").is_not_null()).with_columns(pl.col("t").dt.convert_time_zone(tz).dt.date().cast(pl.Utf8).alias("pt_date"))
             .group_by("pt_date").agg(pl.len().alias("n_turns")))
    old = pl.read_parquet(OUT / "activity_bins.parquet").group_by("pt_date").agg(pl.col("talk").sum().alias("old_talk"),
                                                                                 pl.col("turns").sum().alias("old_turns"),
                                                                                 (pl.col("state") >= 3).sum().alias("old_active"))
    new = pl.read_parquet(path).group_by("pt_date").agg(pl.col("talk").sum().alias("new_talk"), pl.col("turns").sum().alias("new_turns"),
                                                        (pl.col("state") >= 3).sum().alias("new_active"))
    j = (cal.select("pt_date", (pl.col("active_offset_s") % 60).alias("a_mod60"), "holdout").join(talk, on="pt_date", how="left")
         .join(turns, on="pt_date", how="left").join(old, on="pt_date").join(new, on="pt_date")
         .with_columns((pl.col("old_talk") / pl.col("n_talk_events")).alias("old_talk_ratio"),
                       (pl.col("new_talk") / pl.col("n_talk_events")).alias("new_talk_ratio"),
                       (pl.col("old_turns") / pl.col("n_turns")).alias("old_turn_ratio"),
                       (pl.col("new_turns") / pl.col("n_turns")).alias("new_turn_ratio"),
                       (pl.col("new_active") / pl.col("old_active")).alias("active_minutes_fixed_over_old")))
    return j.sort("pt_date")


def main():
    if "--verify" in sys.argv:
        j = verify()
        with pl.Config(tbl_rows=12, tbl_cols=20, tbl_width_chars=220, float_precision=3):
            print(j.select("old_talk_ratio", "new_talk_ratio", "old_turn_ratio", "new_turn_ratio",
                           "active_minutes_fixed_over_old").describe())
            print("days with old talk ratio < 0.8:", j.filter(pl.col("old_talk_ratio") < 0.8).height, "of", j.height)
            print("days with new talk ratio < 0.98:", j.filter(pl.col("new_talk_ratio") < 0.98).height)
        return
    t0 = time.time()
    ev, acts, cal, roster = load_inputs()
    out = build(ev, acts, cal, roster)
    out.write_parquet(OUT / "activity_bins_fixed.parquet", compression="zstd")
    write_provenance("activity_bins_fixed", ["events_core", "actions", "calendar", "roster"],
                     {"fix": "join events to the grid on (pt_date, minute, agent); active_min from the grid",
                      "replaces": "activity_bins.parquet (build_derived.build_activity_bins)", "found_by": "DQ8"})
    print(f"activity_bins_fixed: {out.height} rows, {time.time() - t0:.0f}s")


if __name__ == "__main__":
    main()
