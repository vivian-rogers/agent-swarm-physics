"""Timeline figure (Sec. III): goal periods by author, agent lanes by lab, agents present, scaffold changes A-J.

    uv run python writeup/figures-js/export/timeline.py

Replaces writeup/papers/thermodynamics/figs/timeline.pdf (infra/ai_village_overview/figures.py: fig_timeline).
Sources (processed only):
  roster        data/processed/shared/roster.parquet (46 agents: lab, joined, left; left = null means active at export)
  goal periods  data/processed/shared/period_units.parquet (first start and last end of each goal's units)
  goal author   GOAL_CLASS, and the scaffold-change dates CHANGES (letters A-J), imported from
                infra/ai_village_overview/figures.py so the classes match the appendix goal table (O/D/F/A/P).
Descriptive only: no statistic is computed, so no reserved data is masked; every goal period is drawn.
Checks: 46 agents; 51 goal periods; 4 agents at the start of goal 1 and 21 at the start of goal 51 (paper text).
"""
from __future__ import annotations

import datetime as dt
import importlib.util
import sys

import polars as pl

from common import ROOT, write

SH = ROOT / "data/processed/shared"
EXPORT = "2026-09-20"            # export date: agents still active run to here
X0, X1 = "2025-03-25", "2026-09-27"
LAB_ORDER = ["Anthropic", "OpenAI", "Google", "xAI", "DeepSeek", "Moonshot", "Fine-tuned (Kimi)", "Zhipu", "Meta"]
AUTHOR = {"operator-specified": "O", "agents design content": "D", "free choice / holiday": "F",
          "set by an agent": "A", "private assigned roles": "P"}


def overview_constants():
    """GOAL_CLASS and CHANGES from the overview script, without running its figures."""
    argv = sys.argv
    sys.argv = [argv[0]]
    try:
        spec = importlib.util.spec_from_file_location("ov", ROOT / "infra/ai_village_overview/figures.py")
        ov = importlib.util.module_from_spec(spec); spec.loader.exec_module(ov)
    finally:
        sys.argv = argv
    return ov.GOAL_CLASS, ov.CHANGES


def main():
    goal_class, changes = overview_constants()
    ros = pl.read_parquet(SH / "roster.parquet", columns=["agent", "name", "lab", "joined", "left"])
    assert ros.height == 46, ros.height
    assert set(ros["lab"].unique()) <= set(LAB_ORDER), ros["lab"].unique()
    agents = []
    for r in ros.iter_rows(named=True):
        agents.append(dict(agent=int(r["agent"]), name=r["name"], lab=r["lab"], joined=r["joined"],
                           left=r["left"] or EXPORT, active=r["left"] is None))

    pu = pl.read_parquet(SH / "period_units.parquet", columns=["goal_no", "start", "end", "n_roster", "regime"])
    g = (pu.group_by("goal_no").agg(pl.col("start").min(), pl.col("end").max(), pl.col("regime").first())
         .sort("goal_no"))
    assert g.height == 51 and g["goal_no"].to_list() == list(range(1, 52))
    starts = [s.date().isoformat() for s in g["start"].to_list()]
    goals = []
    for i, row in enumerate(g.iter_rows(named=True)):
        # tiles are contiguous: each goal runs to the next goal's first day; the last to its last unit's end (+1 day)
        end = starts[i + 1] if i + 1 < g.height else (row["end"].date() + dt.timedelta(days=1)).isoformat()
        goals.append(dict(goal=int(row["goal_no"]), start=starts[i], end=end, author=AUTHOR[goal_class[row["goal_no"]]],
                          regime=row["regime"]))

    def n_on(day):
        return sum(a["joined"] <= day < a["left"] for a in agents)
    n_first, n_last = n_on(goals[0]["start"]), n_on(goals[-1]["start"])
    assert (n_first, n_last) == (4, 21), (n_first, n_last)

    data = dict(x0=X0, x1=X1, export=EXPORT, lab_order=LAB_ORDER, agents=agents, goals=goals,
                changes=[dict(letter=k, date=d) for k, d in changes],
                regimes=[dict(name="I", start=X0, end="2026-02-25"), dict(name="II", start="2026-02-25", end="2026-03-24"),
                         dict(name="III", start="2026-03-24", end=X1)],
                checks=dict(n_agents=len(agents), n_goals=len(goals), n_start_g01=n_first, n_start_g51=n_last))
    print(data["checks"], "labs", pl.DataFrame(agents)["lab"].value_counts().sort("count", descending=True).rows())
    write("timeline", data, "writeup/figures-js/export/timeline.py",
          ["data/processed/shared/roster.parquet", "data/processed/shared/period_units.parquet",
           "infra/ai_village_overview/figures.py (GOAL_CLASS, CHANGES)"],
          dict(export=EXPORT, x0=X0, x1=X1))


if __name__ == "__main__":
    main()
