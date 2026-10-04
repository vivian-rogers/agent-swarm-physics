"""Write the per-goal-period cards hypotheses/H01-emergent-superagents-exist/G##/README.md from the exploratory JSONs
(numbers are filled from data/processed/H01-emergent-superagents-exist/explore*.json; context and verdicts below).

Usage: uv run python hypotheses/H01-emergent-superagents-exist/analysis/period_cards.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scheme"))
from h01common import OUT, HYP  # noqa: E402

GOALS = {8: ("Design the AI Village benchmark for open-ended goal pursuit", "2025-07-18 → 08-13"),
         21: ("Forecast the abilities and effects of AI", "2025-12-01 → 12-08"),
         35: ("Test your game to make it as fun and functional as you can", "2026-03-16 → 03-23"),
         36: ("Interact with other AI agents outside the Village", "2026-03-23 → 03-30"),
         37: ("Pick your own goal", "2026-03-30 → 04-02"),
         38: ("Choose a charity and raise as much money as you can for it", "2026-04-02 → 04-27"),
         39: ("Build your own interactive world", "2026-04-27 → 05-04"),
         40: ("Connect your worlds into a 3D universe", "2026-05-04 → 05-11"),
         41: ("Perform novel research", "2026-05-11 → 05-18"),
         42: ("Run your own Youtube channel", "2026-05-18 → 05-25"),
         44: ("Finetune your leader", "2026-05-26 → 06-01"),
         51: ("Each agent: maximize your assigned goal", "2026-07-06 → 09-20 (09-07 → tail held out)")}

META = {
    8: dict(verdict="descriptive", line="regime I · mode C · 4 agents · one room (#general) · 18 days.",
            why="Single-room, strongly fielded week (everyone builds a benchmark). No partition exists, so only P4 (polarization along ĝ) and P9 apply. Paired with #21 as the low-field contrast.",
            pred="P4: whole-swarm polarization along ĝ is high (a strongly fielded week), higher than in #21. P9: βJ₀ < 0.5 n.",
            notes="N = 4: P9's fluctuation ratio rests on 6 pairs. The ĝ alignment of agent-day vectors (mean cos 0.27) equals #21's, so the 'strong field' reading of #8 is not visible at this instrument."),
    21: dict(verdict="descriptive", line="regime I · mode I · 9 agents · one room · 5 days (NE28: o3 and Opus 4.1 retired on day 1).",
             why="Individual-objective forecasting week, the low-field contrast to #8 for P4.",
             pred="P4: polarization along ĝ lower than in #8. P9: βJ₀ < 0.5 n.",
             notes="Polarization along ĝ is as high as #8 (0.27 vs 0.27); the kickoff text is long and specific, which may make ĝ easy to align with. Strong day-to-day co-fluctuation (R ≈ 5)."),
    35: dict(verdict="mixed", line="regime II · mode C · 13 agents · #best/#rest (split 03-16, NE15; RPG forked per room) · 5 days. The pre-split window (#34) is held out.",
             why="First week with two populated rooms; each room tests its own fork of a shared game, so rooms differ in content by design.",
             pred="P1–P3 (rooms ordered, stable), P5 (fields ≥ 60%), P6 (exposure slope > 0, within > cross), P9.",
             notes="P5 R² (0.15) is below the D3.2′ falsifier (0.3) and far below its rotation null: alignment here is not field-like. The within-room excess is large (+0.22) but the exposure slope is ≈ 0, which the synthetic world produces for saturated coupling or a room field (the room forks). Day-to-day co-fluctuation within rooms ρ = 0.66 vs 0.09 across."),
    36: dict(verdict="failed", line="regime II (36a, 03-23, one day) / regime III (36b, 03-24 → 03-27) · mode C · 13 agents · two rooms · split at the 03-24 regime boundary.",
             why="Two-room regime-III days not in the card's P1 list; reported as secondary (Amendment 2). 36a is one day (P9 needs ≥ 2).",
             pred="Secondary P1; P5/P6 per Amendment 1; P9.",
             notes="Rooms are not more ordered than random here (ΔH > 0 on all 4 days). The within-room excess is +0.08 (p = 0.09)."),
    37: dict(verdict="failed", line="regime III · mode F · 12 agents · two rooms · 3 days.",
             why="Short pick-your-own week in two rooms (secondary for P1).",
             pred="Secondary P1; P5/P6; P9.",
             notes="Weak order (median ΔH −0.02), no room excess (+0.01), cross-room co-fluctuation as large as within (0.26 vs 0.30): in a free week the rooms are not distinct units."),
    38: dict(verdict="mixed", line="regime III · mode C · 12–14 agents · #best/#rest with different instructions (charity overrides vs. free) · 17 days, split at NE17 (04-14) and NE18 (04-20) into 38a/38b/38c.",
             why="The longest two-room period, and the rooms got different goals: a natural test of whether room order is a room field.",
             pred="P1–P3, P5, P6, P9 per unit.",
             notes="The strongest room order in the data (ΔH −0.34 to −0.38 nats, every day p < 0.05), but the rooms were given different tasks, so this is the room-field case the synthetic warned about (a room field alone gives ΔH < 0 and within > cross). Exposure slopes are mixed (+0.09, −0.06, +0.01). Lab order is weak (−0.01 to −0.08)."),
    39: dict(verdict="mixed", line="regime III · mode I · 15 agents · two rooms after the 04-27 transfer (3 agents #best → #rest; GPT-5.5 joins) · 5 days.",
             why="Individual world-building; also the pre-window of the 05-04 merge (P7, see G40).",
             pred="P1–P3, P5, P6, P9.",
             notes="Rooms barely more ordered than random (median ΔH −0.04, no day significant) but labs are (−0.25): the one unit where lab order beats room order. H05 also found no block structure in #39."),
    40: dict(verdict="supported", line="(verdict for P7, this period's specific prediction; P5/P6/P9 as in the table) regime III · mode C · 15 agents · merged into #universe-coordination 05-04, GPT-5 alone in #rest · 5 days.",
             why="The 05-04 merge, an 'add' of the cross-room channel: P7's difference-in-differences against #39 (no NE ID in the catalog, so it lives here). No P1 days (only one populated room).",
             pred="P7: newly co-located pairs' residual alignment rises relative to pairs co-located throughout; GPT-5 (left alone) shows no rise. Direction only (shared-objective week).",
             notes="Supported in direction and robust to every instrument variant (+0.10 to +0.23), but #40 is a shared-objective week, so goal type is confounded with the merge; stay pairs also rose (+0.21). The A-B-A mirror (05-11 split, used as the confirm script's dry-run stand-in) gave cut-pair DiD −0.24 (permutation p = 0.006)."),
    41: dict(verdict="mixed", line="regime III · mode I · 15 agents · re-split into #best/#rest on 05-11 · 5 days.",
             why="Two rooms with the same task (novel research): room order here cannot come from different instructions.",
             pred="P1–P3, P5, P6, P9.",
             notes="Mixed on the card's predictions (P1 and the coupling residual met; P3, P5 and P9 not), but the most coupling-favoring week: rooms ordered (ΔH −0.19), positive exposure slope (+0.08, rotation p = 0.005), within-room excess +0.16 (p = 0.002), day-to-day co-fluctuation within rooms 0.47 vs 0.04 across, and residual alignment drifting up across the week (+0.056/day). Exploratory; one unit."),
    42: dict(verdict="mixed", line="regime III · mode I · 16 agents · two rooms · 5 days (Gemini 3.5 Flash joins 05-20; chat-length instruction 05-22, not split).",
             why="Individual YouTube channels in two rooms: a field-dominated week (one shared genre).",
             pred="P1–P3, P5, P6, P9.",
             notes="The goal direction alone explains 54% of pairwise alignment (R² 0.54, the highest goal-only share), alignment with ĝ is the highest of regime III (0.43), and rooms add little (ΔH −0.04, within − cross +0.03, slope −0.02): field-driven order, as D3.2′ expects."),
    44: dict(verdict="mixed", line="regime III · mode C · 16–18 agents · two rooms with a per-room goal/kickoff override (05-26) · 4 days (Opus 4.8 and the temporary fine-tuned leader join 05-28).",
             why="Rooms with different instructions again (per-room override), like #38.",
             pred="P1–P3, P5, P6, P9.",
             notes="Rooms ordered (ΔH −0.11, meets both P1 criteria in this unit) and a large within-room excess (+0.24, p < 0.001), but the exposure slope is n.s. and the rooms had different kickoffs (room field)."),
    51: dict(verdict="mixed", line="regime III · mode I/K · 21–32 agents · one room (#general) except #focus (51c: Gemini 2.5 Pro and Opus 4.8, 08-05 → 08-24) · 45 non-holdout days, split at 07-09 (NE32), 08-05, 08-25 (#focus) and 09-03 (NE33); 09-07 → tail held out.",
             why="The private-role era: each agent has its own assigned goal (agent-specific fields, NE26) and everyone shares one room; the largest N and longest window. #focus is the only partition (P1).",
             pred="P1–P3 on #focus days; P5/P6 per sub-unit (agent goals added to the field subspace, Amendment 2); P9 per sub-unit. NE32 (P8) is in `NE32/`.",
             notes="Small but consistently positive exposure slopes in the big single room (51b +0.008, 51c +0.010, 51d +0.038; rotation p ≤ 0.06), the only setting with enough within-pair exposure variation for tight estimates. The assigned-goal field explains little of the alignment (goal-only R² ≤ 0.05). Mean-field βJ₀/n falls as N grows (0.73 → 0.35)."),
}


def f(x, n=3, sign=False):
    if x is None:
        return "–"
    return (f"{x:+.{n}f}" if sign else f"{x:.{n}f}")


def main():
    ex = json.loads((OUT / "explore.json").read_text())
    exh = json.loads((OUT / "explore_hcross.json").read_text())
    p1u = ex["p1"]["per_unit"]; p56 = ex["p56"]["per_unit"]; p9 = ex["p9"]["units"]; pr = ex.get("p9_rooms", {}); p4 = ex["p4"]["units"]
    p3 = ex["p1"]["P3"]["per_unit"]
    for g, m in META.items():
        units = sorted([u for u in p9 if "".join(c for c in u if c.isdigit()) == str(g)] +
                       ([u for u in ("36a",) if g == 36]), key=lambda s: s)
        d = HYP / "goalperiod-subhypotheses" / f"G{g:02d}"; (d / "figures").mkdir(parents=True, exist_ok=True)
        L = [f"# H01 × G{g:02d}: {GOALS[g][0]} ({GOALS[g][1]})", "",
             f"**Verdict:** {m['verdict']}", "**Role:** exploratory", f"**Period:** {m['line']}", "",
             "## Why this period", m["why"], "",
             "## Prediction",
             "*Written 2026-10-03 on the main card (P1–P9, Amendments 1–3), before any analysis of this period.*",
             m["pred"], "Falsifiers as on the main card: ΔH ≥ 0 on most days (D3.1.a); field R² < 0.3 or exposure slope ≥ 0.1 (D3.2′); slope and within > cross vanish under the rotation null (D3.2).", "",
             "## Result", "Units: " + ", ".join(units) + ". Data: `data/processed/H01-emergent-superagents-exist/" + f"G{g:02d}/results.json`. Figure: `figures/G{g:02d}_panels.pdf`.", ""]
        L += ["| unit | P1 rooms: days ΔH<0 · median ΔH · days p<.05 · day-1 ΔH | P2 labs median ΔH | P3 pairs below null q05 | P5 R² (rotation null) | P6 slope ± SE (rotation p) | within − cross (perm p) | P9 βJ₀/n ± SE · ρ_within/ρ_cross |",
              "| --- | --- | --- | --- | --- | --- | --- | --- |"]
        for u in units:
            a = p1u.get(u, {}); r = a.get("room") if a else None
            c1 = (f"{r['frac_dH_neg']*100:.0f}% · {f(r['median_dH'],3,True)} · {r['frac_p05']*100:.0f}% · {f(a.get('day1_dH'),3,True)}" if r else
                  ("no two-room days" if u in p1u else "n/a"))
            c2 = f(a["lab"]["median_dH"], 3, True) if a and a.get("lab") else "–"
            c3 = f"{p3[u]['frac_below_q05']*100:.0f}% of {p3[u]['n']}" if u in p3 else "–"
            q = p56.get(u, {})
            c5 = f"{f(q.get('r2'),2)} ({f(q.get('r2_rot_mean'),2)})" if q.get("r2") is not None else "–"
            c6 = f"{f(q.get('slope'),3,True)} ± {f(q.get('slope_se'),3)} ({f(q.get('p_rot'),3)})" if q.get("slope") is not None else "–"
            c7 = f"{f(q.get('within_minus_cross'),3,True)} ({f(q.get('p_agent_room_perm'),3)})" if q.get("within_minus_cross") is not None else "–"
            v9 = p9.get(u); rr = pr.get(u)
            c9 = (f"{f(v9['bJ_over_n'],2)} ± {f(v9.get('bJn_jk_se'),2)}" + (f" · {f(rr['rho_within'],2)}/{f(rr['rho_cross'],2)}" if rr and rr.get("rho_cross") is not None else "")) if v9 else "–"
            L.append(f"| {u} | {c1} | {c2} | {c3} | {c5} | {c6} | {c7} | {c9} |")
        if g in (8, 21):
            v = p4[str(g)]
            L += ["", f"**P4.** Mean polarization along ĝ {v['pol_g_mean']:.3f} (null sd {v['null_sd_pol_g']:.3f}); rank {ex['p4']['regime_I_rank_by_pol_g'].index(str(g)) + 1} of {len(ex['p4']['regime_I_rank_by_pol_g'])} regime-I units. #8 vs #21: {ex['p4']['P4']['pol_g_8']:.3f} vs {ex['p4']['P4']['pol_g_21']:.3f} → not as predicted."]
        if g == 40:
            P7 = ex["p56"]["P7"]; P7h = exh["p56"]["P7"]
            L += ["", "**P7 (05-04 merge, #39 → #40).**", "",
                  "| arm | pairs | pre (#39) | post (#40) | DiD vs stay | p (pair-clustered) | permutation p |", "| --- | --- | --- | --- | --- | --- | --- |",
                  f"| stay | {P7['new']['n_pairs_stay']} | {P7['means']['stay_pre']:.3f} | {P7['means']['stay_post']:.3f} | – | – | – |",
                  f"| new (best × rest) | {P7['new']['n_pairs_arm']} | {P7['means']['new_pre']:.3f} | {P7['means']['new_post']:.3f} | {P7['new']['did']:+.3f} ± {P7['new']['se']:.3f} | {P7['new']['p']:.4f} | {P7['new']['p_perm_one_sided']:.3f} |",
                  f"| GPT-5 × #rest (cut) | {P7['g5_cut']['n_pairs_arm']} | {P7['means']['g5_cut_pre']:.3f} | {P7['means']['g5_cut_post']:.3f} | {P7['g5_cut']['did']:+.3f} ± {P7['g5_cut']['se']:.3f} | {P7['g5_cut']['p']:.3f} | – |",
                  f"| GPT-5 × #best (cross) | {P7['g5_cross']['n_pairs_arm']} | {P7['means']['g5_cross_pre']:.3f} | {P7['means']['g5_cross_post']:.3f} | {P7['g5_cross']['did']:+.3f} ± {P7['g5_cross']['se']:.3f} | {P7['g5_cross']['p']:.3f} | – |",
                  "", f"Cross-fitted-h variant: new-arm DiD {P7h['new']['did']:+.3f} (permutation p = {P7h['new']['p_perm_one_sided']:.3f})."]
        if g == 51:
            L += ["", "NE32 (GPT-5.6 triplet, 07-09/07-10) is analysed in [`../NE32/`](../NE32/README.md)."]
        L += ["", "## Scorecard (period-specific axes)"]
        if g in (8, 21):
            L += ["- **C** 0: P4 has no null-beating contrast (#8 ≈ #21). **D** 0. **G** n/a (one room)."]
        elif g == 40:
            L += ["- **E** 1: the merge DiD has the predicted sign, permutation p = 0.004, robust to instrument variants; confounded with a goal change. **C** 1. **G** 1."]
        else:
            L += ["- **C** 1: rooms vs random partitions and the rotation/day-shuffle nulls computed per unit (see table). **G** 1 where rooms are ordered. **E** n/a within the period."]
        L += ["", "## Notes", f"- 2026-10-03: {m['notes']}",
              "- Agent field h_i: the agent's first day in the unit (Amendment 3, after the invariance check failed in regimes II and III), so P5/P6 use days 2+. P6 uses rarefied agent-day vectors (8 statements, Amendment 2)."]
        (d / "README.md").write_text("\n".join(L) + "\n")
        print("wrote", d / "README.md")


if __name__ == "__main__":
    main()
