"""Write goalperiod-subhypotheses/G<NN>/README.md for H31.

  --predict   writes the header, "Why this period" and the dated prediction (before the real-data run on the period);
              uses only period metadata (goal-periods.md) and the outcome-free predictor table.
  --results   fills Verdict, Result and Scorecard from data/processed/H31-consensus-time-spectral-gap/G<NN>/results.json,
              keeping the prediction text unchanged.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

import numpy as np
import polars as pl

sys.path.insert(0, str(Path(__file__).resolve().parent))
import h31lib as L  # noqa: E402

GP = L.ROOT / "hypotheses/hypohypotheses/goal-periods.md"
GDIR = L.HYP / "goalperiod-subhypotheses"
ROOMS = {0: "#general", 2: "#best", 3: "#rest", 4: "#universe-coordination"}
PRED_DATE = "2026-10-03"

# Period-specific expectations, written 2026-10-03 from goal-periods.md and the round-1 LOG entries only
# (H11: #19 frozen, #26 runoff jump, #31 herding waves, #18 last-day convergence, #40 hub fixed by the goal;
#  H12: kickoffs raise diversity; H24: #21 alignment ramped over the week; H20: #38 kickoff relaxation over ~4 days).
SPECIFIC = {
    18: "H11 saw a deadline-driven convergence of the whole swarm onto one repo on the last day. So I expect the main E-P event to be late (τ_P ≥ 8 active h) and locked to the final day rather than to λ₂: a field/deadline event.",
    19: "H11 found the build repo at ≈ 0.6 share from the start (frozen consensus). I expect the dominant E-P event to be **frozen** (left-censored, excluded from the τ fit), with at most minor uncensored events.",
    26: "Election week. E-P project events should be gradual or absent (H11: project labels gradual). **E-V:** the runoff consensus should come within ≤ 1 h of the first runoff message (P10), faster than the E-P-calibrated M_λ forecast. That would make it a decision field, not diffusion.",
    31: "Free week with herding waves onto successive shared repos (H11). I expect several uncensored E-P events with abrupt rises (ρ ≤ 1 window) and τ_P ≤ 2 h: model H's signature, not D's gradual 1/λ₂ approach.",
    40: "The hub was fixed by the goal (H11: spread carried by fields, own worlds plus a hub). I expect the hub E-P event, if any, to be frozen or locked to day 1 (field), and no graph dependence.",
    38: "17-day charity fundraiser, two rooms. Long period, so τ can be long. H20 saw a kickoff relaxation over about 4 active days in content, so I expect an E-C convergence with τ_C of order 10 active h.",
    21: "Forecast week. H24 found content aligned from the first hour and ramping over the week, so I expect an E-C convergence with a long τ_C (≥ 5 h) that the graph does not explain.",
}


def parse_meta():
    txt = GP.read_text()
    meta = {}
    for line in txt.splitlines():
        m = re.match(r"\| (\d+) \| (\S+) → (\S+) \| (\d+)†? \| (\d+) \| [^|]* \| (\S+) \| (\S+) \| (\S+) \|", line)
        if m:
            g = int(m.group(1))
            meta[g] = dict(start=m.group(2), end=m.group(3), days=int(m.group(4)), N=int(m.group(5)), regime=m.group(6),
                           by=m.group(7), mode=m.group(8))
    for m in re.finditer(r"^### (\d+) · (.+)$", txt, re.M):
        g = int(m.group(1))
        if g in meta:
            meta[g]["title"] = m.group(2).strip()
    return meta


def predict(goals):
    meta = parse_meta()
    pp = pl.read_parquet(L.DATA / "predictors_period.parquet").filter(pl.col("variant") == "all")
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from synthetic import eligible_blocks
    elig = set(eligible_blocks())
    for g in goals:
        P = L.load_period(g)
        blocks = L.blocks_of(P)
        if not blocks:
            continue
        mt = meta.get(g, {})
        rows = pp.filter(pl.col("goal_no") == g).sort("room")
        ep = [b for b in blocks if (g, b) in elig]
        role_bits = []
        if g in (19, 26, 31, 40):
            role_bits.append("card candidate")
        role_bits.append("E-P + E-C" if ep else "E-C only")
        if len(blocks) == 2:
            role_bits.append("two-room contrast (T6)")
        lines = [f"# H31 × G{g:02d}: {mt.get('title', '?')} ({mt.get('start', '?')} → {mt.get('end', '?')})", "",
                 "**Verdict:** pending",
                 "**Role:** exploratory (" + "; ".join(role_bits) + ")",
                 f"**Period:** regime {mt.get('regime', '?')} · mode {mt.get('mode', '?')} · {mt.get('N', '?')} agents · "
                 + ", ".join(ROOMS.get(b, f'room {b}') for b in blocks) + f" · {P['days'].height} non-holdout days "
                 f"({L.period_T(P) / 3600:.1f} active h).", "",
                 "## Why this period"]
        why = []
        if g in (19, 26, 31, 40):
            why.append("Named by HH115 and H11 as a consensus period.")
        if ep:
            why.append("H11 project labels are dense enough for E-P (≥ 50% of room-windows have ≥ 3 labeled agents).")
        else:
            why.append("H11 labels are too sparse for E-P, so only content (E-C) is tested.")
        if len(blocks) == 2:
            why.append("Two rooms with the same goal and kickoff, so the field is common and the graphs differ (T6).")
        lines += [" ".join(why), "", "**Predictors** (whole block-period; computed before any outcome):", "",
                  "| Block | N_b | msgs/h | u (reads/h) | λ₂^w,sym (1/h) | λ₂^w,dir | u·λ₂^rw | γ_tr | τ_wave (min) | τ_Vsim (h) |",
                  "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |"]
        for r in rows.iter_rows(named=True):
            lines.append(f"| {ROOMS.get(r['room'], r['room'])} | {r['N_b']:.0f} | {r['msg_rate']:.0f} | {r['u']:.1f} | "
                         f"{r['l2_sym']:.2f} | {r['l2_dir']:.2f} | {r['ul2_rw']:.1f} | {r['g_tr']:.2f} | "
                         f"{60 * r['tau_wave']:.1f} | {r['tau_V']:.3f} |")
        lines += ["", "## Prediction", f"*Written {PRED_DATE}, before running on this period.*", ""]
        pr = [
            "- **Card rules apply unchanged** (E-P, E-V, E-C definitions; tests T1–T7). Per-period verdicts are descriptive; the scaling test (P1, P5) is cross-period.",
            "- **H31 (model D):** if this block's events are uncensored, their τ should sit on the cross-period line τ = c/λ₂^w,sym. Blocks with a larger λ₂^w,sym should be faster.",
            "- **My prior (card):** the timing is set by task structure and announcements, so this period's τ will not track λ₂ beyond noise. E-P rises will be mostly abrupt (ρ ≤ 1 window), and E-C, if present, will be a convergence over days (τ_C 2–15 h).",
        ]
        if len(blocks) == 2:
            r2 = {r["room"]: r for r in rows.iter_rows(named=True)}
            if len(r2) == 2:
                small = min(r2, key=lambda b: r2[b]["N_b"])
                large = max(r2, key=lambda b: r2[b]["N_b"])
                ratio = r2[large]["l2_sym"] / max(r2[small]["l2_sym"], 1e-9)
                d_sign = "faster in the larger room" if ratio > 1 else "faster in the smaller room"
                pr.append(f"- **T6 room contrast:** model D predicts consensus {d_sign} (λ₂ ratio large/small = {ratio:.1f}). "
                          f"Voter V predicts the smaller room ({ROOMS.get(small)}, N ≈ {r2[small]['N_b']:.0f}) faster by "
                          f"≈ N ratio {r2[large]['N_b'] / max(r2[small]['N_b'], 1):.1f}. Field F predicts no difference.")
        if g in SPECIFIC:
            pr.append("- **Period-specific:** " + SPECIFIC[g])
        pr.append("- **Counts against H31 here:** uncensored events whose τ is far off the calibrated line (outside the 80% LOPO interval), or a room contrast with the opposite sign to D.")
        lines += pr + ["", "## Result", "*(pending)*", "", "## Scorecard (period-specific axes)", "*(pending)*", "",
                       "## Notes", f"- {PRED_DATE}: folder and prediction written before the real-data run on this period."]
        f = GDIR / f"G{g:02d}"
        f.mkdir(parents=True, exist_ok=True)
        (f / "README.md").write_text("\n".join(lines) + "\n")
        print("wrote", f / "README.md")


def results(goals):
    for g in goals:
        f = GDIR / f"G{g:02d}" / "README.md"
        rj = L.DATA / f"G{g:02d}" / "results.json"
        if not f.exists() or not rj.exists():
            continue
        R = json.loads(rj.read_text())
        txt = f.read_text()
        txt = re.sub(r"\*\*Verdict:\*\* .*", f"**Verdict:** {R['verdict']}", txt, count=1)
        res = "\n".join(R["result_lines"])
        sc = "\n".join(R["scorecard_lines"])
        txt = re.sub(r"## Result\n.*?\n## Scorecard \(period-specific axes\)\n.*?\n## Notes",
                     f"## Result\n{res}\n\n## Scorecard (period-specific axes)\n{sc}\n\n## Notes", txt, flags=re.S)
        if "results filled" not in txt:
            txt = txt.rstrip() + f"\n- {PRED_DATE}: results filled from `analysis/explore.py` (round 1).\n"
        f.write_text(txt)
        print("updated", f)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--predict", action="store_true")
    ap.add_argument("--results", action="store_true")
    ap.add_argument("--goals", type=int, nargs="*")
    a = ap.parse_args()
    goals = a.goals or sorted(int(p.name[1:]) for p in L.DATA.glob("G*") if p.is_dir())
    if a.predict:
        predict(goals)
    if a.results:
        results(goals)


if __name__ == "__main__":
    main()
