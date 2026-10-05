"""Round-2 blocks in H73's goal-period / NE READMEs.

--phase predict : appends a "## Round 2 (2026-10-05)" block with the dated prediction (before the real round-2 run).
--phase results : fills the block's result lines from r2/r2.json (prediction lines kept verbatim).
Round-1 sections and the top Verdict line are not changed (the round-2 verdict is stated inside the block).
"""
from __future__ import annotations
import argparse
import json
import re

import numpy as np

import h73lib as L

PDIR = L.HYP / "goalperiod-subhypotheses"
STAMP = "2026-10-05 05:07 UTC"
MARK = "## Round 2 (2026-10-05)"

REPL = f"""*Prediction written {STAMP}, before the real round-2 run (card pre-registration 04:46 UTC; templated, layer 1).*
- **R2-1a conversation state:** the unique share of conversation state (received items, pending @-mentions, pending nudge, DQ2 thread depth) u_Cv is positive (within-agent-day permutation p < 0.05); in regime III it exceeds the unique share of own fill u_Cf.
- **R2-1b accommodation** (read vs in-flight sources at the read boundary): the unit's γ is reported if the unit has ≥ 200 read and ≥ 200 in-flight pairs; the verdict is card-level (pooled), not per unit.
- **R2-3 reset-and-hold** (regime I/II periods with ≥ 150 one-reset pairs): ΔC(1) > 0 and T > ½ reported (descriptive per period)."""

NATIVE = {
    "G51": f"""*Prediction written {STAMP}, before the real round-2 run (card pre-registration 04:46 UTC).*
- **R2-2-P1 (Prankster onset transient):** daily split-half shift S_10(k) since 07-06 (difference-in-differences against the other incumbents) fits S∞ + A e^(−k/τ) with A > 0 (CI > 0), τ ∈ [0.5, 14] days (upper bound < 30), and the k = 21–60 level inside its placebo band.
- **R2-2-P2 (general onset transients):** over the 16 incumbents, mean S(k ≤ 2) − mean S(14 ≤ k ≤ 42) > 0 in a sign test (p < 0.05).
- **R2-2b NE38 (agent 40, 07-29; descriptive):** the k = 0–2 shift exceeds all four pseudo-date values and halves by k = 7–20.
- Replication layer: the templated R2-1a/R2-1b lines also apply.""",
    "G12": f"""*Prediction written {STAMP}, before the real round-2 run (card pre-registration 04:46 UTC).*
- **R2-2c judge register by minute (descriptive):** projection on the leave-this-judge-out shared judge direction, relative to the judge's debater mean. (i) The 0–5 min mean is ≥ 0.5 × the window mean (a step); (ii) no build-up (slope per 10 min ≤ 0 or within-window permutation p ≥ 0.05); (iii) switch-off: the 30 min after the window < 0.5 × the window mean.
- Replication layer: the templated R2-1a/R2-1b lines also apply.""",
    "NE41": f"""*Prediction written {STAMP}, before the real round-2 run (card pre-registration 04:46 UTC).*
- **C0 (correction, not a test):** round 1's forced-erasure T_s (0.567) recomputed with H46's agent × unit scaling (R2-A5); expected ≈ 0.55.
- **R2-3, regime III (seen sample; H46 found the reset-and-hold shape here post hoc):** new statistics only. Carry-over ρ_carry < 0.3 (the offset is redrawn at each reset, not carried), and κ_seg ∈ [0.02, 0.10].""",
}


def eligible():
    rep = json.loads((L.DATA / "replication/replication.json").read_text())
    return sorted({v["goal_no"] for k, v in rep.items() if not k.startswith("_")})


def strip_block(txt: str) -> str:
    i = txt.find(MARK)
    return txt if i < 0 else txt[:i].rstrip() + "\n"


def predict():
    for g in eligible():
        key = f"G{g:02d}"
        p = PDIR / key / "README.md"
        body = NATIVE.get(key, REPL)
        txt = strip_block(p.read_text())
        p.write_text(txt + f"\n{MARK}\n**Round-2 result:** pending.\n{body}\n")
    p = PDIR / "NE41" / "README.md"
    txt = strip_block(p.read_text())
    p.write_text(txt + f"\n{MARK}\n**Round-2 result:** pending.\n{NATIVE['NE41']}\n")


def f(x, nd=3):
    return "n/a" if x is None or not np.isfinite(x) else f"{x:.{nd}f}"


def results():
    r2 = json.loads((L.DATA / "r2/r2.json").read_text())
    acc_units = {}
    for reg in ("I", "II", "III"):
        for u, v in (r2["acc"][reg].get("units") or {}).items():
            acc_units[u] = v
    rh_goal = r2["rh"]["I_II"].get("per_goal", {})
    for g in eligible():
        key = f"G{g:02d}"
        p = PDIR / key / "README.md"
        txt = p.read_text()
        i = txt.find(MARK)
        head, blk = txt[:i], txt[i:]
        pred = blk.split("\n", 2)[2]
        lines = []
        cv = r2["cv"].get(key)
        if cv:
            lines.append(f"- **R2-1a:** u_Cv {f(cv['u_Cv'])} (p {f(cv.get('p_Cv'), 2)}), u_Cf {f(cv['u_Cf'])} "
                         f"(regime {cv['regime']}; {cv['n']:,} messages). Conversation state "
                         + ("beats" if cv["u_Cv"] > cv["u_Cf"] else "does not beat") + " own fill here.")
        us = [(u, v) for u, v in acc_units.items() if re.match(rf"^{g}[a-z]?$", u)]
        for u, v in us:
            lines.append(f"- **R2-1b unit {u}:** γ {f(v['gamma'])} [{f(v['lo'])}, {f(v['hi'])}] per read item "
                         f"({v['n_read']:,} read, {v['n_inflight']:,} in-flight pairs at the read boundary).")
        if key in rh_goal:
            v = rh_goal[key]
            lines.append(f"- **R2-3 reset-and-hold (descriptive):** ΔC(1) {f(v['dC1'])} [{f(v['dC1_ci'][0])}, {f(v['dC1_ci'][1])}], "
                         f"κ_seg {f(v['kappa_seg'])}, scaled T {f(v['T'])} [{f(v['T_ci'][0])}, {f(v['T_ci'][1])}] "
                         f"({v['n_across1']} one-reset pairs).")
        summary = NATIVE_RESULTS.get(key)
        if summary:
            res_line, extra = summary(r2)
            lines = extra + lines
        else:
            ok = cv is not None and cv["u_Cv"] > cv["u_Cf"] and (cv.get("p_Cv") or 1) < 0.05
            res_line = ("conversation state carries more unique style share than own fill" if ok
                        else "conversation state does not beat own fill here" if cv else "not run")
        p.write_text(head + f"{MARK}\n**Round-2 result:** {res_line}.\n" + pred.rstrip() + "\n\n**Result (run 2026-10-05; `analysis/r2_run.py` → `data/processed/H73-style-three-components/r2/r2.json`):**\n" + "\n".join(lines) + "\n")
    # NE41
    p = PDIR / "NE41" / "README.md"
    txt = p.read_text(); i = txt.find(MARK); head, blk = txt[:i], txt[i:]
    pred = blk.split("\n", 2)[2]
    c0 = r2["c0"]; rh3 = r2["rh"]["III"]
    lines = [f"- **C0:** forced-erasure T_s (call rule, consecutive messages, copies removed): unscaled with same-agent cells only {f(c0['unscaled_own_only']['T'])} [{f(c0['unscaled_own_only']['T_ci'][0])}, {f(c0['unscaled_own_only']['T_ci'][1])}]; "
             f"scaled (R2-A5, agent-free fallback) {f(c0['scaled']['T'])} [{f(c0['scaled']['T_ci'][0])}, {f(c0['scaled']['T_ci'][1])}] ({c0['scaled']['T_n']:,} pairs).",
             f"- **R2-3 regime III (seen):** ΔC(1) {f(rh3['dC1'])} [{f(rh3['dC1_ci'][0])}, {f(rh3['dC1_ci'][1])}]; κ_seg {f(rh3['kappa_seg'])}; "
             f"ΔC_first {f(rh3['dC_first'])}, ΔC_late {f(rh3['dC_late'])}; carry-over {f(rh3['carry'], 2)} [{f(rh3['carry_ci'][0], 2)}, {f(rh3['carry_ci'][1], 2)}]; "
             f"scaled T (all one-reset pairs) {f(rh3['T'])} [{f(rh3['T_ci'][0])}, {f(rh3['T_ci'][1])}]."]
    okc = np.isfinite(rh3["carry"]) and rh3["carry"] < 0.3
    res = f"C0 scaled T_s {f(c0['scaled']['T'])}; regime-III offset carry-over {f(rh3['carry'], 2)} ({'redrawn' if okc else 'not shown to be redrawn'})"
    p.write_text(head + f"{MARK}\n**Round-2 result:** {res}.\n" + pred.rstrip() + "\n\n**Result (run 2026-10-05):**\n" + "\n".join(lines) + "\n")


def _g51(r2):
    o = r2["onset51"]; a = o["agents"].get("10", {})
    fit = a.get("fit", {})
    p1 = (a.get("A_ci", [0])[0] > 0 and 0.5 <= fit.get("tau", 0) <= 14 and a.get("tau_ci", [0, 99])[1] < 30
          and not (a.get("late_ci", [0])[0] > a.get("placebo_mean", np.inf)))
    n = r2["ne38"]
    lines = [f"- **R2-2-P1 Prankster:** τ {f(fit.get('tau'), 1)} days [{f(a.get('tau_ci', [np.nan])[0], 1)}, {f(a.get('tau_ci', [np.nan, np.nan])[1], 1)}], "
             f"A {f(fit.get('A'))} [{f(a.get('A_ci', [np.nan])[0])}, {f(a.get('A_ci', [np.nan, np.nan])[1])}], S∞ {f(fit.get('S_inf'))}; "
             f"k ≤ 2 mean {f(a.get('early'))}, k = 21–60 mean {f(a.get('late_w'))} [{f(a.get('late_ci', [np.nan])[0])}, {f(a.get('late_ci', [np.nan, np.nan])[1])}] vs placebo mean {f(a.get('placebo_mean'))} → **{'pass' if p1 else 'fail'}**.",
             f"- **R2-2-P2 incumbents:** early minus mid > 0 in {o['P2']['n_pos']}/{o['P2']['n']} (sign p {f(o['P2']['sign_p'], 3)}; median {f(o['P2']['median_diff'])}) → **{'pass' if o['P2']['sign_p'] < 0.05 else 'fail'}**.",
             f"- **NE38 (agent 40):** k = 0–2 shift {f(n['early'])}, k = 7–20 {f(n['later'])}; pseudo-dates " + ", ".join(f"{k[5:]} {f(v)}" for k, v in n["placebo_early"].items()) + f" → **{'met' if n['pass'] else 'not met'}** (descriptive)."]
    return (f"Prankster transient {'passes' if p1 else 'fails'} (τ {f(fit.get('tau'), 1)} d); incumbent onset transients sign p {f(o['P2']['sign_p'], 3)}", lines)


def _g12(r2):
    j = r2["judge_minutes"]
    lines = [f"- **R2-2c:** window mean projection {f(j['window_mean'])} ({j['n_judge']} judge messages); by minute " +
             ", ".join(f"{k} min {f(v[0])} (n {v[1]})" for k, v in j["bins"].items()) +
             f"; slope {f(j['slope_per10min'])} per 10 min (build-up p {f(j['p_buildup'], 3)}); 30 min after the window {f(j['post30_mean'])} (n {j['n_post']}). "
             f"(i) {'pass' if j['P_i'] else 'fail'}, (ii) {'pass' if j['P_ii'] else 'fail'}, (iii) {'pass' if j['P_iii'] else 'fail'}."]
    return (f"judge register by minute: step {'yes' if j['P_i'] else 'no'}, build-up {'no' if j['P_ii'] else 'yes'}, switch-off {'yes' if j['P_iii'] else 'no'}", lines)


NATIVE_RESULTS = {"G51": _g51, "G12": _g12}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--phase", choices=["predict", "results"], required=True)
    a = ap.parse_args()
    predict() if a.phase == "predict" else results()


if __name__ == "__main__":
    main()
