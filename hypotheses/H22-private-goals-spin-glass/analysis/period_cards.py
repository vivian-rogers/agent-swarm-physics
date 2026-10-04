"""Fill the Result / Verdict blocks of the H22 G-folder READMEs from results.json (predictions are written by hand
before each run and are never touched here). Also prints the cross-unit table used in the main card.

Verdict rules (card, Prediction + Amendment 1):
  #51 counted units: supported if P1, P3 and P4 pass; failed if P1 passes and (P3 fails or T_SR > 0 significantly);
  inconclusive if P1 fails. Short units: descriptive.
  Contrast units: H22 expects the ferro / balanced side: raw tau3 >= 0.25 or kappa > 1 ("as predicted") or noise
  floor; reported as descriptive unless counted (38a).

Usage: uv run python hypotheses/H22-private-goals-spin-glass/analysis/period_cards.py
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
H = HERE.parent
sys.path.insert(0, str(HERE))
from figures import DATA, PERIOD, UNITS51, CONTRAST, g  # noqa: E402

COUNTED51 = ("51b", "51c", "51d")


def fmt(x, d=3):
    try:
        if x is None or (isinstance(x, float) and not np.isfinite(x)):
            return "–"
        return f"{x:.{d}f}"
    except Exception:
        return str(x)


def ci(x, d=2):
    return f"[{fmt(x[0], d)}, {fmt(x[1], d)}]" if isinstance(x, list) and len(x) == 2 else "–"


def checks(r):
    c = g(r, "content", "moments", default={})
    f = g(r, "content", "frustration", "shuffle", default={})
    t = g(r, "content", "treatment", "family_adjusted", "SR", default={})
    sy = g(r, "content", "treatment", "family_adjusted", "SY", default={})
    o = g(r, "overlap", default={})
    P1 = g(c, "p_rho", default=1) < 0.05
    P2 = np.isfinite(g(c, "kappa")) and g(c, "kappa") < 1
    t3 = g(c, "tau3_dc"); t3ci = g(c, "tau3_dc_ci90", default=[np.nan, np.nan])
    P3 = np.isfinite(t3) and t3 < 0.25 and np.isfinite(t3ci[1]) and t3ci[1] < 0.5
    P3F = g(f, "p_F_low", default=0) >= 0.05
    P3bal = np.isfinite(t3ci[0]) and t3ci[0] > 0.25
    P4 = (g(t, "T", default=np.nan) < 0) and (g(t, "p_less", default=1) < 0.05)
    P4rival = (g(t, "T", default=np.nan) > 0) and (g(t, "p_greater", default=1) < 0.05)
    P5 = isinstance(o, dict) and g(o, "p_W", default=1) < 0.05 and g(o, "W", default=0) > 1 and g(o, "M", default=0) > 0.2
    return dict(P1=P1, P2=P2, P3=P3, P3F=P3F, P3bal=P3bal, P4=P4, P4rival=P4rival, P5=P5, SY=(g(sy, "T", default=np.nan) > 0 and g(sy, "p_greater", default=1) < 0.05))


def verdict(u, r):
    k = checks(r)
    if u in UNITS51 and u not in COUNTED51:
        return "descriptive"
    if u in UNITS51:
        if not k["P1"]:
            return "inconclusive"
        if k["P3"] and k["P4"]:
            return "supported"
        if k["P4rival"]:
            return "failed"
        if k["P3bal"]:
            return "failed"
        return "mixed" if (k["P3"] or k["P4"]) else "inconclusive"
    # contrast
    c = g(r, "content", "moments", default={})
    ferro = (g(c, "tau3", default=np.nan) >= 0.25) or (g(c, "kappa", default=np.nan) > 1)
    if not k["P1"]:
        return "descriptive (noise floor)"
    return "descriptive (ferro side, as H22 expects for a shared-objective week)" if ferro else "descriptive (not ferro side)"


def table(u, r):
    c = g(r, "content", "moments", default={})
    f = g(r, "content", "frustration", default={})
    sh = g(f, "shuffle", default={}); rel = g(f, "reliable", default={}); gs = g(f, "gs", default={})
    fr = g(r, "content", "family_residual", default={})
    tc = g(r, "talk", "moments", default={})
    o = g(r, "overlap", default={})
    k = checks(r)
    yes = lambda b: "pass" if b else "fail"
    rows = [
        "| Prediction | Observed (90% CI) | Null / reference | Verdict |", "| --- | --- | --- | --- |",
        f"| P1 heterogeneous content couplings | ρ_split = {fmt(g(c, 'rho_split'))}; σ_J = {fmt(g(c, 'sigma'), 4)}; N = {g(c, 'N', default='–')} | per-agent day-permutation null: q95 ρ = {fmt(g(c, 'rho_null_q95'))}, p = {fmt(g(c, 'p_rho'))} | {yes(k['P1'])} |",
        f"| P2 SK ratio κ < 1 | κ̂ = {fmt(g(c, 'kappa'), 2)} {ci(g(c, 'kappa_ci90'))}; J̄ = {fmt(g(c, 'Jbar'), 4)} | glass < 1 < ferro (uninformative if > 1: drive) | {yes(k['P2'])} |",
        f"| P3 drive-robust balance τ₃(dc) < 0.25 | {fmt(g(c, 'tau3_dc'))} {ci(g(c, 'tau3_dc_ci90'))} | SK ≈ 0; factions ≈ 0.5 | {'pass' if k['P3'] else ('fail (balanced)' if k['P3bal'] else 'indeterminate (CI spans both)')}{'' if k['P1'] else '; uninterpretable without P1'} |",
        f"| P3 (secondary) raw τ₃ | {fmt(g(c, 'tau3'))} {ci(g(c, 'tau3_ci90'))} | SK ≈ 0; ferro/drive → 1 | – |",
        f"| P3 (secondary) triangle frustration F | {fmt(g(sh, 'F'))} (F_w {fmt(g(sh, 'Fw'))}; p_neg {fmt(g(sh, 'p_neg'))}) | sign shuffle {fmt(g(sh, 'F_null_mean'))} [{fmt(g(sh, 'F_null_q05'))}, {fmt(g(sh, 'F_null_q95'))}], p_low = {fmt(g(sh, 'p_F_low'))} | {yes(k['P3F'])} (non-specific, Amendment 1) |",
        f"| (desc.) reliable-edge F | {fmt(g(rel, 'F'))} on {g(rel, 'n_tri', default='–')} triangles | random signs {fmt(g(rel, 'F_rand'))} | – |",
        f"| (desc.) ground-state frustration | {fmt(g(gs, 'f'))} | sign shuffle {fmt(g(gs, 'null_mean'))}, p_low = {fmt(g(gs, 'p_low'))} | – (sign-shuffle null flags balance in most synthetic SK runs: not evidence) |",
        f"| (family check) after removing lab×lab block means | τ₃ {fmt(g(fr, 'tau3'))}, τ₃(dc) {fmt(g(fr, 'tau3_dc'))}, F {fmt(g(fr, 'F'))} | F null {fmt(g(fr, 'F_null_mean'))}, p_low {fmt(g(fr, 'p_F_low'))} | – |",
    ]
    if u in UNITS51:
        for cls in ("SR", "OP", "K", "SY", "NC"):
            for adj in ("raw", "family_adjusted"):
                t = g(r, "content", "treatment", adj, cls, default={})
                if t and t.get("n"):
                    rows.append(f"| P4 content T_{cls} ({adj.replace('_', ' ')}) | {fmt(t.get('T'), 4)} (mean {fmt(t.get('mean'), 4)}, n = {t.get('n')}; U mean {fmt(t.get('U_mean'), 4)}) | role permutation: SD {fmt(t.get('null_sd'), 4)}, p_less {fmt(t.get('p_less'))}, p_greater {fmt(t.get('p_greater'))} | " +
                                ("–" if not (cls == "SR" and adj == "family_adjusted") else ("pass" if k["P4"] else ("rival (homophily)" if k["P4rival"] else "fail"))) + " |")
        tc_ = g(r, "content", "treatment_complete", "family_adjusted", "SR", default={})
        if tc_:
            rows.append(f"| (first run) T_SR on the complete-matrix agent set (family-adj.) | {fmt(tc_.get('T'), 4)} (n = {tc_.get('n')}) | p_less {fmt(tc_.get('p_less'))}, p_greater {fmt(tc_.get('p_greater'))} | – |")
        sra = g(r, "static_role_alignment", "SR", default={})
        rows.append(f"| (manipulation) static role field: SR cos(H_i,H_j) − U | {fmt(g(sra, 'T'))} (n = {g(sra, 'n', default='–')}) | role permutation p_greater {fmt(g(sra, 'p_greater'))} | – |")
        tt = g(r, "talk", "treatment", "family_adjusted", "SR", default={})
        rows.append(f"| (secondary) talk T_SR (family-adj.) | {fmt(g(tt, 'T'), 4)} (n = {g(tt, 'n', default='–')}) | p_less {fmt(g(tt, 'p_less'))}, p_greater {fmt(g(tt, 'p_greater'))} | – |")
        mf = g(r, "talk", "mf_role_blocks", default={})
        if isinstance(mf, dict) and "J_in" in mf:
            rows.append(f"| (secondary) talk MF role blocks (H05 block_J) | J_in(SR) {fmt(mf['J_in'])}, J_out {fmt(mf['J_out'])} | – | – |")
    rows.append(f"| (secondary) talk couplings | ρ_split {fmt(g(tc, 'rho_split'))} (p {fmt(g(tc, 'p_rho'))}); κ̂ {fmt(g(tc, 'kappa'), 2)}; τ₃ {fmt(g(tc, 'tau3'))}; τ₃(dc) {fmt(g(tc, 'tau3_dc'))} | pseudo-null | – |")
    if isinstance(o, dict) and o:
        rows.append(f"| P5 overlap synchrony W, memory M | W = {fmt(g(o, 'W'), 2)} (p = {fmt(g(o, 'p_W'))}); M = {fmt(g(o, 'M'), 2)}; q_self {fmt(g(o, 'q_self'))}, q(1) {fmt(g(o, 'q_lag1'))}, q_∞ {fmt(g(o, 'q_inf'))} (N = {g(o, 'N')}) | circular day-shift null (W = 1) | {yes(k['P5']) if g(o, 'counted', default=False) else 'descriptive'} |")
    orf = g(r, "overlap_room_field", default={})
    if isinstance(orf, dict) and orf:
        rows.append(f"| (post hoc) overlap with per-room day fields | W = {fmt(g(orf, 'W'), 2)} (p = {fmt(g(orf, 'p_W'))}); M = {fmt(g(orf, 'M'), 2)} | circular day-shift null | – |")
    lr = g(r, "variants", "largest_room", default={})
    if isinstance(lr, dict) and lr:
        rows.append(f"| (room rival) largest room only (room {lr.get('room')}) | N {lr.get('N')}; ρ_split {fmt(lr.get('rho_split'))} (p {fmt(lr.get('p_rho'))}); κ̂ {fmt(lr.get('kappa'), 2)}; τ₃ {fmt(lr.get('tau3'))}; τ₃(dc) {fmt(lr.get('tau3_dc'))}; F {fmt(g(lr, 'frustration', 'F'))} (null {fmt(g(lr, 'frustration', 'F_null_mean'))}) | – | – |")
    wf = g(r, "variants", "with_focus_agents", default={})
    if isinstance(wf, dict) and wf:
        rows.append(f"| (variant) #focus agents kept | N {wf.get('N')}; ρ_split {fmt(wf.get('rho_split'))} (p {fmt(wf.get('p_rho'))}); κ̂ {fmt(wf.get('kappa'), 2)}; τ₃(dc) {fmt(wf.get('tau3_dc'))} | – | – |")
    return "\n".join(rows)


def key_numbers(u, r):
    c = g(r, "content", "moments", default={})
    t = g(r, "content", "treatment", "family_adjusted", "SR", default={})
    o = g(r, "overlap", default={})
    s = f"ρ_split {fmt(g(c, 'rho_split'), 2)} (p {fmt(g(c, 'p_rho'), 3)}); κ̂ {fmt(g(c, 'kappa'), 1)}; τ₃(dc) {fmt(g(c, 'tau3_dc'), 2)}; τ₃ {fmt(g(c, 'tau3'), 2)}"
    if u in UNITS51 and t:
        s += f"; T_SR {fmt(t.get('T'), 4)} (p< {fmt(t.get('p_less'), 2)}, p> {fmt(t.get('p_greater'), 2)})"
    if isinstance(o, dict) and o:
        s += f"; W {fmt(g(o, 'W'), 2)} (p {fmt(g(o, 'p_W'), 3)})"
    return s


SCORE51 = ("- **C** 1: content couplings beat the per-agent day-permutation null where P1 passes, but none of the "
           "H22-specific statistics (τ₃(dc), T_SR < 0, W) beat their nulls in the predicted direction.\n"
           "- **D** 0: no glass signature (random-sign frustration with conflict-borne negative couplings; collective metastable states).\n"
           "- **G** 1: known structure recovered: same-role pairs share a content field (static SR alignment, role permutation).\n"
           "- **E** n/a within the unit.")
SCOREC = ("- **C** 1 where P1 passes (38a, #44): couplings beat the pseudo-null; low power elsewhere.\n"
          "- **G** 1: the two-room structure shows up as a balanced (factional) block structure (τ₃(dc) ≈ 1 in 38a, #44); "
          "the overlap synchrony in #44 disappears once each room's day field is removed (post hoc).\n"
          "- **D, E** n/a.")


def update_readme(folder: Path, units, results):
    p = folder / "README.md"
    txt = p.read_text()
    blocks, verdicts = [], []
    for u in units:
        r = results[u]
        v = verdict(u, r)
        verdicts.append(v)
        blocks.append(f"**Unit {u}** ({r['D']} days{', day-thirds as pseudo-days' if r.get('pseudo_days') else ''}; "
                      f"N eligible = {r['N_eligible']}; verdict: {v})\n\n" + table(u, r))
    data_ref = f"Data: `data/processed/H22-private-goals-spin-glass/{PERIOD[units[0]]}/<unit>/results.json`; figure: `figures/H22_{folder.name}.pdf`."
    res = "## Result\n" + data_ref + "\n\n" + "\n\n".join(blocks) + "\n"
    txt = re.sub(r"## Result\n.*?(?=\n## Scorecard)", res, txt, flags=re.S)
    sc = SCORE51 if units[0] in UNITS51 else SCOREC
    txt = re.sub(r"## Scorecard \(period-specific axes\)\n.*?(?=\n## Notes)", "## Scorecard (period-specific axes)\n" + sc + "\n", txt, flags=re.S)
    if units[0] not in UNITS51:
        ov = "descriptive"
    else:
        ov = verdicts[0] if len(set(verdicts)) == 1 else ("mixed" if any(v in ("supported", "failed") for v in verdicts) else verdicts[0])
    txt = re.sub(r"^\*\*Verdict:\*\*.*$", f"**Verdict:** {ov}", txt, flags=re.M)
    p.write_text(txt)
    return ov


def main():
    results = {}
    for u in UNITS51 + CONTRAST:
        p = DATA / PERIOD[u] / u / "results.json"
        if p.exists():
            results[u] = json.loads(p.read_text())
    out = {}
    for u in UNITS51:
        if u in results:
            out[u] = update_readme(H / "goalperiod-subhypotheses" / f"G{u}", [u], results)
    for per, us in (("G38", ["38a", "38b", "38c"]), ("G40", ["40"]), ("G44", ["44"])):
        us = [u for u in us if u in results]
        if us:
            out[per] = update_readme(H / "goalperiod-subhypotheses" / per, us, results)
    print(json.dumps(out, indent=1))
    print("\n| Unit | Verdict | Key numbers |\n| --- | --- | --- |")
    for u in results:
        print(f"| {u} | {verdict(u, results[u])} | {key_numbers(u, results[u])} |")


if __name__ == "__main__":
    main()
