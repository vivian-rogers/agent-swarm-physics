"""H54 kickoff rank (Fig. fig:kickoffrank): (a) rank of each period's own kickoff text among the 33 candidates, against
the kickoff-swap null; (b) #51 private goals, weekly role-swap accuracy against chance.

    uv run python writeup/figures-js/export/h54_kickoff_rank.py

Reuses load() from writeup/visuals/H54-kickoff-quench-target/make.py (the old fig_bc.pdf), which recomputes the ranks
from S_kick.npy and asserts they equal the card table. Reads data/processed/H54-kickoff-quench-target/{NE34,G51}/ and
shared/period_affordances.parquet only. Asserted here: no reserved goal period among the 33, and the #51 days end
before the reserved #51 tail. Weekly CIs: the old script's 90% normal interval (1.645 SE).
"""
from __future__ import annotations

import importlib.util
import sys

import numpy as np

from common import ROOT, write


def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
    return m


sc = load_module("shared_common", ROOT / "infra/shared/common.py")
sys.path.insert(0, str(ROOT / "writeup/visuals"))
mk = load_module("h54make", ROOT / "writeup/visuals/H54-kickoff-quench-target/make.py")


def main():
    d = mk.load()
    ho = sc.load_holdout()
    assert not set(d["goals"]) & set(ho["goal_periods_held_out"]), "a reserved period is in the figure"
    tail = [w for w in ho["ne_windows"] if w["id"] == "#51-tail"][0]
    assert d["g51"]["days_used"][1] < tail["start"], d["g51"]["days_used"]
    n, rank, free = d["n"], d["rank"], d["free"]
    assert n == 33 and d["top1"] == 18 and (n + 1) / 2 == 17, (n, d["top1"])                     # paper: 18/33, median 17
    assert f"{d['res']['p_wilcoxon']:.0e}" == "3e-06"
    g51 = d["g51"]
    assert round(g51["swap_accuracy"], 2) == 0.95
    weeks = []
    for r in g51["weekly"]:
        se = float(np.sqrt(r["swap_accuracy"] * (1 - r["swap_accuracy"]) / r["n_pairs"]))
        weeks.append(dict(week=r["week"] + 1, acc=r["swap_accuracy"], lo=r["swap_accuracy"] - 1.645 * se,
                          hi=r["swap_accuracy"] + 1.645 * se, n_pairs=r["n_pairs"], n_agents=r["n_agents"]))
    periods = [dict(goal=int(gn), rank=int(rk), free=bool(fr)) for gn, rk, fr in zip(d["goals"], rank, free)]
    free_top1 = [p["goal"] for p in periods if p["free"] and p["rank"] == 1]
    named = [p for p in periods if not p["free"]]
    print("top1", d["top1"], "named-target top1", sum(p["rank"] == 1 for p in named), "/", len(named),
          "free", [(p["goal"], p["rank"]) for p in periods if p["free"]], "free at rank 1:", free_top1)
    print("weekly", [round(w["acc"], 3) for w in weeks], "overall", round(g51["swap_accuracy"], 4), "p", g51["p_perm"])
    write("h54_kickoff_rank", dict(n=n, periods=periods, top1=d["top1"], null_median=(n + 1) / 2,
                                   null_band=[0.05 * n, 0.95 * n], p_wilcoxon=d["res"]["p_wilcoxon"],
                                   weeks=weeks, acc_all=g51["swap_accuracy"], p_perm=g51["p_perm"]),
          "writeup/figures-js/export/h54_kickoff_rank.py",
          ["data/processed/H54-kickoff-quench-target/NE34/{S_kick.npy,periods.parquet,results.json}",
           "H54-kickoff-quench-target/G51/native.json", "shared/period_affordances.parquet"],
          dict(embedding="bge", weekly_ci="90% normal (1.645 SE)"))


if __name__ == "__main__":
    main()
