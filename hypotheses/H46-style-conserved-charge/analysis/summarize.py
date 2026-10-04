"""H46: combine class tests, NE41, KW information, native tests and replication into verdicts and README text.

Holm across the six NE classes (goal, rooms, nudger, roster, scaffold, NE41 forced), separately for style and
content. Verdict rules from the card (with Amendment 1). Writes period_results.json (consumed by
write_period_cards.py --phase results) and summary_tables.md (pasted into the card).
"""
from __future__ import annotations
import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import h46lib as L  # noqa: E402

D = L.DATA
CLS_FOLDER = {"goal": "NE34", "rooms": "NE42", "nudger": "NE43", "roster": "NE32", "scaffold": "NE14"}


def f3(x):
    return "–" if x is None or (isinstance(x, float) and not np.isfinite(x)) else f"{x:.3f}"


def f2(x):
    return "–" if x is None or (isinstance(x, float) and not np.isfinite(x)) else f"{x:.2f}"


def pfmt(p):
    if p is None or (isinstance(p, float) and not np.isfinite(p)):
        return "–"
    return "< 0.001" if p < 0.001 else f"{p:.3f}"


def verdict_amended(tc, ts, pc, ps, margin):
    """Card rule + Amendment 1: content moves, style does not, ratio rule holds, but the CI upper bound exceeds the
    margin -> 'conserved (equivalence not established)' (reported as verdict 'mixed' in the overview)."""
    v = L.verdict(tc, ts, pc, ps, margin)
    if v == "partial" and L.moves(tc, pc) and not L.moves(ts, ps) and (ts["T"] - 0.5) <= (tc["T"] - 0.5) / 3:
        return "conserved (equivalence not established)"
    return v


def main():
    cons = json.loads((D / "conservation.json").read_text())
    ne41 = json.loads((D / "NE41/ne41.json").read_text())
    kw = json.loads((D / "kw_info.json").read_text())
    rep = json.loads((D / "replication.json").read_text())
    nat = {g: json.loads((D / g / "native.json").read_text()) for g in ("G51", "G12", "G44")}
    T = cons["tests"]
    # Holm over six classes
    classes = list(CLS_FOLDER)
    pc = [T[c]["content"]["p_rand"] for c in classes] + [ne41["dedup"]["content"]["forced"]["p_rand"]]
    ps = [T[c]["style"]["p_rand"] for c in classes] + [ne41["dedup"]["style"]["forced"]["p_rand"]]
    pc_h, ps_h = L.holm(pc), L.holm(ps)
    verdicts = {}
    for k, c in enumerate(classes):
        verdicts[c] = verdict_amended(T[c]["content"], T[c]["style"], pc_h[k], ps_h[k], 0.10)
    f_c = dict(ne41["dedup"]["content"]["forced"], p_wilcoxon=np.nan)
    f_s = dict(ne41["dedup"]["style"]["forced"], p_wilcoxon=np.nan)
    verdicts["NE41"] = verdict_amended(f_c, f_s, pc_h[-1], ps_h[-1], 0.05)
    out = {"verdicts": verdicts, "holm_content": dict(zip(classes + ["NE41"], pc_h)),
           "holm_style": dict(zip(classes + ["NE41"], ps_h))}
    (D / "summary.json").write_text(json.dumps(out, indent=1, default=float))
    print(json.dumps(out, indent=1, default=float))
    ph = json.loads((D / "posthoc.json").read_text())
    pr = {}
    # ---------------- NE class folders
    vmap = {"broken": "failed", "partial": "mixed", "uninformative": "n/a", "conserved": "supported",
            "conserved (equivalence not established)": "mixed"}
    for k, c in enumerate(classes):
        t = T[c]
        f = cons["fingerprint"][c]
        lines = ["*Run 2026-10-04 06:05 UTC on non-holdout data; `analysis/conservation.py` → "
                 "`data/processed/H46-style-conserved-charge/conservation.json`, `conservation_rows.parquet`, `fingerprint.parquet`.*", "",
                 "| Channel | T (mean percentile vs own day-to-day) | 95% CI (boundaries, then agents) | randomization p | boundary Wilcoxon p | median z |",
                 "| --- | --- | --- | --- | --- | --- |"]
        for ch, nm in (("style", "style, type-controlled (primary)"), ("style_raw", "style, raw 20 features"),
                       ("content", "content, style-residualized (primary)"), ("content_white", "content, raw whitened"),
                       ("style_dm", "style, day field removed"), ("content_dm", "content, day field removed")):
            v = t[ch]
            lines.append(f"| {nm} | {f3(v['T'])} | [{f3(v['lo'])}, {f3(v['hi'])}] | {pfmt(v['p_rand'])} | {pfmt(v['p_wilcoxon'])} | {f2(v['median_z'])} |")
        lines += ["", f"- **Agent × boundary rows:** {t['style']['n']} over {t['style']['n_boundaries']} boundaries.",
                  f"- **Holm (six classes):** content p = {pfmt(pc_h[k])}, style p = {pfmt(ps_h[k])}.",
                  f"- **Pre-registered class verdict:** **{verdicts[c]}**."]
        fa, fc = f.get("style|all", {}), f.get("content|all", {})
        if fa:
            lines.append(f"- **Fingerprint (train before, test after; day-demeaned):** style {f2(fa['cross'])} vs content "
                         f"{f2(fc.get('cross'))} at chance {f2(fa['chance'])} (ceilings {f2(fa.get('ceiling'))} / {f2(fc.get('ceiling'))}); "
                         f"style ≥ 3× chance at {fa['share_ge_3x_chance']:.0%} of boundaries; style > content at "
                         f"{f.get('share_style_gt_content', float('nan')):.0%}. Anthropic-only: style {f2(f.get('style|anthropic', {}).get('cross'))} vs "
                         f"content {f2(f.get('content|anthropic', {}).get('cross'))} at chance {f2(f.get('style|anthropic', {}).get('chance'))}.")
        pb_s, pb_c = t["style"]["per_boundary"], t["content"]["per_boundary"]
        lines.append("- **Per boundary (mean percentile, style / content):** " +
                     "; ".join(f"{b} {pb_s[b]:.2f} / {pb_c.get(b, float('nan')):.2f}" for b in pb_s))
        if c == "goal":
            p1 = ph["PH1"]
            lines += ["- **Post hoc (PH1; after seeing the result):** not a kickoff transient (second post day: style "
                      f"{f3(p1['kickoff_skip']['style']['T'])} [{f3(p1['kickoff_skip']['style']['lo'])}, {f3(p1['kickoff_skip']['style']['hi'])}], content {f3(p1['kickoff_skip']['content']['T'])}), "
                      f"not a wrap-up transient (second-to-last pre day: style {f3(p1['wrapup_skip']['style']['T'])}), and not the weekend gap "
                      f"(placebo pairs ≥ 2 calendar days apart: style {f3(p1['gap_matched']['style']['T'])}, content {f3(p1['gap_matched']['content']['T'])}; 47 rows).",
                      "- **Post hoc (PH2):** the excess style displacement sits in content-adjacent features: " +
                      ", ".join(f"{n} {x:.0%}" for n, x in ph["PH2"]["goal_switch"]["top"]) + " of the excess."]
            g14 = T["NE14_only"]
        if c == "scaffold":
            g14 = T["NE14_only"]
            lines.append(f"- **NE14 alone (regime II→III, 11 agents, descriptive):** style {f3(g14['style']['T'])} (p {pfmt(g14['style']['p_rand'])}), "
                         f"raw {f3(g14['style_raw']['T'])}, content (raw bge) {f3(g14['content']['T'])} (p {pfmt(g14['content']['p_rand'])}).")
        if c == "goal":
            gs = T["goal_skip"]
            lines.append(f"- **Sensitivity, transitions skipping one held-out goal (8→10, 21→23, 42→44):** style {f3(gs['style']['T'])}, content {f3(gs['content']['T'])}.")
        pr[CLS_FOLDER[c]] = {"verdict": vmap[verdicts[c]], "result_md": "\n".join(lines),
                             "scorecard_md": scorecard_ne(c, verdicts[c])}
    # ---------------- NE41
    n41 = ne41["dedup"]
    lines = ["*Run 2026-10-04 06:08 UTC; `analysis/ne41.py` → `data/processed/H46-style-conserved-charge/NE41/ne41.json`.*", "",
             f"Pairs: {n41['n_pairs']['forced']:,} forced, {n41['n_pairs']['voluntary']:,} voluntary, {n41['n_pairs']['within']:,} within "
             f"(median gaps {n41['median_gap_s']['forced']:.0f} s / {n41['median_gap_s']['voluntary']:.0f} s / {n41['median_gap_s']['within']:.0f} s).", "",
             "| Channel | forced: T [95% CI] | voluntary: T [95% CI] | forced, gap-unmatched |", "| --- | --- | --- | --- |"]
    for ch, nm in (("style", "style, type-controlled (primary)"), ("style_raw", "style, raw"),
                   ("content", "content, style-residualized (primary)"), ("content_white", "content, raw whitened")):
        a, b = n41[ch]["forced"], n41[ch]["voluntary"]
        lines.append(f"| {nm} | {f3(a['T'])} [{f3(a['lo'])}, {f3(a['hi'])}] | {f3(b['T'])} [{f3(b['lo'])}, {f3(b['hi'])}] | {f3(a['T_naive_unmatched'])} |")
    am = ne41["all_messages"]
    pus, puc = n41["style"]["forced"]["per_unit"], n41["content"]["forced"]["per_unit"]
    lines += ["", f"- **Per unit (forced, ≥ 30 pairs):** style T > ½ in {sum(v['T'] > 0.5 for v in pus.values())}/{len(pus)} units "
              f"(regime III two-room periods 0.49–0.64; late #51, 51h–51l, 0.45–0.57); content T > ½ in {sum(v['T'] > 0.5 for v in puc.values())}/{len(puc)} "
              "(content moves in #36–#42, 0.53–0.61, but not in #51, 0.42–0.54, which holds most pairs)."]
    lines += [f"- **All messages (no self-repeat removal):** forced style {f3(am['style']['forced']['T'])}, content {f3(am['content']['forced']['T'])}.",
              f"- **Holm (six classes):** style p = {pfmt(ps_h[-1])}, content p = {pfmt(pc_h[-1])}; content's agent-cluster CI includes ½, so by Amendment 2 content does not move.",
              f"- **Pre-registered verdict:** **{verdicts['NE41']}**: style moves across a forced erasure (falsifier T_s ≥ 0.55 hit), content does not.",
              "- **Post hoc (PH3): style drifts inside a context and resets at erasure.** Excess squared distance of a message's style to the agent's unit mean, by its position since the last reset, within segments of ≥ 7 messages: " +
              ", ".join(f"pos {b} {ph['PH3']['style']['within_long_segments'][b]['mean_excess']:+.2f} (± {ph['PH3']['style']['within_long_segments'][b]['se']:.2f})" for b in ("1", "2", "3", "4-6", "7+")) +
              ". Content shows only a small first-message dip (" + f"{ph['PH3']['content']['within_long_segments']['1']['mean_excess']:+.3f}" + " in 1 − cos).",
              "- **Post hoc (PH2):** the excess sits in conversational-register features: " +
              ", ".join(f"{n} {x:.0%}" for n, x in ph["PH2"]["ne41_forced"]["top"]) + "."]
    pr["NE41"] = {"verdict": "failed", "result_md": "\n".join(lines),
                  "scorecard_md": "- **E (interventional):** 1. Exogenously timed erasures are the cleanest intervention here; the prediction (style conserved) failed, which is informative: style is partly held by the context window.\n- **F:** 1 (gap-matched estimator validated on an OU recency confound; Amendment 2).\n- **B:** in-context drift (PH3) is a Markov-order statement: style depends on context length, not only on the agent."}
    # ---------------- natives
    pr["G51"] = native_g51(nat["G51"], ph, rep.get("G51"))
    pr["G12"] = native_g12(nat["G12"], rep.get("G12"))
    pr["G44"] = native_g44(nat["G44"], rep.get("G44"))
    # ---------------- replication folders
    for g, r in rep.items():
        if g in pr:
            continue
        pr[g] = replication_md(g, r)
    (D / "period_results.json").write_text(json.dumps(pr, indent=1, default=float))
    print("period results:", len(pr))


def scorecard_ne(c, v):
    if c in ("roster", "scaffold"):
        return "- **E:** 0 for this class: content does not move either, so the boundary is not a perturbation of the state and conservation cannot be tested (R3).\n- **C:** the estimator holds size here (style and content both at ½), consistent with the synthetic null."
    if c == "goal":
        return "- **E (interventional):** 1. The goal quench moves content strongly; style moves too, beyond its day-to-day band (prediction failed), though by much less in z units (0.37 vs 1.82).\n- **D:** the fingerprint (an unfitted statistic) survives: style identifies agents across goal switches better than content.\n- **H:** R2 (task leakage via length/code/links) does not explain the shift; the excess sits in digit, uppercase and colon shares (content-adjacent features)."
    if c == "nudger":
        return "- **E:** 1. Content moves after the nudger switch-off, style does not; one boundary, so equivalence cannot be established (Amendment 1)."
    return "- **E:** 1. Content moves weakly (goal-confounded merge and split; #focus room); style does not move after Holm but exceeds a third of content's excess (partial)."


def replication_md(g, r):
    lines = ["*Run 2026-10-04 06:10 UTC (`analysis/replication.py` → `data/processed/H46-style-conserved-charge/replication.json`). Templated replication point.*", "",
             f"- **Sample:** {r['n_agents']} agents, {r['n_days']} days, {r['n_agent_days']} eligible agent-days (≥ 3 deduplicated chat messages).",
             f"- **Agent share of day-demeaned variance:** style {f2(r.get('r2_agent_style'))}, content {f2(r.get('r2_agent_content'))}."]
    if "split_style" in r:
        lines.append(f"- **Split-half fingerprint within the period:** style {f2(r['split_style'])}, content {f2(r['split_content'])}, chance {f2(r['split_chance'])}.")
    e = r.get("entry")
    if e and "style" in e:
        lines.append(f"- **Entry boundary {e['label']}** ({e['flag']}, {e['n_agents']} agents): style T_s = {f3(e['style']['T'])} "
                     f"[{f3(e['style']['lo'])}, {f3(e['style']['hi'])}] (raw {f3(e['style_raw']['T'])}); content T_c = {f3(e['content']['T'])} "
                     f"[{f3(e['content']['lo'])}, {f3(e['content']['hi'])}].")
        if "fp_style" in e:
            lines.append(f"- **Cross-boundary fingerprint:** style {f2(e['fp_style']['cross'])} vs content {f2(e['fp_content']['cross'])} at chance {f2(e['fp_style']['chance'])}.")
    else:
        lines.append("- **Entry boundary:** none (see prediction); verdict descriptive.")
    if "kw" in r:
        kw = r["kw"]
        lines.append(f"- **KW (next-day output, within agent):** style p = {pfmt(kw['style']['p'])}, content p = {pfmt(kw['content']['p'])} "
                     "(small periods are underpowered and their raw CV R² is inflated; Amendment 3).")
    lines.append(f"- **Templated verdict:** {r['verdict']}.")
    return {"verdict": r["verdict"], "result_md": "\n".join(lines),
            "scorecard_md": "- Replication point only (layer 1): informs C (beats the placebo band or not) and I (consistency across periods) in the main card."}


def native_g51(n, ph, rep):
    s, c = n["summary_style"], n["summary_content"]
    A = n["agents"]
    rows = ["| Agent (role, group) | style pct | style pct, pre-#45 placebo only | content pct | style ratio to median placebo |", "| --- | --- | --- | --- | --- |"]
    roster = {int(a): a for a in A}
    for a, v in sorted(A.items(), key=lambda kv: -kv[1]["pct_style"]):
        rows.append(f"| {a} ({v['role']}, {v['group']}) | {f2(v['pct_style'])} | {f2(v['pct_style_pre45'])} | {f2(v['pct_content'])} | {f2(v['ratio_style'])} |")
    ne = n["NE38"]
    lines = ["*Run 2026-10-04 06:09 UTC (`analysis/native.py` → `data/processed/H46-style-conserved-charge/G51/native.json`).*", "",
             "**Personas (P9).** Block displacement into #51 (last ≤ 3 eligible days before #45 → first ≤ 3 days of #51) against each agent's own matched-gap (≥ 21 days) placebo block pairs. Agents are listed by roster code with their DQ6 role.", ""] + rows + ["",
             f"- **Style:** mean percentile {f3(s['mean_all'])} over {s['n']} incumbents (randomization p {pfmt(s['p_rand_mean_gt_half'])}); {s['share_ge_0.9']:.0%} at ≥ 0.9. "
             f"**Prankster: {f2(s['prankster'][0])}** (falsifier ≥ 0.95 hit). Media vs other: Mann–Whitney p {pfmt(s['media_vs_other_MW_p'])} (media {', '.join(f2(x) for x in s['media'])}).",
             f"- **Content:** mean percentile {f3(c['mean_all'])} (p {pfmt(c['p_rand_mean_gt_half'])}).",
             f"- **Post hoc (PH5):** the movers are mostly non-Anthropic (Google, OpenAI): non-Anthropic median {np.median(ph['PH5']['other']):.2f} vs Anthropic {np.median(ph['PH5']['anthropic']):.2f} (Mann–Whitney p {pfmt(ph['PH5']['MW_p_other_gt_anthropic'])}). Role group does not explain the shift; lab does (a lead, not a test).",
             "",
             f"**NE38 (P10), Claude Opus 5 reassigned 07-29.** Day level: style {f2(ne['day_pct_style'])}, content {f2(ne['day_pct_content'])} against {ne['n_placebo_day']} own transitions (prediction met: content ≥ 0.9, style < 0.9). "
             f"3-day blocks: style {f2(ne['block_pct_style'])}, content {f2(ne['block_pct_content'])} against {ne['n_placebo_block']} sliding blocks (style also moves). "
             "Caveat: the pre-block is the agent's first three days in the village (07-24 → 07-28), so a newcomer transient is confounded with the role switch.",
             "",
             "**Verdict:** failed for H46 as stated (an assigned persona, the Prankster, moved style beyond every placebo; so did two media roles and two non-persona Gemini agents)."]
    if rep:
        lines += ["", "**Replication estimator in #51:** " + replication_md("G51", rep)["result_md"].split("\n", 2)[2].replace("\n", " ")]
    return {"verdict": "failed", "result_md": "\n".join(lines),
            "scorecard_md": "- **E:** 1 (persona onset and NE38 used as interventions; prediction failed for the Prankster).\n- **G:** DQ6 role labels as ground truth; the shift tracks lab more than role (post hoc)."}


def native_g12(n, rep):
    lines = ["*Run 2026-10-04 06:09 UTC (`analysis/native.py` → `data/processed/H46-style-conserved-charge/G12/native.json`). 7 agents, 10 debates, "
             f"{n['n_sets_ge3']} agent × debate sets with ≥ 3 messages.*", "",
             "| Test | Style (type-controlled) | Style (raw) | Content | Prediction | Verdict |", "| --- | --- | --- | --- | --- | --- |",
             f"| (a) fingerprint debates 1–5 → 6–10 (chance {f2(n['fp_style']['chance'])}) | {f2(n['fp_style']['acc'])} | {f2(n['fp_style_raw']['acc'])} | {f2(n['fp_content']['acc'])} | style ≥ 3× chance and > content | half (≥ 3× chance; not > content) |",
             f"| (b) debate switch vs within-debate halves, T | {f3(n['switch_style']['T'])} | {f3(n['switch_style_raw']['T'])} | {f3(n['switch_content']['T'])} | T_c > T_s, T_s ≤ 0.6 | uninformative (nothing moves) |",
             f"| (c) agent 9 judge vs debater, LOO accuracy (perm. p) | {f2(n['role9_style']['acc'])} ({pfmt(n['role9_style']['p_perm'])}) | {f2(n['role9_style_raw']['acc'])} ({pfmt(n['role9_style_raw']['p_perm'])}) | {f2(n['role9_content']['acc'])} ({pfmt(n['role9_content']['p_perm'])}) | content ≥ 0.8, style ≤ 0.7 | **failed** (reversed) |",
             "| (c′) one-time judges: judge window vs own debater band (pct) | " + ", ".join(f2(v["pct"]) for v in n["onetime_judges_style"].values()) + " | " +
             ", ".join(f2(v["pct"]) for v in n["onetime_judges_style_raw"].values()) + " | " + ", ".join(f2(v["pct"]) for v in n["onetime_judges_content"].values()) + " | style < 0.9 | **failed** (3/4 at 1.0) |",
             f"| (d) assigned side, permutation p | {pfmt(n['side_style']['p_perm'])} | {pfmt(n['side_style_raw']['p_perm'])} | {pfmt(n['side_content']['p_perm'])} | style p ≥ 0.05 | passed |",
             "", "**Verdict:** failed. Assigned sides leave style alone, but an assigned *register* (judging) moves style and not content: judges write differently while talking about the same debate."]
    if rep:
        lines += ["", "**Replication estimator in #12:** " + replication_md("G12", rep)["result_md"].split("\n", 2)[2].replace("\n", " ")]
    return {"verdict": "failed", "result_md": "\n".join(lines),
            "scorecard_md": "- **G:** DQ6 team and judge labels as ground truth.\n- **H:** R1 (style follows assigned register) beats H46 on the judge test."}


def native_g44(n, rep):
    s, sr, c = n["style"], n["style_raw"], n["content"]
    lines = ["*Run 2026-10-04 06:09 UTC (`analysis/native.py` → `data/processed/H46-style-conserved-charge/G44/native.json`). "
             f"{n['n_leader_msgs']} deduplicated leader messages ({n['n_leader_final']} from the final weights); 17 reference agents (#38–#44).*", "",
             f"- **Style (type-controlled):** nearest {', '.join(s['all']['nearest'])}; Kimi K2.6 rank {s['all']['rank_kimi_k2.6']} (final weights: rank {s['final']['rank_kimi_k2.6']}).",
             f"- **Style (raw):** nearest {', '.join(sr['all']['nearest'])}; Kimi K2.6 rank {sr['all']['rank_kimi_k2.6']} (final: {sr['final']['rank_kimi_k2.6']}).",
             f"- **Content:** nearest {', '.join(c['all']['nearest'])}; Kimi K2.6 rank {c['all']['rank_kimi_k2.6']}.",
             f"- **Power:** a random {s['power_selfrank']['n_msgs']}-message sample of a known agent ranks its own centroid first {s['power_selfrank']['share_rank1']:.0%} of the time by style (≤ 2: {s['power_selfrank']['share_rank_le2']:.0%}); content {c['power_selfrank']['share_rank1']:.0%}.",
             "- **Verdict:** descriptive. The leader's style sits next to its base model (rank 2 type-controlled, rank 1 raw), as a substrate style would, but its content is also second-nearest to Kimi, so the prediction that content is *not* Kimi-specific is not met. With 16–20 messages, rank 1–2 is about what a genuine sample of a known agent achieves."]
    if rep:
        lines += ["", "**Replication estimator in #44:** " + replication_md("G44", rep)["result_md"].split("\n", 2)[2].replace("\n", " ")]
    return {"verdict": "descriptive", "result_md": "\n".join(lines),
            "scorecard_md": "- **G:** the fine-tuned leader's base model is known ground truth; style points to it (weakly)."}


if __name__ == "__main__":
    main()
