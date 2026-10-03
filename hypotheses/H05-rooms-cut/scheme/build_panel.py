"""H05 scheme: agent x 1-min bin spins with the agent's current room, non-holdout days only.

Inputs (shared tables, data/processed/shared/): activity_bins, calendar, rooms_timeline, roster.
Outputs (data/processed/H05-rooms-cut/):
  panel.parquet      pt_date, minute, agent, active (state>=3), talk (state==4), room (-1 = unknown), goal_no, regime
  agent_day.parquet  pt_date, agent, room_mode, purity, active_frac, talk_frac, n_bins, goal_no, regime
  _provenance.json

Holdout: days are dropped if calendar.holdout is true OR infra holdout_mask flags them (belt and braces).
Exploration starts 2026-03-16 (#best/#rest exist); regime II days (#35, #36 before 03-24) are kept but labeled.

Usage: uv run python hypotheses/H05-rooms-cut/scheme/build_panel.py
"""
from __future__ import annotations

import datetime as dt
import json
import sys
from pathlib import Path

import polars as pl

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "infra/shared"))
from common import REVISION, git_commit, holdout_mask  # noqa: E402

SH = ROOT / "data/processed/shared"
OUT = ROOT / "data/processed/H05-rooms-cut"
START = "2026-03-16"


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    cal = pl.read_parquet(SH / "calendar.parquet").filter(pl.col("pt_date") >= START)
    hm = holdout_mask(cal["pt_date"].to_list(), cal["goal_no"].to_list())
    cal = cal.with_columns(pl.Series("hm", hm)).filter(~pl.col("holdout") & ~pl.col("hm")).drop("hm")
    days = cal["pt_date"].to_list()
    ab = (pl.scan_parquet(SH / "activity_bins.parquet").filter(pl.col("pt_date").is_in(days))
          .select("pt_date", "minute", "agent", "state").collect())
    ab = ab.join(cal.select("pt_date", "win_start", "goal_no", pl.col("regime").cast(pl.Utf8)), on="pt_date")
    ab = ab.with_columns((pl.col("win_start") + pl.duration(seconds=pl.col("minute") * 60 + 30)).alias("t"))
    rt = pl.read_parquet(SH / "rooms_timeline.parquet").select("agent", "room", pl.col("t_start").alias("t")).sort("agent", "t")
    ab = ab.sort("agent", "t").join_asof(rt, on="t", by="agent", strategy="backward")
    panel = (ab.select("pt_date", pl.col("minute").cast(pl.Int16), "agent",
                       (pl.col("state") >= 3).cast(pl.Int8).alias("active"),
                       (pl.col("state") == 4).cast(pl.Int8).alias("talk"),
                       pl.col("room").fill_null(-1).cast(pl.Int8),
                       "goal_no", "regime")
             .sort("pt_date", "minute", "agent"))
    panel.write_parquet(OUT / "panel.parquet", compression="zstd")

    rm = (panel.filter(pl.col("room") >= 0).group_by("pt_date", "agent", "room").agg(pl.len().alias("n"))
          .sort("n", descending=True).group_by("pt_date", "agent")
          .agg(pl.col("room").first().alias("room_mode"), (pl.col("n").first() / pl.col("n").sum()).alias("purity")))
    ad = (panel.group_by("pt_date", "agent").agg(pl.col("active").mean().alias("active_frac"),
                                                 pl.col("talk").mean().alias("talk_frac"), pl.len().alias("n_bins"),
                                                 pl.col("goal_no").first(), pl.col("regime").first())
          .join(rm, on=["pt_date", "agent"], how="left").sort("pt_date", "agent"))
    ad.write_parquet(OUT / "agent_day.parquet", compression="zstd")

    prov_path = OUT / "_provenance.json"
    prov = json.loads(prov_path.read_text()) if prov_path.exists() else {}
    prov["panel"] = {"built_by": "hypotheses/H05-rooms-cut/scheme/build_panel.py", "git_commit": git_commit(),
                     "inputs": [{"source": "ai-village", "revision": REVISION,
                                 "tables": ["shared/activity_bins", "shared/calendar", "shared/rooms_timeline"]}],
                     "params": {"start": START, "active": "state>=3", "talk": "state==4", "bin": "1 min",
                                "room": "as-of join of rooms_timeline.t_start at bin midpoint", "holdout": "excluded",
                                "n_days": len(days)},
                     "built_at": dt.datetime.now(dt.timezone.utc).isoformat()}
    prov_path.write_text(json.dumps(prov, indent=1))
    print("panel", panel.height, "rows;", len(days), "days;", panel["agent"].n_unique(), "agents")


if __name__ == "__main__":
    main()
