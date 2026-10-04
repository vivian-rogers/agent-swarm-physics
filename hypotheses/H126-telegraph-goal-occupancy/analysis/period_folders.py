"""H126 period folders. Phase 1 (`--predict`): write each G/NE folder's README with the dated prediction, before any
real-data statistic. Phase 2 (`--results`): fill the Result section and the verdict from results/*.json.

Usage: uv run python hypotheses/H126-telegraph-goal-occupancy/analysis/period_folders.py --predict
       uv run python hypotheses/H126-telegraph-goal-occupancy/analysis/period_folders.py --results
"""
from __future__ import annotations

import argparse
import json
import math
import re
import sys
from pathlib import Path

import polars as pl

HERE = Path(__file__).resolve().parent
H = HERE.parent
ROOT = H.parents[1]
SH = ROOT / "data/processed/shared"
OUTD = ROOT / "data/processed/H126-telegraph-goal-occupancy"
GP = H / "goalperiod-subhypotheses"
sys.path.insert(0, str(ROOT / "infra/shared"))
from common import load_holdout  # noqa: E402

PRED_DATE = "2026-10-04 ~22:25 UTC"
EXCL = {23, 51}

REPL = """*Written {date}, before running on this period.*
Replication layer (card P1–P3, per unit {units}):
- **P1 exponential dwells:** held-out-day ΔLL(M4s − M2a) per statement ≤ its parametric-bootstrap 95th percentile, or the M4s dwell CV < 2 in both states. Heavy-tailed (both conditions violated) counts against; it is the kill if it happens in > ½ of all units.
- **P2 dwells predict occupancy:** the held-out-day predicted agent-window occupancy is within 20% of the observed (|ρ_p| ≤ ln 1.2); off by > 30% counts against (kill if in > ½ of all units).
- **P3 kickoff (if this period has an eligible kickoff design from #{prev}):** Δln k_on 90% CI above 0 and Δln k_off CI containing 0.
- Expectation for this period: regime {regime}, mode {mode}, N ≈ {N}. {extra}
- Unit verdict: supported if P1 and P2 hold; failed if heavy-tailed or |ρ_p| > ln 1.3; mixed otherwise. P3 is reported separately."""


def meta():
    pa = pl.read_parquet(SH / "period_affordances.parquet")
    return pa


def predict():
    h = load_holdout()
    held = set(h["goal_periods_held_out"])
    pa = meta()
    pa = pa.filter(~pl.col("holdout") & ~pl.col("goal_no").is_in(list(held | EXCL)) & (pl.col("mode") != "F"))
    for g, sub in pa.group_by("goal_no", maintain_order=True):
        g = int(g[0])
        r0 = sub.row(0, named=True)
        units = ", ".join(sub["unit_id"].to_list())
        first, last = sub["first_day"].min(), sub["last_day"].max()
        extra = ""
        if g == 12:
            extra = ("#12 has a scheduled field (debate rounds, DQ6): P2 may fail by drift (R-drift); see native N1 below. ")
        if r0["regime"] == "III":
            extra += "Regime III: call gaps between statements are 5–17 calls, so dwells are resolved on the call clock; P5 (call beats wall clock) is expected here."
        else:
            extra += "Regime I/II: statements are dense on the call clock (median gap 1–4 calls)."
        txt = f"""# H126 × G{g:02d}: goal #{g} ({first} → {last})

**Verdict:** pending
**Role:** exploratory
**Period:** regime {r0['regime']} · mode {r0['mode']} · {r0['N']} agents · units {units} · {first} → {last}.

## Why this period
An assigned (non-free) goal period outside the holdout: the goal field should hold the on-goal occupancy at 0.1–0.5 (H105), so both dwell types are observed.

## Prediction
{REPL.format(date=PRED_DATE, units=units, prev=g - 1, regime=r0['regime'], mode=r0['mode'], N=r0['N'], extra=extra)}
"""
        if g == 12:
            txt += """
**Native N1 (G12, scheduled field):** with M2s rates split by the DQ6 debate windows (pre/deb = debate on), Δln k_on (debate − outside) 90% CI above 0 and Δln k_off CI containing 0 (credence 0.3). Counts against: Δln k_off CI below 0 with |Δln k_off| ≥ Δln k_on.
"""
        txt += """
## Result
(pending)

## Scorecard (period-specific axes)
(pending)

## Notes
- Data: `data/processed/H126-telegraph-goal-occupancy/` (`stmts.parquet`, `results/`).
"""
        d = GP / f"G{g:02d}"
        d.mkdir(parents=True, exist_ok=True)
        (d / "README.md").write_text(txt)
    # natives
    (GP / "G51").mkdir(parents=True, exist_ok=True)
    (GP / "G51" / "README.md").write_text(f"""# H126 × G51: goal #51, private goals (2026-07-06 → 2026-09-06, head units 51a–51l)

**Verdict:** pending
**Role:** exploratory (native)
**Period:** regime III · mode I/K · 21 agents · private goals and roles · units 51a–51l (the #51 tail is held out).

## Why this period
Each agent has its own private goal (`agent_goal`), so each agent has its own field. #51 has the most statements per agent of any period and the longest run of stationary assignments: the best-powered test of the dwell shape, and the only period where per-agent rates can be compared across units (an agent-level property, exception (b)).

## Prediction
*Written {PRED_DATE}, before running on this period.*
**Native N2:** along each agent's own goal direction (own decoy threshold), P1's exponential rule holds in ≥ 2/3 of the 12 units, and per-agent ln k_on is stable across consecutive units (median Spearman across agents ≥ 0.3). Credence 0.35. Counts against: heavy-tailed in > ½ of units, or median Spearman ≤ 0.
P2 (occupancy within 20%) is also computed per unit.

## Result
(pending)

## Scorecard (period-specific axes)
(pending)

## Notes
- Own-goal directions from `embeddings/goals.parquet` (`kind = agent_goal`, latest row per agent, as H105); agents in a unit only after their goal's `valid_from`.
""")
    (GP / "NE38").mkdir(parents=True, exist_ok=True)
    (GP / "NE38" / "README.md").write_text(f"""# H126 × NE38: Opus 5's goal reassignment (2026-07-29 16:51 UTC, inside #51)

**Verdict:** pending
**Role:** exploratory (native)
**Period:** regime III · one agent (agent 40, Claude Opus 5) · 2026-07-24 → 2026-08-04, split at 2026-07-29 16:51 UTC.

## Why this period
A human changed one agent's goal (word puzzles → mathematics). The new goal is a field step on one spin with the rest of the swarm unchanged: the cleanest single-agent kickoff. H105 saw its occupancy along the new goal go 0.00 → 0.96.

## Prediction
*Written {PRED_DATE}, before running on this period.*
**Native N3:** along Opus 5's new-goal direction, M2 with segment-specific rates gives Δln k_on 90% CI above 0 and Δln k_off CI containing 0 (the field raises the on-rate only). Credence 0.2. Counts against: Δln k_off CI below 0 (the field holds the agent on goal). Note before data: an occupancy of 0.96 needs k_on/k_off ≈ 24, which is hard to reach by k_on alone on a per-call clock.

## Result
(pending)

## Scorecard (period-specific axes)
(pending)
""")
    print("wrote prediction folders")


VMAP = {"inconclusive": "mixed"}


def _fmt(x, d=2):
    return "n/a" if x is None or (isinstance(x, float) and not math.isfinite(x)) else f"{x:.{d}f}"


def results():
    units = json.loads((OUTD / "results/units.json").read_text())
    kick = {k["design"]: k for k in json.loads((OUTD / "results/kick.json").read_text())}
    nat = json.loads((OUTD / "results/natives.json").read_text())
    by_g = {}
    for u in units:
        if not u.get("eligible"):
            continue
        g = int("".join(ch for ch in u["design"][1:] if ch.isdigit()))
        by_g.setdefault(g, []).append(u)
    summary = []
    for d in sorted(GP.glob("G*")):
        if d.name == "G51":
            continue
        g = int(d.name[1:])
        txt = (d / "README.md").read_text()
        us = by_g.get(g, [])
        lines = ["| Unit | agents | statements | P1 dLL(M4−M2) vs N0 q95; CV max | P2 ρ_p (held-out) | p_win | p_dw | τ_on / τ_off (calls, median) | q₀ / q₁ | P5 dLL(call−wall) |",
                 "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |"]
        kills = 0
        for u in us:
            kills += abs(u["rho_p"]) > math.log(1.3)
            lines.append(f"| {u['design'][1:]} | {u['n_agents']} | {u['n_stmt']} | {u['dll4_held']:+.4f} vs {u['null_q95']:.4f}; "
                         f"{max(u['cv_on'], u['cv_off']):.2f} ({u['P1']}) | {u['rho_p']:+.2f} ({u['P2']}) | {_fmt(u['p_win'])} | "
                         f"{_fmt(u['p_dw'])} | {_fmt(u['tau_on_med'], 1)} / {_fmt(u['tau_off_med'], 1)} | {u['q0']:.3f} / {u['q1']:.2f} | "
                         f"{u['dllw_held']:+.4f} |")
        k = kick.get(f"K{g:02d}")
        ktxt = ""
        if k and k.get("eligible"):
            ktxt = (f"\n**P3 kickoff (#{g-1} tail → #{g}, {k['n_agents']} agents):** Δln k_on {k['dln_a']:+.2f} [{k['a_lo']:+.2f}, {k['a_hi']:+.2f}], "
                    f"Δln k_off {k['dln_b']:+.2f} [{k['b_lo']:+.2f}, {k['b_hi']:+.2f}] (90% agent bootstrap); p {k['p_F']:.3f} → {k['p_A']:.3f}; **{k['P3']}**.\n")
        elif k:
            why = k.get("error") or f"{k.get('n_agents', 0)} agents with ≥ 20 statements in both segments"
            ktxt = f"\n**P3 kickoff:** not testable ({why}).\n"
        if not us:
            verdict, body = "n/a", "No unit met the eligibility rule (≥ 3 agents with ≥ 10 statements in each day fold)."
        else:
            verdict = "failed" if kills > len(us) / 2 else "descriptive"
            body = "\n".join(lines)
        if k and k.get("eligible"):
            sym = k["a_lo"] > 0 and k["b_hi"] < 0
            if sym and k["P3"] == "inconclusive":
                ktxt = ktxt.replace("**inconclusive**", "**both rates move (R-sym): counts against P3 under A1**")
            if verdict != "failed":
                verdict = {"k_on": "supported", "k_off": "failed"}.get(k["P3"], "failed" if sym else "mixed")
        extra = ""
        if g == 12:
            for r in [x for x in nat["N12"] if x.get("eligible")]:
                verdict = "failed" if r["N1"] == "failed" else verdict
                extra += (f"\n**Native N1 ({r['design'][4:]}):** Δln k_on (debate − outside) {r['dln_a']:+.2f} [{r['a_lo']:+.2f}, {r['a_hi']:+.2f}], "
                          f"Δln k_off {r['dln_b']:+.2f} [{r['b_lo']:+.2f}, {r['b_hi']:+.2f}]; debate share of statements {r['share_D']:.2f}; **{r['N1']}**.\n")
        res = (f"*Run 2026-10-04 (UTC), after Amendment A1. bge_small, deduplicated, call clock, M2a with jointly fitted emissions. "
               f"P1, P2 are descriptive after A1 (P2's kill kept); P3 is the primary test. Period verdict after A1: failed if P3 "
               f"counts against (k_off, or both rates move) or the P2 kill (|ρ_p| > ln 1.3) holds in > ½ of the units; supported if "
               f"P3 = k_on; descriptive otherwise.*\n\n{body}\n{ktxt}{extra}\n"
               f"Data: `data/processed/H126-telegraph-goal-occupancy/results/`.")
        txt = re.sub(r"\*\*Verdict:\*\* \S+", f"**Verdict:** {verdict}", txt, count=1)
        txt = txt.split("## Result")[0] + "## Result\n" + res + "\n\n## Scorecard (period-specific axes)\n" + \
            ("C: P2 consistency check; D: held-out-day occupancy (non-discriminating, A1); E: kickoff rates (P3) where testable; "
             "F: synthetic recovery of rates on this regime's skeleton.\n") + "\n## Notes\n- Codes only; see the card for the pipeline.\n"
        (d / "README.md").write_text(txt)
        summary.append((d.name, verdict))
    # natives
    rows = [r for r in nat["N51"] if r.get("eligible")]
    lines = ["| Unit | agents | statements | P1 dLL vs N0 q95; CV max | P2 ρ_p | p_win | τ_on / τ_off (calls) | q₀ / q₁ |", "| --- | --- | --- | --- | --- | --- | --- | --- |"]
    for r in rows:
        lines.append(f"| {r['unit']} | {r['n_agents']} | {r['n_stmt']} | {r['dll4_held']:+.4f} vs {r['null_q95']:.4f}; "
                     f"{max(r['cv_on'], r['cv_off']):.2f} ({r['P1']}) | {r['rho_p']:+.2f} | {_fmt(r['p_win'])} | "
                     f"{_fmt(r['tau_on_med'], 1)} / {_fmt(r['tau_off_med'], 1)} | {r['q0']:.3f} / {r['q1']:.2f} |")
    stab = nat.get("N51_stability", {})
    d = GP / "G51"
    txt = (d / "README.md").read_text()
    expo = sum(r["P1"] == "exponential" for r in rows)
    v51 = "descriptive"
    res = ("*Run 2026-10-04 (UTC), after Amendment A1 (the shape test has no power, so N2's first clause is descriptive).*\n\n"
           + "\n".join(lines) + f"\n\nExponential by the P1 rule in {expo}/{len(rows)} units (uninformative after A1). "
           f"Per-agent ln k_on stability across consecutive units: median Spearman {_fmt(stab.get('median_rho_kon'))} "
           f"over {stab.get('n_pairs', 0)} unit pairs (ln k_off: {_fmt(stab.get('median_rho_koff'))}).\n")
    if stab.get("median_rho_kon") is not None and math.isfinite(stab["median_rho_kon"]):
        v51 = "supported" if stab["median_rho_kon"] >= 0.3 else ("failed" if stab["median_rho_kon"] <= 0 else "mixed")
    txt = re.sub(r"\*\*Verdict:\*\* \S+", f"**Verdict:** {v51}", txt, count=1)
    txt = txt.split("## Result")[0] + "## Result\n" + res + "\n## Scorecard (period-specific axes)\nB: stationarity of per-agent rates across units (agent-level property, exception (b)); F: shape not identifiable (A1).\n"
    (d / "README.md").write_text(txt)
    r = nat["NE38"]
    d = GP / "NE38"
    txt = (d / "README.md").read_text()
    res = (f"*Run 2026-10-04 (UTC), after Amendment A1 (N3 is low-power: 30% for a true k_on step).*\n\n"
           f"Opus 5: {r['n_F']} statements before, {r['n_A']} after; raw on-goal fraction {r['f_on_F']:.2f} → {r['f_on_A']:.2f}. "
           f"k_on {r['a_F']:.4f} → {r['a_A']:.4f} per call (Δln {r['dln_a']:+.2f} [{r['a_lo']:+.2f}, {r['a_hi']:+.2f}]); "
           f"k_off {r['b_F']:.4f} → {r['b_A']:.4f} (Δln {r['dln_b']:+.2f} [{r['b_lo']:+.2f}, {r['b_hi']:+.2f}]); 90% parametric bootstrap. "
           f"Emissions q₀ {r['q0']:.3f}, q₁ {r['q1']:.2f}. **N3 {r['N3']}.**\n")
    txt = re.sub(r"\*\*Verdict:\*\* \S+", f"**Verdict:** {VMAP.get(r['N3'], r['N3'])}", txt, count=1)
    txt = txt.split("## Result")[0] + "## Result\n" + res + "\n## Scorecard (period-specific axes)\nE: a one-agent field step (natural experiment).\n"
    (d / "README.md").write_text(txt)
    print(summary, v51, r["N3"])


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--predict", action="store_true")
    ap.add_argument("--results", action="store_true")
    a = ap.parse_args()
    if a.predict:
        predict()
    if a.results:
        results()
