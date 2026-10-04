"""Write H17 goal-period folders (G<NN>/README.md).

--predict  creates each folder with its dated prediction and 'Verdict: pending' (run BEFORE run_period.py).
--results  fills Result, Scorecard and Verdict from data/processed/H17-behavior-metastable-sets/G<NN>/result.json,
           keeping the prediction text exactly as written.

Usage: uv run python hypotheses/H17-behavior-metastable-sets/analysis/write_period_folders.py --predict|--results
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
CARD = HERE.parent
ROOT = CARD.parents[1]
DATA = ROOT / "data/processed/H17-behavior-metastable-sets"
sys.path.insert(0, str(HERE))
from periods import PERIODS, REGIME3  # noqa: E402

MODE_NAME = {"C": "shared objective", "I": "each agent its own objective", "K": "competition", "F": "free / none",
             "M": "mixed", "I/K": "individual roles, some competing"}


def goal_meta():
    md = (ROOT / "hypotheses/hypohypotheses/goal-periods.md").read_text()
    meta = {}
    for m in re.finditer(r"^\| (\d+) \| (\S+) → (\S+) \| (\S+) \| (\S+) \| (\S+) \| (\S+) \| (\S+) \| (\S+) \|", md, re.M):
        g = int(m.group(1))
        meta[g] = {"start": m.group(2), "end": m.group(3), "d": m.group(4), "N": m.group(5), "reg": m.group(7),
                   "mode": m.group(9)}
    for m in re.finditer(r"^### (\d+) · (.+)$", md, re.M):
        meta.setdefault(int(m.group(1)), {})["title"] = m.group(2).strip()
    return meta


def why(g, reg):
    if g == 51:
        return ("The longest stationary-ish window (45 non-holdout days, 8 h/day, 21 → 32 agents): the most power for "
                "per-agent MSMs, and the only period where weekly blocks can measure within-period drift of t2* "
                "(O10) against the between-period spread (P4a).")
    if g == 37:
        return "First regime-III period and a free-choice period: the undriven reference for P4d."
    if g == 31:
        return "Regime-I free-choice period (about nine agents converged on one task): the undriven regime-I reference for P4d."
    if g == 38:
        return ("Longest 4-h regime-III period (17 days): the most power of the 4-h periods. Outreach approval (G) "
                "arrives on 04-14 inside the period (descriptive only, no prediction).")
    if reg == "III":
        return "A regime-III non-holdout period: one of the 8 periods for the primary tests (P3b, Holm across periods) and for P4."
    if reg == "II":
        return "Regime II (rooms + discrete sessions): comparison period between regimes I and III (descriptive for P4c)."
    return ("Regime-I comparison period (one room, discrete computer sessions): sets the regime-I distribution of t2* "
            "for P4c and for the #32 confirmation (P9).")


def prediction(g, reg):
    common = [
        "- **CK (P2):** the crisp-set CK test passes at τ_c = 5 min (max |Δ| < 0.05 for k ≤ 4).",
        "- **P3b (sets beyond sticky states):** t2\\* above the N2 sojourn-null 95th percentile and t2\\*/median(N2) ≥ 1.25.",
        "- **P8:** the MSM beats R1 (sticky-only) and M0 on held-out days at τ_c.",
        "- **P3a:** t2\\* above the N1 shuffled floor.",
        "- **P5:** per-agent I² of ln t2 ≥ 0.5 (if ≥ 3 agents qualify).",
    ]
    if reg == "III":
        common += [
            "- **P3d:** idle sits in a set of its own (alone or with consolidate) in the m = 2 split.",
            "- **P3e:** 5 ≤ t2\\* ≤ 60 active minutes.",
            "- **P6:** max |δ_i| ≥ 0.1 with a bootstrap CI excluding 0; if the m = 2 cores are a work state and idle, chat has q⁺ > 0.5 and 1 − q⁻ < 0.5.",
            "- **P7:** σ(τ = 1) above the N2 95th percentile; σ_macro/σ_micro (m = 3) < 0.5.",
        ]
    else:
        common += [
            "- **P4c (regime part):** t2\\* above the median of the regime-III periods (session on/off makes a slow two-set process).",
            "- **Regime-I set identity (credence 0.6):** the m = 2 split separates in-session computer work (browse/type/shell) from out-of-session states (chat/idle/session events).",
        ]
    if g == 51:
        common += ["- **O10/P4a:** the between-week CV of t2\\* inside #51 is smaller than the between-period CV of the regime-III periods."]
    if g in (31, 37):
        common += ["- **P4d:** this free-choice period is not the fastest (smallest t2\\*) of its regime. Descriptive."]
    return common


def write_predict():
    meta = goal_meta()
    for g, reg in PERIODS.items():
        d = CARD / "goalperiod-subhypotheses" / f"G{g:02d}"
        (d / "figures").mkdir(parents=True, exist_ok=True)
        f = d / "README.md"
        if f.exists():
            print("exists, not overwriting:", f)
            continue
        m = meta.get(g, {})
        mode = m.get("mode", "?")
        lines = [
            f"# H17 × G{g:02d}: {m.get('title', '')} ({m.get('start', '?')} → {m.get('end', '?')})", "",
            "**Verdict:** pending",
            "**Role:** exploratory",
            f"**Period:** regime {reg} · mode {mode} ({MODE_NAME.get(mode, '')}) · N = {m.get('N', '?')} at start · "
            f"{m.get('d', '?')} active days" + (" (non-holdout days 07-06 → 09-04 only; the #51 tail is held out)" if g == 51 else "") + ".", "",
            "## Why this period", why(g, reg), "",
            "## Prediction",
            "*Written 2026-10-03, before running on this period.* The card's predictions (`../../README.md`, \"Prediction\") as they apply here; "
            "states = H14 coarse 6-state minute grid, pooled MSM over present agent-days, τ_c = 5 min:",
            *prediction(g, reg),
            "", "Verdict rule (card): **supported** if CK passes, P3b holds and P8 holds; **mixed** if exactly one of CK or P3b fails; **failed** if both fail.",
            "", "## Result", "*Pending.*", "", "## Scorecard (period-specific axes)", "*Pending.*", "", "## Notes", ""]
        f.write_text("\n".join(lines))
        print("wrote", f)


def fmt(v, nd=2):
    if v is None:
        return "–"
    if isinstance(v, bool):
        return "yes" if v else "no"
    if isinstance(v, (int,)):
        return str(v)
    try:
        return f"{v:.{nd}f}"
    except (TypeError, ValueError):
        return str(v)


def write_results():
    for g, reg in PERIODS.items():
        f = CARD / "goalperiod-subhypotheses" / f"G{g:02d}" / "README.md"
        rj = DATA / f"G{g:02d}" / "result.json"
        if not (f.exists() and rj.exists()):
            continue
        r = json.loads(rj.read_text())
        t = f.read_text()
        v = r["verdict"]
        t = re.sub(r"^\*\*Verdict:\*\* .*$", f"**Verdict:** {v['verdict']}", t, flags=re.M)
        p = r["primary"]
        p["dll_R1"] = p["ll_tauc"]["M1"] - p["ll_tauc"]["R1"]
        p["dll_M0"] = p["ll_tauc"]["M1"] - p["ll_tauc"]["M0"]
        p["folds_R1"] = f"{p['folds_beat_R1_tauc']}/{p['folds_tauc']} folds"
        p["n_agents"] = len(p["per_agent"])
        p["w5_shift"] = None  # n/a: action-composition vectors violate the shifted estimator's independent-noise assumption
        rows = [
            "| Prediction | Observed | Null / reference | Verdict |", "| --- | --- | --- | --- |",
            f"| P2 CK passes at τ_c (max \\|Δ\\| < 0.05, k ≤ 4) | max \\|Δ\\| = {fmt(p['ck_max'], 3)}; bootstrap-significant: {fmt(p['ck_sig_fail'])} | — | {'pass' if v['ck_pass'] else 'fail'} |",
            f"| P2 ITS plateau by τ ≤ 15 min | τ\\* = {fmt(p['plateau_tau'])} | — | {'pass' if p['plateau_tau'] is not None else 'no plateau'} |",
            f"| P3a t2\\* > N1 | t2\\* = {fmt(p['t2'], 1)} min [{fmt(p['t2_ci'][0], 1)}, {fmt(p['t2_ci'][1], 1)}] | N1 p95 {fmt(p['n1_p95'], 1)} | {'pass' if p['t2'] > p['n1_p95'] else 'fail'} |",
            (f"| P3b t2\\* > N2 and ratio ≥ 1.25 (400 surrogates, Holm across the 8 regime-III periods) | ratio t2\\*/N2 median = {fmt(p['t2'] / p['n2_med_400'])}; Holm p = {fmt(p['n2_p_holm'], 3)} | N2 median {fmt(p['n2_med_400'], 1)}; N3 median {fmt(p['n3_med'], 1)} | {'pass' if v['p3b'] else 'fail'} |"
             if 'n2_med_400' in p else
             f"| P3b t2\\* > N2 p95 and ratio ≥ 1.25 | ratio t2\\*/N2 median = {fmt(p['t2'] / p['n2_med'] if p['n2_med'] else None)} | N2 median {fmt(p['n2_med'], 1)}, p95 {fmt(p['n2_p95'], 1)}; N3 median {fmt(p['n3_med'], 1)} | {'pass' if v['p3b'] else 'fail'} |"),
            f"| P3c m ∈ {{2,3}}, crispness ≥ 0.75, t2/t3 ≥ 2 | m = {p['m']}, crispness {fmt(p['crispness'])}, t2/t3 = {fmt(p['sep'], 1)} | — | {'pass' if v['p3c'] else 'fail'} |",
            f"| sets (m = 2 split) | {p['sets_m2']} | — | {('idle alone/with consolidate: ' + fmt(v['p3d'])) if reg == 'III' else 'descriptive'} |",
            f"| sets (m = {p['m']}) | {p['sets_m']} | — | descriptive |",
            f"| R1 sticky-only t2 at τ_c | t2\\*/t2_R1 = {fmt(p['t2'] / p['t2_R1'] if p['t2_R1'] else None)} | t2_R1 = {fmt(p['t2_R1'], 1)} | descriptive |",
            f"| P8 MSM beats R1 and M0 on held-out days | ΔLL/pair vs R1 = {fmt(p['dll_R1'], 4)} ({p['folds_R1']}); vs M0 = {fmt(p['dll_M0'], 4)} | — | {'pass' if v['p8'] else 'fail'} |",
            f"| order 2 vs 1 (τ = 1) | ΔLL/transition = {fmt(p['dll_o2'], 4)} | — | {'order 2 better' if (p['dll_o2'] or 0) > 0 else 'order 1 suffices'} |",
            f"| P5 per-agent I² of ln t2 | I² = {fmt(p['I2'])} ({p['n_agents']} agents; block-bootstrap SEs); own/shrink beats pooled for {fmt(p['frac_agent_beats'])} of agents | — | {'pass' if v['p5'] else ('n/a' if v['p5'] is None else 'fail')} |",
            f"| P6 committor asymmetry max \\|δ\\| | {fmt(p['delta_max'], 3)} (CI excl. 0: {fmt(p['delta_sig'])}); cores {p['cores']} | 0 under detailed balance | {('pass' if v['p6'] else 'fail') if reg == 'III' else 'descriptive'} |",
            f"| P7 σ(τ=1) > N2 p95; σ_macro/σ_micro < 0.5 | σ = {fmt(p['ep'], 4)} nats/min; macro share {fmt(p['ep_macro_share'])} | N2 p95 {fmt(p['ep_n2_p95'], 4)} | {('pass' if v['p7'] else 'fail') if reg == 'III' else 'descriptive'} |",
            f"| mixing time t_mix(¼) | {fmt(p['t_mix'], 0)} min | — | descriptive |",
            f"| R3 half-day t2\\* (first / second half) | {fmt(p['t2_half1'], 1)} / {fmt(p['t2_half2'], 1)} | — | descriptive |",
            f"| robustness: 5-min windows (hard / soft counts / shifted = n/a) | {fmt(p['w5_hard'], 1)} / {fmt(p['w5_soft'], 1)} / {fmt(p['w5_shift'], 1)} min | — | descriptive |",
            f"| robustness: records (≈5-min lag) | t2 ≈ {fmt(p['rec_t2_min'], 1)} min | — | descriptive |",
            f"| stuckness covariates | error share {fmt(p['err_share'], 3)}; output {fmt(p['out_rate'], 2)}/agent-h; idle share {fmt(p['idle_share'])} | — | for P4b |",
        ]
        extra = r.get("extra_lines", [])
        res = ("*Run 2026-10-03* (`analysis/run_period.py`; numbers in `data/processed/H17-behavior-metastable-sets/"
               f"G{g:02d}/result.json`; figure `figures/its_ck.pdf`).\n\n" + "\n".join(rows) + ("\n\n" + "\n".join(extra) if extra else ""))
        t = re.sub(r"## Result\n.*?\n## Scorecard", "## Result\n" + res.replace("\\", "\\\\") + "\n\n## Scorecard", t, flags=re.S)
        sc = r.get("scorecard_lines", [])
        t = re.sub(r"## Scorecard \(period-specific axes\)\n.*?\n## Notes", "## Scorecard (period-specific axes)\n" + "\n".join(sc).replace("\\", "\\\\") + "\n\n## Notes", t, flags=re.S)
        notes = r.get("notes", [])
        if notes and "## Notes\n" in t and not any(n in t for n in notes):
            t = t.replace("## Notes\n", "## Notes\n" + "\n".join(notes) + "\n", 1)
        f.write_text(t)
        print("results ->", f)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--predict", action="store_true")
    ap.add_argument("--results", action="store_true")
    a = ap.parse_args()
    if a.predict:
        write_predict()
    if a.results:
        write_results()
