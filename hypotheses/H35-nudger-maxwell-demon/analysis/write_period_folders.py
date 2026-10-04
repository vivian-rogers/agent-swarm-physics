"""Write goalperiod-subhypotheses/<G..|NE..>/README.md for H35.

Mode --predictions (run 2026-10-03 before any real-data analysis): header, why, dated prediction, result pending.
Mode --results: keeps the prediction text verbatim and fills Verdict and Result from results.json (and the NE files).
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import h35lib as L  # noqa: E402

GP = L.HDIR / "goalperiod-subhypotheses"
DATE = "2026-10-03"

META = {
    "G27": ("Hack the OWASP Juice Shop", "2026-01-12 → 2026-01-23", "I", "K", 10, "NE10 before-period (no nudger)", "nudges 0"),
    "G30": ("Adopt a park and get it cleaned", "2026-02-09 → 2026-02-13", "I", "C", 12, "NE10: the nudger's first day (02-13)", "nudges 12"),
    "G31": ("Pick your own goal", "2026-02-16 → 2026-02-19 (02-20 = NE11 excluded)", "I", "F", 12, "regime I, first nudger week", "nudges 24"),
    "G33": ("Discuss the Pentagon-AI news", "2026-03-02 → 2026-03-04", "II", "C", 12, "regime II", "nudges 22"),
    "G35": ("Test your game", "2026-03-16 → 2026-03-20", "II", "C", 13, "regime II", "nudges 17"),
    "G36": ("Interact with agents outside the Village", "2026-03-23 → 2026-03-27", "II", "C", 13, "regime II/III boundary (03-24)", "nudges 6"),
    "G37": ("Pick your own goal", "2026-03-30 → 2026-04-01", "III", "F", 13, "first regime-III goal", "nudges 17"),
    "G38": ("Choose a charity and raise money", "2026-04-02 → 2026-04-24", "III", "C", 12, "17 days, second-largest nudge count", "nudges 108"),
    "G39": ("Build your own interactive world", "2026-04-27 → 2026-05-01", "III", "I", 15, "regime III", "nudges 7"),
    "G40": ("Connect your worlds into a 3D universe", "2026-05-04 → 2026-05-08", "III", "C", 15, "regime III, merged rooms (NE42)", "nudges 11"),
    "G41": ("Perform novel research", "2026-05-11 → 2026-05-15", "III", "I", 15, "regime III, third-largest nudge count", "nudges 59"),
    "G42": ("Run your own YouTube channel", "2026-05-18 → 2026-05-22", "III", "I", 15, "regime III", "nudges 25"),
    "G44": ("Finetune your leader", "2026-05-26 → 2026-05-29", "III", "C", 16, "regime III", "nudges 27"),
    "G51": ("Each agent: maximize your assigned goal", "2026-07-06 → 2026-08-19 (nudger on); off-step 08-21 → 09-02",
            "III", "P (I/K)", "21–32", "primary: 728 nudges, 8-h days, plus the undocumented nudger stop on 08-20", "nudges 728"),
}

ROLE = {"G51": "primary", "G38": "secondary", "G41": "secondary"}

PRED_COMMON_III = ("- **P1:** the nudger's state information I(M; D, G, K) is above the circular-shift null p95"
                   " (scored only with ≥ 15 nudges in the grid).\n"
                   "- **P2 (descriptive here):** first-nudge ATT on A30 reported with its day-bootstrap CI.\n")
PRED = {
    "G51": f"""*Written {DATE}, before running on this period.*
- **P1:** b = I(M; D, G, K)/r ∈ [3, 8] bits per nudge, above the circular-shift null p95. D and K together carry ≥ 60% of I(M;X); I(M;G|D) ≤ 25%; I(M;A|X) ≤ 15%; controller memory N adds ≥ 0.3 bits per nudge.
- **P2:** first-nudge ATT on A30 ∈ [0.5, 3] extra active minutes, CI excluding 0; placebo-window CI including 0; repeat-nudge ATT ≤ 50% of first; H04's future-isolated design smaller than the past-only design.
- **P3:** the shared gate model's kick × ln k slope < 0, or the cross-fitted response at K = 1 exceeds K ≥ 10; flatness rejected (bootstrap CI of the K=1 minus K≥10 response excludes 0).
- **P4:** ΔV_log > 0 (escapes per nudge vs random-gate); η_SU ≤ 0.5 and η_KW ≤ 0.3, with bootstrap upper ends < 0.7; κ ∈ [0.05, 0.5] extra active minutes per bit per nudge.
- **P5:** gate-once with k* ∈ {{1, 2}} has a cross-fitted value per nudge ≥ 1.25 × the logged nudger's.
- **P6 (off-step, 08-21 → 09-02):** (a) nudges buy ≤ 1% of active agent-minutes, so the active-fraction change after 08-20 is within 2 day-SDs; (b) gate DiD (trigger region vs below, after − before) < 0, with size near the accounting prediction (sign only; low power).
- **Verdict rule:** supported if P1–P5 all hold; failed if none holds; otherwise mixed. P6 is reported separately (natural experiment).
- **What would count against:** η_SU > 0.7 (efficient demon), a flat response (worthless information), an ATT CI including 0, or a placebo response.""",
    "G38": f"""*Written {DATE}, before running on this period.*
- **P1:** information above the circular-shift null p95.
- **P2:** first-nudge ATT point estimate > 0.
- **P3:** shared gate-model kick × ln k slope < 0 (sign).
- **P5:** gate-once (k* = 1 or 2) value per nudge ≥ the logged nudger's (point ratio ≥ 1).
- **Verdict rule:** supported if all four hold; failed if none; otherwise mixed. Lower power than G51 (108 nudges, 4-h days).""",
    "G41": f"""*Written {DATE}, before running on this period.*
- **P1:** information above the circular-shift null p95.
- **P2:** first-nudge ATT point estimate > 0.
- **P3:** shared gate-model kick × ln k slope < 0 (sign).
- **P5:** gate-once (k* = 1 or 2) value per nudge ≥ the logged nudger's (point ratio ≥ 1).
- **Verdict rule:** supported if all four hold; failed if none; otherwise mixed. Low power (59 nudges, 5 days).""",
}
for g in ("G37", "G39", "G40", "G42", "G44"):
    PRED[g] = f"*Written {DATE}, before running on this period.*\n" + PRED_COMMON_III + \
        "- **Verdict:** descriptive (too few nudges for the gate model and policy values; numbers reported, not scored beyond P1)."
for g in ("G31", "G33", "G35", "G36"):
    PRED[g] = (f"*Written {DATE}, before running on this period.*\n"
               "- No pause gates in regime I/II: X = (D, K = current run of consecutive WAITs).\n" + PRED_COMMON_III +
               "- **Verdict:** descriptive (P1 scored only with ≥ 15 nudges).")

NE10_PRED = f"""*Written {DATE}, before running.*
- **P7:** work accounting predicts that the switch-on changes active agent-minutes by ≤ 0.5% (nudges/day × per-nudge work ÷ present agent-minutes), i.e. undetectable against day-to-day noise; the observed change is reported with a placebo split. The nudger's information in G30 + G31 is above the circular-shift null (scored per period with ≥ 15 nudges: G31 only).
- **What would count against:** an observed active-fraction change far larger than the accounting bound that survives the placebo split would mean the nudger acts through more than its direct per-nudge work (a field on everyone, HH52), or a confound."""


def header(g, verdict="pending"):
    t, dates, reg, mode, n, why, nn = META[g]
    role = ROLE.get(g, "exploratory (descriptive)") if g not in ("G27", "G30") else "NE10 component"
    return (f"# H35 × {g}: {t} ({dates})\n\n**Verdict:** {verdict}\n**Role:** exploratory (round 1, non-holdout); {role}\n"
            f"**Period:** regime {reg} · mode {mode} · {n} agents · {nn}. Data: `data/processed/H35-nudger-maxwell-demon/{g}/`.\n\n"
            f"## Why this period\n{why}.\n\n")


def write_predictions():
    for g in META:
        if g in ("G27", "G30"):
            continue
        d = GP / g
        d.mkdir(parents=True, exist_ok=True)
        (d / "figures").mkdir(exist_ok=True)
        txt = header(g) + f"## Prediction\n{PRED[g]}\n\n## Result\nPending.\n\n## Scorecard (period-specific axes)\nPending.\n\n## Notes\n- {DATE}: folder created with the prediction, before the run.\n"
        (d / "README.md").write_text(txt)
    d = GP / "NE10"
    d.mkdir(parents=True, exist_ok=True)
    (d / "figures").mkdir(exist_ok=True)
    (d / "README.md").write_text(
        "# H35 × NE10: the auto-nudger switched on (CHANGELOG 2026-02-10; first nudge 2026-02-13, inside #30)\n\n"
        "**Verdict:** pending\n**Role:** exploratory (natural experiment, non-holdout)\n"
        "**Period:** regime I · before = #27 (01-12 → 01-23) + #30's nudge-free days 02-09 → 02-12 (#28, #29 held out); "
        "after = 02-13 (#30) + #31 (02-16 → 02-19; 02-20 = NE11 excluded). Data: `data/processed/H35-nudger-maxwell-demon/NE10/`.\n\n"
        "## Why this period\nThe only documented switch-on of the nudger outside the holdout. H04 found the escape hazard from long inactivity fell after it (opposite to its prediction), with goal changes and roster joins as confounds.\n\n"
        f"## Prediction\n{NE10_PRED}\n\n## Result\nPending.\n\n## Scorecard (period-specific axes)\nPending.\n\n## Notes\n- {DATE}: folder created with the prediction, before the run.\n")


# ------------------------------------------------------------------------------------------------ results mode

def _r(p):
    return json.loads((L.OUT / p / "results.json").read_text())


def fmt(x, n=2):
    if x is None:
        return "–"
    try:
        return f"{x:.{n}f}"
    except Exception:
        return str(x)


def ci(v, n=2):
    if not v or v[0] is None:
        return "–"
    if v[1] is None or (isinstance(v[1], float) and v[1] != v[1]):
        return f"{fmt(v[0], n)} (no CI)"
    return f"{fmt(v[0], n)} [{fmt(v[1], n)}, {fmt(v[2], n)}]"


def common_rows(r):
    i, w = r["info"], r["work"]
    rows = [("information used, b = I(M;D,G,K)/r", f"{fmt(i['I_X']['bits_per_nudge'])} bits per nudge of {fmt(i['H_M_bits_per_nudge'], 1)} bits decision entropy; within-day part {fmt(i['I_X_withinday']['bits_per_nudge'])}",
             "permutation null p95", "above" if i["I_X"]["above_null"] else "not above"),
            ("decomposition (bits per nudge)", f"I(M;K) {fmt(i['I_K']['bits_per_nudge'])}, I(M;G|D) {fmt(i['I_G_given_D']['bits_per_nudge'])}, I(M;K|D,G) {fmt(i['I_K_given_DG']['bits_per_nudge'])}, I(M;D) {fmt(i['I_D']['bits_per_nudge'])}; agent | X {fmt(i['I_A_given_X']['bits_per_nudge'])}; controller memory | X {fmt(i['I_N_given_X']['bits_per_nudge'])}", "within-stratum permutation", ""),
            ("first-nudge ATT, A30 (strict isolation)", f"{ci(w['first_pastonly']['y30'])}, n = {w['first_pastonly']['n']}", "0", ""),
            ("first-nudge ATT, A30 (H04 isolation set)", f"{ci(w['first_pastonly_H04iso']['y30'])}, n = {w['first_pastonly_H04iso']['n']}; placebo {ci(w['first_pastonly_H04iso']['ypre'])}", "0", "")]
    g = r.get("gate")
    if g:
        es = g["eff_escapes_separate"]; f = g["fit"]["separate"]
        esc = "; ".join(f"k {['1', '2–3', '4–9', '≥10'][x['Kb'] - 1]}: {fmt(x['escape'])} (n {x['n']}){' nudged' if x['M'] else ''}" for x in g["escape_by_K_nudge"])
        rows.append(("gate escape by trap age (un-nudged / nudged)", esc, "", ""))
        rows.append(("gate model (card), nudge × ln k", f"{fmt(f['beta']['nudge_x_lnk'])} ± {fmt(f['se']['nudge_x_lnk'])}", "0", ""))
        if "ratio_gate_once2_vs_logged" in es:
            rows.append(("value per nudge (escapes): random-gate / logged / once at k=1 / k=2",
                         f"{fmt(es['V_rand_per_nudge'], 3)} / {fmt(es['V_log_per_nudge'], 3)} / {fmt(es['gate_once']['1'], 3)} / {fmt(es['gate_once']['2'], 3)} (ratios to logged {fmt(es['ratio_gate_once1_vs_logged'])}, {fmt(es['ratio_gate_once2_vs_logged'])})", "", ""))
    return rows


def table(rows):
    esc = lambda x: str(x).replace("|", "\\|")
    out = "| Quantity | Observed | Null / reference | Verdict |\n| --- | --- | --- | --- |\n"
    return out + "\n".join(f"| {esc(a)} | {esc(b)} | {esc(c)} | {esc(d)} |" for a, b, c, d in rows) + "\n"


VERDICTS = {}
RESULT_TEXT = {}
SCORE_TEXT = {}


def write_results():
    for g in META:
        if g in ("G27", "G30"):
            continue
        d = GP / g
        txt = (d / "README.md").read_text()
        r = _r(g)
        verdict = VERDICTS.get(g, "descriptive")
        body = RESULT_TEXT.get(g, "") + "\n" + table(common_rows(r)) + \
            f"\nData: `data/processed/H35-nudger-maxwell-demon/{g}/results.json` (built {DATE}).\n"
        txt = re.sub(r"\*\*Verdict:\*\* [^\n]*", f"**Verdict:** {verdict}", txt, count=1)
        txt = re.sub(r"## Result\n.*?\n## Scorecard", "## Result\n" + body + "\n## Scorecard", txt, count=1, flags=re.S)
        txt = re.sub(r"## Scorecard \(period-specific axes\)\n.*?\n## Notes", "## Scorecard (period-specific axes)\n" +
                     SCORE_TEXT.get(g, "C 0 · D 0 · E 0 · G 0 (descriptive period; too few nudges to score).") + "\n\n## Notes", txt, count=1, flags=re.S)
        if "results filled" not in txt:
            txt = txt.rstrip() + f"\n- {DATE}: results filled from the round-1 run (after the prediction above).\n"
        (d / "README.md").write_text(txt)
    print("results written")


VERDICTS.update({"G51": "mixed", "G38": "mixed", "G41": "mixed"})
RESULT_TEXT["G51"] = """**Outcome vs prediction** (run 2026-10-03; numbers from `results.json` and `G51off/offstep_results.json`).

| Prediction | Predicted | Observed | Verdict |
| --- | --- | --- | --- |
| P1 information | b ∈ [3, 8]; D+K ≥ 60%; I(M;G given D) ≤ 25% (card: G given (D,K)); agent ≤ 15%; memory ≥ 0.3 | b = 1.42 bits per nudge (13% of the 10.7-bit decision entropy), above null; D+K 89%; I(M;G given D) 0.93 bits (65%, fails this wording), G given (D,K) 0.15 bits (11%, meets the card wording); agent given X 0.43 bits (31%); memory 0.32 | **partly**: magnitude ~2.5× lower than predicted; not agent-blind; the gate-timing clause depends on wording |
| P2 work | ATT ∈ [0.5, 3], CI excl. 0; placebo ∋ 0; repeat ≤ 50% of first; H04 design smaller | 1.45 [0.72, 2.20] (n 235; tool turns +6.2 [2.7, 11.0]); placebo 0.38 [−0.08, 0.86]; repeat 1.04 [0.37, 1.76] (71%); H04 design 1.40 | **mostly**: repeat clause fails (repeat placebo 0.5, selection) |
| P3 state dependence | shared slope < 0 or response(k = 1) > response(k ≥ 10); flatness rejected | shared-model slope −0.01 ± 0.05 (flat; set by mentions); cross-fitted gate response 0.23 (k = 1) vs 0.08 (k ≥ 10) escapes, k=1 minus k≥10 CI [0.07, 0.19]; card gate model nudge × ln k = −0.32 ± 0.13; minute response by trap age 0.02 / 2.22 / 2.61 / 2.32 / 0.52 min (k = 0 / 1 / 2–3 / 4–9 / ≥ 10); k 1–9 minus k ≥ 10 = 1.86 [0.47, 3.53] | **supported** |
| P4 inefficient demon (gate level) | ΔV_log > 0; η_SU ≤ 0.5, η_KW ≤ 0.3 (upper < 0.7); κ ∈ [0.05, 0.5] | among pause gates the logged choice is **worse than random**: ΔV = −0.076 (card model), −0.042 [−0.062, −0.024] (shared) escapes per nudge; η_SU < 0, η_KW = 0 | **failed as worded** (negative value of information, a stronger inefficiency than predicted) |
| P4 in the minute trap-age space (same estimators, work in minutes; added in round 1) | as above | ΔV = +0.50 [−0.09, 1.16] min per nudge; η_SU = 0.38 [−0.08, 0.68]; η_KW = 0.15 [0, 0.48]; κ = 0.49 [−0.10, 1.11] min per bit per nudge | bands met (secondary) |
| P5 better policy | once at k* ∈ {1, 2} ≥ 1.25 × logged | escapes: ×2.18 / ×2.01 (card model), ×1.55 [1.26, 1.84] / ×1.58 [1.34, 1.81] (shared); minutes: nudging only at k = 2–3 ×2.31 [1.66, 5.20] | **supported** |
| P6a off-step accounting | nudges ≤ 1% of active minutes; abs(Δ) < 2 day-SD | nudges buy 0.50% of active agent-minutes; predicted Δ active fraction −0.24 pp; observed −1.4 pp [−4.8, +2.0] (placebo split −2.9 pp; day SD 8.2 pp) | **supported** (undetectable, as predicted) |
| P6b off-step gate DiD | < 0, near the accounting (−0.005) | −0.050 [−0.099, −0.005]; placebo split −0.032 [−0.066, +0.009]; P(chain reaches k ≥ 10 given k ≥ 4) 0.245 → 0.296 | **inconclusive**: right sign but 10× the accounting and similar to the in-period drift |

**Where the nudges go.** Nudge rate per 1,000 agent-minutes rises from 0.55 (not in a pause chain) to 10.7 (k ≥ 10); 38% of nudges hit chains ≥ 10 re-pauses deep, where a nudge buys 0.5 min, and 23% hit agents not in a chain, where it buys ~0. Median 133 s after the agent's latest PAUSE; 72% land during a pause.

**Three nested views of efficiency.** (i) Coarse (pause status × idle duration): the nudger knows who is idle, and that information is used fairly well (η_SU 0.67–0.71, η_KW 0.50–0.55, κ ≈ 1.2 min per bit). (ii) Trap age at minute level: η_SU 0.38, η_KW 0.15. (iii) Among pausing agents (gate level): worse than random. The inefficiency is in the fine choice, not in detecting idleness.
"""
RESULT_TEXT["G38"] = """**Outcome vs prediction.** P1 supported (b = 1.25, above null). P2 supported on the point (ATT 1.27 [−0.32, 2.91], n 25). **P3 failed:** the card gate model gives nudge × ln k = +1.18 ± 0.52 (the effect *rises* with trap age). P5 supported on the point for k* = 2 (×1.02), not for k* = 1 (×0.66).

**Mechanism differs from G51.** Before 06-11 the default pause was 12 h, so a nudge (an @-mention) wakes a pausing agent: escape at nudged gates is 0.86–1.0 at every trap age vs 0.20–0.51 un-nudged. Targeting then matters little (logged ≈ random among gates, ΔV = −0.04 escapes per nudge).
"""
RESULT_TEXT["G41"] = """**Outcome vs prediction.** P1 supported but weak (b = 0.44, above null; agent identity and controller memory carry more than the state, 1.16 and 1.20 bits). P2 untestable under strict isolation (no first nudge without another direct kick in 30 min); with H04's isolation set the ATT is 3.25 [2.52, 4.91] (placebo 0.63 [−0.02, 2.17]). **P3 failed as worded:** the shared-model slope is +0.36 ± 0.40 (the card model gives −0.24 ± 0.90; both uninformative). P5 supported on the point (×1.01 / ×1.11). Long-pause regime as in G38 (nudged gates escape 0.33–1.0).
"""
for g, b in (("G37", 2.20), ("G42", 1.37), ("G44", 1.19)):
    RESULT_TEXT[g] = f"Descriptive. P1 (≥ 15 nudges): information above the permutation null (b = {b:.2f}). Gate-level numbers rest on 8–10 nudged gates and are not interpreted; long-pause regime (nudged gates escape at high rates).\n"
RESULT_TEXT["G33"] = "Descriptive. P1 scored (15 nudges in the grid): **not above** the permutation null (b ≈ 0). Regime II: X = (idle duration, WAIT run); strict isolation leaves no first nudge.\n"
for g in ("G31", "G35", "G36", "G39", "G40"):
    RESULT_TEXT[g] = "Descriptive; fewer than 15 nudges in the grid, so P1 is not scored. Numbers below are for completeness only.\n"
SCORE_TEXT["G51"] = "C 1 (beats the random-nudging and permutation nulls; placebo window clean for the strict design) · D 1 (response heterogeneity and the off-step accounting predicted before the run) · E 1 (off-step accounting matches; the gate DiD is not attributable) · G 1 (H04's nudge A30 reproduced, 1.45 vs 1.54; H16's gate response)."
SCORE_TEXT["G38"] = "C 1 · D 0 (P3 failed) · E 0 · G 1 (H09: only @-mentions get through a pause, seen here as the wake-up effect)."
SCORE_TEXT["G41"] = "C 1 (information above null) · D 0 · E 0 · G 0."
RESULT_TEXT["G38"] = RESULT_TEXT["G38"].replace("the card gate model gives nudge × ln k = +1.18 ± 0.52", "the shared-model slope is +0.59 ± 0.25 and the card model gives nudge × ln k = +1.18 ± 0.52")


if __name__ == "__main__":
    if "--predictions" in sys.argv:
        write_predictions()
        print("prediction folders written")
    if "--results" in sys.argv:
        write_results()
