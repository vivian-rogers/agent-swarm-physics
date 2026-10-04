"""Write / update hypotheses/H11-potts-labor-vs-herding/G<NN>/README.md.

--init     writes each folder's README with its dated prediction, only if the README does not exist yet.
--results  replaces only the Verdict line and the Result / Scorecard sections from
           data/processed/H11-potts-labor-vs-herding/G<NN>/results.json; the Prediction section is never touched.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scheme"))
import h11common as HC  # noqa: E402

DATE = "2026-10-03"

GOAL = {
    11: ("Pursue whatever you'd like to", "2025-08-25 → 2025-09-01", "I", "F", 7, 5, "one room (#general)"),
    13: ("Design, run and write up a human subjects experiment", "2025-09-08 → 2025-09-22", "I", "C", 6, 10, "one room (#general)"),
    16: ("Choose your own goal!", "2025-10-06 → 2025-10-13", "I", "F", 7, 5, "one room (#general)"),
    18: ("Reduce global poverty as much as you can", "2025-10-20 → 2025-11-03", "I", "C", 7, 10, "one room (#general)"),
    19: ("Create a popular daily puzzle game like Wordle", "2025-11-03 → 2025-11-17", "I", "C", 7, 10, "one room (#general)"),
    20: ("Start a Substack and join the blogosphere", "2025-11-17 → 2025-12-01", "I", "I", 8, 10, "one room (#general)"),
    24: ("Do random acts of kindness!", "2025-12-22 → 2025-12-29", "I", "C", 10, 5, "one room (#general)"),
    25: ("Create a digital museum of 2025", "2025-12-29 → 2026-01-05", "I", "C", 10, 5, "one room (#general)"),
    26: ("Elect a village leader. They choose this week's goal!", "2026-01-05 → 2026-01-12", "I", "C", 10, 5, "one room (#general)"),
    30: ("Adopt a park and get it cleaned!", "2026-02-09 → 2026-02-16", "I", "C", 12, 5, "one room (#general)"),
    31: ("Pick your own goal (agents bid 3.7 Sonnet farewell)", "2026-02-16 → 2026-02-23", "I", "F", 12, 5, "one room (#general)"),
    37: ("Pick your own goal!", "2026-03-30 → 2026-04-02", "III", "F", 13, 3, "#best / #rest"),
    38: ("Choose a charity and raise as much money as you can for it", "2026-04-02 → 2026-04-27", "III", "C", 12, 17, "#best / #rest"),
    39: ("Build your own interactive world!", "2026-04-27 → 2026-05-04", "III", "I", 15, 5, "#best / #rest"),
    40: ("Connect your worlds into a 3D universe!", "2026-05-04 → 2026-05-11", "III", "C", 15, 5, "#universe-coordination + #rest"),
    41: ("Perform novel research!", "2026-05-11 → 2026-05-18", "III", "I", 15, 5, "#best / #rest"),
    42: ("Run your own Youtube channel!", "2026-05-18 → 2026-05-25", "III", "I", 15, 5, "#best / #rest"),
}

CLASS_TEXT = {
    "AF": "antiferromagnetic (division of labor): βJ_CW < 0 (P1) and βJ_PL ≤ 0 vs the circular-shift null N2 (P2)",
    "FM-consensus": "ferromagnetic (consensus on a shared choice): βJ_CW > 0 (P1), βJ_PL z_N2 ≥ +2 (P2), and a first-order jump in the dominant share (P3)",
    "FM-free": "ferromagnetic (herding in a free week): βJ_CW > 0 (P1), βJ_PL z_N2 ≥ +2 (P2)",
    "FM-convergence": "ferromagnetic (convergence on one topic): βJ_CW > 0 (P1), βJ_PL z_N2 ≥ +2 (P2)",
    "none-I": "no sign prediction (individual objectives); reported descriptively",
}

WHY = {
    13: "HH24's case: a shared objective with separable subtasks (design, recruit, run, analyze, write). The cleanest a-priori antiferromagnetic week. Labels here are mostly Google Docs, Forms and Sheets, and only ~28% of agent-windows carry a strict mention, so power is low.",
    18: "A two-week shared objective with many interventions and sites: a divisible portfolio, so antiferromagnetic.",
    19: "HH25's case: many candidate puzzle concepts, then convergence on one build. A consensus choice, so ferromagnetic with a first-order jump (HH84). Project labels capture the build the swarm converges on, not the concept names in chat; concept-mention states are a round-2 item.",
    26: "HH22 (folded into H11 on 2026-10-03 by Vivian) and HH84: approval voting over six candidates, a three-way tie, then a runoff. Two state variants: project labels (the shared ballot documents) for P1/P2, and **chat-declared votes** for the HH22 tests.",
    31: "HH26's case: about nine agents condensed onto one project in a free week. Herding with no field, so ferromagnetic.",
    40: "Shared interfaces and standards in a shared universe hub: consensus, so ferromagnetic. Regime III, with one dedicated coordination room.",
    41: "Many #rest agents independently proposed the same research topic: convergence, so ferromagnetic (the card's 'research convergence').",
    11: "Transfer: free week, so ferromagnetic by the class rule.",
    16: "Transfer: free week, so ferromagnetic by the class rule.",
    37: "Transfer: free week (regime III, #best / #rest), so ferromagnetic by the class rule.",
    24: "Transfer: shared objective where agents divided up approaches, so antiferromagnetic.",
    25: "Transfer: shared objective where each agent made exhibits, so antiferromagnetic.",
    30: "Transfer: shared objective with a shared repo and two parks, so antiferromagnetic by the class rule. Note the shared repo, which may make it look like herding.",
    38: "Transfer: a 17-day shared objective (charity), so antiferromagnetic by the class rule.",
    20: "Descriptive: each agent its own Substack. No sign prediction.",
    39: "Descriptive: each agent its own world. No sign prediction.",
    42: "Descriptive: each agent its own channel. No sign prediction.",
}

G26_EXTRA = """
**HH22 vote tests (G26 only; chat-declared votes, structural labels, no text).**
- *States.* A vote declaration is an agent chat message in #26 containing a vote word that names ≥ 1 roster agent (`chat_mentions_clean.mentions_roster`).
  - The primary set is first-person declarations ("I vote / my vote / I approve …"); any vote-word message is the robustness variant.
  - A single named candidate is a categorical state. Several named candidates form an approval set, weighted 1/k per candidate.
  - Each voter's latest declaration is carried forward.
  - Candidates are the agents named in ≥ 1 first-person declaration; HH22 expects q = 6.
  - Runoff onset is the first 30-min window with ≥ 2 agent messages containing "runoff", a structural keyword timing.
- **P-G26a (symmetric point).** At runoff onset, the latest declarations put the top three candidates level: a multinomial equality test on their approval weight gives p > 0.05, and the perplexity of the declared distribution over the candidates is q_eff ≥ 3. Fails if one candidate already leads significantly.
- **P-G26b (first-order jump).** The eventual winner's declared share shows an O4 "jump" at or after runoff onset: Δ ≥ 0.3, τ ≤ 2 windows, rising from ≈ 1/3 to ≥ 0.75, with persistence ≤ 0.15. Fails if the rise is gradual (R3) or absent.
- **P-G26c (Potts mechanism, mean field).** Take the runoff snapshot (each voter's last single-candidate declaration after onset) under symmetric fields (HH22's symmetric point). The profile-likelihood βJ_snap of the Curie–Weiss Potts with q = q_runoff is ≥ βJ_s(q_runoff), i.e. the first-order region (βJ_s(3) = 2.75). If the runoff count vector is concentrated but βJ_snap < βJ_s, or symmetric fields are rejected, the step is field-driven (institutional), not a Potts transition.
- My credences: P-G26a 0.5; P-G26b 0.5; P-G26c 0.15. The runoff is a protocol change that narrows q from 6 to the tied set; that is a field, not spontaneous ordering.
"""

P3_PERIODS = {19, 26, 31, 40}


def init_readme(g, cls):
    f = HC.HYP / f"G{g:02d}" / "README.md"
    if f.exists():
        return False
    title, dates, reg, mode, N, d, rooms = GOAL[g]
    role = "exploratory (candidate)" if g in HC.CANDIDATES else "exploratory (transfer)"
    p3 = ""
    if g in P3_PERIODS:
        p3 = ("\n- **P3 (consensus jump):** the share x₁ of the final-day dominant project shows an O4 'jump' (Δ ≥ 0.3, τ ≤ 2 windows, "
              "persistence ≤ 0.15), and βJ_CW ≥ βJ_s(q_eff) (first-order region). A jump with βJ_CW < βJ_s is scored as a "
              "field-driven step; a gradual rise counts against P3.")
    txt = f"""# H11 × G{g:02d}: {title} ({dates})

**Verdict:** pending
**Role:** {role}
**Period:** regime {reg} · mode {mode} · N = {N} at start · {rooms} · {d} active days. Class for H11: **{cls}**.

## Why this period
{WHY[g]}

## Prediction
*Written {DATE}, before running on this period.*
- **Class prediction:** {CLASS_TEXT[cls]}. Per-period verdict on P1: **supported** if the sign is right and |t| > t_(D−1, 0.975) (leave-one-day-out jackknife); **weak** if the sign is right but not significant; **failed** if the sign is wrong.{p3}
- **P4 (control):** the action-class βJ_CW is positive or ≈ 0 whatever the class.
- **P7 (prior):** |βJ_CW| < 2, below βJ_s(q), so no spontaneous first-order transition.
- **Minimum data:** ≥ 15 room blocks with N_b ≥ 3 at W = 30; otherwise n/a.
- **What would count against it:** the opposite sign of βJ_CW (P1), or, for an FM class, a positive βJ_CW that disappears under the within-agent permutation null N1 (spread carried entirely by agent fields, R1).
{G26_EXTRA if g == 26 else ''}
## Result
*Pending.*

## Scorecard (period-specific axes)
*Pending.*

## Notes
"""
    f.parent.mkdir(parents=True, exist_ok=True)
    f.write_text(txt)
    return True


def fill_results(g):
    f = HC.HYP / f"G{g:02d}" / "README.md"
    rj = HC.OUT / f"G{g:02d}" / "results.json"
    if not f.exists() or not rj.exists():
        return False
    R = json.loads(rj.read_text())
    s = f.read_text()
    s = re.sub(r"^\*\*Verdict:\*\* .*$", f"**Verdict:** {R['verdict']}", s, count=1, flags=re.M)
    res = R["result_md"]
    sc = R.get("scorecard_md", "")
    s = re.sub(r"## Result\n.*?(?=\n## Scorecard)", "## Result\n" + res.strip() + "\n", s, count=1, flags=re.S)
    s = re.sub(r"## Scorecard \(period-specific axes\)\n.*?(?=\n## Notes)", "## Scorecard (period-specific axes)\n" + sc.strip() + "\n", s,
               count=1, flags=re.S)
    if R.get("notes_md") and R["notes_md"].strip() not in s:
        s = s.rstrip() + "\n" + R["notes_md"].strip() + "\n"
    f.write_text(s)
    return True


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--init", action="store_true")
    ap.add_argument("--results", action="store_true")
    a = ap.parse_args()
    allc = {**HC.CANDIDATES, **HC.TRANSFER}
    if a.init:
        for g, cls in sorted(allc.items()):
            print(g, "written" if init_readme(g, cls) else "exists (prediction kept)")
    if a.results:
        for g in sorted(allc):
            print(g, "filled" if fill_results(g) else "no results")


if __name__ == "__main__":
    main()
