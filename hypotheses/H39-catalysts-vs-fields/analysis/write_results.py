"""Results stage for H39 period folders: fills verdicts and results, keeping each Prediction section verbatim.

Called by write_period_folders.py --stage results.
"""
from __future__ import annotations

import json
import re

import numpy as np

import h39lib as L
from write_period_folders import GP, NE_FOLDERS, POINT_PERIODS, REGIME3, UNNUMBERED, goal_info, header, keep_prediction

RUN_DATE = "2026-10-04"
B4 = ["work", "chat", "idle", "consolidate"]
CLS_NAME = {"N_tgt": "nudges", "H_any": "human messages (any)", "H_men": "human, mentioned", "H_und": "human, unmentioned",
            "A_men": "@-mentions"}


def f(x, d=3):
    return "–" if x is None or (isinstance(x, float) and not np.isfinite(x)) else f"{x:+.{d}f}"


def ci(c, d=2):
    return "" if not c else f" [{c[0]:+.{d}f}, {c[1]:+.{d}f}]"


def unit_row(name, u):
    if not u or "p_F" not in u:
        return f"| {name} | {u.get('n_ep', 0) if u else 0} | too few | | | | | |"
    dpi = ", ".join(f"{B4[s][0]} {u['dpi'][s]:+.3f}" for s in range(min(4, len(u["dpi"]))))
    st = "powered" if u["status"] == "ok" else "underpowered"
    esc_idle = u["esc"][2] if len(u["esc"]) > 2 else None
    return (f"| {name} | {u['n_ep']} ({st}) | **{L.unit_class(u)}** | {u['K']:+.3f}{ci(u['K_ci'])} | {u['phi_exc']:.3f} | "
            f"{u['p_F']:.3f} | {dpi} | {f(esc_idle, 2)} |")


def score_period(g, r):
    """Per-period verdict against the dated predictions."""
    checks = []
    b4 = r.get("b4", {})
    u = b4.get("N_tgt")
    if g >= 31 and u and u.get("status") == "ok":
        ok = L.unit_class(u) == "both" and u["dpi"][2] < 0 and u["esc"][2] > 0
        checks.append(("P1 nudges: both, idle share down, idle escape up", ok))
    u = b4.get("H_any")
    if u and u.get("status") == "ok":
        ok = L.unit_class(u) == "both" and u["dpi"][1] > 0
        checks.append(("P2 human messages: both, chat share up", ok))
    u = b4.get("A_men")
    if u and u.get("status") == "ok":
        ok = L.unit_class(u) in ("field", "both") and abs(u["K"]) < 0.2 and u["dpi"][1] > 0
        checks.append(("P3 @-mentions: field toward chat, |K| < 0.2", ok))
    e = r.get("erasure", {}).get("CF_b6")
    e4 = r.get("erasure", {}).get("CF_b4")
    if g in REGIME3 and e and e.get("status") == "ok":
        ok = e["dpi"][0] > 0 and (e["dpi"][1] + e["dpi"][2]) < 0 and e["p_dpi"][0] < 0.05 and abs(e4["K"]) < 0.10
        checks.append(("P4 erasure: browse up, type+shell down, |K_B4| < 0.10", ok))
    if not checks:
        return "descriptive", checks
    n = sum(ok for _, ok in checks)
    v = "supported" if n == len(checks) else ("failed" if n == 0 else "mixed")
    return v, checks


P9_NOTE = None


def autooff_block():
    p = L.OUT / "steps" / "autooff_results.json"
    if not p.exists():
        return ""
    A = json.loads(p.read_text())
    out = ("\n**Post hoc step S20260821 (automated speaker silent from 08-21; P9).** Balanced panel of "
           f"{A['2x2']['n_agents']} agents; placebo = G51 day boundaries of the same shape.\n\n"
           "| Window | class | K (pct) | φ pct | Δπ_idle (pct) | idle escape ln ratio (pct) |\n| --- | --- | --- | --- | --- | --- |\n")
    for k, r in A.items():
        b, j = r["b4"], r["judge_b4"]
        out += (f"| {k} days | {j.get('cls')} | {b['K']:+.3f} ({j.get('K_pct', 0):.0f}) | {j.get('phi_pct', 0):.0f} | "
                f"{b['dpi'][2]:+.3f} ({r['dpi_idle_pct']:.0f}) | {b['esc'][2]:+.3f} ({r['idle_esc_pct']:.0f}) |\n")
    out += ("\nP9 (neither) ✓. With the nudger off, idle escape is lower (−0.12 to −0.14, at the 26th and 10th placebo percentiles) "
            "and K is the lowest of 20 placebos in the 5 + 5 window (−0.08, below the 0.10 floor), while the idle share does not move: "
            "at swarm level the nudger's removal looks like a weak loss of catalysis, not of a field. Confounded with time in goal; post hoc.\n")
    return out


def period_readme(g, r, steps_by_folder, titles, rows):
    path = GP / f"G{g:02d}" / "README.md"
    pred = keep_prediction(path)
    old_txt = path.read_text()
    p9 = re.search(r"(- \*\*2026-10-04, post hoc discovery, prediction written before running it\.\*\*.*?)(\n|$)", old_txt, re.S)
    p9 = p9.group(1) if p9 else None
    v, checks = score_period(g, r)
    gi = rows.get(g, {})
    txt = header(f"H39 × G{g:02d}: {titles.get(g, '')} ({gi.get('start', '?')} → {gi.get('end', '?')})", v,
                 "exploratory (round 1, non-holdout)",
                 f"regime {r['regime']} · mode {gi.get('mode', '?')} · {r['n_agent_days']} agent-days on {len(r['days'])} non-holdout days "
                 f"({r['days'][0]} → {r['days'][-1]}) · {r['n_minutes']:,} agent-minutes on the trimmed grid.")
    old = path.read_text()
    why = re.search(r"## Why this period\n(.*?)\n\n## Prediction", old, re.S)
    txt += "\n## Why this period\n" + (why.group(1) if why else "") + "\n\n## Prediction\n" + pred + "\n\n## Result\n"
    txt += (f"Run {RUN_DATE} with `analysis/run_period.py --period G{g:02d}`; numbers in "
            f"`data/processed/H39-catalysts-vs-fields/G{g:02d}/results.json`. Window W = 30 min; 300 day-bootstrap resamples; "
            "200 placebo draws. B4 occupancy of the period (work, chat, idle, consolidate): "
            + ", ".join(f"{x:.2f}" for x in r["occupancy_b4"]) + ".\n\n")
    txt += "| Lever (B4) | episodes | class (A1 rule) | K [95% CI] | φ_exc | placebo p_F | Δπ (w, c, i, c) | idle escape ln ratio |\n| --- | --- | --- | --- | --- | --- | --- | --- |\n"
    for c in ("N_tgt", "H_any", "H_men", "H_und", "A_men"):
        txt += unit_row(CLS_NAME[c], r["b4"].get(c, {})) + "\n"
    if "erasure" in r:
        for k, lab in (("CF_b4", "forced erasure (CF)"), ("CV_b4", "voluntary erasure (CV)"),
                       ("CF_b4_nocons", "CF, no-consolidate chain (A2)"), ("CV_b4_nocons", "CV, no-consolidate chain (A2)")):
            txt += unit_row(lab, r["erasure"].get(k, {})) + "\n"
        e6 = r["erasure"].get("CF_b6", {})
        if "dpi" in e6:
            txt += (f"\nForced erasure on B6 (browse, type, shell, chat, idle, consolidate): Δπ = "
                    + ", ".join(f"{x:+.3f}" for x in e6["dpi"]) + f"; K = {e6['K']:+.3f}.\n")
    cont = r.get("content", {})
    lines = []
    for c in ("N_tgt", "H_any", "H_men", "A_men"):
        x = cont.get(c) if isinstance(cont, dict) else None
        if isinstance(x, dict) and "field_c" in x:
            lines.append(f"| {CLS_NAME[c]} | {x['n_ep']} | {x['field_c_std']:+.2f} (p {x['p_field_c']:.3f}) | {x['cat_c']:+.3f}{ci(x['cat_c_ci'])} (p {x['p_cat_c']:.3f}) |")
    if lines:
        txt += ("\nContent (O6), drift toward the kick message in SD units of the controls' drift, and diffusion (ln ratio of "
                "perpendicular squared steps):\n\n| Lever | episodes | drift toward message | diffusion |\n| --- | --- | --- | --- |\n"
                + "\n".join(lines) + "\n")
    for s in steps_by_folder.get(f"G{g:02d}", []):
        txt += "\n" + step_block(s)
    if g == 51:
        txt += autooff_block()
    txt += "\n**Scored predictions:** " + ("; ".join(f"{n}: {'✓' if ok else '✗'}" for n, ok in checks) if checks else
                                         "no class powered (≥ 20 episodes); descriptive only") + ".\n"
    txt += "\n## Scorecard (period-specific axes)\n"
    pw = [c for c in ("N_tgt", "H_any", "A_men") if r["b4"].get(c, {}).get("status") == "ok"]
    beat = [c for c in pw if L.unit_class(r["b4"][c]) != "neither"]
    txt += (f"- **C (adequacy):** {len(beat)}/{len(pw)} powered message levers beat the placebo-episode null on at least one component.\n"
            "- **D/E:** the stationary decomposition is an unfitted statistic of matched windows; " + ("E: the 08-21 automated-speaker switch-off (post hoc, P9)" if g == 51 else "no natural experiment inside the period")
            + (" except the scaffold step below." if f"G{g:02d}" in steps_by_folder else ".") + "\n")
    txt += "\n## Notes\n- Matched controls use the past only and both arms are cut at the next kick (design fix from the synthetic null).\n"
    if p9:
        txt += p9 + "\n"
    if g in REGIME3:
        txt += "- Erasure: the full B4/B6 chain mixes in the consolidation clock (consolidate is depleted right after any consolidation); the no-consolidate chain (A2) is the cleaner read.\n"
    path.write_text(txt)
    return v


def step_block(s):
    b, c = s.get("b4", {}), s.get("c6", {})
    out = (f"**Step {s['id']}** ({s['label']}; pre {', '.join(s['pre'])} → post {', '.join(s['post'])}; {s['n_agents']} agents in the balanced panel; "
           f"placebo pool: {s.get('placebo_pool')} {s.get('era')}, n = {s.get('n_placebo')}).\n\n"
           "| State family | class | φ (percentile in placebo) | K (percentile) | Δπ |\n| --- | --- | --- | --- | --- |\n")
    if b:
        out += (f"| behavior B4 | **{b.get('cls')}** | {b['phi']:.3f} ({b['phi_pct']:.0f}) | {b['K']:+.3f} ({b['K_pct']:.0f}) | "
                + ", ".join(f"{B4[k]} {b['dpi'][k]:+.3f}" for k in range(4)) + " |\n")
    if c:
        out += f"| content C6 | **{c.get('cls')}** | {c['phi']:.3f} ({c['phi_pct']:.0f}) | {c['K']:+.3f} ({c['K_pct']:.0f}) | (clusters) |\n"
    if s.get("flag"):
        out += f"\nFlag: {s['flag']}.\n"
    return out


def ne_readme(ne, S, steps):
    path = GP / ne / "README.md"
    pred = keep_prediction(path)
    old = path.read_text()
    title = re.search(r"^# (.*)$", old, re.M).group(1)
    role = re.search(r"\*\*Role:\*\* (.*)$", old, re.M).group(1)
    why = re.search(r"## Why this test\n(.*?)\n\n## Prediction", old, re.S)
    body, verdict = "", "pending"
    if ne == "NE34":
        ks = [s for s in steps if s["cls"] == "kickoff"]
        kk = S["steps"]["kickoffs"]
        body += (f"Run {RUN_DATE} with `analysis/run_steps.py`; numbers in `data/processed/H39-catalysts-vs-fields/steps/steps_results.json`. "
                 f"{kk['n']} kickoffs (content usable in {kk['n_content']}; the 2025 periods #2–#8 have too few 30-min content windows).\n\n")
        body += "| Kickoff | era | agents | B4 class | B4 φ pct | B4 K (pct) | Δπ work, chat, idle | C6 class | C6 φ pct | C6 K pct |\n| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |\n"
        for s in ks:
            b, c = s.get("b4", {}), s.get("c6", {})
            body += (f"| {s['id']}{' (' + s['flag'] + ')' if s.get('flag') else ''} | {s['era']} | {s['n_agents']} | {b.get('cls')} | {b.get('phi_pct', 0):.0f} | "
                     f"{b.get('K', 0):+.3f} ({b.get('K_pct', 0):.0f}) | {b['dpi'][0]:+.3f}, {b['dpi'][1]:+.3f}, {b['dpi'][2]:+.3f} | "
                     f"{c.get('cls', '–')} | {c.get('phi_pct', float('nan')):.0f} | {c.get('K_pct', float('nan')):.0f} |\n")
        p5 = [("content φ above placebo p95 in ≥ 70%", kk["c6_field_share"] >= 0.7, f"{kk['c6_field_share']:.0%} (5/20; 4/20 at or above the 95th percentile rank)"),
              ("content K above placebo median in ≥ 60%", kk["c6_K_above_median_share"] >= 0.6, f"{kk['c6_K_above_median_share']:.0%}"),
              ("behavior φ above placebo p95 in ≤ 30%", kk["b4_phi_above_p95_share"] <= 0.3, f"{kk['b4_phi_above_p95_share']:.0%}"),
              ("behavior K inside placebo band in ≥ 70%", kk["b4_K_inside_share"] >= 0.7, f"{kk['b4_K_inside_share']:.0%}")]
        body += "\n| P5 part | observed | verdict |\n| --- | --- | --- |\n" + "".join(f"| {a} | {o} | {'✓' if b else '✗'} |\n" for a, b, o in p5)
        body += (f"\n- Behavior: individually 27% of kickoffs exceed the placebo p95, but the kickoffs taken together do shift occupancy more than "
                 f"ordinary day boundaries (Stouffer p = {kk['b4_stouffer_F']:.1g}); the mean shift is small (work {kk['b4_dpi_mean'][0]:+.3f}, idle {kk['b4_dpi_mean'][2]:+.3f}).\n"
                 "- Content: strongly era-dependent. Regime-III kickoffs (#36 → #42) exceed the placebo p95 in 4 of 6; regime-I 4-h kickoffs in 0 of 13, "
                 "because content already changes as much between two ordinary days of a regime-I goal (placebo content TV median 0.56 vs 0.29 in regime III).\n")
        n = sum(b for _, b, _ in p5)
        verdict = "mixed" if 0 < n < 4 else ("supported" if n == 4 else "failed")
    elif ne == "NE42":
        for sid in ("K39-40", "K40-41"):
            s = next(x for x in steps if x["id"] == sid)
            body += step_block(s) + "\n"
        m = next(x for x in steps if x["id"] == "K39-40")["b4"]["dpi"][1]
        sp = next(x for x in steps if x["id"] == "K40-41")["b4"]["dpi"][1]
        body += (f"P6: merge Δπ_chat {m:+.3f} (predicted > 0: {'✓' if m > 0 else '✗'}, not beyond placebo); split Δπ_chat {sp:+.3f} "
                 f"(predicted < 0: {'✓' if sp < 0 else '✗'}). The split is flagged beyond the regime-III day-boundary placebo (B4 'both'), "
                 "but so are 4 of the other regime-III kickoffs, so the room change is not separable from the goal change. **Inconclusive**, as predicted for significance; the split's chat sign is wrong.\n")
        verdict = "mixed"
    elif ne == "NE15":
        s = next(x for x in steps if x["id"] == "NE15")
        body += step_block(s) + "\nDescriptive only (two weeks apart, across NE14; #34 held out). No verdict.\n"
        verdict = "descriptive"
    elif ne == "NE41":
        E = S["erasure"]
        body += (f"Pooled over the regime-III periods (per-period rows in the G folders). Run {RUN_DATE}.\n\n"
                 "| Chain | class (A1 rule) | K pooled [95% CI] | mean φ_exc | Δπ pooled |\n| --- | --- | --- | --- | --- |\n")
        for k, lab in (("CF_b4", "CF, B4 full"), ("CF_b4_nocons", "CF, B4 without consolidate (A2)"), ("CF_b6", "CF, B6 full"),
                       ("CF_b6_nocons", "CF, B6 without consolidate (A2)"), ("CV_b4", "CV, B4 full"), ("CV_b4_nocons", "CV, B4 without consolidate (A2)")):
            v = E[k]
            names = v.get("state_names", B4 if "b4" in k else ["browse", "type", "shell", "chat", "idle", "consolidate"])
            if "b4" in k and "nocons" in k:
                names = B4[:3]
            body += (f"| {lab} | {v['cls']} | {v['K_meta']['est']:+.3f}{ci(v['K_meta']['ci'])} | {v['phi_exc_mean']:.3f} | "
                     + ", ".join(f"{names[i]} {m['est']:+.3f}" for i, m in enumerate(v["dpi_meta"]) if i < len(names)) + " |\n")
        ts = E["CF_b6"]["dpi_type_shell"]
        body += (f"\nP4: browse up ✓ ({E['CF_b6']['dpi_meta'][0]['est']:+.3f}{ci(E['CF_b6']['dpi_meta'][0]['ci'], 3)}); type + shell down ✗ "
                 f"({ts['est']:+.3f}{ci(ts['ci'], 3)}: up, not down); |K_B4| < 0.10 ✗ on the point estimate ({E['CF_b4']['K_meta']['est']:+.3f}, CI spans 0) and ✗ in the "
                 f"no-consolidate chain ({E['CF_b4_nocons']['K_meta']['est']:+.3f}, CI excludes 0); CF and CV same class ✗ (CF both / CV field in the A2 chain).\n"
                 "\nReading: right after a forced erasure the agent is *less* idle and works more (browse and type up, idle −0.13 in the A2 chain), and it switches "
                 "state *more slowly* (work escape down): an anti-catalytic field toward work. The consolidation clock confounds the full chain. "
                 "This does not contradict H15's write dip directly: H15 counted functional-output turns (git commit/push, deploy), these are activity states.\n")
        verdict = "failed"
    else:
        s = next((x for x in steps if x["id"] == ne), None)
        if s:
            body += step_block(s)
            b = s.get("b4", {})
            pp = {"NE10": ("neither", "Δπ_idle < 0"), "NE16": ("catalyst", None), "NE07": ("neither", None)}.get(ne, ("neither", None))
            ok = b.get("cls") == pp[0]
            extra = ""
            if ne == "NE10":
                extra = f" Direction: Δπ_idle {b['dpi'][2]:+.3f} (predicted < 0: {'✓' if b['dpi'][2] < 0 else '✗'})."
                ok = ok and b["dpi"][2] < 0
            body += f"\nPrediction (P7): {pp[0]} → observed {b.get('cls')}.{extra} {'✓' if ok else '✗'}\n"
            verdict = "supported" if ok else "failed"
    txt = header(title, verdict, role, "see Prediction for the windows; non-holdout days only.")
    txt += "\n## Why this test\n" + (why.group(1) if why else "") + "\n\n## Prediction\n" + pred + "\n\n## Result\n" + body + "\n## Notes\n- Run " + RUN_DATE + "; placebos are within-goal day boundaries of the same era (regime × hours) and window shape, excluding ±1 day around the tested scaffold steps.\n"
    path.write_text(txt)
    return verdict


def main():
    S = json.loads((L.OUT / "summary.json").read_text())
    steps = S["steps"]["list"]
    titles, rows = goal_info()
    by_folder = {}
    for s in steps:
        by_folder.setdefault(s["folder"], []).append(s)
    verdicts = {}
    for g in POINT_PERIODS:
        p = L.OUT / f"G{g:02d}" / "results.json"
        if p.exists():
            verdicts[f"G{g:02d}"] = period_readme(g, json.loads(p.read_text()), by_folder, titles, rows)
    for ne in NE_FOLDERS:
        verdicts[ne] = ne_readme(ne, S, steps)
    L.jdump(verdicts, L.OUT / "period_verdicts.json")
    print(verdicts)


if __name__ == "__main__":
    main()
