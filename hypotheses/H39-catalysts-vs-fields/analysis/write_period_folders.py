"""Write H39 goal-period (G<NN>) and spanning (NE<NN>) READMEs.

  --stage predictions   create each README with its dated prediction (before the real-data run); verdict pending
  --stage results       fill verdicts and results from data/processed/H39-catalysts-vs-fields/, keeping the
                        Prediction section exactly as written

Usage: uv run python hypotheses/H39-catalysts-vs-fields/analysis/write_period_folders.py --stage predictions
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import h39lib as L  # noqa: E402

GP = L.HDIR / "goalperiod-subhypotheses"
PRED_DATE = "2026-10-04 (UTC)"
POINT_PERIODS = [3, 4, 5, 6, 8, 10, 11, 12, 13, 16, 17, 18, 19, 20, 21, 23, 24, 25, 26, 27, 30, 31, 33, 35,
                 37, 38, 39, 40, 41, 42, 44, 51]
REGIME3 = {37, 38, 39, 40, 41, 42, 44, 51}
UNNUMBERED = {8: ("S20250801", "2025-08-01", "prompt: encouraged the agent to keep going (activity instruction)"),
              18: ("S20251022", "2025-10-22", "prompt: keep working right up until the end of each day (activity instruction)"),
              44: ("S20260528", "2026-05-28", "prompt: keep messages short (text-only models); first-person # bash comments (style)")}
NE_FOLDERS = {
    "NE34": ("Goal kickoffs (every non-holdout consecutive pair in one regime)", "kickoff"),
    "NE42": ("#best and #rest merged (05-04) and split back (05-11)", "room"),
    "NE15": ("#best / #rest split (03-16)", "room"),
    "NE41": ("Forced context erasure at the 41-turn consolidation cap (regime III)", "erasure"),
    "NE10": ("Auto-nudger switched on (first nudges 2026-02-13, #30)", "scaffold"),
    "NE07": ("Prompt: 'don't do nothing' (2025-12-04, #21)", "scaffold"),
    "NE16": ("Fix of empty responses that left agents stuck; memory-instruction fix (2026-03-26, #36)", "scaffold"),
    "NE17": ("Outreach approval system (2026-04-14, #38)", "scaffold"),
    "NE18": ("History search: verbatim segments, 10-day window (2026-04-20, #38)", "scaffold"),
    "NE03": ("Chat messages fetched into context limited (2025-08-20, #10)", "scaffold"),
    "NE06": ("Internal-review prompt changes; Gemini one tool call per turn (2025-11-20, #20)", "scaffold"),
}


def goal_info():
    txt = (L.ROOT / "hypotheses/hypohypotheses/goal-periods.md").read_text()
    titles = {int(m.group(1)): m.group(2).strip() for m in re.finditer(r"^### (\d+) · (.+)$", txt, re.M)}
    rows = {}
    for m in re.finditer(r"^\| (\d+) \| (\S+) → (\S+) \| [^|]+\| (\S+) \| [^|]+\| (\S+) \| [^|]+\| (\S+) \|", txt, re.M):
        rows[int(m.group(1))] = dict(start=m.group(2), end=m.group(3), N=m.group(4), reg=m.group(5), mode=m.group(6))
    return titles, rows


def period_prediction(g: int) -> str:
    lines = [f"*Written {PRED_DATE}, before running on this period.* The card's predictions (P1–P4, P7) as they apply here; "
             "a class is scored only if powered (≥ 20 episodes), otherwise reported as descriptive.",
             "- **Per-unit class rule** (with Amendment A1, made after the synthetic validation and before any real data): field = placebo p_F < 0.05 and φ_exc ≥ 0.10; catalyst = K bootstrap CI excluding 0 and |K| ≥ 0.10."]
    if g >= 31:
        lines.append("- **Nudges (N_tgt), P1:** both: Δπ_idle < 0 and idle escape up (ln e^K_idle/e^C_idle > 0); K > 0. "
                     "Against: π unchanged with K > 0 (pure catalyst, HH52) or K ≈ 0 (pure field).")
    else:
        lines.append("- **Nudges:** none (the nudger starts 2026-02-13)" + (" ; G30 has nudges only on its last day, expected underpowered." if g == 30 else "."))
    lines.append("- **Human messages (H_any; H_men, H_und reported), P2:** both, with the field toward chat (Δπ_chat > 0); "
                 "H_men ≥ H_und in |Δπ_chat|. Content: drift toward the message > 0. Low power expected outside G04–G06 and G51.")
    lines.append("- **@-mentions (A_men), P3:** field toward chat (Δπ_chat > 0), |K| < 0.2; content drift toward the message > 0.")
    if g in REGIME3:
        lines.append("- **Context erasure (NE41: CF forced, CV voluntary), P4:** on B6 Δπ_browse > 0 and Δπ_type+shell < 0; "
                     "|K| < 0.10 on B4; CF and CV the same class.")
    if g in UNNUMBERED:
        sid, date, label = UNNUMBERED[g]
        exp = "field (Δπ_idle < 0) if anything, most likely inside the placebo band" if "activity" in label else "neither on behavior; a content (C6) field if anything"
        lines.append(f"- **Scaffold step {sid} ({date}; {label}), P7:** {exp}. Judged against within-goal day-boundary placebos of the same era.")
    lines.append("- **Period verdict:** supported if every powered class matches its predicted class and direction; failed if none does; "
                 "mixed otherwise; descriptive if no class is powered.")
    return "\n".join(lines)


def ne_prediction(ne: str) -> str:
    hd = f"*Written {PRED_DATE}, before running this test.*"
    if ne == "NE34":
        return hd + """ P5 (card):
- Content (C6): φ above the placebo p95 in ≥ 70% of usable kickoffs; content K above the placebo median in ≥ 60% (faster topic churn after a kickoff, H20).
- Behavior (B4): φ above the placebo p95 in ≤ 30% of kickoffs; K inside the placebo [p2.5, p97.5] in ≥ 70% (H04: kickoffs change what, not how much).
- Class: content field (or both); behavior neither. Unit = the transition (named exception c). Placebo = within-goal day boundaries of the same era (regime × hours) and window shape (2 + 2 days unless fewer exist), balanced agent panel.
- Against: behavior φ above p95 in > 30% of kickoffs (kickoffs are behavior fields), or content φ above p95 in < 70% (goals do not tilt content more than an ordinary day change)."""
    if ne == "NE42":
        return hd + """ P6 (card): the merge (05-04, kickoff #39 → #40) gives Δπ_chat > 0 and the split (05-11, #40 → #41) gives Δπ_chat < 0 on B4 (more or fewer interlocutors). Both are kickoff-confounded; expected inconclusive: neither step above the regime-III placebo p95 for φ, and neither K outside the placebo band. Compared descriptively with the other regime-III kickoffs (#37 → #38, #38 → #39, #41 → #42)."""
    if ne == "NE15":
        return hd + """ P6 (card): not testable on non-holdout data as a before/after (the pre-split days are in #34 / NE30, held out). Descriptive only: #33 (last 2 days) vs #35 (first 2 days), regime II, two weeks apart and across NE14; no verdict."""
    if ne == "NE41":
        return hd + """ P4 (card), pooled over the regime-III periods G37–G42, G44, G51 (per-period numbers in the G folders):
- B6: after a forced erasure (CF) the agent browses/looks more and types/shells less: pooled Δπ_browse > 0 and Δπ_type + Δπ_shell < 0 with CIs excluding 0 (H15's write dip).
- B4: |K| < 0.10 (no catalysis). The consolidate state is mechanically depleted right after a consolidation and is not interpreted.
- CF and CV (voluntary) give the same class.
- Design: episode = a CF (CV) event with no kick or other consolidation in the 10 min before; s0 = the last non-consolidate state before it; controls = matched minutes ≥ 10 min after the agent's last consolidation; both arms cut at the next kick or consolidation."""
    if ne == "NE10":
        return hd + """ P7 (card): within #30, 02-11 and 02-12 (no nudges) vs 02-13 (first nudges): Δπ_idle < 0 and idle escape up (the P1 direction), **not** significant at step level (one post day; placebo shape 2 + 1). HH52's check (idle escape rate vs stationary idle fraction) is answered mainly by the nudge point-lever units (P1); NE23 (off/on) is held out for confirmation."""
    if ne == "NE16":
        return hd + """ P7 (card): catalyst: K above the placebo p97.5 (escape at fixed occupancy rises once stalls are fixed); φ inside the placebo band. 03-24, 03-25 vs 03-26, 03-27 (regime III, #36)."""
    if ne == "NE07":
        return hd + """ P7 (card): an activity instruction, so a field if anything (Δπ_idle < 0), but underpowered: expected inside the placebo band (at most 1 of the 4 prompt steps above the placebo p95). 12-02, 12-03 vs 12-04, 12-05 (#21; DeepSeek-V3.2 joins 12-04 and is outside the balanced panel)."""
    return hd + """ P7 (card): a tool or channel change: neither (φ inside the placebo p95; K inside the placebo [p2.5, p97.5]) on behavior states; content not predicted. Judged against within-goal day-boundary placebos of the same era and window shape."""


def header(title: str, verdict: str, role: str, period_line: str) -> str:
    return f"# {title}\n\n**Verdict:** {verdict}\n**Role:** {role}\n**Period:** {period_line}\n"


def write_predictions():
    titles, rows = goal_info()
    for g in POINT_PERIODS:
        d = GP / f"G{g:02d}"
        d.mkdir(parents=True, exist_ok=True)
        r = rows.get(g, {})
        t = titles.get(g, "")
        why = ["Point levers (matched windows) on B4/B6 behavior states and content drift."]
        if g >= 31:
            why.append("Nudger on: nudge episodes available.")
        if g in REGIME3:
            why.append("Regime III: forced context erasures (NE41) available.")
        if g in (4, 5, 6, 51):
            why.append("Many human messages (public chat era / #51).")
        if g in UNNUMBERED:
            why.append(f"Contains the unnumbered CHANGELOG step {UNNUMBERED[g][0]} ({UNNUMBERED[g][1]}).")
        txt = header(f"H39 × G{g:02d}: {t} ({r.get('start', '?')} → {r.get('end', '?')})", "pending", "exploratory (round 1, non-holdout)",
                     f"regime {r.get('reg', '?')} · mode {r.get('mode', '?')} · N ≈ {r.get('N', '?')} agents · non-holdout days only.")
        txt += "\n## Why this period\n" + " ".join(why) + "\n\n## Prediction\n" + period_prediction(g) + "\n\n## Result\npending\n\n## Scorecard (period-specific axes)\npending\n\n## Notes\n"
        (d / "README.md").write_text(txt)
    for ne, (title, kind) in NE_FOLDERS.items():
        d = GP / ne
        d.mkdir(parents=True, exist_ok=True)
        role = "descriptive (pre side held out)" if ne == "NE15" else "exploratory (round 1, non-holdout; spanning test)"
        txt = header(f"H39 × {ne}: {title}", "pending", role, "see Prediction for the windows; non-holdout days only.")
        txt += "\n## Why this test\n" + {"kickoff": "Goal kickoffs are the candidate *fields* of HH52; transitions are the object (exception c).",
                                       "room": "Room changes alter who an agent hears: a candidate field toward or away from chat.",
                                       "erasure": "A context erasure removes the session channel at a scaffold-set time (H15): a lever the operator controls through the cap.",
                                       "scaffold": "A dated scaffold change inside a goal period: a quasi-intervention on every agent."}[kind]
        txt += "\n\n## Prediction\n" + ne_prediction(ne) + "\n\n## Result\npending\n\n## Notes\n"
        (d / "README.md").write_text(txt)
    print("predictions written:", len(POINT_PERIODS), "G folders,", len(NE_FOLDERS), "NE folders")


def keep_prediction(path: Path) -> str:
    t = path.read_text()
    m = re.search(r"## Prediction\n(.*?)\n## Result", t, re.S)
    return m.group(1).rstrip() if m else ""


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--stage", choices=["predictions", "results"], required=True)
    a = ap.parse_args()
    if a.stage == "predictions":
        write_predictions()
    else:
        import write_results  # noqa: E402  (results stage lives in write_results.py)
        write_results.main()
