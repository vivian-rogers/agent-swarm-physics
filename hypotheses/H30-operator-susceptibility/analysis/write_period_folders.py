"""Write goalperiod-subhypotheses/G<NN>/README.md for H30.

--predict : writes the header, why-this-period and the dated prediction (before the period is run).
--results : fills Verdict and Result from data/processed/H30-operator-susceptibility/G<NN>/results.json, keeping the
            prediction text exactly as written.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from h30lib import HYP, OUT, ROOT  # noqa: E402

PERIODS = ["G04", "G05", "G06", "G13", "G30", "G31", "G33", "G35", "G37", "G38", "G39", "G40", "G41", "G42", "G44", "G51"]
PRED_DATE = "2026-10-03"

WHY = {
    "G04": "Regime I, 4 agents, 2 h days, public chat: the densest human input in the data (≈ 69 human messages/day, 336 naming an agent). The best period for the human content gauge and a long (25-day) daily series.",
    "G05": "Regime I holiday week with very dense human chat (≈ 176 messages/day over 5 days): many kicks per day, few days.",
    "G06": "Regime I merch-store competition, 15 days, ≈ 30 human messages/day: a second long human-dense daily series.",
    "G13": "Regime I, 6 agents, a human-subjects experiment week with ≈ 5 human messages/day: a low-dose human period (10 days).",
    "G30": "Regime I; the nudger switches on 2026-02-13 (NE10) inside this period (12 nudges): the first nudges.",
    "G31": "Regime I free week, 25 nudges; first week of the nudger at full strength.",
    "G33": "Regime II (rooms + sessions), 3 days, 22 nudges.",
    "G35": "Regime II, 5 days, 17 nudges; the #best/#rest split (NE15) on its first day.",
    "G37": "First regime-III goal (3 days, 20 nudges).",
    "G38": "Regime III, 17 days, 110 nudges with tailored content: the second-longest nudge series; NE17 (04-14) and NE18 (04-20) inside.",
    "G39": "Regime III, 5 days, 7 nudges and 13 human messages: low power.",
    "G40": "Regime III, 5 days, 11 nudges; rooms merged (NE42).",
    "G41": "Regime III, 5 days, 59 nudges (≈ 12/day) with tailored content.",
    "G42": "Regime III, 5 days, 25 nudges.",
    "G44": "Regime III, 4 days, 27 nudges and 59 human messages (the fine-tuned-leader week, non-holdout).",
    "G51": "Regime III, 8 h days, up to 32 agents, 729 nudges over the 45 non-holdout days (≈ 16/day, nearly pure template): the main daily series. #51 tail (09-07 → 09-21) is held out.",
}

PRED = {
    "human_dense": [
        "P3: χ_act(H_men) > χ_act(H_und), ratio ≥ 2; χ_act(H_und) > 0 (CI excluding 0 counts toward the 2-of-3 rule over G04–G06).",
        "P4: χ_con(H_und or H_men) > 0 with CI excluding 0, size 0.02–0.10; H_men ≥ H_und.",
        "P6: the daily human *content* gauge has permutation-calibrated R₁ < 0.5; the activity heterogeneity test is not run (dense chat, A1).",
        "Against: χ_con ≤ 0 or χ_act(H_men) ≤ χ_act(H_und).",
    ],
    "nudge_low": [
        "P1: χ_act(N_tgt) point estimate > 0 (CI expected to include 0 at this dose).",
        "P2: χ_act(N_by) within ±0.15 min of 0 if estimable.",
        "No stability statistics (too few days or kicks); the daily series is descriptive.",
        "Against (weakly): a negative point estimate with CI excluding 0.",
    ],
    "G38": [
        "P1: χ_act(N_tgt) > 0 with CI excluding 0, 0.8–2.5 min.",
        "P2: χ_act(N_by) within ±0.15 min of 0; χ_coll within a factor 1.5 of χ_act(N_tgt).",
        "P5: χ_con(N_tgt) may be > 0 (tailored nudges); no threshold. Bias bound −0.02 (A1).",
        "P6: permutation test does not reject a constant daily χ_act(N_tgt); R₁ < 0.3.",
        "P7: per-kick slope of the activity response on goal day has a CI including 0.",
        "P8 (low power): the per-kick slope on turns since reset is negative.",
        "P11: pre-window placebo for N_tgt within ±0.5 min; day-swap null band includes 0.",
    ],
    "G41": [
        "P1: χ_act(N_tgt) > 0 (point; CI may include 0 with 5 days).",
        "P2: χ_act(N_by) within ±0.15 min of 0.",
        "P5: χ_con(N_tgt) may be > 0 (tailored nudges).",
    ],
    "G44": [
        "P1: χ_act(N_tgt) point estimate > 0.",
        "P3: χ_act(H_men) > χ_act(H_und); per-recipient human χ_act below regime I's.",
        "P4: χ_con(H_und) > 0 (point; CI may include 0 with 4 days).",
    ],
    "G51": [
        "P1: χ_act(N_tgt) > 0 with CI excluding 0, 0.8–2.5 min.",
        "P2: χ_act(N_by) within ±0.15 min of 0; χ_coll per nudge within a factor 1.5 of χ_act(N_tgt).",
        "P5: χ_con(N_tgt) within ±0.02 with CI including 0 (template nudges; bias bound −0.02).",
        "P6: permutation test does not reject a constant daily χ_act(N_tgt); permutation-calibrated R₁ < 0.3; lag-1 autocorrelation of the daily series not distinguishable from 0; ≥ 5-day windows needed.",
        "P7: per-kick slope on goal day has a CI including 0 (no aging; HH116 fails).",
        "P8: activity response early in the context cycle (turns 0–13) ≥ 1.3 × late (28+), and the per-kick slope on turns since reset < 0 (credence ~40%).",
        "P10: no lab's χ_act(N_tgt) differs from the pooled value after Holm correction.",
        "P11: pre-window placebo within ±0.5 min; day-swap null band includes 0; pseudo-true content null centered on 0.",
        "Against P6 (for HH116): permutation p < 0.05 with R₁ ≥ 0.5 and positive lag-1 autocorrelation.",
    ],
}
KIND = {"G04": "human_dense", "G05": "human_dense", "G06": "human_dense", "G13": "human_dense",
        "G30": "nudge_low", "G31": "nudge_low", "G33": "nudge_low", "G35": "nudge_low", "G37": "nudge_low",
        "G39": "nudge_low", "G40": "nudge_low", "G42": "nudge_low", "G38": "G38", "G41": "G41", "G44": "G44", "G51": "G51"}


def goal_meta():
    txt = (ROOT / "hypotheses/hypohypotheses/goal-periods.md").read_text()
    titles = {int(m.group(1)): m.group(2).strip() for m in re.finditer(r"^### (\d+) · (.+)$", txt, re.M)}
    rows = {}
    for m in re.finditer(r"^\| (\d+) \| (\S+) → (\S+) \| ([^|]+)\| ([^|]+)\| ([^|]+)\| (\S+) \| (\S+) \| (\S+) \|", txt, re.M):
        g = int(m.group(1))
        rows[g] = {"start": m.group(2), "end": m.group(3), "d": m.group(4).strip(), "N": m.group(5).strip(),
                   "reg": m.group(7), "mode": m.group(9)}
    return titles, rows


def header(p, titles, rows, verdict="pending"):
    g = int(p[1:])
    r = rows.get(g, {})
    t = titles.get(g, "")
    lines = [f"# H30 × {p}: {t} ({r.get('start', '?')} → {r.get('end', '?')})", "",
             f"**Verdict:** {verdict}", "**Role:** exploratory",
             f"**Period:** regime {r.get('reg', '?')} · mode {r.get('mode', '?')} · {r.get('N', '?')} agents at start · {r.get('d', '?')} active days"
             + (" (non-holdout part only: 07-06 → 09-04; the #51 tail is held out)" if p == "G51" else "") + ".", ""]
    return lines


def write_predict():
    titles, rows = goal_meta()
    for p in PERIODS:
        d = HYP / "goalperiod-subhypotheses" / p
        (d / "figures").mkdir(parents=True, exist_ok=True)
        f = d / "README.md"
        if f.exists() and "## Prediction" in f.read_text():
            print("exists, kept:", f)
            continue
        L = header(p, titles, rows)
        L += ["## Why this period", WHY[p], "", "## Prediction", f"*Written {PRED_DATE}, before running on this period.*", ""]
        L += [f"- {x}" for x in PRED[KIND[p]]]
        L += ["", "## Result", "*(pending)*", "", "## Scorecard (period-specific axes)", "*(pending)*", "", "## Notes",
              f"- {PRED_DATE}: folder and prediction written before the run (card Amendment A1 applies)."]
        f.write_text("\n".join(L) + "\n")
        print("wrote", f)


def fmt(x, k=2):
    if x is None:
        return "–"
    if isinstance(x, (list, tuple)) and len(x) == 3:
        if x[0] is None:
            return "–"
        lo, hi = x[1], x[2]
        return f"{x[0]:.{k}f} [{lo:.{k}f}, {hi:.{k}f}]" if lo is not None and hi is not None else f"{x[0]:.{k}f}"
    if isinstance(x, float):
        return f"{x:.{k}f}"
    return str(x)


def _c(c, k=2):
    if not c or c[0] is None:
        return None
    if c[1] is None or c[2] is None or max(abs(c[1]), abs(c[2])) > 50 * max(1.0, abs(c[0])) or c[2] - c[1] < 1e-9:
        return f"{c[0]:.{k}f} (CI unstable)"
    return f"{c[0]:.{k}f} [{c[1]:.{k}f}, {c[2]:.{k}f}]"


def verdict_line(p: str, R: dict) -> str:
    """'<verdict> — key numbers' for the Verdict line (read by the dashboard and the summary builder); kept short."""
    v = R.get("verdict", {}).get("overall", "mixed").replace(" (low power)", "")
    parts = []
    n = R["act_n"].get("N_tgt") or 0
    if n >= 5:
        a = R["act_nofe"].get("N_tgt")
        parts.append(f"nudge {_c(a)} min (n {n})" if n >= 50 else f"nudge {a[0]:.2f} min (n {n})")
    cu, cm = (R["con"].get("H_und") or {}), (R["con"].get("H_men") or {})
    if cu.get("n", 0) >= 30 and cu.get("orth"):
        ok = cu["orth"][1] is not None and cu["orth"][2] - cu["orth"][1] > 1e-9 and cu["orth"][1] > 0
        parts.append(f"content {cu['orth'][0]:.3f}{'*' if ok else ''}" + (f", named {cm['orth'][0]:.3f}" if cm.get("n", 0) >= 30 else ""))
    if p in ("G04", "G05", "G06", "G13"):
        parts.append("human activity ≈ 0")
    low = (n < 30 and p not in ("G04", "G05", "G06", "G13")) or R["n_days"] <= 5
    return f"{v} — " + "; ".join(parts) + ("; low power" if low else "")


def write_results():
    titles, rows = goal_meta()
    for p in PERIODS:
        rf = OUT / p / "results.json"
        f = HYP / "goalperiod-subhypotheses" / p / "README.md"
        if not rf.exists() or not f.exists():
            continue
        R = json.loads(rf.read_text())
        txt = f.read_text()
        pred = txt[txt.index("## Prediction"):txt.index("## Result")]
        notes = txt[txt.index("## Notes"):] if "## Notes" in txt else "## Notes\n"
        verdict = verdict_line(p, R)
        L = header(p, titles, rows, verdict)
        L += ["## Why this period", WHY[p], "", pred.rstrip(), "", "## Result"]
        L += [f"Days: {R.get('n_days')}; kicks by class: {R.get('n_kicks')}; content pairs with statements on both sides: {R.get('n_pairs')}.", ""]
        L += ["| Prediction | Observed | Null / reference | Verdict |", "| --- | --- | --- | --- |"]
        for row in R.get("verdict", {}).get("rows", []):
            L.append(f"| {row['id']} | {row['observed']} | {row.get('null', '')} | {row['verdict']} |")
        L += ["", f"Daily gauge: `data/processed/H30-operator-susceptibility/{p}/daily.parquet`; figure: `figures/daily_gauge.pdf`."]
        if R.get("notes"):
            L += [""] + [f"- {n}" for n in R["notes"]]
        L += ["", "## Scorecard (period-specific axes)"] + [f"- {s}" for s in R.get("scorecard", [])]
        L += ["", notes.rstrip(), f"- 2026-10-03: round-1 results filled in from `results.json`."]
        f.write_text("\n".join(L) + "\n")
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
