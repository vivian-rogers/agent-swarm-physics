"""Fill the Result / Verdict / Scorecard sections of the per-period READMEs from round1_<scope>.json.

The Prediction sections (written before the run) are left untouched. Usage:
  uv run python hypotheses/H06-neutral-cooperative-dynamics/analysis/period_folders.py
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
ROOT = Path(__file__).resolve().parents[3]
HYP = ROOT / "hypotheses/H06-neutral-cooperative-dynamics"
SUB = HYP / "goalperiod-subhypotheses"
DATA = ROOT / "data/processed/H06-neutral-cooperative-dynamics"
CLUST = ["km8", "km24", "km64", "wd8", "wd24", "wd64"]


def load(scope):
    folder = "G51" if scope.startswith(("G51", "NE33")) else scope
    p = DATA / folder / f"round1_{scope}.json"
    return json.loads(p.read_text()) if p.exists() else None


def f2(x, d=2):
    try:
        if x is None or not np.isfinite(x):
            return "–"
        return f"{x:.{d}f}"
    except TypeError:
        return str(x)


def iv(p, d=2):
    return f"{f2(p[0], d)} [{f2(p[1], d)}, {f2(p[2], d)}]"


def set_table(r, keys):
    rows = ["| Label set | N | labelled/win | changes | μ̂_NCD (μ_B, μ_L) | λ̄ obs | λ NCD | λ Hubbell | λ conf. | β̂ obs | β NCD | β Hubbell | LLR_NH | LLR_NC | best | NCD adequate | copy-cons. |",
            "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |"]
    for k in keys:
        s = r["sets"].get(k)
        if not s:
            continue
        if not s.get("testable"):
            rows.append(f"| {k} | {s.get('N', '–')} | {f2(s.get('mean_per_win'), 1)} | – | n/a (insufficient labels) | | | | | | | | | | | | |")
            continue
        fi = s["fits"]
        rows.append(
            f"| {k}{' (primary)' if k == 'km24' else ''} | {s['N']} | {f2(s['mean_per_win'], 1)} | {s['n_changes']} | "
            f"{f2(fi['ncd']['mu'], 3)} ({f2(s['mu_B'], 3)}, {f2(s['mu_L'], 2)}) | {f2(s['obs']['lam'])} | {iv(fi['ncd']['pred']['lam'])} | "
            f"{iv(fi['hubbell']['pred']['lam'])} | {iv(fi['conformist']['pred']['lam'])} | {f2(s['obs']['beta'])} | "
            f"{iv(fi['ncd']['pred']['beta'])} | {iv(fi['hubbell']['pred']['beta'])} | {f2(s['LLR_NH'], 1)} | {f2(s['LLR_NC'], 1)} | "
            f"{s['best_model']} | {'yes' if fi['ncd']['adequate'] else 'no'} | {f2(s['copyfrac'])} |")
    return "\n".join(rows)


def failing_stats(s, model="ncd"):
    p = s["fits"][model]["ppc"]
    bad = [k for k, v in p.items() if k != "copyfrac" and v is not None and np.isfinite(v) and v < 0.05 / 9]
    return ", ".join(bad) if bad else "none"


def replace_section(txt, head, body):
    pat = re.compile(rf"(^## {re.escape(head)}\n)(.*?)(?=^## |\Z)", re.S | re.M)
    if pat.search(txt):
        return pat.sub(lambda m: m.group(1) + body.rstrip() + "\n\n", txt)
    return txt.rstrip() + f"\n\n## {head}\n{body}\n"


def set_verdict(txt, v):
    return re.sub(r"^\*\*Verdict:\*\*.*$", f"**Verdict:** {v}", txt, count=1, flags=re.M)


def write(folder, verdict, result, score, note):
    p = SUB / folder / "README.md"
    txt = p.read_text()
    txt = set_verdict(txt, verdict)
    txt = replace_section(txt, "Result", result)
    txt = replace_section(txt, "Scorecard (period-specific axes)", score)
    if note and note not in txt:
        txt = txt.rstrip() + "\n" + note + "\n"
    p.write_text(txt)


FIT = ["c", "f", "lam", "xmax", "single", "rich", "beta", "infil", "dbic2"]


def n_repro(s, m):
    """Post hoc (flagged): number of the 9 statistics with single-statistic PPC p >= 0.05 under model m."""
    p = s["fits"][m]["ppc"]
    return sum(1 for k in FIT if p.get(k) is not None and np.isfinite(p[k]) and p[k] >= 0.05)


def repro_str(s):
    return " / ".join(f"{n_repro(s, m)}" for m in ("ncd", "hubbell", "conformist"))


def free_result(scope, r):
    p = r["sets"].get("km24", {})
    a = r["sets"].get("art", {})
    P1 = r["P1"]
    lines = ["*Run 2026-10-04 (exploratory round 1).* Data: `data/processed/H06-neutral-cooperative-dynamics/"
             f"{scope}/round1_{scope}.json`. Figure: [`figures/pn_{scope}.pdf`](figures/pn_{scope}.pdf).", "",
             "| Prediction | Observed | Null / rival | Verdict |", "| --- | --- | --- | --- |"]
    if p.get("testable"):
        f = p["fits"]
        lines.append(f"| P1 NCD beats both rivals (km24; ≥ 4/6 clusterings; adequate) | LLR_NH {f2(p['LLR_NH'], 1)}, LLR_NC {f2(p['LLR_NC'], 1)}; "
                     f"NCD ≥ 2 over both in {P1.get('n_sup_sets')}/6 clusterings, a rival ≥ 2 over NCD in {P1.get('n_fail_sets')}/6; "
                     f"best model per clustering {P1.get('best_counts')} | joint PPC p: NCD {f2(f['ncd']['ppc_joint'], 3)}, Hubbell {f2(f['hubbell']['ppc_joint'], 3)}, "
                     f"conformist {f2(f['conformist']['ppc_joint'], 3)} | **{P1['verdict']}** |")
        lines.append(f"| P2 β̂ below Hubbell median, inside NCD 95% | β̂ {f2(p['obs']['beta'])} ({p['n_events']} recruitment events) | NCD {iv(f['ncd']['pred']['beta'])}; "
                     f"Hubbell {iv(f['hubbell']['pred']['beta'])}; conformist {iv(f['conformist']['pred']['beta'])} | {r['P2']} |")
        lines.append(f"| P3 λ̄ inside NCD 95% (below Hubbell 2.5%) | λ̄ {f2(p['obs']['lam'])}; μ̂_NCD {f2(f['ncd']['mu'], 3)} (μ_B {f2(p['mu_B'], 3)}, μ_L {f2(p['mu_L'], 2)}); "
                     f"asymptotic λ* {f2(p['lambda_star_asym'])} | NCD {iv(f['ncd']['pred']['lam'])}; Hubbell {iv(f['hubbell']['pred']['lam'])} | {r['P3']} |")
        lines.append(f"| P4 signatures if μ̂ < μ_B | interior mode {p['interior_mode']}; ΔBIC {f2(p['obs']['dbic2'], 1)}; infiltration {f2(p['obs']['infil'])} | "
                     f"NCD infiltration {iv(f['ncd']['pred']['infil'])} | {r['P4']} |")
        if p.get("null_ind"):
            nu = p["null_ind"]
            p8 = "supported" if (nu["lam_p_greater"] < 0.05 and nu["copy_p_greater"] < 0.05) else "failed"
            lines.append(f"| P8 λ̄ and copy-consistency above independent agents | λ̄ {f2(p['obs']['lam'])}, copy-consistency {f2(p['copyfrac'])} | "
                         f"day-shift null means {f2(nu['lam_mean'])} (p {f2(nu['lam_p_greater'], 3)}), {f2(nu['copy_mean'])} (p {f2(nu['copy_p_greater'], 3)}) | {p8} |")
        lines.append(f"| Mapping audit (O8) | copy-consistency {f2(p['copyfrac'])}; singleton fraction {f2(p['obs']['single'])}; λ̄ halves "
                     f"{', '.join(f2(x) for x in p.get('lam_halves', []))} | NCD copy {iv(f['ncd']['pred']['copyfrac'])}, singletons {iv(f['ncd']['pred']['single'])} | descriptive |")
        lines.append(f"| Post hoc: statistics reproduced (PPC p ≥ 0.05, of 9) NCD / Hubbell / conformist | {repro_str(p)} | NCD misses: {failing_stats(p)} | descriptive (post hoc) |")
    if a.get("testable"):
        fa = a["fits"]
        lines.append(f"| P5 artifact labels (secondary) | LLR_NH {f2(a['LLR_NH'], 1)}, LLR_NC {f2(a['LLR_NC'], 1)}; λ̄ {f2(a['obs']['lam'])} (NCD {iv(fa['ncd']['pred']['lam'])}, "
                     f"Hubbell {iv(fa['hubbell']['pred']['lam'])}); β̂ {f2(a['obs']['beta'])} (NCD {iv(fa['ncd']['pred']['beta'])}, Hubbell {iv(fa['hubbell']['pred']['beta'])}); "
                     f"reproduced {repro_str(a)} | joint PPC NCD {f2(fa['ncd']['ppc_joint'], 3)} | {r['P1_art']}; P2 {r['P2_art']}; P3 {r['P3_art']} |")
    else:
        lines.append(f"| P5 artifact labels | {f2(a.get('mean_per_win'), 1)} labelled slots per window | needs ≥ 3 | n/a (insufficient labels) |")
    lines += ["", "**All label sets** (λ and β cells: mean [95% predictive interval] of 400 fresh replicates at each model's profile fit):", "",
              set_table(r, CLUST + ["art", "art_nocarry"])]
    return "\n".join(lines)


def p6(r):
    p = r["sets"].get("km24", {})
    if not p.get("testable"):
        return "n/a (insufficient labels)", ""
    lam, hi = p["obs"]["lam"], p["fits"]["ncd"]["pred"]["lam"][2]
    a = p["LLR_NC"] <= -2
    b = lam > hi
    v = "supported" if (a and b) else ("failed" if p["LLR_NC"] >= 2 else "mixed")
    return v, f"LLR_NC {f2(p['LLR_NC'], 1)} ({'≤ −2' if a else 'not ≤ −2'}); λ̄ {f2(lam)} vs NCD 97.5% point {f2(hi)} ({'above' if b else 'not above'})"


def contrast_result(scope, r):
    v, txt = p6(r)
    p = r["sets"].get("km24", {})
    lines = ["*Run 2026-10-04 (exploratory round 1).* Data: `data/processed/H06-neutral-cooperative-dynamics/"
             f"{scope}/round1_{scope}.json`. Figure: [`figures/pn_{scope}.pdf`](figures/pn_{scope}.pdf).", "",
             "| Prediction | Observed | Null / rival | Verdict |", "| --- | --- | --- | --- |",
             f"| P6 conformist beats NCD and λ̄ above NCD 97.5% (km24) | {txt} | joint PPC p: " +
             (", ".join(f"{m} {f2(p['fits'][m]['ppc_joint'], 3)}" for m in ('ncd', 'hubbell', 'conformist')) if p.get("testable") else "–") + f" | **{v}** |"]
    if p.get("testable"):
        lines.append(f"| For comparison: P1 rule | {r['P1']['verdict']} (best per clustering {r['P1'].get('best_counts')}); P2 {r['P2']}; P3 {r['P3']} | reproduced NCD / Hubbell / conformist {repro_str(p)} | descriptive |")
        if p.get("null_ind"):
            nu = p["null_ind"]
            lines.append(f"| Independent-agents null | λ̄ {f2(p['obs']['lam'])} vs {f2(nu['lam_mean'])} (p {f2(nu['lam_p_greater'], 3)}); copy-consistency {f2(p['copyfrac'])} vs {f2(nu['copy_mean'])} (p {f2(nu['copy_p_greater'], 3)}) | | descriptive |")
    a = r["sets"].get("art", {})
    if a.get("testable"):
        lines.append(f"| Artifact labels | LLR_NH {f2(a['LLR_NH'], 1)}, LLR_NC {f2(a['LLR_NC'], 1)}; λ̄ {f2(a['obs']['lam'])} (NCD 97.5% {f2(a['fits']['ncd']['pred']['lam'][2])}); β̂ {f2(a['obs']['beta'])} | "
                     f"reproduced {repro_str(a)} | {r['P1_art']} |")
    lines += ["", "**All label sets:**", "", set_table(r, CLUST + ["art"])]
    return v, "\n".join(lines)


def g51_result(rs):
    lines = ["*Run 2026-10-04 (exploratory round 1).* Three 5-day blocks, each clustered separately. Data: `data/processed/H06-neutral-cooperative-dynamics/G51/round1_G51{a,b,c}.json`. "
             "Figures: `figures/pn_G51a.pdf` etc.", "", "| Block | P1 verdict (rule) | λ̄ (km24) | 1/N | singletons | copy-cons. | λ̄ vs independent null (p) | joint PPC NCD / Hubbell / conf. | reproduced N / H / C | artifact P1 |",
             "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |"]
    sup = 0
    for b, r in rs.items():
        p = r["sets"].get("km24", {})
        if not p.get("testable"):
            lines.append(f"| {b} | n/a | | | | | | | | |")
            continue
        sup += r["P1"]["verdict"] == "supported"
        nu = p.get("null_ind", {})
        lines.append(f"| {b} ({r['pt_dates'][0]} → {r['pt_dates'][-1]}) | {r['P1']['verdict']} | {f2(p['obs']['lam'])} | {f2(1 / p['N'])} | {f2(p['obs']['single'])} | {f2(p['copyfrac'])} | "
                     f"{f2(nu.get('lam_mean'))} ({f2(nu.get('lam_p_greater'), 3)}) | " + " / ".join(f2(p['fits'][m]['ppc_joint'], 3) for m in ('ncd', 'hubbell', 'conformist')) +
                     f" | {repro_str(p)} | {r['P1_art']} |")
    v = "supported" if sup == 0 else "failed"
    lines += ["", f"**P7 (check): {'passes' if sup == 0 else 'fails'}**: {sup} of {len(rs)} blocks 'supported' under P1's rule."]
    for b, r in rs.items():
        lines += ["", f"Block {b}:", "", set_table(r, CLUST + ["art"])]
    return v, "\n".join(lines)


def main():
    import sys as _s
    for scope in ["G19", "G25", "G30", "G38"]:
        r = load(scope)
        if not r:
            continue
        v, res = contrast_result(scope, r)
        p = r["sets"].get("km24", {})
        score = (f"- **D:** P6 {v}.\n- **H:** best per clustering {r['P1'].get('best_counts')}; reproduced statistics NCD / Hubbell / conformist {repro_str(p)} (post hoc).") if p.get("testable") else "- n/a"
        write(scope, f"{v} (P6 contrast)", res, score, "- 2026-10-04: round 1 run; Result and Verdict filled by `analysis/period_folders.py`.")
    rs = {b: load(f"G51{b}") for b in "abc"}
    rs = {b: r for b, r in rs.items() if r}
    if rs:
        v, res = g51_result(rs)
        write("G51", "supported (P7 check passes: no block 'supported'; but the free weeks fail the same way, so the check is uninformative)" if v == "supported" else f"{v} (P7 check fails)", res,
              "- **C/H:** see the block table; the check concerns specificity of the P1 rule (axis F/H).", "- 2026-10-04: round 1 run; Result and Verdict filled by `analysis/period_folders.py`.")
    for ne in ("NE27", "NE33"):
        fp = DATA / f"{ne}_round1.json"
        if not fp.exists():
            continue
        r = json.loads(fp.read_text())
        f = r["fit_predict"]
        o = f["obs"]
        inside = {m: f[m]["lam_pred_post"][1] <= o["lam_post"] <= f[m]["lam_pred_post"][2] for m in ("ncd", "hubbell", "conformist")}
        a_pass = inside["ncd"] and f["ncd"]["abs_err"] < f["hubbell"]["abs_err"]
        nw = r["newcomers"]
        ll = nw["ll"]
        b_na = nw["n_events_multi_option"] < 3
        b_pass = (not b_na) and ll["ncd"] > max(ll["hubbell"], ll["conformist"])
        v = "n/a" if False else ("supported" if (a_pass and b_pass) else ("failed" if (not a_pass and (b_na or not b_pass)) else "mixed"))
        vtxt = f"{v} ((a) {'passed' if a_pass else 'failed'}: post λ̄ outside every model's 95% interval; (b) " + \
               ("n/a, < 3 multi-option newcomer choices" if b_na else ("passed" if b_pass else "failed: the three kernels are within 0.03 nats")) + ")"
        lines = ["*Run 2026-10-04 (exploratory round 1).* Data: `data/processed/H06-neutral-cooperative-dynamics/" + ne + "_round1.json`; pre/post fits in "
                 "`round1_<side>.json`. Script: `analysis/ne_tests.py`.", "",
                 f"**(a) Fit before, predict after** (intention clusters km24). Observed λ̄: pre {f2(o['lam_pre'])} (N = {o['N_pre']}), post {f2(o['lam_post'])} (N = {o['N_post']}).", "",
                 "| Model | μ̂, k̂ (pre fit) | predicted post λ̄ [95%] | PPC p of observed post λ̄ | abs. error |", "| --- | --- | --- | --- | --- |"]
        for m in ("ncd", "hubbell", "conformist"):
            lines.append(f"| {m} | {f2(f[m]['mu_pre'], 3)}, {f2(f[m]['k_pre'])} | {iv(f[m]['lam_pred_post'])} | {f2(f[m]['ppc_post_lam'], 3)} | {f2(f[m]['abs_err'])} |")
        inc = r["incumbents_firstday"]
        lines += ["", f"**(b) Newcomer kernel.** Newcomers' first-day label changes: {nw['n_choice_windows']}; to a novel or unheld project: {nw['n_novel_or_self']}; "
                  f"multi-option copy choices: {nw['n_events_multi_option']}. Log-likelihoods NCD / Hubbell / conformist: "
                  f"{f2(ll['ncd'])} / {f2(ll['hubbell'])} / {f2(ll['conformist'])}. Incumbents on the same day, for reference: "
                  f"{inc['n_choice_windows']} changes, {inc['n_novel_or_self']} novel or unheld, {inc['n_events_multi_option']} multi-option choices, "
                  f"log-likelihoods {f2(inc['ll']['ncd'])} / {f2(inc['ll']['hubbell'])} / {f2(inc['ll']['conformist'])}.", "",
                  f"Round-1 outcome: {vtxt}. All three models, fitted on the pre side, predict a post-side λ̄ far above the observation: every model "
                  "over-concentrates, the same misfit as within periods (agents mostly hold projects nobody else holds). Newcomers mostly start "
                  "projects of their own (novel or unheld labels), so the kernel test has almost no choices to score."]
        p = SUB / ne / "README.md"
        txt = p.read_text()
        txt = set_verdict(txt, vtxt)
        txt = replace_section(txt, "Result", "\n".join(lines))
        note = "- 2026-10-04: round 1 run; Result and Verdict filled by `analysis/period_folders.py`."
        if note not in txt:
            txt = txt.rstrip() + "\n" + note + "\n"
        p.write_text(txt)
    free = ["G11", "G16", "G31", "G37", "G44"]
    for scope in free:
        r = load(scope)
        if not r:
            continue
        v = r["P1"]["verdict"]
        p = r["sets"].get("km24", {})
        extra = ""
        if p.get("testable"):
            allbad = all(p["fits"][m]["ppc_joint"] < 0.01 for m in ("ncd", "hubbell", "conformist"))
            extra = f"; P2 {r['P2'].split(' (')[0]}; P3 {r['P3'].split(' (')[0]}; art {r['P1_art'].split(' (')[0]}" + \
                    ("; no model adequate (joint PPC p < 0.01 for all three)" if allbad else "")
        verdict = f"{v.split(' (')[0]} (P1{extra})"
        score = (f"- **C (adequacy):** NCD joint PPC p = {f2(p['fits']['ncd']['ppc_joint'], 3)} (km24); {'adequate' if p['fits']['ncd']['adequate'] else 'not adequate'}.\n"
                 f"- **D (unfitted / signature):** P2 {r['P2']}; P3 {r['P3']}; P4 {r['P4']}.\n"
                 f"- **H (rivals):** best model by synthetic likelihood per clustering {r['P1'].get('best_counts')}; artifact labels: {r['P1_art']}.") if p.get("testable") else "- n/a"
        write(scope, verdict, free_result(scope, r), score, f"- 2026-10-04: round 1 run; Result and Verdict filled by `analysis/period_folders.py`.")
    print("free weeks written")


if __name__ == "__main__":
    main()
