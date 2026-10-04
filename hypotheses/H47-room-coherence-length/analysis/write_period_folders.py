"""Write the H47 period / NE folders with their dated predictions (verdict pending), before the real-data run.

Replication folders get the card's templated prediction (labelled as such); native folders get their own design.
Results are filled later by write_period_results.py (it replaces the "## Result" section and the verdict line).

Usage: uv run python hypotheses/H47-room-coherence-length/analysis/write_period_folders.py
"""
from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import h47lib as L  # noqa: E402

import polars as pl  # noqa: E402

GP = L.HYP / "goalperiod-subhypotheses"
WHEN = "2026-10-04 ~06:10 UTC"

TITLE = {35: "Test your game to make it as fun and functional as you can!", 36: "Interact with other AI agents outside the Village!",
         37: "Pick your own goal!", 38: "Choose a charity and raise as much money as you can for it",
         39: "Build your own interactive world!", 40: "Connect your worlds into a 3D universe!", 41: "Perform novel research!",
         42: "Run your own Youtube channel!", 44: "Finetune your leader!", 51: "Each agent: Maximize your assigned goal!"}
MODE = {35: "C", 36: "C", 37: "F", 38: "C", 39: "I", 40: "C", 41: "I", 42: "I", 44: "C", 51: "I/K"}

REPL_PRED = f"""*Written {WHEN}, before running H47 on this period. Templated replication prediction (card P1, P2), not tailored.*
- **P1 (coherence length = room):** at w30, pooled over the period's units, C_B = ρ_c/ρ_w ≤ 0.3 and the room-relabel permutation p for Δ_B = ρ_w − ρ_c is < 0.05.
- **P2 (flat inside the room):** G = ρ_w,low/ρ_w,high ≥ 0.6, and (1 − C_B) > (1 − G).
- **Leadership (card P4), if this period starts with a multi-room goal change:** |L| not significant (cohort-relabel p ≥ 0.05).
- **Verdict rule (card):** supported if C_B ≤ 0.3 and p < 0.05; failed if C_B ≥ 0.6 or p > 0.2; mixed otherwise.
- Against: C_B ≥ 0.6 (content co-moves across rooms as much as within) or no difference from random room labels."""

NATIVE = {
    "G41": dict(role="native", why="""Both rooms got the **same instruction** (perform novel research); #rest converged on multi-agent coordination and #best on AI-judge bias by themselves (goal-periods.md). A room-specific instruction drive is absent by design, so a sharp room boundary here must come from the channel (coupling, or drives the rooms generate themselves), not from the operator. It is also the A in NE42's A-B-A (it follows the merged #40).""",
                pred=f"""*Written {WHEN}, before running H47 on this period.*
- **P5a (primary):** C_B(41) ≤ 0.3 with room-relabel p < 0.01 (w30).
- **P5b:** the boundary is as sharp as in the instruction-driven G38/G44: |C_B(41) − median(C_B(38), C_B(44))| ≤ 0.15.
- **P5c (symmetry breaking):** the between-room centroid separation (F statistic vs a within-day room-relabel null) rises over the week (Spearman over days > 0), starting low on day 0 after the merged week.
- Replication items (P1, P2) also reported; leadership at the #41 kickoff (cohorts = new rooms): |L| not significant.
- **Against:** C_B(41) ≥ 0.6 (no boundary without instructions), or a boundary much weaker than in G38/G44 (then the room boundary is mostly the operator's drive)."""),
    "G38": dict(role="native", why="""The rooms got **different instructions** for the charity goal (the drive-confounded contrast to G41). Five units (NE17 outreach approval, two joins, NE18). If room coherence is an instruction drive, the room-specific kickoff directions should carry the within-room co-fluctuation, and the boundary should be sharper than in G41.""",
                pred=f"""*Written {WHEN}, before running H47 on this period.*
- **P6a (primary):** instruction-direction share ≤ 0.15: projecting out the unit's goal, kickoff and per-room kickoff directions (L0 → L1) lowers Δ_B by at most 15% (pooled w30).
- **P6b:** day-0 between-room separation larger than G41's day 0.
- Replication items (P1, P2) also reported; leadership at the #38 kickoff: |L| not significant.
- **Against:** a large instruction share (> 0.3): the boundary is carried by the operator's room-specific instructions."""),
    "G44": dict(role="native", why="""Room-specific instructions again: #best fine-tunes a leader, #rest picks its own goals (goal-periods.md). Two units (44a, 44b: the Opus 4.8 and fine-tuned-leader joins). The day before the kickoff (05-25, #43) is held out, so the leadership pre-baseline uses 05-22.""",
                pred=f"""*Written {WHEN}, before running H47 on this period.*
- **P6a (primary):** instruction-direction share ≤ 0.15 (pooled w30).
- **P6b:** day-0 between-room separation larger than G41's day 0.
- Replication items (P1, P2) also reported; leadership at the #44 kickoff (pre-baseline 05-22): |L| not significant.
- **Against:** a large instruction share (> 0.3)."""),
    "NE42": dict(role="native", why="""**A-B-A:** #best/#rest in #39 (A), merged into #universe-coordination for #40 (B; GPT-5 left alone in #rest, Gemini 2.5 Pro joined late on 05-04), split back to the same partition for #41 (A, identical instructions). Goal-confounded (each phase is a new goal; #40's goal is a shared objective). If coherence follows the channel, content correlation between agents of different A-rooms should rise to within-room levels in #40 and fall back in #41. A persistent team identity (a drive following the old partition) predicts the boundary survives the merge. Also two room events for the detector test (05-04 merge, 05-11 split).""",
                 pred=f"""*Written {WHEN}, before running H47 on these periods.*
- **P7a (primary):** with pairs labelled by the A partition, r_X = ρ_XP/ρ_WP ≤ 0.3 in #39 and #41 and ≥ 0.7 in #40 (w30, L1).
- **P7b:** DiD = r_X(40) − mean(r_X(39), r_X(41)) > 0.4 with partition-permutation p < 0.05.
- **P7c:** residual partition memory in #40: r_X(40) < 0.9.
- **Detector (card P3, Amendment 1):** R1_swarm and the per-room R1 (R1_room) fire within ±1 day of the merge (05-04) and the split (05-11) [goal-confounded].
- **Synthetic reading rule (card Amendment 1, from the run before real data):** under room coupling with a weak global drive, r_X in the A phases is 0.39–0.52, not ≤ 0.3, so P7a's A-phase threshold is strict; the DiD is the informative part (channel worlds: DiD 0.47, > 0.4 in 75%; team-identity worlds: DiD −0.06).
- **Against:** r_X(40) ≈ r_X(39) ≈ r_X(41) (the boundary is a team identity, not the channel)."""),
    "G51": dict(role="native", why="""The private-role era: one room (#general, 21–32 agents) except the **#focus weeks** (51g, 08-05 → 08-21), when an agent-made side room held about two core members plus short visitors (DQ6: everyone is assigned to #general; #focus is a presence deviation). Two leverages: (1) an A-B-A on a self-made room (51f → 51g → 51h); (2) one big room with many agents, where coherence could be limited by who talks to whom (conversational distance) instead of the room. Also two room events for the detector (#focus opens 08-05; #focus empties by 08-24). The #51 tail (from 09-07) is held out.""",
                pred=f"""*Written {WHEN}, before running H47 on this period.*
- **P8a (primary):** r_F = ρ_FG/ρ_GG (focus members vs general members, over general–general pairs) drops in 51g: r_F(51g) < min(r_F(51f), r_F(51h)) − 0.2 (focus-label permutation for the DiD).
- **P8b:** in the single-room units, correlation is flat across conversational tiers: median G ≥ 0.6.
- **51g as a two-room unit (replication rule):** reported, but #focus has 1–3 members per window, so C_B is near unpowered.
- **Detector (card P3, Amendment 1):** at the #focus opening (08-05), R1_swarm z < 3; R1_loc ≥ 2 within ±1 day [low credence: about two core members; synthetic #focus-like AUC 0.63]; R1_room (persistent rooms only) misses it, since #focus has no history.
- **Against:** r_F unchanged in 51g (a two-agent side room doesn't cut coherence) or G ≪ 1 (coherence in a big room is conversation-limited)."""),
}
REPL_WHY = {
    "G35": "First week after the NE15 split (the split itself is confirmatory-only: its pre-side #34 is held out). Regime II. #best 4 agents, #rest 10. Same game task in both rooms but separate forks of the RPG (NE15), so room-specific artifact drives exist.",
    "G36": "Two rooms, three units (36a regime II; NE14 regime boundary on 03-24; NE16 on 03-26). Outreach goal. Kickoff 03-23 is a multi-room goal change for the leadership test.",
    "G37": "Two rooms, three days, free goal (mode F). H26 found content co-moving across rooms here (its smallest room excess), so it is the likeliest replication failure.",
    "G39": "Two rooms; #best only 4 agents. The A of NE42's A-B-A (also scored there). H05 found no talk block structure in #39.",
    "G42": "Two rooms, two units (a join on 05-20). H26 found mostly global content co-fluctuation here.",
}


def period_line(units: pl.DataFrame, g: int) -> str:
    u = units.filter(pl.col("goal_no") == g).sort("seq")
    if u.height == 0:
        return ""
    days = sum(u["n_days"].to_list())
    ag = max(u["n_agents"].to_list())
    regs = "/".join(sorted(set(u["regime"].to_list())))
    rooms = sorted({r for rr in u["rooms"].to_list() for r in rr})
    splits = "; ".join(f"{a} ({b})" for a, b in zip(u["unit_id"].to_list(), u["reason"].to_list()))
    return (f"**Period:** regime {regs} · mode {MODE.get(g, '?')} · up to {ag} agents · rooms {rooms} · {days} active days (non-holdout). "
            f"Units (shared `period_units`): {splits}.")


def write(folder: str, title: str, role: str, period: str, why: str, pred: str):
    d = GP / folder
    (d / "figures").mkdir(parents=True, exist_ok=True)
    txt = f"""# H47 × {folder}: {title}

**Verdict:** pending
**Role:** {role}
{period}

## Why this period
{why}

## Prediction
{pred}

## Result
(pending)

## Scorecard (period-specific axes)
(pending)

## Notes
- {WHEN}: folder and prediction written before the real-data run.
"""
    (d / "README.md").write_text(txt)


def main():
    units = pl.read_parquet(L.OUT / "units.parquet")
    for f, why in REPL_WHY.items():
        g = int(f[1:])
        write(f, f"{TITLE[g]}", "replication", period_line(units, g), why, REPL_PRED)
    for f, spec in NATIVE.items():
        if f == "NE42":
            per = ("**Period:** #39 (2026-04-27 → 05-01, two rooms) → #40 (05-04 → 05-08, one merged room) → #41 (05-11 → 05-15, "
                   "two rooms, same partition). Regime III, 15 agents. Not held out.")
            write(f, "#best/#rest merge and split, A-B-A (2026-05-04 / 05-11)", spec["role"], per, spec["why"], spec["pred"])
        else:
            g = int(f[1:])
            write(f, TITLE[g], spec["role"], period_line(units, g), spec["why"], spec["pred"])
    print("written", sorted(list(REPL_WHY) + list(NATIVE)))


if __name__ == "__main__":
    main()
