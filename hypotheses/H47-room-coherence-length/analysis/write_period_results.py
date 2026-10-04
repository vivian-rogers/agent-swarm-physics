"""Fill the H47 period / NE folders with results (verdict line, ## Result, ## Scorecard, a dated note) from
data/processed/H47-room-coherence-length/results/*.json. Keeps the dated predictions untouched.

Usage: uv run python hypotheses/H47-room-coherence-length/analysis/write_period_results.py
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import h47lib as L  # noqa: E402

GP = L.HYP / "goalperiod-subhypotheses"
RES = L.OUT / "results"
WHEN = "2026-10-04"


def J(n):
    return json.loads((RES / f"{n}.json").read_text())


def f(x, d=2):
    return "–" if x is None or (isinstance(x, float) and x != x) else f"{x:.{d}f}"


def pv(x):
    return "–" if x is None else (f"{x:.3f}" if x >= 0.001 else "< 0.001")


S, coh, lead, det, sep, ne, g51 = (J(n) for n in ("summary", "coherence", "leadership", "detector", "separation", "ne42", "g51"))
P = S["periods"]
KICK = {"G36": "#36", "G37": "#37", "G38": "#38", "G39": "#39", "G41": "#41", "G42": "#42", "G44": "#44"}
FIRST = J("posthoc_first_statement")


def repl_table(g):
    r = P[g]; c = coh[g]
    rows = ["| Prediction | Observed | Null / reference | Verdict |", "| --- | --- | --- | --- |"]
    rows.append(f"| P1: C_B ≤ 0.3 and room-relabel p < 0.05 (w30, pooled over {', '.join(r['units'])}) | ρ_w {f(r['rho_w'])}, ρ_c {f(r['rho_c'])}, **C_B {f(r['C_B'])}** "
                f"[day-bootstrap {f(r['C_B_ci'][0]) if r['C_B_ci'] else '–'}, {f(r['C_B_ci'][1]) if r['C_B_ci'] else '–'}], p {pv(r['p_DB'])} | permutation median C_B {f(c['w30'].get('null_CB_med'))} | "
                f"{'met' if (r['C_B'] <= 0.3 and r['p_DB'] < 0.05) else 'not met'} |")
    sharp = (r["G"] or -9) > r["C_B"]
    rows.append(f"| P2: G ≥ 0.6 and (1 − C_B) > (1 − G) | G {f(r['G'])} (tier-permutation p for G < null: {pv(r['p_G'])}); boundary drop {'>' if sharp else '≤'} within-room drop | G = 1 if flat inside rooms | "
                f"{'met' if (r['G'] >= 0.6 and sharp) else ('half' if sharp or r['G'] >= 0.6 else 'not met')} |")
    rows.append(f"| Day resolution (secondary) | C_B {f(r['C_B_day'])}, p {pv(r['p_day'])} | units ≥ 3 days only | – |")
    rob = r["rob"]
    rows.append(f"| Robustness (C_B) | L0 {f(rob.get('L0'))} · no dedup {f(rob.get('no_dedup'))} · DQ5 style {f(rob.get('style'))} · DQ6 assigned rooms {f(rob.get('assigned'))} | – | – |")
    pu = coh[g]["per_unit"]
    rows.append("| Per unit (w30) | " + " · ".join(f"{u}: {f(v['obs']['C_B'])} (p {pv(v.get('p_DB'))})" for u, v in pu.items() if v) + " | 100 permutations each | descriptive |")
    if g in sep:
        rows.append(f"| Between-room separation F (per day) | day 0 {f(sep[g]['day0_F'], 1)} (z {f(sep[g]['day0_z'], 1)}), median {f(sep[g]['median_F'], 1)}, Spearman over days {f(sep[g]['spearman_F_day'])} | within-day room-relabel null (F ≈ 1) | descriptive |")
    k = KICK.get(g)
    if k:
        e = lead[k]; fs = FIRST.get(k, {})
        rows.append(f"| Leadership at the {k} kickoff (card P4): no lead | L {f(e['L'])} (agent-bootstrap [{f(e['L_ci'][0])}, {f(e['L_ci'][1])}]), cohort-relabel p {pv(e['p_L'])}; dT50 {e['dT50_bins']} bins (p {pv(e['p_T50'])}) | "
                    f"post hoc: first post-kickoff statement after {f(fs.get('best', {}).get('latency_med_min'), 1)} / {f(fs.get('rest', {}).get('latency_med_min'), 1)} min (#best / #rest), shift fraction y {f(fs.get('best', {}).get('y_first_med'))} / {f(fs.get('rest', {}).get('y_first_med'))} | "
                    f"{'met (no lead)' if e['p_L'] >= 0.05 else 'not met (L significant)'} |")
    return "\n".join(rows)


def write(folder, verdict, result, scorecard, note):
    p = GP / folder / "README.md"
    t = p.read_text()
    t = re.sub(r"\*\*Verdict:\*\* .*", f"**Verdict:** {verdict}", t, count=1)
    t = re.sub(r"## Result\n.*?\n## Scorecard", f"## Result\n{result}\n\n## Scorecard", t, flags=re.S)
    t = re.sub(r"## Scorecard \(period-specific axes\)\n.*?\n## Notes", f"## Scorecard (period-specific axes)\n{scorecard}\n\n## Notes", t, flags=re.S)
    if note not in t:
        t = t.rstrip() + f"\n- {WHEN}: {note}\n"
    p.write_text(t)


FIGLINE = "Figure: `figures/{g}_h47.pdf` (per-unit ρ_w/ρ_c, between-room separation per day, kickoff response curves). Data: `data/processed/H47-room-coherence-length/results/` (`coherence.json`, `separation.json`, `leadership.json`)."


def main():
    note = "results filled from `analysis/explore.py` (round 1, exploratory, non-holdout only)."
    for g in ("G35", "G36", "G37", "G39", "G42"):
        r = P[g]
        v = r["verdict_rule"]
        extra = {"G35": "Sharpest replication boundary (separate RPG forks per room). Inside rooms correlation is flat across mention tiers (G ≈ 1), the only period where the room behaves as a flat block.",
                 "G36": "Supported, with identical room kickoffs. Inside the rooms, correlation is concentrated in pairs that mention each other (G 0.51).",
                 "G37": "Mixed: the boundary is weak (cross-room correlation half the within-room level; permutation p 0.08); at day level C_B ≈ 1. Identical room kickoffs, free goal, rooms barely separated (F ≤ 3).",
                 "G39": "Mixed: weak boundary (C_B 0.57, p 0.11), the lowest within-room correlation of all periods (ρ_w 0.08), identical kickoffs and barely separated rooms (F 1.1–2.3). Matches H05's finding of no talk block structure in #39. Also the A1 phase of NE42.",
                 "G42": "Mixed: the boundary is significant (p 0.02) but shallow (C_B 0.54); identical kickoffs; rooms barely separated (F 1.2–2.3)."}[g]
        res = repl_table(g) + "\n\n" + extra + "\n\n" + FIGLINE.format(g=g)
        sc = (f"- **C (adequacy):** {'beats' if r['p_DB'] < 0.05 else 'does not beat'} the room-relabel null (p {pv(r['p_DB'])}).\n"
              f"- **F (robustness):** C_B moves ≤ {max(abs((r['rob'][k] or r['C_B']) - r['C_B']) for k in r['rob']):.2f} across L0, dedup, DQ5 style vectors and DQ6 assigned rooms.\n"
              f"- **G (ground truth):** room kickoffs {'identical' if r['instr'] == 'identical' else r['instr']} (shared goal_fields).")
        write(g, v, res, sc, note)
    # ---------------- G41 native
    r = P["G41"]
    b = [P["G38"]["C_B"], P["G44"]["C_B"]]
    med = sorted(b)[0] / 2 + sorted(b)[1] / 2
    res = ("| Native prediction | Observed | Null | Verdict |\n| --- | --- | --- | --- |\n"
           f"| P5a (primary): C_B(41) ≤ 0.3, room-relabel p < 0.01 | C_B {f(r['C_B'])}, p {pv(r['p_DB'])} (day level {f(r['C_B_day'])}) | permutation median {f(coh['G41']['w30'].get('null_CB_med'))} | **met** |\n"
           f"| P5b: |C_B(41) − median(C_B(38), C_B(44))| ≤ 0.15 | {f(r['C_B'])} vs {f(med)}: difference {f(abs(r['C_B'] - med))} | – | not met (just) |\n"
           f"| P5c: separation rises over the week, low on day 0 | day-0 F {f(sep['G41']['day0_F'], 1)} (z {f(sep['G41']['day0_z'], 1)}); Spearman over days {f(sep['G41']['spearman_F_day'])} | F ≈ 1 under the null | not met: rooms already separated on the kickoff day |\n"
           f"| Replication P2 | G {f(r['G'])} (p {pv(r['p_G'])}) | – | not met (correlation concentrated in talking pairs) |\n"
           f"| Leadership at #41 (cohorts = new rooms) | L {f(lead['#41']['L'])}, p {pv(lead['#41']['p_L'])}; both rooms at y ≈ 1 from the first 15 min | – | met (no lead) |\n\n"
           "**Reading.** With the same instruction in both rooms, content still co-moves inside rooms and not across them (C_B 0.17, the third-sharpest boundary). So a sharp boundary does not need a room-specific operator drive. But the rooms had split into different topics from the first day (the separation is as large as in G38/G44), and the post hoc cross-period pattern says sharp boundaries go with separated topics. This week cannot say whether the topic split is coupling (each room's conversation picks its topic) or a fast room-level drive (who is in the room). It is the A2 phase of NE42.\n\n"
           + FIGLINE.format(g="G41"))
    sc = ("- **C:** beats the room-relabel null (p 0.003).\n- **E:** A2 of NE42 (the boundary returns after the merge; see NE42).\n"
          "- **G:** identical-instruction ground truth (one kickoff, in the merged room); topic divergence matches the goal-periods notes (#rest coordination, #best judge bias).")
    write("G41", "supported", res, sc, note)
    # ---------------- G38 / G44 native
    for g in ("G38", "G44"):
        r = P[g]
        res = ("| Native prediction | Observed | Null | Verdict |\n| --- | --- | --- | --- |\n"
               f"| P6a (primary): instruction-direction share ≤ 0.15 | all static directions: {f(r['instr_share_all'])}; room-kickoff difference only: {f(r['instr_share_instr'], 3)} | – | **met** |\n"
               f"| P6b: day-0 separation > G41's day 0 ({f(sep['G41']['day0_F'], 1)}) | {f(sep[g]['day0_F'], 1)} (z {f(sep[g]['day0_z'], 1)}) | F ≈ 1 under the null | {'met' if sep[g]['day0_F'] > sep['G41']['day0_F'] else 'not met'} |\n"
               f"| Replication P1 | C_B {f(r['C_B'])} [{f(r['C_B_ci'][0])}, {f(r['C_B_ci'][1])}], p {pv(r['p_DB'])} | – | met |\n"
               f"| Replication P2 | G {f(r['G'])} (p {pv(r['p_G'])}) | – | not met |\n"
               f"| Leadership at the {KICK[g]} kickoff | L {f(lead[KICK[g]]['L'])}, p {pv(lead[KICK[g]]['p_L'])} | – | {'met (no lead)' if lead[KICK[g]]['p_L'] >= 0.05 else 'not met (L significant)'} |\n\n")
        if g == "G38":
            res += ("**Reading.** The room-specific charity instructions (room kickoff cosine 0.86) give one of the two sharpest boundaries (C_B 0.07), but the instruction *direction* itself carries ~0.1% of the room excess: the static field is removed by the agent means, and the time-varying room co-fluctuation lies elsewhere. **The #38 lead index is the one significant L of eight (p 0.044, expected about 0.4 false positives in 8 tests),** and it is not a lead in time: both response curves are flat from the first 15 minutes. #best's kickoff-day content already matches its next two days, while #rest's day-0 content stays near its pre-day position (first-statement shift 0.10). That reads as a room-specific instruction arc (a room drive), not one room leading another.\n\n")
        else:
            res += ("**Reading.** Room-specific instructions (room kickoff cosine 0.81; #best fine-tunes a leader, #rest picks its own goals) and the sharpest boundary of all (C_B −0.04: no cross-room correlation). The instruction direction carries ~0.1% of the room excess. The leadership pre-baseline is 05-22 (05-25 is held out).\n\n")
        res += FIGLINE.format(g=g)
        sc = (f"- **C:** beats the room-relabel null (p {pv(r['p_DB'])}).\n- **G:** room-specific kickoffs (goal_fields kickoff_room cosine {'0.86' if g == 'G38' else '0.81'}); DQ6 assigned rooms give the same C_B.\n"
              "- **H:** the static instruction direction (R-drive in its simplest form) does not carry the room excess; time-varying room drives are not excluded.")
        write(g, "supported", res, sc, note)
    # ---------------- NE42 native
    o = ne["obs"]
    ev = {e["ref"]: e for e in det["events"]}
    res = ("| Native prediction | Observed | Null | Verdict |\n| --- | --- | --- | --- |\n"
           f"| P7a (primary): r_X ≤ 0.3 in #39 and #41, ≥ 0.7 in #40 | #39 {f(o['39']['r_X'])} · #40 {f(o['40']['r_X'])} · #41 {f(o['41']['r_X'])} (ρ_XP / ρ_WP: {f(o['39']['rho_XP'], 3)}/{f(o['39']['rho_WP'], 3)}, {f(o['40']['rho_XP'], 3)}/{f(o['40']['rho_WP'], 3)}, {f(o['41']['rho_XP'], 3)}/{f(o['41']['rho_WP'], 3)}) | partition-permutation medians {', '.join(f(x) for x in ne['null_rX_median'])}; one-sided p (r_X low) {pv(ne['p_unit_low']['39'])}, {pv(ne['p_unit_low']['40'])}, {pv(ne['p_unit_low']['41'])} | not met (#39 above 0.3; #40 and #41 as predicted) |\n"
           f"| P7b: DiD = r_X(40) − mean(r_X(39), r_X(41)) > 0.4, p < 0.05 | **DiD {f(ne['DiD'])}** [day bootstrap {f(ne['DiD_ci'][0])}, {f(ne['DiD_ci'][1])}], p {pv(ne['p_DiD'])} | 1,000 joint partition permutations | **met** |\n"
           f"| P7c: residual partition memory in #40 (r_X < 0.9) | r_X(40) {f(o['40']['r_X'])}: cross-partition pairs correlate *more* than within-partition pairs | – | not met (no memory) |\n"
           f"| Detector, 05-04 merge (goal-confounded) | R1_swarm z {f(ev['NE42a']['R1_d0'])} (hit); R1_room undefined (new room, the old #rest held one agent); R1_loc {f(ev['NE42a']['R1_loc_d0'])} | placebo FAR 0 at z ≥ 3 (11 multi-room placebo days) | R1_swarm only |\n"
           f"| Detector, 05-11 split (goal-confounded) | R1_swarm {f(ev['NE42b']['R1_d0'])}, R1_room {f(ev['NE42b']['R1_room_d0'])} (both hit); R1_loc {f(ev['NE42b']['R1_loc_d0'])} | – | both fire |\n"
           f"| Leadership at #40 (cohorts = previous rooms) | L {f(lead['#40']['L'])}, p {pv(lead['#40']['p_L'])} (a level offset: ex-#best closer to its later content all day) | – | no lead |\n\n"
           f"Partition: {ne['n_part'][0]} #best and {ne['n_part'][1]} #rest agents with the same modal room in #39 and #41 (none dropped).\n\n"
           "**Reading.** The strongest result of round 1. Content coherence follows the chat channel: agents from different A-rooms correlate at about 0.57× and 0.17× the within-room level while separated, and at 1.37× once merged, then drop back the week after (DiD 1.0, p 0.001). A persistent team identity (synthetic: DiD ≈ −0.06) is rejected. The pre-registered A-phase threshold (≤ 0.3) fails only in #39, as the synthetic warned (A-phase r_X 0.39–0.52 under coupling with a weak global drive). Caveats: every phase is a new goal (#40 a shared objective, which by itself raises cross-pair correlation as a global drive), and N = 15 agents.\n\n"
           "Figure: `figures/NE42_h47.pdf`. Data: `results/ne42.json`, `results/detector.json`.")
    sc = ("- **C:** DiD beats 1,000 joint partition permutations (p 0.001).\n- **D:** an unfitted, pre-registered contrast (P7b) met.\n"
          "- **E:** the A-B-A is the interventional test: the boundary follows the channel (goal-confounded).\n- **H:** beats the team-identity rival; R-global not excluded for #40 itself (shared objective).")
    write("NE42", "mixed", res, sc, note + " Verdict mixed by the pre-registered rule (P7a fails at #39); the informative DiD (P7b) is met.")
    # ---------------- G51 native
    rf = g51["r_F"]
    gs = g51["single_room_G"]
    r = P["G51"]
    res = ("| Native prediction | Observed | Null | Verdict |\n| --- | --- | --- | --- |\n"
           f"| P8a (primary): r_F(51g) < min(r_F(51f), r_F(51h)) − 0.2 | 51f {f(rf['51f']['r_F'])} · 51g {f(rf['51g']['r_F'])} · 51h {f(rf['51h']['r_F'])}; DiD {f(g51['DiD'])} (ρ_FG {f(rf['51f']['rho_FG'], 3)} / {f(rf['51g']['rho_FG'], 3)} / {f(rf['51h']['rho_FG'], 3)}) | focus-label permutation p (DiD low) {pv(g51['p_DiD_low'])} | **not met**: the two focus members were already decoupled before #focus existed |\n"
           f"| P8b: median G ≥ 0.6 in the single-room units | median G {f(g51['median_G_single'])} (" + ", ".join(f"{u} {f(v['G'])}" for u, v in gs.items()) + ") | tier permutation | **not met**: in one room of 21–32 agents, correlation lives in pairs that address each other |\n"
           f"| 51g as a two-room unit (replication rule) | C_B {f(r['C_B'])}, p {pv(r['p_DB'])}; G {f(r['G'])} | 2 #focus members | supported by the replication rule, near-unpowered |\n"
           f"| Detector, #focus opens (08-05; clean) | R1_swarm {f(ev['focus-open']['R1_d0'])}, R1_room {f(ev['focus-open']['R1_room_d0'])}, R1_loc {f(ev['focus-open']['R1_loc_d0'])} (#focus cohort of 2) | – | no detector fires |\n"
           f"| Detector, #focus empties (08-24; clean) | R1_swarm {f(ev['focus-close']['R1_d0'])}, R1_room {f(ev['focus-close']['R1_room_d0'])}, R1_loc {f(ev['focus-close']['R1_loc_d0'])} | – | no detector fires |\n\n"
           f"Focus members (modal room #focus on ≥ 2 days of 51g): agents {g51['focus_members']} (13 days each).\n\n"
           "**Reading.** The self-made side room did not visibly cut coherence: its two core members were already about 0.1× as correlated with #general as #general pairs were with each other *before* #focus opened. The side room formalized a split that had already happened (selection), and the pair statistic with 2 members is very noisy. The informative result is P8b: in the big single room, content correlation is concentrated in pairs that talk to each other (median G 0.18). Coherence inside a large room is shorter than the room.\n\n"
           "Data: `results/g51.json`, `results/detector.json`.")
    sc = ("- **C:** 51g C_B beats the room-relabel null (p 0.007), but with two members.\n- **G:** DQ6 confirms #focus is a presence deviation (everyone assigned to #general).\n"
          "- **H:** R-conversation (coherence set by who talks to whom) wins inside the big room.")
    write("G51", "failed", res, sc, note)
    print("period results written")


if __name__ == "__main__":
    main()
