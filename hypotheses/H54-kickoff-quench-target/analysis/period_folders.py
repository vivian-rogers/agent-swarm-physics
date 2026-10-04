"""Write goalperiod-subhypotheses/G<NN>/README.md (replication: templated; native: G51, G44, G38, G26) and NE34/README.md.

Numbers come from data/processed/H54-kickoff-quench-target/{NE34, G<NN>}/. Predictions quoted here were written in the
card on 2026-10-04 before any real-data run (replication: templated, labelled as such; native: N1-N4).
"""
from __future__ import annotations

import json
import re

import polars as pl

import h54lib as L

SUB = L.HYP / "goalperiod-subhypotheses"
MODE = {3: 'F', 4: 'C', 5: 'F', 6: 'K', 7: 'F', 8: 'C', 10: 'I', 11: 'F', 12: 'M', 13: 'C', 16: 'F', 17: 'I', 18: 'C', 19: 'C',
        20: 'I', 21: 'I', 24: 'C', 25: 'C', 26: 'C', 27: 'K', 30: 'C', 31: 'F', 33: 'C', 35: 'C', 36: 'C', 37: 'F', 38: 'C',
        39: 'I', 40: 'C', 41: 'I', 42: 'I', 44: 'C', 51: 'I/K'}
NATIVE = {51, 44, 38, 26}


def titles():
    t = {}
    for line in (L.ROOT / "hypotheses/hypohypotheses/goal-periods.md").read_text().splitlines():
        m = re.match(r"^### (\d+) · (.+)$", line)
        if m:
            t[int(m.group(1))] = m.group(2).strip()
    return t


def f(x, d=2):
    if x is None:
        return "–"
    try:
        if x != x:
            return "–"
    except Exception:
        pass
    return f"{x:.{d}f}" if isinstance(x, float) else str(x)


def rep_verdict(pi):
    if pi is None or pi != pi:
        return "n/a"
    return "supported" if pi >= 0.9 else ("failed" if pi < 0.75 else "mixed")


def replication_block(r, res):
    rows = [
        ("P1 own-kickoff percentile π (32 decoys, genericness-corrected)", f"{f(r['pi'])} (rank {r['rank']} of 33; raw {f(r['pi_raw'])})", "≥ 0.90"),
        ("P1 own kickoff ranked first", "yes" if r["top1"] == 1 else "no", "top-1"),
        ("P1 within-regime percentile", f(r["pi_reg"]), "≥ 0.90"),
        ("P1b beats both neighbouring kickoffs", "yes" if r["adj_win"] == 1 else "no", "yes"),
        ("P1c displacement percentile (move vs previous last day)", f(r.get("pi_disp")), "≥ 0.85"),
        ("P1c jump toward the kickoff J_p", f(r.get("jump")), "> 0"),
        ("P1d goal-text percentile", f(r["pi_goal"]), "(kickoff vs goal text)"),
        ("raw centroid–kickoff cosine", f(r["S_own_raw"]), "–"),
        ("quench depth D_p (excess over decoys)", f(r["depth_ex"]), "–"),
        ("day-1 residual spread σ_p (rarefied)", f(r["spread"]), "–"),
        ("kickoff specificity S_text / S_count / S_emb", f"{f(r['S_text'])} / {f(r['S_count'])} / {f(r['S_emb'])}", "–"),
    ]
    out = ["| Statistic | Observed | Predicted |", "| --- | --- | --- |"] + [f"| {a} | {b} | {c} |" for a, b, c in rows]
    pj = res.get("projects_h31") or []
    if pj:
        kf = [x for x in pj if x["cls"] == "kickoff_frozen"]
        out.append("")
        out.append(f"**H31 projects here (read-only):** {len(pj)} (block, project) rows; kickoff-frozen {len(kf)}, of which named by the goal text or kickoff "
                   f"{sum(x['named'] for x in kf)}, pre-existing {sum(x['pre_existing'] for x in kf)}. "
                   f"Instant {sum(x['cls'] == 'instant' for x in pj)}, gradual {sum(x['cls'] == 'gradual' for x in pj)}, no consensus {sum(x['cls'] == 'none' for x in pj)}.")
    rem = res.get("remanence")
    if rem:
        k = rem["kick"]
        out.append(f"**Remanence (HH182):** kickoff excess {f(rem['first_ex'])} on day 1 → {f(rem['last_ex'])} on the last day ({rem['n_days']} days); "
                   f"exponential-plateau fit τ = {f(k['tau'], 1)} active days, A∞ = {f(k['A_inf'])} (ΔBIC vs constant {f(k['bic_const'] - k['bic_exp'], 1)}).")
    pl_ = res.get("plan")
    if pl_:
        out.append(f"**First concrete plan (HH181):** posted {f(pl_['min_after_kick'], 1)} min after the kickoff; centrality excess over "
                   f"{pl_['n_decoys']} day-1 decoy messages Δ_P = {f(pl_['delta_P'])} (percentile {f(pl_['pct_P'])}).")
    hm = res.get("human") or {}
    if hm.get("n"):
        out.append(f"**Human messages (HH180):** {hm['n']} mid-period messages scored; median re-quench excess {f(hm['median_delta'])}.")
    return "\n".join(out)


def write_period(p, r, res, t, cal):
    d = cal.filter(pl.col("goal_no") == p)
    days = d.height
    dates = f"{d['pt_date'].min()} → {d['pt_date'].max()}" if days else "–"
    folder = SUB / f"G{p:02d}"
    folder.mkdir(parents=True, exist_ok=True)
    rooms = "two rooms (#best, #rest)" if p in (35, 36, 37, 38, 39, 41, 42, 44) else ("#general" if r["regime"] == "I" else "rooms")
    extra = ""
    if p in (4, 24):
        extra = " The kickoff is a fallback (the day's longest human message), flagged."
    if MODE.get(p) == "F":
        extra += " Free-choice week: the kickoff names no shared object, so the card's prior was weakest here."
    native_txt = ""
    if p in NATIVE:
        native_txt = native_section(p)
    verdict, role = rep_verdict(r["pi"]), "replication"
    if p in NATIVE:
        verdict, role = NATIVE_VERDICT[p], "native"
    lines = [f"# H54 × G{p:02d}: {t.get(p, '')} ({dates})", "",
             f"**Verdict:** {verdict}", f"**Role:** {role}",
             f"**Period:** regime {r['regime']} · mode {MODE.get(p, '?')} · {r['n_agents']} agents with ≥ 3 day-1 statements · {rooms} · "
             f"{days} non-holdout active days. Day 1 = statements after the first kickoff message.{extra}", ""]
    if p in NATIVE:
        lines += native_txt.split("\n") + [""]
        lines += ["## Replication layer (templated, same as every eligible kickoff)", ""]
    else:
        lines += ["## Why this period",
                  "One of the 33 eligible kickoffs (layer 1, replication): the common estimators give one comparable point per kickoff. "
                  "The cross-kickoff tests (swap null, specificity, remanence, family susceptibility) are in [`../NE34/README.md`](../NE34/README.md).", "",
                  "## Prediction",
                  "*Templated, written 2026-10-04 in the card before any real-data run (card P1, P1b, P1c, P2).*",
                  "- The day-1 centroid identifies this period's kickoff: own percentile π ≥ 0.90 among 32 decoy kickoffs, ideally top-1; it beats both neighbouring kickoffs.",
                  "- Where a previous period is available, the day-1 move points at the kickoff (displacement percentile ≥ 0.85, jump > 0).",
                  "- Projects H31 found frozen at this kickoff are ones the goal text or kickoff names.",
                  "- **Per-period verdict rule:** supported if π ≥ 0.90; failed if π < 0.75; mixed otherwise.", "",
                  "## Result"]
    lines += [replication_block(r, res), "",
              f"Data: `data/processed/H54-kickoff-quench-target/G{p:02d}/results.json`; cross-kickoff tables `data/processed/H54-kickoff-quench-target/NE34/`.", ""]
    if p not in NATIVE:
        lines += ["## Scorecard (period-specific axes)",
                  f"- **C:** own kickoff vs 32 decoy kickoffs (swap null): π = {f(r['pi'])}.",
                  "- **G:** H31's frozen projects (where present) checked against the goal text and kickoff.", ""]
    lines += ["## Notes", "- 2026-10-04: folder written by `analysis/period_folders.py` after the round-1 run; the prediction above was dated in the card before the run."]
    (folder / "README.md").write_text("\n".join(lines) + "\n")


NATIVE_VERDICT = {51: "supported (N1 and N1b; the shared-kickoff replication fails here, as private goals predict)",
                  44: "mixed (N2 two domains failed; N2b vague room more spread supported)",
                  38: "failed (N3 room swap at chance; underpowered, disclosed)",
                  26: "mixed (day-1 target identified; the leader's goal announcement did not re-quench beyond decoys)"}


def native_section(p):
    n = json.loads((L.OUT / f"G{p:02d}" / "native.json").read_text())
    if p == 51:
        ne = n["NE38"]
        wk = ", ".join(f(w["swap_accuracy"]) for w in n["weekly"])
        rob = json.loads((L.OUT / "NE34" / "robustness.json").read_text())
        return "\n".join([
            "## Why this period",
            "The only period where every agent has its **own** written target (`agent_goal`, 33 rows; DQ6 roles, 7 rival pairs). If the kickoff text is the quench target, each agent should land on its own private goal, not on the shared kickoff. NE38 (07-29 16:51 UTC: a human reassigns Claude Opus 5 from a game-dev goal to a mathematics goal) is a single-agent re-quench inside it.",
            "",
            "## Prediction",
            "*Written 2026-10-04 in the card (N1, N1b) before running on this period.*",
            "- N1: role-swap pair accuracy ≥ 0.75 (pairs with different roles; permutation p < 0.01); centered alignment cos(v_i − m, ĝ_i − mean ĝ) > 0 on average; accuracy ≥ 0.65 in the last pre-tail week. Credence 0.75 / 0.6.",
            "- N1b: Opus 5's alignment with its new goal rises after 07-29 by more than the other agents' alignment with that goal (difference in differences > 0, day-bootstrap CI excluding 0). Credence 0.6.",
            "- Counts against: accuracy ≤ 0.6; no rise.",
            "",
            "## Result",
            "| Test | Observed | Null / reference | Verdict |",
            "| --- | --- | --- | --- |",
            f"| N1 role-swap accuracy (first day per agent) | {f(n['swap_accuracy'])} ({n['n_agents']} agents, {n['n_roles']} roles, {n['n_pairs']} pairs), p = {f(n['p_perm'], 4)} | synthetic no-private-field 0.47–0.50 | supported |",
            f"| own-goal percentile among other roles' goals | median {f(n['own_goal_pct_median'])}, top-1 {f(n['own_goal_top1'])} | 0.5 | supported |",
            f"| centered alignment | mean {f(n['centered_alignment_mean'])}, positive in {f(n['centered_alignment_pos_rate'])}, p = {f(n['centered_alignment_p'], 4)} | 0 | supported |",
            f"| own goal vs shared kickoff (excess over decoys) | own goal {f(n['excess_own_goal_median'])} vs shared kickoff {f(n['excess_shared_kickoff_median'])}; own wins for {f(n['own_goal_beats_kickoff_rate'])} of agents | – | agents land on their own target |",
            f"| persistence: weekly accuracy, weeks 1–9 of the head | {wk} | ≥ 0.65 in the last week | supported (no decay) |",
            f"| robustness (post hoc): chat only / style-residualized / both | {f(rob['R3_g51_chat']['swap_accuracy'])} / {f(rob['R3_g51_style']['swap_accuracy'])} / {f(rob['R3_g51_chat_style']['swap_accuracy'])} | – | holds |",
            f"| N1b NE38 DiD, alignment with the new goal | {f(ne['new']['did'])} [{f(ne['new']['ci95'][0])}, {f(ne['new']['ci95'][1])}] (Opus 5 +{f(ne['new']['opus5_change'])}, others +{f(ne['new']['control_change'])}) | 0 | supported |",
            f"| NE38 DiD, alignment with the old (game-dev) goal | {f(ne['old']['did'])} [{f(ne['old']['ci95'][0])}, {f(ne['old']['ci95'][1])}] | 0 | moves off the old target |",
            "",
            "The shared #51 kickoff itself is *not* identified by the day-1 centroid (replication π below): with private targets, the swarm centroid points at no one's goal. This is the replication failure the private-goal reading predicts.",
            "",
            "Figure: [`../../figures/summary_obs_b.pdf`](../../figures/summary_obs_b.pdf) (weekly accuracy; NE38 series).",
            "",
            "## Scorecard (period-specific axes)",
            "- **C:** role-swap permutation null and synthetic no-field band beaten at p = 0.0002.",
            "- **E:** NE38 is an intervention on one agent's field: predicted sign and a large size, CI excluding 0 (4 pre days, 8 post days).",
            "- **G:** ground truth = the assigned goal texts and DQ6 roles; agents' positions recover them.",
            "- **Caveat:** goal restatement is part of the mechanism. Excluding intentions (where agents restate their role) leaves the accuracy unchanged, but chat can quote the goal too."])
    if p in (44, 38):
        pr = n["per_room"]
        pred = ("*Written 2026-10-04 in the card (N2, N2b) before running on this period.*\n"
                "- N2: each agent is closer to its own room's kickoff (room-swap accuracy ≥ 0.8); the rooms separate along u = k̂_best − k̂_rest more than along other kickoff-difference axes (axis-swap percentile ≥ 0.95). Credence 0.65.\n"
                "- N2b (HH179 within one day): the vague #rest kickoff (agents choose their own goals; 43 words) leaves more spread than the specific #best kickoff (fine-tune a leader) and a lower own-kickoff depth. Credence 0.6.\n"
                "- Synthetic power (Amendment 1): room-swap accuracy ≥ 0.8 in only 48% of runs at a day-1 target share of 0.15.") if p == 44 else (
                "*Written 2026-10-04 in the card (N3) before running on this period.*\n"
                "- N3: room-swap accuracy ≥ 0.7 along the weaker contrast (room-kickoff cosine 0.60). Credence 0.4.\n"
                "- Synthetic power is low at this N (4 + 8) unless the room quench is deep.")
        why = ("The two rooms got different instructions on the same day: #best (4 agents) was told to fine-tune a Kimi leader; #rest (12 agents) to choose its own goals. Room kickoffs have cosine 0.39. HH183's two domains, and HH179 inside one period (same day, regime, roster)."
               if p == 44 else
               "The two rooms' kickoff texts differ (cosine 0.60), one of only two periods with room-specific instructions (the other is #44). Uses the shared `goal_fields` room vectors, which fix H01's #38 room swap.")
        verdict_n2 = "failed" if n["room_swap"]["accuracy"] < 0.6 else ("supported" if n["room_swap"]["accuracy"] >= (0.8 if p == 44 else 0.7) else "mixed")
        rows = [f"| room-swap accuracy | {f(n['room_swap']['accuracy'])} ({n['n_agents']} agents; mean margin {f(n['room_swap']['mean_margin'])}), permutation p = {f(n['room_swap_p_perm'])} | 0.5 | {verdict_n2} |",
                f"| separation along k̂_best − k̂_rest (Cohen d) | {f(n['axis_d'])}; percentile among {n['n_null_axes']} other kickoff-difference axes {f(n['axis_pct_abs'])} (signed {f(n['axis_pct_signed'])}) | ≥ 0.95 | {'failed' if n['axis_pct_abs'] < 0.95 else 'supported'} |"]
        for room, lab in (("2", "#best"), ("3", "#rest")):
            x = pr[room]
            rows.append(f"| {lab} (n = {x['n']}): spread σ (rarefied) / own-kickoff depth / alignment own vs other kickoff | {f(1 - x['q_rare'])} / {f(x['depth_own_room_kick'])} / {f(x['align_own'])} vs {f(x['align_other'])} | – | – |")
        if p == 44:
            rows.append(f"| N2b: σ_rest > σ_best and lower depth | σ {f(1 - pr['3']['q_rare'])} vs {f(1 - pr['2']['q_rare'])}; depth {f(pr['3']['depth_own_room_kick'])} vs {f(pr['2']['depth_own_room_kick'])} | – | supported |")
        reading = ("**Reading.** One quenched domain plus a disordered remainder, not two domains. #best sits tightly on its own kickoff (alignment 0.52 vs 0.07 with the other room's text). #rest is not on its own kickoff at all: its depth is below the decoy kickoffs, because a choose-your-own-goal instruction names no target, and it is more spread out. The room-swap test assumed two targets, so it fails by construction: #rest agents are, if anything, slightly closer to #best's text than to their own. HH179 holds inside the period. The room-size confound (4 vs 12) and the stronger #best models are caveats."
                   if p == 44 else
                   "**Reading.** As in #44, the #best room (4 agents) is tight and near its kickoff, while #rest (8 agents) aligns with neither room's text. The room-swap contrast is too weak (the two texts share most of their content) to separate the rooms. Post hoc: the #best room kickoff is the more specific one (S_text 0.40 vs −0.85), the same direction as #44's HH179 contrast. That makes 2/2 two-instruction periods, with room size and model strength as confounds.")
        return "\n".join(["## Why this period", why, "", "## Prediction", pred, "", "## Result",
                          "| Test | Observed | Null | Verdict |", "| --- | --- | --- | --- |"] + rows +
                         ["", reading, "", f"Figure: [`figures/rooms_axis.pdf`](figures/rooms_axis.pdf). Data: `data/processed/H54-kickoff-quench-target/G{p}/native.json`.", "",
                          "## Scorecard (period-specific axes)",
                          "- **C:** room-swap permutation and axis-swap nulls (not beaten).",
                          "- **D:** the within-period specificity contrast (HH179) is an unfitted prediction" + (" (supported)." if p == 44 else " (post hoc here)."),
                          "- **F:** underpowered at this N (synthetic S5)."])
    if p == 26:
        lines = ["## Why this period",
                 "The kickoff names a **decision procedure** (elect a leader who picks the week's goal), not an object. The elected leader's goal announcement (DQ6: result 19:35 UTC on 01-05; announcement by DeepSeek-V3.2 41 s later, found by rule, message id in `g26_leader.json`) is an agent-authored second target on day 1. That makes this period HH181 (a concrete plan completes the target) and HH180 (a re-quench) in their cleanest form.",
                 "", "## Prediction",
                 "*Written 2026-10-04 in the card (N4) before running on this period.*",
                 "- The day-1 centroid identifies the election kickoff (π ≥ 0.9).",
                 "- After the leader's announcement, the other agents' centroid moves toward its vector by more than toward decoy agent messages from the same day (excess > 0, decoy percentile ≥ 0.9).",
                 "- The frozen or instant projects after it are ones the announcement names. Credence 0.6.",
                 "", "## Result", "| Test | Observed | Null | Verdict |", "| --- | --- | --- | --- |",
                 f"| day-1 own-kickoff percentile | see replication table (π = 0.97, rank 2) | 0.5 | supported |"]
        for lab in ("0-60min", "60-180min", "rest_of_day1"):
            if lab in n:
                x = n[lab]
                lines.append(f"| move toward the announcement, {lab} | excess over {n['n_decoys']} decoys {f(x['excess'])}, decoy percentile {f(x['pct'])} | ≥ 0.9 | failed |")
        dd = "; ".join(f"day {x['day']}: kickoff {f(x['ex_kick'])}, leader {f(x['ex_leader'])}" for x in n["daily"])
        lines += [f"| projects named by the announcement | {n['announcement_projects']} artifacts named; none of the 8 H31 #26 projects (1 frozen, 6 instant) is named by it | – | failed |",
                  "", f"**Daily excess over decoys** (kickoff vs leader announcement as targets): {dd}.", "",
                  "**Reading.** Before the result, day-1 content sits very close to the election kickoff (excess 0.54, the highest of any segment). After the result, alignment with *both* the kickoff and the announcement collapses toward 0. The swarm leaves the election topic, but not toward the announcement's text as embedded. The six instant project waves later on day 1 are artifacts the announcement never names. An agent-authored plan did not act as a text quench target here; the operational target was whatever the agents then built. n = 1 period.",
                  "", "## Scorecard (period-specific axes)",
                  "- **E:** the election result is a dated step: the predicted re-quench toward the leader's text is absent.",
                  "- **G:** DQ6 ground truth (phases, winner) used for timing."]
        return "\n".join(lines)
    return ""


def write_ne34(res, rob):
    P1, P2, P3 = res["P1"], res["P2"], res["P3"]
    lines = ["# H54 × NE34: the kickoff as quench target, across all eligible goal changes",
             "",
             "**Verdict:** mixed (P1 supported: day-1 centroids identify their own kickoff; P2 mixed: frozen projects are the goal-text-named ones, enrichment 1.95 for any naming and 3.2 for goal-text naming; P3 failed: text specificity does not set the spread)",
             "**Role:** replication (cross-kickoff tests; exception (c), the transition is the object)",
             "**Period:** 33 eligible non-holdout kickoffs (#3–#51 minus holdout and #23), regimes I (22), II (3), III (8). Each period is compared in its own regime's whitened basis.",
             "",
             "## Why this",
             "A goal change replaces the field. Across many kickoffs a swap design is possible: each day-1 centroid can be scored against its own kickoff and 32 others. The specificity, remanence and family questions need many kickoffs.",
             "",
             "## Prediction",
             "*Written 2026-10-04 in the card (P1–P7, credences there) before any real-data run; Amendment 1 after the synthetic run.*",
             "",
             "## Result",
             "| Prediction | Observed | Verdict |",
             "| --- | --- | --- |",
             f"| P1 median π ≥ 0.9, top-1 ≥ 50%, Wilcoxon p < 0.001 | median {f(P1['median_pi'])}, top-1 {f(P1['top1'])} (within regime {f(P1['within_regime']['top1'])}), p = {P1['p_wilcoxon']:.1e} | **supported** |",
             f"| P1b beats both neighbouring kickoffs in ≥ 80% | {f(res['P1b']['adj_win_rate'])} | supported |",
             f"| P1c displacement median π ≥ 0.85; jump > 0 in ≥ 80% | {f(res['P1c']['median_pi_disp'])} (n = {res['P1c']['n']}); {f(res['P1c']['jump_pos_rate'])} (median jump {f(res['P1c']['median_jump'])}) | supported |",
             f"| P1d kickoff beats goal text in ≥ 60% | {f(res['P1d']['kick_beats_goal_cc'])} (goal text alone: median π {f(res['P1d']['median_pi_goal'])}, top-1 {f(res['P1d']['top1_goal'])}) | failed (equally good targets) |",
             f"| P2 precision ≥ 0.6, enrichment ≥ 2, Fisher p < 0.05 | precision {f(P2['named']['precision'])} (9/13), base {f(P2['named']['base_rate'])}, enrichment {f(P2['named']['enrichment'])}, p = {f(P2['named']['p_fisher'], 3)} (stratified permutation {f(P2['named']['p_perm_strat'], 3)}) | **mixed** (power ≈ 0.3–0.5) |",
             f"| P2, goal-text naming only (secondary) | precision {f(P2['named_goal']['precision'])}, base {f(P2['named_goal']['base_rate'])}, enrichment {f(P2['named_goal']['enrichment'])}, p = {P2['named_goal']['p_fisher']:.1e} (stratified {f(P2['named_goal']['p_perm_strat'], 3)}); leave-one-period-out min enrichment {f(rob['R5_p2_lopo']['min_enrichment'])} | strong |",
             f"| P2b ≥ half of frozen projects are carry-overs (rival R1) | pre-existing {f(P2['P2b_carry']['pre_existing_share'])} (1/13); carry-over 1/9 known | failed (R1 rejected) |",
             f"| P2c same pattern, own rule on deterministic labels | any naming: enrichment {f(P2['P2c_own_rule']['enrichment'])}, p = {f(P2['P2c_own_rule']['p_fisher'], 4)}; goal text: enrichment 4.40, p = 1e-5 | holds |",
             f"| P3 Spearman(S_text, σ) ≤ −0.35 | {f(P3['S_text']['spread_rho'])} (partial {f(P3['S_text']['spread_partial_rho'])}); S_count {f(P3['S_count']['spread_rho'])} | **failed** |",
             f"| P3, embedding distinctiveness S_emb (secondary) | spread {f(P3['S_emb']['spread_rho'])} (p = {f(P3['S_emb']['spread_p_one'], 3)}; partial {f(P3['S_emb']['spread_partial_rho'])}, p = {f(P3['S_emb']['spread_partial_p2'], 2)}); regime I {f(rob['R4_real']['regimeI_rho_Semb_spread'][0])}, regime III {f(rob['R4_real']['regimeIII_rho_Semb_spread'][0])} | weak, regime-III driven |",
             f"| P3b Spearman(S_text, depth) ≥ 0.35 | {f(P3['S_text']['depth_rho'])} | failed (S_emb +0.58 is partly mechanical) |",
             f"| P3c frozen share rises with S_text (per-project, n_named controlled) | coefficient {f(res['P3c']['logit']['coef'][2])} ± {f(res['P3c']['logit']['se'][2])}; per-period ρ {f(res['P3c']['period_frac_rho_S_text'])} (count-inflated) | failed |",
             f"| P4 human re-quench median Δ > 0 (HH180) | {f(res['P4']['median_delta'], 3)}, positive {f(res['P4']['pos_rate'])}, sign p = {f(res['P4']['p_sign'], 3)} (n = {res['P4']['n']}); vs specificity ρ {f(res['P4']['rho_spec'])}; vs receptive fraction ρ {f(res['P4']['rho_receptive'])} (75% of messages read by all within 30 min) | main part holds; moderators failed |",
             f"| P5 remanence (HH182): last-day excess > 0 in ≥ 70% | {f(res['P5']['last_ex_pos_rate'])} (n = {res['P5']['n_periods']}); plateau A∞ median {f(res['P5']['median_A_inf'])} from {f(res['P5']['median_A_1'])}; τ_K median {f(res['P5']['median_tau_K_days'])} active days | supported |",
             f"| P5 τ_K ≥ 3 τ_H | τ_K ≈ {f(res['P5']['median_tau_K_active_hours'], 1)} active h vs τ_H < 1 h (grid floor) | supported (rough) |",
             f"| P5 previous-kickoff remanence on day 1 | median {f(res['P5']['prev_kick_day1']['median'], 3)}, p = {f(res['P5']['prev_kick_day1']['p_wilcoxon'])} | failed (the new kickoff erases the old one) |",
             f"| P6 first plan central in ≥ 60% (HH181) | {f(res['P6']['pos_rate'])} (median percentile {f(res['P6']['median_pct'])}, p = {f(res['P6']['p_wilcoxon_pct'], 3)}); vs S_text ρ {f(res['P6']['rho_spec'])} (predicted < 0); plans name no frozen project | central: holds; moderator and naming: failed |",
             f"| P7 family susceptibility (HH184) | lab effect p = {f(res['P7']['chi']['p_perm_agent_lab'])}; agent split-half r = {f(res['P7']['chi']['split_half_r'])} (style-residualized {f(res['P7']['chi_style']['split_half_r'])}); individual moves toward the kickoff in {f(res['P7']['chi_pos_rate'])} of agent-kickoffs | failed |",
             "",
             "**Robustness (post hoc, `robustness.json`).** P1 without near-echo statements (cosine to own kickoff > 0.5 dropped, 9% of statements): median π 0.97, top-1 0.45. At > 0.3 dropped (28%): 0.91 / 0.30. With DQ5 style-residualized vectors: 1.0 / 0.52. Chat only: 1.0 / 0.52.",
             "",
             "**Post hoc moderator.** P1 fails exactly where the kickoff names no shared target: free-choice weeks #3 (π 0.0) and #16 (0.13), #51's private goals (0.25), #44's half-free week (0.47). Free-mode median π 0.81 vs 1.0 elsewhere (Mann–Whitney p = 0.02).",
             "",
             "Data: `data/processed/H54-kickoff-quench-target/NE34/` (`periods.parquet`, `S_kick.npy`, `projects` via `../projects.parquet`, `human.parquet`, `remanence.parquet`, `plans.parquet`, `chi.parquet`, `results.json`, `robustness.json`). Figures: `../../figures/summary_obs.pdf`, `remanence.pdf`, `synthetic_validation.pdf`.",
             "",
             "## Scorecard (period-specific axes)",
             "- **C:** swap null beaten (P1); base-rate and stratified nulls for naming (P2); decoy-message null for human re-quenches.",
             "- **D:** unfitted: displacement direction, neighbour decoys, frozen-project naming, remanence plateau.",
             "- **E:** each kickoff is a step; predicted target identified in 29/33 (π ≥ 0.75).",
             "- **H:** rival R1 (carry-over, inertia) and R0 rejected; R2 (genre) controlled by genericness correction; R3 (first plan) partly (plans are central but name no frozen project); R4 (family) shows no susceptibility differences.",
             "",
             "## Notes",
             "- 2026-10-04: written after the round-1 run by `analysis/period_folders.py`."]
    folder = SUB / "NE34"
    folder.mkdir(parents=True, exist_ok=True)
    (folder / "README.md").write_text("\n".join(lines) + "\n")


def main():
    res = json.loads((L.OUT / "NE34" / "results.json").read_text())
    rob = json.loads((L.OUT / "NE34" / "robustness.json").read_text())
    per = pl.read_parquet(L.OUT / "NE34" / "periods.parquet")
    t = titles()
    cal = L.calendar()
    for r in per.iter_rows(named=True):
        p = r["goal_no"]
        g = json.loads((L.OUT / f"G{p:02d}" / "results.json").read_text())
        write_period(p, r, g, t, cal)
    write_ne34(res, rob)
    print(f"wrote {per.height} period folders + NE34")


if __name__ == "__main__":
    main()
