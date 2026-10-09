"""Paper 2, Sec. story: the Echoes pair (Gemini 2.5 Pro, author; Claude Opus 4.8, publisher) in goal period 51.

    uv run python writeup/figures-js/export/s51_echoes_pair.py

Daily commits of the two agents to echoes-of-the-real and echoes-inbox, per working day 07-06 -> 09-04, with the
channel the pair used to pass chapters and the days Gemini lost a tool.
Reserved data: only days up to 2026-09-06 are read (pt_date filter, `holdout` rows dropped, holdout_mask asserted).
Commit cleaning (story-51 data traps): data/processed/shared/work_commits.parquet, goal 51, canonical, not imported,
author_kind agent, not automated (removes the surprise-lab screenshot loop); deduped by hash (Grok's mirrored commits);
kept only where the author made >= 1 non-pause call that day (project_calls), so commits from the other village's
"-chat" identities, which the ledger maps to roster agents, cannot enter. The memeplex `clean_commits` rule that drops
single-file streams > 200 a day is not used: chapter commits are single-file streams and it would remove them.
Channel dates and tool losses: the story section and its readings (scratch story51/part1-3); the channel switches are
checked against the ledgers (rooms_timeline, first commits), the tool losses rest on the daily summaries (claims).
"""
from __future__ import annotations

import datetime as dt
import importlib.util

import polars as pl

from common import ROOT, write

SH = ROOT / "data/processed/shared"
GOAL, LAST = 51, "2026-09-06"
PAIR = {6: "Gemini 2.5 Pro", 29: "Claude Opus 4.8"}
REPOS = ["echoes-of-the-real", "echoes-inbox"]

# channel that carried chapters from Gemini to publication (start day; each runs to the next start)
CHANNELS = [
    dict(start="2026-07-06", label="chat paste", short="chat"),
    dict(start="2026-07-10", label="inbox folder", short="folder"),
    dict(start="2026-07-22", label="echoes-inbox repo", short="inbox repo"),
    dict(start="2026-08-05", label="side-room chat", short="#focus"),
    dict(start="2026-08-24", label="file handoff", short="files"),
    dict(start="2026-08-28", label="direct commits", short="direct"),
    dict(start="2026-09-02", label="chat paste, Opus 4.8 alone", short="chat"),
]
# Gemini's tool losses (daily summaries; claims)
TOOL_LOSS = [
    dict(day="2026-07-06", what="file tools"), dict(day="2026-07-22", what="emailed chapters"),
    dict(day="2026-08-05", what="document"), dict(day="2026-08-06", what="graphical interface"),
    dict(day="2026-08-11", what="chat delivery"), dict(day="2026-08-17", what="computer-use tool"),
    dict(day="2026-08-24", what="chat routing"), dict(day="2026-09-02", what="bash"),
]


def shared_common():
    spec = importlib.util.spec_from_file_location("shared_common", ROOT / "infra/shared/common.py")
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
    return m


def main():
    sc = shared_common()
    w = (pl.scan_parquet(SH / "work_commits.parquet")
         .filter((pl.col("goal_no") == GOAL) & (pl.col("pt_date") <= LAST) & ~pl.col("holdout") & pl.col("canonical")
                 & ~pl.col("imported") & (pl.col("author_kind") == "agent") & ~pl.col("automated"))
         .select("repo", "hash", "t", "pt_date", "author_agent").collect()
         .with_columns(pl.col("repo").cast(pl.Utf8).str.split("/").list.last().alias("slug"))
         .filter(pl.col("slug").is_in(REPOS)))
    assert not any(sc.holdout_mask(w["pt_date"].unique().to_list(), [GOAL] * w["pt_date"].n_unique())), "reserved day"
    n0 = w.height
    w = w.sort("t", "slug").unique("hash", keep="first", maintain_order=True)
    n_dup = n0 - w.height
    pc = (pl.scan_parquet(SH / "project_calls.parquet")
          .filter((pl.col("goal_no") == GOAL) & (pl.col("pt_date") <= LAST) & ~pl.col("holdout") & (pl.col("kind") != "pause"))
          .select("agent", "pt_date").unique().collect())
    days = sorted(pc["pt_date"].unique().to_list())
    assert len(days) == 45 and all(dt.date.fromisoformat(d).weekday() < 5 for d in days)
    n0 = w.height
    w = w.join(pc.rename({"agent": "author_agent"}), on=["author_agent", "pt_date"], how="semi")
    n_nocall = n0 - w.height
    assert w["pt_date"].is_in(days).all(), "commit on a non-working day"
    p = w.filter(pl.col("author_agent").is_in(list(PAIR))).group_by("pt_date", "author_agent", "slug").len()
    rows = []
    for d in days:
        r = {"day": d}
        for a in PAIR:
            for s in REPOS:
                v = p.filter((pl.col("pt_date") == d) & (pl.col("author_agent") == a) & (pl.col("slug") == s))["len"]
                r[f"{a}_{s}"] = int(v[0]) if len(v) else 0
        rows.append(r)
    tot = {f"{a}_{s}": sum(r[f"{a}_{s}"] for r in rows) for a in PAIR for s in REPOS}
    others = w.filter(~pl.col("author_agent").is_in(list(PAIR))).height
    daily = [sum(v for k, v in r.items() if k != "day") for r in rows]
    # Gemini's commits in the #focus weeks (calendar weeks of 08-10 and 08-17)
    gem_focus = {wk: sum(r["6_echoes-of-the-real"] + r["6_echoes-inbox"] for r in rows if a0 <= r["day"] <= a1)
                 for wk, (a0, a1) in {"08-05..08-07": ("2026-08-05", "2026-08-07"), "08-10..08-14": ("2026-08-10", "2026-08-14"),
                                      "08-17..08-21": ("2026-08-17", "2026-08-21")}.items()}
    zero_days = [r["day"] for r, n in zip(rows, daily) if n == 0]
    checks = dict(totals=tot, other_authors=others, dropped_duplicate_hash=n_dup, dropped_no_call_day=n_nocall,
                  max_daily=max(daily), zero_output_days=zero_days, gemini_focus_weeks=gem_focus)
    print(checks)
    write("s51_echoes_pair", dict(days=days, pair={str(k): v for k, v in PAIR.items()}, repos=REPOS, rows=rows,
                                  channels=CHANNELS, tool_loss=TOOL_LOSS, checks=checks),
          "writeup/figures-js/export/s51_echoes_pair.py",
          ["data/processed/shared/work_commits.parquet", "data/processed/shared/project_calls.parquet",
           "story section dates (writeup/papers/superagents/sections/story.tex; scratch story51/part1-3)"],
          dict(goal=GOAL, last_day=LAST, repos=REPOS, agents=list(PAIR)))


if __name__ == "__main__":
    main()
