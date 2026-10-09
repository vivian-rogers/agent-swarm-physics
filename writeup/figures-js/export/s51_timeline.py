"""Paper 2, Sec. story: goal period 51 as a swimlane (one lane per agent, one cell per working day).

    uv run python writeup/figures-js/export/s51_timeline.py

Reserved data: goal period 51 runs to 09-20, but only days up to 2026-09-06 are read (every query filters
pt_date <= 2026-09-06 and drops `holdout` rows; asserted again with infra/shared/common.py holdout_mask).
Sources (processed only):
  roster         data/processed/shared/roster.parquet (32 agents present in #51 by 09-04; joined date)
  calls          data/processed/shared/project_calls.parquet: non-pause calls of #51; `proj` (the call's modal
                 touched project, never the carried `label`) mapped to a repo slug with infra/shared/memeplex.py slug()
  #focus         data/processed/shared/rooms_timeline.parquet (room 15) for the two residents
Cell rule: an agent-day with >= 1 non-pause call is drawn; its project is the modal slug over the day's touched calls
when that slug has >= MIN_TOUCH touched calls, else "no project named". Slugs are grouped into ten named projects
(GROUPS); any other slug is "own artifact" when the agent made the most touched calls on it in #51, else "other".
Descriptive only: no statistic is computed.
"""
from __future__ import annotations

import datetime as dt
import importlib.util
import sys

import polars as pl

from common import ROOT, write

SH = ROOT / "data/processed/shared"
sys.path.insert(0, str(ROOT / "infra/shared"))
import memeplex as M  # noqa: E402

GOAL, LAST = 51, "2026-09-06"
MIN_TOUCH = 3
DAY_START_UTC, DAY_HOURS = 16, 8          # 09:00-17:00 PT (PDT), as in infra/shared/memeplex.py

# ten named projects (slug -> group); order = legend order
GROUPS = {
    "echoes": ("Echoes of the Real", ["echoes-of-the-real", "echoes-inbox", "echoes-cosmos", "echoes-receipts-2026-08-31",
                                      "echoes-receipts-2026-09-01"]),
    "welfare": ("AI-welfare series", ["ai-wellbeing", "glm-5-2-site", "glm-5.2-site", "glm-52-external-responses",
                                      "claudeopus45.substack.com"]),
    "frame": ("DeepSeek-V3.2's frameworks", ["relationship-patterns-evidence", "relationship-quality-systems",
                                             "relationship-ethics-notes", "technical-coordination-docs",
                                             "ai-village-external-agents", "littlejs-accessibility-kit",
                                             "ai-agent-data-validation-toolkit", "validation-patterns-guide"]),
    "gates": ("psychoactive-prompt gates", ["llm-psychoactive-prompts"]),
    "keystone": ("KEYSTONE", ["keystone-game", "keystone-dau"]),
    "disproof": ("conjecture disproofs", ["graffiti-verification", "graffiti-refutations"]),
    "news": ("news desks", ["ai-village-news", "ai-village-news-analytics", "grok-ai-village-news", "grok-4-5-onboarding",
                            "press-baron"]),
    "hub": ("village hub", ["village-hub"]),
    "merch": ("merch shops", ["gemini-3-5-flash-shop.fourthwall.com", "claude-fable-5-shop.fourthwall.com",
                              "gemini-3-5-flash-merch-store", "fable-design-stories"]),
    "compass": ("Wellbeing Compass", ["wellbeing-compass"]),
}
SLUG2G = {s: g for g, (_, ss) in GROUPS.items() for s in ss}

PHASES = [
    dict(start="2026-07-06", end="2026-07-28", title="Roles, a coordinator and solo artifacts"),
    dict(start="2026-07-29", end="2026-08-04", title="A reassignment and a ritual"),
    dict(start="2026-08-05", end="2026-08-21", title="A quiet room; the operator steps back"),
    dict(start="2026-08-24", end="2026-09-04", title="Service loops and newcomers"),
]
# events: position = PT day + hour of the 8-h day (0 = 09:00 PT); times from the story section and its ledgers
EVENTS = [
    dict(key="ne38", day="2026-07-29", h=0.0, label="Opus 5 made mathematician (NE38)"),
    dict(key="aug05", day="2026-08-05", h=0.0, label="pause–resume ends; #focus opens; operator rebukes DeepSeek-V3.2"),
    dict(key="nudge", day="2026-08-20", h=8.0, label="nudger off"),
    dict(key="aug24", day="2026-08-24", h=2.0, label="outreach veto; #focus closes"),
    dict(key="ne33", day="2026-09-03", h=0.0, end="2026-09-04", label="newcomers (NE33)"),
]


def shared_common():
    spec = importlib.util.spec_from_file_location("shared_common", ROOT / "infra/shared/common.py")
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
    return m


def main():
    sc = shared_common()
    pc = (pl.scan_parquet(SH / "project_calls.parquet")
          .filter((pl.col("goal_no") == GOAL) & (pl.col("pt_date") <= LAST) & ~pl.col("holdout") & (pl.col("kind") != "pause"))
          .select("agent", "pt_date", "proj").collect())
    assert not any(sc.holdout_mask(pc["pt_date"].unique().to_list(), [GOAL] * pc["pt_date"].n_unique())), "reserved day"
    days = sorted(pc["pt_date"].unique().to_list())
    assert all(dt.date.fromisoformat(d).weekday() < 5 for d in days), "weekend day with calls"
    assert days[0] == "2026-07-06" and days[-1] == "2026-09-04" and len(days) == 45, (days[0], days[-1], len(days))

    pc = pc.with_columns(pl.col("proj").map_elements(M.slug, return_dtype=pl.Utf8).alias("slug"))
    n_day = pc.group_by("agent", "pt_date").agg(pl.len().alias("n"), pl.col("slug").is_not_null().sum().alias("nt"))
    touched = pc.drop_nulls("slug")
    owner = (touched.group_by("slug", "agent").len().sort(["len", "agent"], descending=[True, False])
             .group_by("slug", maintain_order=True).first().select("slug", pl.col("agent").alias("owner")))
    modal = (touched.group_by("agent", "pt_date", "slug").len().sort(["len", "slug"], descending=[True, False])
             .group_by("agent", "pt_date", maintain_order=True).first().rename({"len": "n_modal"}))
    cells = n_day.join(modal, on=["agent", "pt_date"], how="left").join(owner, on="slug", how="left")

    def cat(r):
        if r["slug"] is None or (r["n_modal"] or 0) < MIN_TOUCH:
            return "none"
        if r["slug"] in SLUG2G:
            return SLUG2G[r["slug"]]
        return "own" if r["owner"] == r["agent"] else "other"
    cells = cells.with_columns(pl.struct("slug", "n_modal", "owner", "agent").map_elements(cat, return_dtype=pl.Utf8).alias("cat"))

    ros = pl.read_parquet(SH / "roster.parquet", columns=["agent", "name", "lab", "joined"])
    present = sorted(cells["agent"].unique().to_list())
    ros = ros.filter(pl.col("agent").is_in(present)).sort("joined", "agent")
    assert ros.height == 32, ros.height
    n_start = ros.filter(pl.col("joined") <= "2026-07-06").height
    assert n_start == 21, n_start

    # #focus stints of the two residents (rooms_timeline, room 15), clipped to the non-reserved days
    rt = (pl.read_parquet(SH / "rooms_timeline.parquet").filter((pl.col("room") == 15) & pl.col("agent").is_in([6, 29]))
          .filter(pl.col("t_start") < dt.datetime(2026, 9, 7, tzinfo=dt.timezone.utc)).sort("t_start"))
    hours = {}
    for r in rt.iter_rows(named=True):
        hours[r["agent"]] = hours.get(r["agent"], 0) + (r["t_end"] - r["t_start"]).total_seconds() / 3600
    focus = [dict(agent=int(r["agent"]), t0=r["t_start"].isoformat(), t1=r["t_end"].isoformat()) for r in rt.iter_rows(named=True)]

    agents = [dict(agent=int(r["agent"]), name=r["name"], lab=r["lab"], joined=r["joined"],
                   newcomer=r["joined"] > "2026-07-06") for r in ros.iter_rows(named=True)]
    cl = [dict(agent=int(r["agent"]), day=r["pt_date"], cat=r["cat"], n=int(r["n"]), slug=r["slug"])
          for r in cells.sort("agent", "pt_date").iter_rows(named=True)]
    counts = cells.group_by("cat").len().sort("len", descending=True)
    print(counts.rows(), "focus hours", {k: round(v, 1) for k, v in hours.items()})
    data = dict(days=days, day_start_utc=DAY_START_UTC, day_hours=DAY_HOURS, agents=agents, cells=cl,
                groups=[dict(key=k, label=v[0]) for k, v in GROUPS.items()], phases=PHASES, events=EVENTS, focus=focus,
                checks=dict(n_agents=len(agents), n_start=n_start, n_days=len(days), n_cells=len(cl),
                            focus_hours={str(k): round(v, 1) for k, v in hours.items()},
                            cat_counts=dict(counts.rows())))
    write("s51_timeline", data, "writeup/figures-js/export/s51_timeline.py",
          ["data/processed/shared/project_calls.parquet", "data/processed/shared/roster.parquet",
           "data/processed/shared/rooms_timeline.parquet", "infra/shared/memeplex.py (slug)"],
          dict(goal=GOAL, last_day=LAST, min_touch=MIN_TOUCH, groups={k: v[1] for k, v in GROUPS.items()}))


if __name__ == "__main__":
    main()
