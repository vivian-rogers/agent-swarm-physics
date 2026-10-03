"""Build the H03 processed tables from the shared Phase 0 tables (no raw rescans).

Outputs (data/processed/H03-self-excited-criticality/):
  days.parquet    one row per NON-HOLDOUT village day (realization): day_id, pt_date, goal_no, regime,
                  mode, T_s (window length), first_day (goal's first day), n_active (agents with >= 1 agent event),
                  n_talk, n_all, n_exo, weekday, documented_hours
  events.parquet  agent events inside each non-holdout window: day_id, t_s (seconds since win_start), agent, talk,
                  turn_first (False if within 1 s of the same agent's previous event: ALL uses turn_first only)
  exo.parquet     human + automated USER_TALK from 1 h before win_start to win_end: day_id, t_s, kind

Holdout: a day is dropped if calendar.holdout is true OR holdout_mask(pt_date, goal_no) is true.
Run: uv run python hypotheses/H03-self-excited-criticality/scheme/build.py
"""
from __future__ import annotations

import datetime as dt
import json
import re
import sys
from pathlib import Path

import polars as pl

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
from infra.shared.common import REVISION, git_commit, holdout_mask  # noqa: E402

SHARED = ROOT / "data/processed/shared"
OUT = ROOT / "data/processed/H03-self-excited-criticality"
EXO_LEAD_S = 3600.0
MERGE_S = 1.0


def goal_modes() -> dict[int, str]:
    """Coupling mode per goal from the 'At a glance' table of goal-periods.md. #51 (I/K, private roles) -> 'P'."""
    txt = (ROOT / "hypotheses/hypohypotheses/goal-periods.md").read_text()
    modes = {}
    for line in txt.splitlines():
        m = re.match(r"^\| (\d+) \| [^|]+\| [^|]+\| [^|]+\| [^|]+\| [^|]+\| ([A-Z]) \| ([A-Z/]+) \|", line)
        if m:
            g, by, mode = int(m.group(1)), m.group(2), m.group(3)
            modes[g] = "P" if by == "P" else mode
    assert len(modes) == 51, len(modes)
    return modes


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    cal = pl.read_parquet(SHARED / "calendar.parquet").sort("pt_date")
    mask = holdout_mask(cal["pt_date"].to_list(), cal["goal_no"].to_list())
    cal = cal.with_columns(h2=pl.Series(mask))
    first = cal.group_by("goal_no").agg(pl.col("pt_date").min().alias("first_date"))
    cal = cal.join(first, on="goal_no").with_columns(first_day=pl.col("pt_date") == pl.col("first_date"))
    keep = cal.filter(~pl.col("holdout") & ~pl.col("h2") & (pl.col("goal_no") > 0)).sort("pt_date")
    keep = keep.with_row_index("day_id").with_columns(pl.col("day_id").cast(pl.Int32))
    modes = goal_modes()
    keep = keep.with_columns(mode=pl.col("goal_no").replace_strict(modes, return_dtype=pl.String))

    ev = pl.read_parquet(SHARED / "events_core.parquet",
                         columns=["t", "pt_date", "goal_no", "actor_kind", "agent", "action_type"])
    win = keep.select("day_id", "pt_date", "win_start", "win_end", pl.col("goal_no").alias("day_goal"))

    ag = (ev.filter(pl.col("actor_kind") == "agent")
          .join(win, on="pt_date", how="inner")
          .filter((pl.col("t") >= pl.col("win_start")) & (pl.col("t") <= pl.col("win_end"))))
    # sanity: every event's goal equals its day's goal (kickoffs land before the window opens)
    bad = ag.filter(pl.col("goal_no") != pl.col("day_goal")).height
    events = (ag.with_columns(t_s=(pl.col("t") - pl.col("win_start")).dt.total_microseconds() / 1e6,
                              talk=pl.col("action_type") == "AGENT_TALK")
              .select("day_id", "t_s", "agent", "talk").sort("day_id", "t_s"))

    hx = ev.filter(pl.col("action_type").cast(pl.String) == "USER_TALK",
                   pl.col("actor_kind").cast(pl.String).is_in(["human", "automated"]))
    # exo events: match by UTC time to [win_start - lead, win_end] of a kept day (not by pt_date)
    exo_rows = []
    for d in win.iter_rows(named=True):
        lo = d["win_start"] - dt.timedelta(seconds=EXO_LEAD_S)
        sub = hx.filter((pl.col("t") >= lo) & (pl.col("t") <= d["win_end"]))
        if sub.height:
            exo_rows.append(sub.select(
                pl.lit(d["day_id"], dtype=pl.Int32).alias("day_id"),
                ((pl.col("t") - d["win_start"]).dt.total_microseconds() / 1e6).alias("t_s"),
                pl.col("actor_kind").cast(pl.String).alias("kind")))
    exo = pl.concat(exo_rows).sort("day_id", "t_s")

    cnt = events.group_by("day_id").agg(n_all=pl.len(), n_talk=pl.col("talk").sum(),
                                        n_active=pl.col("agent").n_unique())
    ecnt = exo.filter(pl.col("t_s") >= 0).group_by("day_id").agg(n_exo=pl.len())
    days = (keep.join(cnt, on="day_id", how="left").join(ecnt, on="day_id", how="left")
            .with_columns(T_s=(pl.col("win_end") - pl.col("win_start")).dt.total_microseconds() / 1e6,
                          n_exo=pl.col("n_exo").fill_null(0))
            .select("day_id", "pt_date", "goal_no", pl.col("regime").cast(pl.String), "mode", "T_s",
                    "first_day", "n_active", "n_talk", "n_all", "n_exo", "weekday", "documented_hours")
            .sort("day_id"))
    days = days.filter(pl.col("n_all").is_not_null())

    # ALL = agent *turns*: an agent's events within MERGE_S of its own previous event are one compound turn
    # (93% of pooled gaps < 0.1 s are same-agent logging of one turn). turn_first marks the kept event.
    events = (events.sort("day_id", "agent", "t_s")
              .with_columns(turn_first=(pl.col("t_s").diff().over("day_id", "agent").fill_null(1e9) >= MERGE_S))
              .sort("day_id", "t_s")
              .with_columns(pl.col("t_s").cast(pl.Float64), pl.col("agent").cast(pl.Int8)))
    days.write_parquet(OUT / "days.parquet", compression="zstd")
    events.write_parquet(OUT / "events.parquet", compression="zstd")
    exo.write_parquet(OUT / "exo.parquet", compression="zstd")

    # tie / near-tie audit of the pooled streams (structural; affects kernel-timescale bounds)
    def ties(df):
        g = df.sort("day_id", "t_s").with_columns(dt_=pl.col("t_s").diff().over("day_id")).drop_nulls("dt_")
        return {"n": g.height, "frac_eq0": float((g["dt_"] == 0).mean()), "frac_lt1s": float((g["dt_"] < 1).mean())}
    audit = {"goal_mismatch_events": bad, "ties_all": ties(events), "ties_turns": ties(events.filter("turn_first")), "ties_talk": ties(events.filter("talk")),
             "n_days": days.height, "goals": sorted(set(days["goal_no"].to_list()))}
    print(json.dumps(audit, indent=1))

    prov = {"built_by": "hypotheses/H03-self-excited-criticality/scheme/build.py", "git_commit": git_commit(),
            "inputs": [{"source": "ai-village", "revision": REVISION,
                        "tables": ["shared/events_core", "shared/calendar", "shared/kicks (inspected)"]}],
            "params": {"holdout": "calendar.holdout | holdout_mask(pt_date, goal_no)", "exo_lead_s": EXO_LEAD_S,
                       "event_sets": {"TALK": "action_type == AGENT_TALK", "ALL": "actor_kind == agent, same-agent repeats within merge_s collapsed (turn_first)"}, "merge_s": MERGE_S,
                       "mode_source": "hypotheses/hypohypotheses/goal-periods.md (At a glance); #51 coded P"},
            "audit": audit,
            "built_at": dt.datetime.now(dt.timezone.utc).isoformat()}
    (OUT / "_provenance.json").write_text(json.dumps(prov, indent=1))


if __name__ == "__main__":
    main()
