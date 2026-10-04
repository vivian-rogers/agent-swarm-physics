"""Write / update the H13 goal-period folders (G<NN>/README.md).

--init     write each folder's header, "Why this period" and dated Prediction (only if the README does not exist yet).
--results  replace the Verdict line, the Result and Scorecard sections from data/processed/H13-family-fields/explore.json
           (the Prediction section is never touched).

Usage: uv run python hypotheses/H13-family-fields/analysis/period_folders.py --init | --results
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parents[1]
ROOT = HERE.parents[1]
DATA = ROOT / "data/processed/H13-family-fields"

PRED_DATE = "2026-10-03 23:50 UTC"

PERIODS = {
    "G35": dict(
        title="Test your game to make it as fun and functional as you can!", dates="2026-03-16 → 03-20",
        units=["35"],
        period="regime II · mode C · 13 agents · two rooms (#best: GPT-5.4, Opus 4.6, Gemini 3.1 Pro; #rest: the other 10) · 5 days.",
        why="First two-room period: lab and room are crossed by design (#best holds one agent per big lab). The rooms evolved separate forks of one RPG (NE15), so a strong room field is expected in content. Regime II basis, so it is outside the invariance check (a3), a4 and d2.",
        pred=[
            "P1: T_field > 0, lab-permutation p < 0.05.",
            "P2: survives style residualization with retention ≥ 0.5.",
            "P5/P7-y1 (talk): room dominates: b_room > b_lab, b_lab n.s. H05 found within-room talk coupling > cross-room here, so b_room should be > 0.",
            "P6: Δ_content not significant.",
            "P7-y2 (content field): b_lab > 0 at p < 0.05 (family persists across rooms), with a large b_room (separate forks).",
            "P7-y3 (content co-movement): b_room > b_lab.",
            "P8: Anthropic 'genuinely' rate ≥ 2× others; T_lex > 0; leave-one-out classification above chance.",
            "Counts against: b_lab (y2) ≤ 0 or n.s.; b_lab (y1) > b_room.",
        ]),
    "G36": dict(
        title="Interact with other AI agents outside the Village!", dates="2026-03-24 → 03-27 (36b; 03-23, regime II, dropped)",
        units=["36b"],
        period="regime III (first days after perma-computer-use, NE14) · mode C · 13 agents · two rooms · 4 days. Split: 03-23 (one regime II day) is dropped because the whitening basis is per regime.",
        why="Two-room shared-objective week right after the regime boundary: family vs room, and the first regime III unit for the invariance check.",
        pred=[
            "P1: T_field > 0 (p < 0.05). P2: retention ≥ 0.5.",
            "P5/P7-y1: talk b_lab n.s., b_room ≥ b_lab. H05 found no talk block structure in #36, so b_room may be weak.",
            "P6: Δ_content n.s.",
            "P7-y2: b_lab > 0 (p < 0.05); b_room small (shared task, no room-specific goal).",
            "P7-y3: b_room > b_lab.",
            "P8: 'genuinely' ratio ≥ 2; T_lex > 0; classification above chance.",
        ]),
    "G37": dict(
        title="Pick your own goal!", dates="2026-03-30 → 04-01",
        units=["37"],
        period="regime III · mode F (free) · 10 eligible agents (Anthropic 5, OpenAI 3, Google 1, DeepSeek 1) · two rooms · 3 days.",
        why="A free week: with no imposed goal, a family's prior should show most clearly. Expected the largest T_field of the regime III units, descriptively. K = 2 multi-member labs (Google has one agent).",
        pred=[
            "P1: T_field > 0 (p < 0.05), expected among the largest of all units.",
            "P2: retention ≥ 0.5.",
            "P5/P7-y1: talk b_lab n.s.",
            "P6: Δ_content n.s.",
            "P7-y2: b_lab > 0; b_room small (no room-specific goal). P7-y3: b_room > b_lab.",
            "P8: 'genuinely' ratio ≥ 2; classification above chance (only 2 classes, so chance = 0.5 among multi-member labs).",
            "Low power: 3 days and 10 agents. A null here counts against P1 only through the count rule.",
        ]),
    "G38": dict(
        title="Choose a charity and raise as much money as you can for it", dates="2026-04-02 → 04-24",
        units=["38a", "38b", "38c"],
        period="regime III · mode C · 12–14 agents (Opus 4.7 joins 04-17, Kimi K2.6 04-22) · two rooms · 17 days. Split at NE17 (04-14, outreach approval) and NE18 (04-20, history search) into 38a (8 days), 38b (4), 38c (5), as in H01.",
        why="The longest two-room shared-objective period. Three sub-units give a within-period replication of the family field and of family vs room.",
        pred=[
            "In each of 38a, 38b and 38c: P1 T_field > 0 (p < 0.05); P2 retention ≥ 0.5.",
            "P5/P7-y1: talk b_lab n.s., b_room > b_lab.",
            "P6: Δ_content n.s.",
            "P7-y2: b_lab > 0 (p < 0.05); b_room modest (one shared goal; room-specific kickoffs).",
            "P7-y3: b_room > b_lab.",
            "P8: 'genuinely' ratio ≥ 2; classification above chance.",
            "The family field direction should be stable across 38a/38b/38c (descriptive; part of a3).",
        ]),
    "G39": dict(
        title="Build your own interactive world!", dates="2026-04-27 → 05-01",
        units=["39"],
        period="regime III · mode I · 15 agents · two rooms, reshuffled 04-27 · 5 days.",
        why="Individual-objective week: each agent builds its own world, so position differences come from priors rather than a shared task. Family vs room with a new room partition.",
        pred=[
            "P1: T_field > 0 (p < 0.05). P2: retention ≥ 0.5.",
            "P5/P7-y1: talk b_lab n.s. H05 found no talk block structure in #39, so b_room may be weak too.",
            "P6: Δ_content n.s.",
            "P7-y2: b_lab > 0 (p < 0.05); b_room small. P7-y3: b_room ≥ b_lab.",
            "P8: 'genuinely' ratio ≥ 2; classification above chance.",
        ]),
    "G40": dict(
        title="Connect your worlds into a 3D universe!", dates="2026-05-04 → 05-08",
        units=["40"],
        period="regime III · mode C · 15 agents · one room (#universe-coordination) except GPT-5, alone in #rest · 5 days.",
        why="The cleanest regime III **one-room** unit before #51: family coupling (b1, b2) without the room confound. GPT-5 is excluded from b1/b2 (it sits alone in another room) but kept in (a) and (d). No (c).",
        pred=[
            "P1: T_field > 0 (p < 0.05). P2: retention ≥ 0.5.",
            "P5: Δ_talk = J_in − J_out n.s. (p ≥ 0.05); enrichment J_in/J_out < 1.3.",
            "P6: Δ_content n.s.",
            "P8: 'genuinely' ratio ≥ 2; T_lex > 0; classification above chance.",
            "Counts against P5/P6: Δ_talk or Δ_content > 0 at p < 0.05.",
        ]),
    "G41": dict(
        title="Perform novel research!", dates="2026-05-11 → 05-15",
        units=["41"],
        period="regime III · mode I · 15 agents · two rooms · 5 days.",
        why="The rooms converged on different research topics (#rest: multi-agent coordination; #best: AI-judge bias). A strong room field in content, crossed with family.",
        pred=[
            "P1: T_field > 0 (p < 0.05). P2: retention ≥ 0.5.",
            "P5/P7-y1: talk b_lab n.s., b_room > b_lab (H05: talk block structure passes here).",
            "P6: Δ_content n.s.",
            "P7-y2: b_lab > 0 (p < 0.05) **despite** a large b_room (room topics).",
            "P7-y3: b_room > b_lab.",
            "P8: 'genuinely' ratio ≥ 2; classification above chance.",
        ]),
    "G42": dict(
        title="Run your own Youtube channel!", dates="2026-05-18 → 05-22",
        units=["42"],
        period="regime III · mode I · 15–16 agents (Gemini 3.5 Flash joins 05-20) · two rooms · 5 days.",
        why="Individual-objective two-room week. Google has 3 agents here, the most of any pre-#51 unit.",
        pred=[
            "P1: T_field > 0 (p < 0.05). P2: retention ≥ 0.5.",
            "P5/P7-y1: talk b_lab n.s.",
            "P6: Δ_content n.s.",
            "P7-y2: b_lab > 0 (p < 0.05). P7-y3: b_room ≥ b_lab.",
            "P8: 'genuinely' ratio ≥ 2; classification above chance.",
        ]),
    "G44": dict(
        title="Finetune your leader!", dates="2026-05-26 → 05-29",
        units=["44"],
        period="regime III · mode D/C · 16–18 agents (Opus 4.8 and the temporary Fine-tuned Leader join) · two rooms with different tasks (#best fine-tunes a Kimi leader; #rest picks creative work) · 4 days. The fine-tuned leader is its own lab label ('Fine-tuned (Kimi)').",
        why="The strongest room-specific task split in the data: a hard test of whether family identity survives a large room field (P7-y2).",
        pred=[
            "P1: T_field > 0 (p < 0.05). P2: retention ≥ 0.5.",
            "P5/P7-y1: talk b_lab n.s., b_room > b_lab.",
            "P6: Δ_content n.s.",
            "P7-y2: b_lab > 0 (p < 0.05) with the largest b_room of all units.",
            "P7-y3: b_room > b_lab.",
            "P8: 'genuinely' ratio ≥ 2; classification above chance.",
        ]),
    "G51": dict(
        title="Each agent: Maximize your assigned goal!", dates="2026-07-06 → 09-04 (non-holdout part; the tail 09-07 → 09-18 is held out)",
        units=["51a", "51b", "51c", "51d", "51e"],
        period="regime III · mode I/K (private assigned roles, NE26) · 21 → 32 agents, 8 h/day · essentially one room (#general). Split as in H01: 51a 07-06 → 07-08; 51b 07-09 → 08-04 (NE32 triplet onboarding; joins); 51c 08-05 → 08-24 (#focus: Gemini 2.5 Pro and Opus 4.8 in a side room, excluded from b in 51c); 51d 08-25 → 09-02; 51e 09-03 → 09-04 (NE33 batch join; 2 days, descriptive only).",
        why="The most families (K = 5: Anthropic, OpenAI, Google, Moonshot, DeepSeek; Zhipu from 08-28) and the most data, in one room: the best test of the K×K family coupling matrix (b) without a room confound, of newcomer classification (d2) and of the NE32 isolated triplet (d3). Assigned roles are agent-specific fields; pairs sharing a role are dropped from the family statistics. One same-role pair is same-family (the YouTubers GPT-5.2 and GPT-5.6 Terra).",
        pred=[
            "In each of 51a–51d: P1 T_field > 0 (p < 0.05); P2 retention ≥ 0.5.",
            "P4: T' > 0 in at least some sub-units.",
            "P5: Δ_talk n.s. (p ≥ 0.05) in ≥ 2/3 of 51a–51d; enrichment < 1.3.",
            "P6: Δ_content n.s. in ≥ 1/2.",
            "P8: 'genuinely' ratio ≥ 2; T_lex > 0; leave-one-out classification above chance.",
            "If P3 passes: newcomers classified into their own family at ≥ 60%.",
            "d3 (descriptive): on 07-09 the triplet aligns more with the OpenAI field than with other families' fields.",
            "Agent-specific role fields add variance, so per-unit power is lower than the N suggests.",
        ]),
}


def init():
    for g, p in PERIODS.items():
        d = HERE / g
        (d / "figures").mkdir(parents=True, exist_ok=True)
        f = d / "README.md"
        if f.exists():
            print("exists, not overwritten:", f)
            continue
        preds = "\n".join(f"- {x}" for x in p["pred"])
        txt = f"""# H13 × {g}: {p['title']} ({p['dates']})

**Verdict:** pending
**Role:** exploratory
**Period:** {p['period']}
**Units analysed:** {', '.join(p['units'])}

## Why this period
{p['why']}

## Prediction
*Written {PRED_DATE}, before running on this period.* The card's P1–P8 (`../README.md`, Prediction) as they apply here:
{preds}

## Result
(pending)

## Scorecard (period-specific axes)
(pending)

## Notes
- Data: `data/processed/H13-family-fields/{g}/`. Per-period figures: `figures/`.
"""
        f.write_text(txt)
        print("wrote", f)


if __name__ == "__main__":
    if "--init" in sys.argv:
        init()
    elif "--results" in sys.argv:
        from period_results import write_results  # noqa: E402
        write_results(PERIODS, HERE, DATA)
