"""Write the H62 period READMEs (goalperiod-subhypotheses/G<NN>/README.md and NE42/README.md).

  --predict   before the real-data run: verdict pending, predictions dated
  --results   after explore.py / natives.py: fills Result, Scorecard and the verdict (prediction text unchanged)
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
HYP = HERE.parent
ROOT = HYP.parents[1]
GP = ROOT / "hypotheses/hypohypotheses/goal-periods.md"
DATA = ROOT / "data/processed/H62-ideas-travel-reply-graph"
GOALS = [5, 6, 7, 8, 10, 11, 12, 13, 16, 17, 18, 19, 20, 21, 23, 24, 25, 26, 27, 30, 31, 33, 35, 36, 37, 38, 39, 40,
         41, 42, 44, 51]
NATIVE = {12, 51}
STAMP = "2026-10-04 19:45 UTC"
NSTAMP = "2026-10-04 19:33 UTC"

NATIVE_PRED = {
    51: f"""## Native test: the largest rooms (dilution)
*Prediction written {NSTAMP}, before any native statistic.* #51 has the largest rooms of the village (median ≈ 23 agents posting per room-day vs 5–14 elsewhere). Attention dilution (H18: per-pair coupling ∝ N^−0.6; H34: per-pair branching ∝ N^−0.55) should hit room-only exposure hardest, while a reply partner is read whatever the room size.
- **N51-a:** Λ(#51) ≥ 2 with lower 95% CI > 1, and Λ(#51) above the median Λ of the other eligible regime-III periods.
- **N51-b:** T_room(#51) is below every other eligible regime-III period's T_room, while T_rep(#51) lies inside the range of the other regime-III periods.
- Credence 0.5. Verdict: supported = N51-a and N51-b pass; failed = both fail; mixed = otherwise.
""",
    12: f"""## Native test: debate teams (DQ6)
*Prediction written {NSTAMP}, before any native statistic.* #12 is a judged debate with DQ6 team labels in one room. A team is a shared stance field. Every channel indicator is split by whether the source agent is on the recipient's team (same) or not (cross).
- **N12-a:** HR for reply-channel exposure from the other team ≥ HR for room-only exposure from team-mates (ideas cross a team boundary along reply edges at least as well as they move through the shared team field).
- **N12-b:** T_rep,cross > T_room,cross (point estimates; CIs reported).
- Credence 0.4 (936 ideas; power is low). Verdict: supported = both pass; failed = both fail; mixed = otherwise; descriptive if a cell has < 10 adoptions.
""",
}
NE42_PRED = f"""## Prediction
*Written {NSTAMP}, before any native statistic.* NE42: #best and #rest merged into one room on 2026-05-04 (#40) and split back on 05-11 (#41) at a fixed roster. The merge raises agents posting per room-day (7 → 14 → 7 in H62's count) and leaves the reply ties to form as before.
- **N42-a (room channel dilutes):** T_room(#40) < T_room(#39) and T_room(#40) < T_room(#41).
- **N42-b (reply channel does not):** T_rep(#40) within ±30% of the mean of T_rep(#39) and T_rep(#41).
- **N42-c (merged week, cross-group pairs):** among pairs split by the #39 partition, reply-channel exposures transmit at ≥ 2× the room-only rate (T_rep,cross / T_room,cross ≥ 2).
- Credence 0.4 (the goal changes with the merge, which also changes topics). Verdict: supported = N42-a and N42-b pass; failed = both fail; mixed = otherwise.
"""


def goal_meta() -> dict[int, dict]:
    txt = GP.read_text()
    out = {}
    for m in re.finditer(r"^\| (\d+) \| (\S+) → (\S+) \| (\S+) \| (\d+) \| (\S+) \| (\S+) \| (\S+) \| (\S+) \| ([^|]+) \|$", txt, re.M):
        out[int(m.group(1))] = dict(start=m.group(2), end=m.group(3), N=int(m.group(5)), regime=m.group(7),
                                    mode=m.group(9))
    for m in re.finditer(r"^### (\d+) · (.+)$", txt, re.M):
        if int(m.group(1)) in out:
            out[int(m.group(1))]["title"] = m.group(2).strip()
    return out


PRED = f"""## Prediction
*Written {STAMP}, before running on this period* (after the card's predictions at 19:25 UTC and the synthetic validation and amendments A1–A2 of the card; no channel-resolved statistic had been computed on real data).

| # | Prediction here | Counts against |
| --- | --- | --- |
| P1 | Sharper locking on the reply graph: Λ = HR_rep / HR_room > 1 with lower 95% CI > 1 (recency window, idea-stratified) | CI includes 1 or Λ < 1 |
| P2 | Per-edge transmissibility T_rep / T_room > 1 (CI > 1) | ratio ≤ 1 |
| P3 | Room-only exposure is mostly a field: C_room (seen vs unread room-only uses at 300 s) CI includes 1 or C_room < 1.5; C_rep > 1 (where Model B has ≥ 10 adoptions per cell) | C_room > 1.5 with CI > 1 |
| P4 | The reply channel's share of the contagion share exceeds its share of exposure events by ≥ 2× | ratio < 1.2 |
| P6 | Under the tie-only guard, Λ lower CI > 1 | guard Λ CI includes 1 |

**Verdict rule (card, with amendment A2, 19:44 UTC):** supported = Λ lower 95% CI > 1, T_rep / T_room lower 95% CI > 1 and C_rep lower 95% CI > 1 (reading matters inside the reply channel; unread-only coding, A1); mixed = a reply premium without C_rep CI > 1, or C_rep underpowered (consistent with a thread field); failed = Λ ≤ 1 and T_rep / T_room ≤ 1; n/a = < 20 adoptions at reply-channel or at room-only recency calls.
"""


def f(x, d=2):
    try:
        return "–" if x is None or x != x else f"{x:.{d}f}"
    except TypeError:
        return "–"


def card(g: int, meta: dict, r: dict | None, natives: dict) -> str:
    m = meta.get(g, {})
    nat = natives.get(f"G{g:02d}")
    role = "native (with the replication estimator)" if g in NATIVE else "replication"
    verdict = (nat["verdict"] if nat else "pending") if g in NATIVE else (r["verdict"] if r else "pending")
    head = (f"# H62 × G{g:02d}: {m.get('title', f'goal #{g}')} ({m.get('start', '?')} → {m.get('end', '?')})\n\n"
            f"**Verdict:** {verdict}\n**Role:** {role}\n"
            f"**Period:** regime {m.get('regime', '?')} · mode {m.get('mode', '?')} · {m.get('N', '?')} agents · "
            "non-holdout days only (held-out days masked with `holdout_mask`).\n")
    why = ("\n## Why this period\nReplication layer: the common H62 estimator (channel-resolved, idea-stratified adoption "
           "hazard; reply channel vs room-only exposure) on every period H34 analysed."
           + (" This period also hosts a native test (section below), with its own dated prediction." if g in NATIVE else "")
           + "\n\n")
    res = "## Result\n(pending: run `analysis/explore.py`)\n"
    sc = "## Scorecard (period-specific axes)\n(pending)\n"
    if r:
        if not r.get("eligible"):
            res = (f"## Result\n**n/a.** {r.get('A_adopt_rec_rep', 0)} adoptions at reply-channel recency calls and "
                   f"{r.get('A_adopt_rec_room', 0)} at room-only calls (eligibility ≥ 20 each).\n")
            sc = "## Scorecard (period-specific axes)\nNot informative (ineligible).\n"
        else:
            res = (f"## Result\n**{r['verdict']}.** {r['n_ideas']} ideas; {r['A_n_adopt']} adoptions in {r['A_n_strata']} idea "
                   f"strata; median agents posting per room-day {f(r['N_room'], 1)}; {r['n_parent_edges']} DQ2 parent edges.\n\n"
                   "| Prediction | Observed | Reference | Verdict |\n| --- | --- | --- | --- |\n"
                   f"| P1 Λ > 1 (CI) | Λ = {f(r['Lam'])} [{f(r.get('Lam_lo'))}, {f(r.get('Lam_hi'))}] (bootstrap); HR_rep {f(r['A_hr_rec_rep'], 1)} "
                   f"({r['A_adopt_rec_rep']} adoptions), HR_room {f(r['A_hr_rec_room'], 1)} ({r['A_adopt_rec_room']}) | room-contagion synthetic Λ ≈ 0.8 | "
                   f"{'pass' if r.get('Lam_lo', 0) > 1 else 'fail'} |\n"
                   f"| P2 T_rep / T_room > 1 (CI) | {f(r.get('T_ratio'))} [{f(r.get('T_ratio_lo'))}, {f(r.get('T_ratio_hi'))}]; T_rep {f(r.get('T_rep'), 3)} "
                   f"({r.get('n_rep')} events), T_room {f(r.get('T_room'), 3)} ({r.get('n_room')}) | 1 | {'pass' if r.get('T_ratio_lo', 0) > 1 else 'fail'} |\n"
                   f"| P3 C_room ≈ 1; C_rep > 1 | C_room {f(r.get('C_room'))} [{f(r.get('C_room_wlo'))}, {f(r.get('C_room_whi'))}]"
                   f"{'' if r.get('B_room_power') else ' (underpowered)'}; C_rep {f(r.get('C_rep'))} [{f(r.get('C_rep_wlo'))}, {f(r.get('C_rep_whi'))}]"
                   f"{'' if r.get('B_rep_power') else ' (underpowered)'} | thread-field synthetic C_rep ≈ 1 | descriptive |\n"
                   f"| P4 contagion share ≥ 2× exposure share | reply share of R_c {f(r.get('Rc_share_rep'))} vs of exposures {f(r.get('exp_share_rep'))} "
                   f"(ratio {f(r.get('P4_ratio'))}) | 1 | {'pass' if (r.get('P4_ratio') or 0) >= 2 else 'fail'} |\n"
                   f"| P6 guard Λ > 1 (CI) | {f(r.get('LamG'))} [{f(r.get('LamG_lo'))}, {f(r.get('LamG_hi'))}]; guard T ratio {f(r.get('G_T_ratio'))} | 1 | "
                   f"{'pass' if r.get('LamG_lo', 0) > 1 else 'fail'} |\n\n"
                   f"Branching decomposition: R̂ = {f(r.get('R_hat'), 3)} = reply {f(r.get('R_rep'), 3)} + room-only {f(r.get('R_room'), 3)} "
                   f"(+ human {f(r.get('R_hum'), 3)}). Data: `data/processed/H62-ideas-travel-reply-graph/G{g:02d}/`; "
                   "numbers from `analysis/explore.py` → `results/periods.json`.\n")
            sc = ("## Scorecard (period-specific axes)\n"
                  f"H (rival exposure models): Λ {f(r['Lam'])}, T ratio {f(r.get('T_ratio'))}. C (convergence): C_room {f(r.get('C_room'))}, "
                  f"C_rep {f(r.get('C_rep'))}. F (guard): Λ_guard {f(r.get('LamG'))}. E, G: not informed by this replication.\n")
    nblock = ""
    if g in NATIVE:
        nblock = NATIVE_PRED[g] + "\n" + (nat["text"] if nat else "(native result pending: run `analysis/natives.py`)\n") + "\n"
        res = res.replace("## Result", "## Result (replication estimator)") + (
            f"\nReplication verdict for this period: **{r['verdict']}**.\n" if r else "")
    notes = ("\n## Notes\n- Reply channels use only DQ2 edges posted before the use; the adopting message's own parent never "
             "enters (circularity guard; RE-V2 known issue).\n")
    return head + why + nblock + PRED + "\n" + res + "\n" + sc + notes


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--predict", action="store_true")
    ap.add_argument("--results", action="store_true")
    a = ap.parse_args()
    meta = goal_meta()
    rows, natives = {}, {}
    if a.results:
        rows = {r["goal"]: r for r in json.loads((DATA / "results/periods.json").read_text())}
        npath = DATA / "results/natives.json"
        natives = json.loads(npath.read_text()) if npath.exists() else {}
    for g in GOALS:
        d = HYP / f"goalperiod-subhypotheses/G{g:02d}"
        (d / "figures").mkdir(parents=True, exist_ok=True)
        (d / "README.md").write_text(card(g, meta, rows.get(g), natives))
    d = HYP / "goalperiod-subhypotheses/NE42"
    (d / "figures").mkdir(parents=True, exist_ok=True)
    nat = natives.get("NE42")
    (d / "README.md").write_text(
        "# H62 × NE42: rooms merged then split at a fixed roster (#39 → #40 → #41; 2026-05-04 / 2026-05-11)\n\n"
        f"**Verdict:** {nat['verdict'] if nat else 'pending'}\n**Role:** native\n"
        "**Period:** #39 (two rooms), #40 (merged, regime III, mode C), #41 (split back); 15 agents; non-holdout days. "
        "Exception (c) of CLAUDE.md: the transition is the object; each week is fitted separately and the weeks are compared.\n\n"
        "## Why this period\nThe only A-B-A change of room size at a fixed roster: an intervention on room-only exposure "
        "that leaves reply ties free to form (axis E).\n\n" + NE42_PRED + "\n## Result\n"
        + (nat["text"] if nat else "(pending: run `analysis/natives.py`)\n"))
    print(f"wrote {len(GOALS)} + NE42 period READMEs ({'results' if a.results else 'predictions'})")


if __name__ == "__main__":
    main()
