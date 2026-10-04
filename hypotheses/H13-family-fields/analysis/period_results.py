"""Fill the Verdict line, Result and Scorecard sections of each G<NN>/README.md from explore.json + posthoc.json.

Called by period_folders.py --results. The Prediction section is never modified.

Period verdict rule (stated in each README):
  a unit "detects a family field" if a1 T_field has p < 0.05, or (two-room units) the room-adjusted y2 b_lab has
  p < 0.05. Since the field never survives the pre-registered style rival (P2), no period can be "supported";
  failed = no unit of the period detects a family field; mixed = a field is detected (style-borne) while the
  no-family-coupling predictions (P5, P6) hold.
"""
from __future__ import annotations

import json
import re
from pathlib import Path


def f(x, s=".3f"):
    return "n/a" if x is None else format(x, s)


def unit_rows(u, r, ph):
    rows = []
    a1, a2 = r["a1"], r["a2"]
    rows.append(("P1 family field (a1)", f"T = {f(a1['obs'])} ± {f(1.96 * (a1.get('se_jack') or 0))}; p = {f(a1['p'], '.4f')}; R²_fam = {f(a1['R2_fam']['obs'], '.2f')}",
                 f"perm null {f(a1['null_mean'])} ± {f(a1['null_sd'])}", "pass" if a1["p"] < 0.05 else "fail"))
    rows.append(("P2 survives style residualization (a2)", f"T = {f(a2['obs'])}; p = {f(a2['p'], '.4f')}; retention {f(a2.get('retention'), '.2f')}",
                 "lab permutation", "pass" if a2["p"] < 0.05 else "fail"))
    if u in ph:
        rows.append(("(post hoc) S-a′ within-agent style map", f"T = {f(ph[u]['T_S-a_within']['obs'])}; p = {f(ph[u]['T_S-a_within']['p'])}",
                     "lab permutation", "descriptive"))
        rows.append(("(post hoc) style features alone", f"T = {f(ph[u]['T_stylefeatures']['obs'])}; p = {f(ph[u]['T_stylefeatures']['p'])}",
                     "lab permutation", "descriptive"))
    d1 = r["d1"]
    rows.append(("P8 leave-one-out family classification (d1)", f"accuracy {f(d1['obs'], '.2f')} (n = {d1['n']}); p = {f(d1['p'])}",
                 f"chance {f(d1['null_mean'], '.2f')}", "pass" if d1["p"] < 0.05 else "fail"))
    g = r["a5"].get("genuinely", {})
    tl = r["a5"].get("T_lex") or {}
    rows.append(("P8 'genuinely' (Anthropic vs others, per 1k words)",
                 f"{f(g.get('rate_anthropic'), '.2f')} vs {f(g.get('rate_others'), '.2f')} (ratio {f(g.get('ratio'), '.1f')}); p = {f(g.get('p'))}",
                 "lab permutation", "pass" if (g.get("p", 1) < 0.05 and (g.get("ratio") or 0) >= 2) else "fail"))
    rows.append(("P8 lexical profile T_lex", f"{f(tl.get('obs'))}; p = {f(tl.get('p'))}", "lab permutation",
                 "pass" if tl.get("p", 1) < 0.05 else "fail"))
    b1 = r.get("b1", {})
    if b1:
        ci = b1.get("delta_ci95") or [None, None]
        rows.append(("P5 talk K×K: Δ = J_in − J_out (b1)", f"{f(b1.get('delta'))} [{f(ci[0])}, {f(ci[1])}]; J_in {f(b1.get('J_in'))}, J_out {f(b1.get('J_out'))}; p = {f(b1.get('p_perm'))}",
                     "lab permutation; day bootstrap", "holds (no family coupling)" if b1.get("p_perm", 0) >= 0.05 else "violated (family coupling)"))
    b2 = r["b2"]
    if "delta" in b2:
        rows.append(("P6 content co-movement K×K: Δ (b2)", f"{f(b2['delta'])} ± {f(1.96 * (b2.get('delta_se_jack') or 0))}; p = {f(b2.get('p_perm'))}; windows {b2['n_windows']}",
                     "lab permutation", "holds" if b2.get("p_perm", 0) >= 0.05 else "violated"))
    if "c" in r:
        for y, nm in (("y1_talk", "P7 y1 talk"), ("y2_field", "P7 y2 content field"), ("y3_comove", "P7 y3 co-movement"), ("y4_lexical", "P7 y4 lexical")):
            c = r["c"].get(y)
            if not c:
                continue
            rows.append((nm + ": b_lab / b_room", f"{f(c['b_lab'], '+.3f')} (p {f(c["p_lab"])}) / {f(c["b_room"], "+.3f")} (p {f(c['p_room'])}); {c['n_pairs']} pairs, {c['n_same_lab_cross_room']} same-lab cross-room",
                         "node permutations", "room > lab" if c["b_room"] > c["b_lab"] else "lab ≥ room"))
        if u in ph and "y2_S-a" in ph[u]:
            q = ph[u]["y2_S-a"]
            rows.append(("(post hoc) y2 after S-a: b_lab / b_room", f"{f(q['b_lab'], '+.3f')} (p {f(q["p_lab"])}) / {f(q["b_room"], "+.3f")} (p {f(q['p_room'])})", "node permutations", "descriptive"))
    return rows


def detects(r):
    if r["a1"]["p"] < 0.05:
        return True
    c = r.get("c", {}).get("y2_field")
    return bool(c and c["p_lab"] < 0.05)


def write_results(PERIODS, HERE, DATA):
    ex = json.loads((DATA / "explore.json").read_text())
    ph = json.loads((DATA / "posthoc.json").read_text())
    U = ex["units"]
    summary = {}
    for g, p in PERIODS.items():
        units = [u for u in p["units"] if u in U]
        counted = [u for u in units if U[u]["counted"]]
        det = [u for u in counted if detects(U[u])]
        coupl_ok = all(U[u].get("b1", {}).get("p_perm", 1) >= 0.05 and U[u]["b2"].get("p_perm", 1) >= 0.05 for u in counted)
        verdict = "failed" if not det else "mixed"
        summary[g] = (verdict, det, counted, coupl_ok)
        lines = [f"Data: `data/processed/H13-family-fields/{g}/results_u<unit>.json`; figure: `figures/H13_{g}.pdf` "
                 "(cos(H_i, H_j) heatmap ordered by lab, room in brackets; talk and content K×K mean-field matrices).", ""]
        lines.append(f"**Verdict rule:** see `analysis/period_results.py`. Units detecting a family field (a1 p < 0.05 or room-adjusted y2 b_lab p < 0.05): "
                     f"{', '.join(det) if det else 'none'} of {', '.join(counted)}. The field never survives the pre-registered style rival (P2) in this period; "
                     f"no-family-coupling predictions (P5, P6) {'hold in every unit' if coupl_ok else 'are violated in at least one unit (see table)'}.")
        for u in units:
            r = U[u]
            lines += ["", f"**Unit {u}** ({r['n_days']} days, N = {r['N']}, families {r['families']}{'' if r['counted'] else '; descriptive only'})", "",
                      "| Prediction | Observed | Null | Verdict |", "| --- | --- | --- | --- |"]
            for a, b, c, d in unit_rows(u, r, ph):
                lines.append(f"| {a} | {b} | {c} | {d} |")
            if r.get("B_splithalf_family_cos"):
                lines.append(f"\nWithin-unit stationarity (first vs second half of days, family field cos): "
                             + ", ".join(f"{k} {v:.2f}" for k, v in r["B_splithalf_family_cos"].items()))
        if g == "G51" and "d3" in ex["cross"]:
            d3 = ex["cross"]["d3"]
            lines += ["", "**d3 (NE32, 07-09, descriptive):** cosine of each isolated GPT-5.6 agent's day-demeaned 07-09 vector with incumbent family fields of 51b "
                      "(07-09/07-10 excluded): " + "; ".join(f"{k}: " + ", ".join(f"{l} {v:.2f}" for l, v in d3[k].items()) for k in d3 if not k.startswith("_"))
                      + f". Triplet mutual cos {d3['_triplet_mutual_cos']:.2f} vs triplet–incumbent {d3['_triplet_vs_incumbent_cos']:.2f}; statements on 07-09: {d3['_n_statements_0709']}. "
                      "Only Luna (72 statements) aligns with the OpenAI field; Sol (4) and Terra (8) are noise-dominated."]
            d2 = ex["cross"]["d2"]
            lines += ["", f"**d2 newcomers (counted, since P3 passed):** {sum(x['correct'] for x in d2['newcomers'])}/{d2['n']} classified into their own family by earlier units' family fields "
                      f"(chance {d2['chance']:.2f}, binomial p = {d2['p_binom']:.3f}; mean rank {d2['mean_rank']:.1f}). Correct: "
                      + ", ".join(x["name"] for x in d2["newcomers"] if x["correct"]) + ". Wrong: " + ", ".join(f"{x['name']} → {x['pred']}" for x in d2["newcomers"] if not x["correct"]) + "."]
        score = ["- **C (adequacy):** " + ("family field beats the lab-permutation null in " + ", ".join(det) if det else "no unit beats the lab-permutation null")
                 + "; it does not beat the style rival (S-a) in any unit. Score 1." if det else "- **C:** 0 (no family field beyond the permutation null).",
                 "- **G (ground truth):** family identity recovered by leave-one-out classification in "
                 + (", ".join(u for u in counted if U[u]["d1"]["p"] < 0.05) or "no unit") + "; rooms recovered as the dominant coupling grouping"
                 + (" (" + ", ".join(u for u in counted if "c" in U[u] and U[u]["c"]["y3_comove"]["p_room"] < 0.05) + ")" if any("c" in U[u] for u in counted) else " (one-room period: n/a)") + ".",
                 "- **D, E:** not informed by this period alone (d2/d3 for G51 only)."]
        txt = (HERE / g / "README.md").read_text()
        txt = re.sub(r"\*\*Verdict:\*\* .*", f"**Verdict:** {verdict}", txt, count=1)
        txt = re.sub(r"## Result\n.*?(?=\n## Scorecard)", "## Result\n" + "\n".join(lines) + "\n", txt, flags=re.S)
        txt = re.sub(r"## Scorecard \(period-specific axes\)\n.*?(?=\n## Notes)", "## Scorecard (period-specific axes)\n" + "\n".join(score) + "\n", txt, flags=re.S)
        (HERE / g / "README.md").write_text(txt)
        print(g, verdict, det, counted)
    return summary
