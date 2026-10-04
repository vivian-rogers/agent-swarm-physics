"""Write H100 period folders.

    --predict   before any outcome: structure (agents per room, days, regime) + the dated prediction per period
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
import h100lib as L  # noqa: E402

GP = H / "goalperiod-subhypotheses"
STAMP = "2026-10-04 ~20:30 UTC"
TITLES = {35: "RPG forks per room", 36: "#36", 37: "#37", 38: "room-specific instructions", 39: "#39 after the 04-27 reshuffle",
          41: "#41 after the NE42 split", 42: "#42", 44: "room-specific instructions"}
ROLE = {35: "replication", 36: "replication", 37: "replication", 42: "replication",
        38: "native", 39: "native", 41: "native", 44: "native"}

WHY = {
    35: "First week of the #best/#rest split (NE15). Each room forked the RPG, so the rooms work on different code "
        "from day 1: a room-specific *artifact* field set by the operator's split. Regime II basis, so composition "
        "is not estimated (agent constants use the regime-III basis).",
    36: "Identical room kickoffs (H47). The regime-III days (36b, 36c) only; DeepSeek-V3.2 visits #best on 03-26/27 "
        "and is dropped from O1 here (it is H102's hopper).",
    37: "Identical room kickoffs; three days. The 04-02 move happens at its end (pre side of the G38 mover test).",
    42: "Identical room kickoffs; Gemini 3.5 Flash joins #best on 05-20. Pre side of the 05-25 mover test.",
    38: "Room-specific kickoffs (cosine 0.86 between the two room kickoff vectors, H47): the only long period with an "
        "explicit room field. Sonnet 4.6 moves #rest → #best at its start (04-02).",
    39: "The 04-27 reshuffle: Opus 4.6, Sonnet 4.6 and GPT-5.4 move #best → #rest at the goal start; GPT-5.5 joins "
        "#best. Identical room kickoffs. The cleanest swap in the non-holdout data.",
    41: "Identical room kickoffs, rooms split back to #39's partition after the NE42 merge (#40). H47 found the rooms "
        "separated from day 0. Zero explicit field: the clean test of spontaneous divergence, and of remanence "
        "across the merge.",
    44: "Room-specific kickoffs (cosine 0.81) and heavy operator traffic in #best (57 human messages vs 2 in #rest). "
        "Gemini 3.1 Pro moves #best → #rest at its start (05-25).",
}

PRED = {
    "replication": [
        "Q > 1 with relabel p < 0.05 (P1).",
        "f_comp ≤ 0.3 (P2; not estimated for #35).",
        "Identical-kickoff periods (#36, #37, #42): Q_spont > 1 with p < 0.05 and f_spont ≥ 0.5 (P4); f_field along "
        "the operator-message direction ≤ 0.1 (P3).",
        "#35: f_field along the operator-message direction ≤ 0.1; the fork artifact field is not measured, so the "
        "divergence counts as spontaneous/endogenous by the card's rule.",
        "Verdict rule: supported if Q_res > 1 (p < 0.05) and f_comp < 0.5; failed if Q ≤ 1 (p > 0.2) or f_comp ≥ 0.7.",
        "Counts against: Q within the relabel null, or a room difference that is all composition.",
    ],
    38: ["Q > 1 (p < 0.05); f_comp ≤ 0.3.",
         "P3: f_field along the room-kickoff direction ≥ 0.15 and above the direction null (p < 0.05).",
         "Q_spont > 1 (p < 0.05): a divergence beyond the field.",
         "P5 (04-02 mover, Sonnet 4.6, #rest → #best): φ_post ≥ 0.5 and φ_post − φ_comp ≥ 0.5; φ_pre ≤ 0; day-1 φ ≥ 0.5.",
         "Counts against: f_field at chance (≈ 0.03) or the mover staying with #rest (φ_post < 0)."],
    39: ["Q > 1 (p < 0.05); f_comp ≤ 0.3; Q_spont > 1 (p < 0.05) (identical kickoffs).",
         "P5 (04-27 movers Opus 4.6, Sonnet 4.6, GPT-5.4, #best → #rest): φ_post ≥ 0.5 and φ_post − φ_comp ≥ 0.5 for "
         "≥ 2 of 3; φ_pre ≤ 0; day-1 φ ≥ 0.5.",
         "P7 swap-carry: R_room and R_agent both within the relabel null; if either is significant, R_room > R_agent.",
         "Counts against: movers keep #best's position (φ_post < 0: agent-carried state), or φ_post ≈ φ_comp "
         "(composition)."],
    41: ["Q_spont > 1 with p < 0.01 (P4, zero explicit field); f_spont ≥ 0.5.",
         "P6: remanence R(#39, #41) within the relabel null (|z| < 2): the divergence regenerates after the merge.",
         "Counts against: Q_spont within the null (the separation is composition) or R(#39, #41) > 0 with z ≥ 2 "
         "(room memory through the merge)."],
    44: ["Q > 1 (p < 0.05); f_comp ≤ 0.3.",
         "P3: f_field along the room-kickoff direction ≥ 0.15 and above the direction null (p < 0.05).",
         "P5 (05-25 mover, Gemini 3.1 Pro, #best → #rest): φ_post ≥ 0.5 and φ_post − φ_comp ≥ 0.5; φ_pre ≤ 0.",
         "Counts against: f_field at chance, or the mover staying with #best."],
}


def structure(tab, P):
    m = L.period_rows(tab, P)
    sub = tab.filter(pl.Series(m))
    nb = sub.filter(pl.col("room") == L.BEST)["agent"].n_unique()
    nr = sub.filter(pl.col("room") == L.REST)["agent"].n_unique()
    days = sorted(sub["pt_date"].unique().to_list())
    reg = "II" if P == 35 else "III"
    return nb, nr, days, reg


def predict():
    tab = pl.read_parquet(L.DATA / "agent_days.parquet")
    for P in L.MULTI:
        nb, nr, days, reg = structure(tab, P)
        d = GP / f"G{P}"
        (d / "figures").mkdir(parents=True, exist_ok=True)
        role = ROLE[P]
        preds = PRED["replication"] if role == "replication" else PRED[P]
        txt = (f"# H100 × G{P}: {TITLES[P]} ({days[0]} → {days[-1]})\n\n**Verdict:** pending\n**Role:** {role}\n"
               f"**Period:** regime {reg} · #best {nb} agents, #rest {nr} agents (agent-days by room of the day) · "
               f"{len(days)} non-holdout days{' (36b + 36c; 36a is regime II)' if P == 36 else ''}.\n\n"
               f"## Why this period\n{WHY[P]}\n\n## Prediction\n*Written {STAMP}, before running on this period "
               f"(card predictions applied{'; templated replication prediction' if role == 'replication' else ''}).*\n"
               + "\n".join(f"- {p}" for p in preds)
               + "\n\n## Result\n*(pending)*\n\n## Scorecard (period-specific axes)\n*(pending)*\n\n## Notes\n"
               f"- Data: `data/processed/H100-room-symmetry-breaking/results/results.json` (key `G{P}`).\n")
        (d / "README.md").write_text(txt)
    print("predict: wrote", len(L.MULTI), "folders")


def results():
    R = json.loads((L.DATA / "results/results.json").read_text())
    for P in L.MULTI:
        d = GP / f"G{P}" / "README.md"
        t = d.read_text()
        r = R["periods"][f"G{P}"]
        t = re.sub(r"\*\*Verdict:\*\* .*", f"**Verdict:** {r['verdict']}", t, count=1)
        t = re.sub(r"## Result\n.*?\n## Scorecard \(period-specific axes\)\n.*?\n## Notes",
                   "## Result\n" + r["result_md"] + "\n\n## Scorecard (period-specific axes)\n" + r["scorecard_md"]
                   + "\n\n## Notes", t, flags=re.S)
        d.write_text(t)
    print("results: updated", len(L.MULTI), "folders")


if __name__ == "__main__":
    if "--predict" in sys.argv:
        predict()
    if "--results" in sys.argv:
        results()
