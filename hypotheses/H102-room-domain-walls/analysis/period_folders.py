"""Write H102 period folders.

    --predict   before any outcome: structure (agents per domain, hoppers, days) + the dated prediction per unit
    --results   after run.py: fill the Verdict line and the Result section from results/results.json
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

import polars as pl

HERE = Path(__file__).resolve().parent
H = HERE.parent
sys.path.insert(0, str(HERE))
import h102lib as L  # noqa: E402

GP = H / "goalperiod-subhypotheses"
STAMP = "2026-10-04 ~20:32 UTC"
FOLDER = {u: (u if u.startswith("G") else "G51") for u in L.UNITS}
ROLE = {"G35": "replication", "G37": "replication", "G39": "replication", "G41": "replication", "G42": "replication",
        "G38": "native", "G44": "native", "51g": "native", "G36": "native"}
TITLE = {"G35": "RPG forks per room", "G36": "one hopper (DeepSeek-V3.2's #best stint)", "G37": "identical kickoffs",
         "G38": "room-specific instructions", "G39": "identical kickoffs after the 04-27 reshuffle",
         "G41": "identical kickoffs, rooms split by their own choice (H47)", "G42": "identical kickoffs",
         "G44": "room-specific instructions", "51g": "#general / #focus hoppers (unit 51g)"}
WHY = {
    "G35": "The rooms forked the RPG and worked on separate code (H07): a work split. Fixed rooms, no hoppers.",
    "G37": "Identical kickoffs; rooms barely separated in H47 (C_B 0.55). Fixed rooms, no hoppers: the identical-task "
           "comparison for the bimodality half.",
    "G39": "Identical kickoffs after the 04-27 reshuffle. Fixed rooms within the period.",
    "G41": "Identical kickoffs, yet H47 found the rooms split topics on day 1 (C_B 0.17): a work split chosen by the "
           "rooms. Fixed rooms, no hoppers.",
    "G42": "Identical kickoffs. Fixed rooms, no hoppers.",
    "G38": "Room-specific kickoffs: the domains are set by an operator field. No hoppers, so the wall should be empty, "
           "and the domain axis should lie along the room-kickoff difference.",
    "G44": "Room-specific kickoffs (and heavy operator traffic in #best). No hoppers.",
    "51g": "The only unit with repeated hopping: #focus opened 08-05 as a side room; two agents live there, two hop "
           "many times, four visit briefly. Private agent goals (NE26) give each agent its own field, so R-field is "
           "a live rival.",
    "G36": "DeepSeek-V3.2 moves #rest → #best on 03-26 (19:48 UTC) and back on 03-30 (17:43, first day of #37): "
           "the only within-period hopper in the two-room era. One agent, about two days inside.",
}
PRED = {
    "replication": ["D ≥ 2 with relabel p < 0.05 (P1); for G35 and G41 (work split) this is the card's P1 core; for "
                    "G37, G39, G42 (identical kickoffs) D is expected lower than the split periods' median.",
                    "Stayers' interior occupancy I ≤ 0.15 in split periods (P1).",
                    "Cross-domain read share P < 0.02 (fixed rooms; H41 cage) (P4).",
                    "Verdict rule: supported if D ≥ 2 with p < 0.05; failed if D < 1 or p > 0.2; mixed otherwise.",
                    "Counts against: D within the relabel null."],
    "G38": ["D ≥ 2 with relabel p < 0.05 and I = 0 (P1, P4).", "P5: cos(u, u_f) above the 95th percentile of the "
            "direction null.", "P < 0.02 (no hopping read-outs).",
            "Counts against: positions not bimodal by room, or an axis unrelated to the instructions."],
    "G44": ["D ≥ 2 with relabel p < 0.05 and I = 0 (P1, P4).", "P5: cos(u, u_f) above the 95th percentile of the "
            "direction null.", "P < 0.02.", "Counts against: positions not bimodal by room."],
    "51g": ["Two domains: the #focus core sits away from #general stayers (D ≥ 2 with relabel p < 0.05, two core "
            "agents; descriptive).",
            "P2: hoppers with ≥ 5 hop-days have s(all) above the #general stayers' 95th percentile and below 1; their "
            "s(home) (statements made in #general) exceeds the stayers' median for ≥ 2/3 of them.",
            "P3: κ_R > 0 (p < 0.05) and κ_R > κ_U (posted-unread placebo); hopper fixed effects.",
            "Counts against (HH332 kill): hoppers' s(all) within the stayers' range."],
    "G36": ["P6: DeepSeek-V3.2's s on its #best-stint statements exceeds its pre-stint s by ≥ 0.3; after the stint "
            "(#37 days, #37 axis) it falls back toward 0.",
            "Counts against: no shift during the stint (s change < 0.1)."],
}


def predict():
    dom = pl.read_parquet(L.DATA / "domains.parquet")
    st = pl.read_parquet(L.DATA / "statements.parquet")
    for u in L.UNITS:
        d = GP / FOLDER[u]
        (d / "figures").mkdir(parents=True, exist_ok=True)
        du = dom.filter(pl.col("unit") == u)
        days = sorted(st.filter(pl.col("unit") == u)["pt_date"].unique().to_list())
        roles = du.group_by("role", "home").len().sort("home", "role")
        rtxt = "; ".join(f"home room {r['home']}: {r['len']} {r['role']}" for r in roles.to_dicts())
        role = ROLE[u]
        preds = PRED["replication"] if role == "replication" else PRED[u]
        txt = (f"# H102 × {FOLDER[u]}: {TITLE[u]} ({days[0]} → {days[-1]})\n\n**Verdict:** pending\n**Role:** {role}\n"
               f"**Period:** regime {'II' if u == 'G35' else 'III'} · {du.height} agents ({rtxt}) · {len(days)} "
               f"non-holdout days{' (unit 51g only; the rest of #51 is single-room)' if u == '51g' else ''}"
               f"{' (36b + 36c)' if u == 'G36' else ''}.\n\n## Why this period\n{WHY[u]}\n\n## Prediction\n"
               f"*Written {STAMP}, before running on this period (card predictions applied"
               f"{'; templated replication prediction' if role == 'replication' else ''}).*\n"
               + "\n".join(f"- {p}" for p in preds)
               + "\n\n## Result\n*(pending)*\n\n## Scorecard (period-specific axes)\n*(pending)*\n\n## Notes\n"
               f"- Data: `data/processed/H102-room-domain-walls/results/results.json` (key `{u}`).\n")
        (d / "README.md").write_text(txt)
    print("predict: wrote", len(L.UNITS), "folders")


def results():
    R = json.loads((L.DATA / "results/results.json").read_text())
    for u in L.UNITS:
        p = GP / FOLDER[u] / "README.md"
        t = p.read_text()
        r = R["units"][u]
        t = re.sub(r"\*\*Verdict:\*\* .*", f"**Verdict:** {r['verdict']}", t, count=1)
        t = re.sub(r"## Result\n.*?\n## Scorecard \(period-specific axes\)\n.*?\n## Notes",
                   "## Result\n" + r["result_md"] + "\n\n## Scorecard (period-specific axes)\n" + r["scorecard_md"]
                   + "\n\n## Notes", t, flags=re.S)
        p.write_text(t)
    print("results: updated", len(L.UNITS), "folders")


if __name__ == "__main__":
    if "--predict" in sys.argv:
        predict()
    if "--results" in sys.argv:
        results()
