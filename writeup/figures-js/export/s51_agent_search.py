"""Paper 2, Sec. results: the automatic search for individuals in goal period 51 (Fig. fig:search; card H148).
Panel a: each agent's single-atom colonial A as a z-score against within-day permutations of its own states, on the
odd days and on the even days (30-min bins). Panel b: how many local maxima the boundary search found on the real
data and on rotated data, at the agent level (67 atoms) and the element level (140 atoms), and how many held out of
sample.

    uv run python writeup/figures-js/export/s51_agent_search.py
"""
from __future__ import annotations

import json
import math

from common import ROOT, write

SRC = ROOT / "data/processed/H148-agent-discovery-51/results"


def main():
    a = json.load(open(SRC / "agents_w30.json"))
    e = json.load(open(SRC / "elements_w30.json"))
    ag = [s for s in a["singles"] if s["kind"] == "agent" and all(isinstance(s[k], (int, float)) and math.isfinite(s[k]) for k in ("z_h0", "z_h1"))]
    ag.sort(key=lambda s: -(s["z_h0"] + s["z_h1"]) / 2)
    n_ind = sum(1 for s in ag if s["individual"])
    print(len(ag), "agents;", n_ind, "individual on both halves:", [s["name"] for s in ag if s["individual"]])
    assert a["predictions"]["P1"]["n_agents"] == 27 and n_ind == 1
    assert len(ag) == 27, len(ag)      # the card's 27 agents present >= 10 days; the five late newcomers have no z
    P7a, P7e = a["predictions"]["P7"], e["predictions"]["P7"]
    assert P7a["real_local_maxima"] == 16 and round(P7a["rotated_local_maxima_mean"], 1) == 13.3
    assert P7e["real_local_maxima"] == 72 and round(P7e["rotated_local_maxima_mean"], 1) == 69.0
    counts = [dict(level="agents", real=P7a["real_local_maxima"], rotated=P7a["rotated_local_maxima_mean"],
                   real_held=P7a["real_held_maxima"], rotated_held=P7a["rotated_held_maxima_mean"]),
              dict(level="elements", real=P7e["real_local_maxima"], rotated=P7e["rotated_local_maxima_mean"],
                   real_held=P7e["real_held_maxima"], rotated_held=P7e["rotated_held_maxima_mean"])]
    agents = [dict(name=s["name"], z_odd=s["z_h0"], z_even=s["z_h1"], individual=s["individual"]) for s in ag]
    write("s51_agent_search", dict(agents=agents, counts=counts, z_thr=1.96, n_agents=len(ag), n_individual=n_ind),
          "writeup/figures-js/export/s51_agent_search.py",
          ["data/processed/H148-agent-discovery-51/results/agents_w30.json",
           "data/processed/H148-agent-discovery-51/results/elements_w30.json"], dict(bins="30 min"))


if __name__ == "__main__":
    main()
