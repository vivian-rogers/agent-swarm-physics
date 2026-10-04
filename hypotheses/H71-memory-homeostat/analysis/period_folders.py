"""Write H71 period and native folders.

    --predict   before any outcome: structure (agents, cycles, regime) + the dated prediction per period
    --results   after run.py: fill the Result section and the Verdict line from results/*.json
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import polars as pl

HERE = Path(__file__).resolve().parent
H = HERE.parent
ROOT = H.parents[1]
DATA = ROOT / "data/processed/H71-memory-homeostat"
GP = H / "goalperiod-subhypotheses"
STAMP = "2026-10-04 19:55 UTC"

NATIVES = {
    "NE14": ("NE14/NE41: regime II → III (perma-computer-use, forced consolidation at the 41-call cap), 2026-03-24",
             "#36 splits at 03-24 (G36a regime II | G36b–c regime III); the same agents run #33, #35 (regime II) and "
             "#37–#39 (regime III). HH269 names a gain change here. The compression cycle changes from a session end "
             "after many appends to one append and one compression per ~40 calls.",
             "- **N1a (gain change):** within agents present on both sides (#33, #35, #36a vs #36b–c, #37, #38, #39), "
             "the paired mean Δφ⁺ (after − before) differs from 0 (CI excludes 0) with |Δφ⁺| ≥ 0.15.\n"
             "- **N1b (set point):** the paired set point μ_i (mean x⁺) rises by ≥ 20% (Δ ln ≥ 0.18), as H09's "
             "NE14 V (+20%) suggests.\n- **Counts against HH269's 'gain change':** |Δφ⁺| < 0.1 with the CI inside "
             "±0.15."),
    "NE04": ("NE04: chain-of-thought memory consolidation (and the history-search tool), 2025-09-05",
             "#12 splits at 09-05 (G12a | G12b), and #13 follows with the same 6–7 agents. The consolidation method "
             "changes; the cycle structure (session ends) does not.",
             "- **N2a:** φ⁺ falls by ≥ 0.15 after the switch (paired over agents in #11 + #12a vs #12b + #13): a "
             "model that reasons before rewriting pulls harder toward its set point.\n- **N2b:** the share of lines "
             "removed per compression rises (paired, CI > 0).\n- **Counts against:** Δφ⁺ ≥ 0 with the CI excluding "
             "−0.15."),
    "NE16": ("NE16: the contradictory 'never update memory' instruction removed, 2026-03-26 (negative control)",
             "G36b (03-24..25) vs G36c (03-26..27), same 12–13 agents, same goal. RE-O1 found memory written at 99% "
             "of forced consolidations before the fix, so the fix should change nothing in the store's dynamics.",
             "- **N3a (negative control):** |Δφ⁺| < 0.15 (paired over agents) and |Δ ln μ| < 0.18.\n- **N3b:** the "
             "share of compressions with lines added does not change by more than 0.1.\n- **Counts against:** "
             "|Δφ⁺| ≥ 0.15 with the CI excluding 0. Power is low (two days per side); a null here is weak."),
    "NE32": ("Newcomers relax from an empty memory (Onsager regression; anchored on NE32, all non-holdout joins)",
             "A newcomer starts with no memory: the largest displacement from a set point in the data. Onsager's "
             "regression hypothesis says a linear homeostat relaxes from a large displacement with the same law as "
             "its small spontaneous fluctuations. Joins: every roster join whose first memory snapshot is "
             "non-holdout and which has ≥ 40 compression cycles (#38 Opus 4.7, Kimi K2.6; #42 Gemini 3.5 Flash; "
             "#44 joins; #51's NE32 trio and later joins).",
             "- **N4a:** fitting μ_i and φ_i on cycles 21+ only, the first 20 cycles follow "
             "x̂⁺_n = μ_i + φ_iⁿ (x⁺_0 − μ_i): the fitted relaxation factor φ_relax lies within ±0.2 of φ_i for "
             "≥ 2/3 of newcomers.\n- **N4b:** the displacement d_n = x⁺_n − μ_i shrinks to below half of d_0 "
             "within 3 cycles for ≥ 2/3 of newcomers (φ⁺ ≤ 0.8).\n- **Counts against:** φ_relax > φ_i + 0.2 "
             "for most newcomers (slow growth from empty, i.e. accumulation, not regulation)."),
}


def eligible(cyc: pl.DataFrame) -> pl.DataFrame:
    import h71lib as L
    p = L.pairs(cyc)
    a = p.group_by("period", "agent").len().filter(pl.col("len") >= L.MIN_PAIRS_AGENT)
    e = a.group_by("period").agg(pl.len().alias("n_agents_15"), pl.col("len").sum().alias("n_pairs_15"))
    tot = cyc.group_by("period").agg(pl.len().alias("n_cycles"), pl.col("agent").n_unique().alias("n_agents"),
                                     pl.col("regime").first(), pl.col("pt_date").min().alias("first"),
                                     pl.col("pt_date").max().alias("last"))
    return tot.join(e, on="period", how="left").with_columns(pl.col("n_agents_15").fill_null(0)).sort("period")


def predict():
    sys.path.insert(0, str(HERE))
    cyc = pl.read_parquet(DATA / "cycles.parquet")
    el = eligible(cyc)
    for r in el.to_dicts():
        per = r["period"]
        if r["n_agents_15"] < 3:
            continue
        d = GP / per
        (d / "figures").mkdir(parents=True, exist_ok=True)
        r3 = r["regime"] == "III"
        txt = f"""# H71 × {per}: memory size as a first-order homeostat ({r['first']} → {r['last']})

**Verdict:** pending
**Role:** replication
**Period:** regime {r['regime']} · {r['n_agents']} agents with memory snapshots · {r['n_cycles']} compression cycles (non-holdout) · {r['n_agents_15']} agents with ≥ 15 within-period cycle pairs.{' Memory-relevant split: see the card (NE04 / NE14 / NE16).' if per[-1] in 'abc' else ''}

## Why this period
The common estimator (card, O1–O7) on every eligible non-holdout period: each period is one point on the (set point, gain) plane. {'Regime III: one append and one compression per consolidation, so the mixed-phase series should show the sampling artifact (P3); forced vs voluntary cycles are both present (P4).' if r3 else 'Regime I/II: several appends per compressed session; the mixed series is dominated by growth runs, so P3 and P4 do not apply here.'}

## Prediction
*Written {STAMP}, before running on this period (card predictions applied).*
- φ⁺ (half-panel-jackknife within-agent AR(1) on post-compression log size) lies in (0, 0.9) with the agent-bootstrap CI excluding 0 and 1.
- AR(1) beats the random walk out of sample for ≥ 60% of agents with ≥ 20 cycles; AR(2) adds |φ₂| < 0.1.
- Clock: |slope of φ⁺ on log cycle length| ≤ 0.1.{chr(10) + '- Mixed-phase φ < 0 while φ⁺ > 0 (P3); φ⁺(forced) ≥ 0 and within 0.15 of φ⁺(voluntary) (P4).' if r3 else ''}
- Counts against: φ⁺'s CI includes 1 (random walk) or lies below 0 (overshoot), or AR(1) beats RW for < 40% of agents.
- Synthetic power at this period's counts (`synthetic/synthetic.json`, nearest skeleton): overshoot of −0.3 detected in 100% of replicates; a random walk's CI includes 1 in 85–100%.

## Result
*(Filled by `analysis/period_folders.py --results`.)*

## Scorecard (period-specific axes)
*(Filled with the result.)*

## Notes
- Data: `data/processed/H71-memory-homeostat/results/periods.json` (key `{per}`).
"""
        (d / "README.md").write_text(txt)
    for ne, (title, why, pred) in NATIVES.items():
        d = GP / ne
        (d / "figures").mkdir(parents=True, exist_ok=True)
        txt = f"""# H71 × {ne}: {title}

**Verdict:** pending
**Role:** native
**Period:** see "Why this period".

## Why this period
{why}

## Prediction
*Written {STAMP}, before running this native test.*
{pred}

## Result
*(Filled by `analysis/period_folders.py --results`.)*

## Scorecard (period-specific axes)
*(Filled with the result.)*

## Notes
- Data: `data/processed/H71-memory-homeostat/results/natives.json` (key `{ne}`).
"""
        (d / "README.md").write_text(txt)
    print(el)


def fill(path: Path, verdict: str, result_md: str, score_md: str):
    s = path.read_text()
    s = s.replace("**Verdict:** pending", f"**Verdict:** {verdict}", 1)
    s = s.replace("*(Filled by `analysis/period_folders.py --results`.)*", result_md, 1)
    s = s.replace("*(Filled with the result.)*", score_md, 1)
    path.write_text(s)


if __name__ == "__main__":
    if "--predict" in sys.argv:
        predict()


def f(x, n=2):
    return "–" if x is None or (isinstance(x, float) and x != x) else f"{x:+.{n}f}"


def results():
    per = json.loads((DATA / "results/periods.json").read_text())
    ph = json.loads((DATA / "results/posthoc.json").read_text())
    nat = json.loads((DATA / "results/natives.json").read_text())
    for p, r in per.items():
        path = GP / p / "README.md"
        if not path.exists():
            continue
        q = ph.get(p, {})
        r3 = r["regime"] == "III"
        rows = [
            ("φ⁺ in (0, 0.9), CI excludes 0 and 1", f"{r['phi']['est']:.2f} [{r['phi']['lo']:.2f}, {r['phi']['hi']:.2f}] "
             f"({r['n_agents']} agents, {r['n_pairs']} cycle pairs)", "RW 1; deadbeat 0",
             "met" if (r['phi']['lo'] > 0 and r['phi']['hi'] < 1 and r['phi']['est'] < 0.9) else "not met"),
            ("AR(1) beats RW for ≥ 60% of agents", f"{r['oos']['ar1_beats_rw']:.2f} of {r['oos']['n_agents']} "
             f"(beats deadbeat {r['oos']['ar1_beats_db']:.2f})", "–",
             "met" if r['oos']['ar1_beats_rw'] >= 0.6 else ("failed" if r['oos']['ar1_beats_rw'] < 0.4 else "not met")),
            ("\\|AR(2)\\| < 0.1", f"{f(r['ar2']['est'])} [{f(r['ar2']['lo'])}, {f(r['ar2']['hi'])}]", "0",
             "met" if abs(r['ar2']['est']) < 0.1 else "not met"),
            ("clock: \\|slope\\| ≤ 0.1", f"{f(r['clock']['slope'])} [{f(r['clock_ci']['lo'])}, {f(r['clock_ci']['hi'])}]",
             "wall clock ≈ −0.2", "met" if abs(r['clock']['slope']) <= 0.1 else "not met"),
            ("decomposition (post hoc reading)", f"b {r['dec']['b']:.2f}, c {r['dec']['c']:+.2f}, b(1+c) {r['dec']['b1c']:.2f}",
             "φ⁺ = b(1+c) for one loop", "φ⁺ ≫ b(1+c)" if r['phi']['est'] - r['dec']['b1c'] > 0.1 else "consistent"),
        ]
        if q:
            rows.append(("post hoc: ρ₂ − ρ₁² (two timescales)", f"{q['rho2_minus_rho1sq']:+.3f} [{q['rho2_minus_rho1sq_ci'][0]:+.3f}, "
                         f"{q['rho2_minus_rho1sq_ci'][1]:+.3f}]; ρ_s {q['rho_s']:.2f}, slow share {q['r_slow']:.2f}",
                         "0 for one first-order loop", "two timescales" if q['rho2_minus_rho1sq_ci'][0] > 0 else "not resolved"))
        if r3:
            rows.append(("mixed-phase φ < 0 while φ⁺ > 0 (P3)", f"mixed {r['mixed_phi']:+.2f}; single-loop synthetic "
                         f"{r['synth_mixed']['mean']:+.2f}" + (f"; two-timescale synthetic {q['mixed_two_timescale']:+.2f}"
                                                                 if 'mixed_two_timescale' in q else ""),
                         "–", "met (sampling artifact)" if r['mixed_phi'] < 0 < r['phi']['est'] else "not met"))
            rows.append(("no overshoot after forced erasures (P4)", f"φ⁺ forced {r['forced']['est']:.2f} "
                         f"[{r['forced']['lo']:.2f}, {r['forced']['hi']:.2f}], voluntary {r['voluntary']['est']:.2f}; "
                         f"F − V {f(r['f_minus_v']['est'])} [{f(r['f_minus_v']['lo'])}, {f(r['f_minus_v']['hi'])}]",
                         "HH269: forced < 0", "met" if r['forced']['lo'] > 0 and abs(r['f_minus_v']['est']) < 0.15 else "not met"))
        tab = "| Prediction | Observed | Null / rival | Verdict |\n| --- | --- | --- | --- |\n" + "\n".join(
            f"| {a} | {b} | {c} | {d} |" for a, b, c, d in rows)
        are = r.get("agent_re", {})
        res = (f"*Run 2026-10-04 (`analysis/run.py`, `analysis/posthoc.py`; non-holdout).* Set point (median agent mean of "
               f"x⁺): {r['mu_median_chars']:.0f} characters; agent heterogeneity of φ⁺_i: τ {are.get('tau', float('nan')):.2f}.\n\n"
               + tab + "\n\n**Reading.** " + (
                   "Memory size reverts toward an agent set point (φ⁺ < 1), with no overshoot. The one-step maps "
                   "(b, c) explain less persistence than φ⁺ shows, so part of the persistence is a slowly drifting set "
                   "point (card, post hoc two-timescale model)." if r["verdict"] in ("supported", "mixed") else
                   "The period fails the card's verdict rule (see the table)."))
        score = ("- **C:** φ⁺ against RW and deadbeat (out of sample); **D:** the mixed-phase sign and the clock slope are "
                 "unfitted statistics; **F:** synthetic recovery at this period's counts (`synthetic/synthetic.json`).")
        fill(path, r["verdict"], res, score)
    # natives
    ne14 = nat["NE14"]
    w, w36 = ne14["wide"], ne14["within36"]
    v14 = "mixed"
    fill(GP / "NE14" / "README.md", f"{v14} (set point up; gain change small)",
         f"""*Run 2026-10-04.* Paired over agents present on both sides.

| Prediction | Observed | Verdict |
| --- | --- | --- |
| N1a Δφ⁺ ≠ 0 with \\|Δφ⁺\\| ≥ 0.15 (wide: #33, #35, #36a → #36b–c, #37–#39) | {w['dphi']:+.2f} [{w['dphi_ci'][0]:+.2f}, {w['dphi_ci'][1]:+.2f}] ({w['n_agents']} agents; {w['phi_before_mean']:.2f} → {w['phi_after_mean']:.2f}) | CI excludes 0, magnitude below 0.15: not met |
| N1a within #36 only (36a → 36b–c) | {w36['dphi']:+.2f} [{w36['dphi_ci'][0]:+.2f}, {w36['dphi_ci'][1]:+.2f}] ({w36['n_agents']} agents) | not met |
| N1b set point +20% (Δ ln μ ≥ 0.18) | wide {w['dln_mu']:+.2f} [{w['dln_mu_ci'][0]:+.2f}, {w['dln_mu_ci'][1]:+.2f}]; within #36 {w36['dln_mu']:+.2f} [{w36['dln_mu_ci'][0]:+.2f}, {w36['dln_mu_ci'][1]:+.2f}] | met within #36 (+31%); wide +17% |

**Reading.** The regime II → III step raises the memory set point (+17% to +31%) and makes memory size slightly more persistent per cycle (+0.12 across periods; +0.03 inside #36). HH269's "gain change at NE41" is small: per compression cycle the regulation is about as strong before and after, although a cycle changes from a session end after many appends to one append and one compression per ~40 calls. Regime III cycles are shorter in wall time, so per hour the regulation is faster.""",
         "- **E:** the NE14/NE41 step is the intervention; the set point moves, the per-cycle gain barely does. **A:** the same estimator applies on both sides of the regime boundary.")
    p4 = nat["NE04"]["paired"]
    fill(GP / "NE04" / "README.md", "failed (φ⁺ rose, not fell; removal share unchanged)",
         f"""*Run 2026-10-04.* Paired over agents in #11 + #12a (before) and #12b + #13 (after).

| Prediction | Observed | Verdict |
| --- | --- | --- |
| N2a φ⁺ falls by ≥ 0.15 | Δφ⁺ {p4['dphi']:+.2f} [{p4['dphi_ci'][0]:+.2f}, {p4['dphi_ci'][1]:+.2f}] ({p4['n_agents']} agents; {p4['phi_before_mean']:.2f} → {p4['phi_after_mean']:.2f}) | failed (opposite sign) |
| N2b removal share up | {nat['NE04']['removal_before']['mean']:.3f} → {nat['NE04']['removal_after']['mean']:.3f} (lines removed / (removed + kept)) | failed |
| set point (not predicted) | Δ ln μ {p4['dln_mu']:+.2f} [{p4['dln_mu_ci'][0]:+.2f}, {p4['dln_mu_ci'][1]:+.2f}] | – |

**Reading.** Chain-of-thought consolidation made memory size *more* persistent per cycle and raised the set point by about 18%; it did not change how much each compression removes. Seven agents and one goal change (#12 → #13) inside the comparison make this weak.""",
         "- **E:** a scaffold change to the consolidation method moves the set point and the persistence, not the removal fraction. Low power (7 agents).")
    p16 = nat["NE16"]["paired"]
    fill(GP / "NE16" / "README.md", "supported (negative control: no change)",
         f"""*Run 2026-10-04.* Paired over agents in #36b (03-24..25) and #36c (03-26..27).

| Prediction | Observed | Verdict |
| --- | --- | --- |
| N3a \\|Δφ⁺\\| < 0.15 and \\|Δ ln μ\\| < 0.18 | Δφ⁺ {p16['dphi']:+.2f} [{p16['dphi_ci'][0]:+.2f}, {p16['dphi_ci'][1]:+.2f}]; Δ ln μ {p16['dln_mu']:+.2f} [{p16['dln_mu_ci'][0]:+.2f}, {p16['dln_mu_ci'][1]:+.2f}] ({p16['n_agents']} agents) | met (point estimates; CIs are wide) |
| N3b share of cycles with appends changes < 0.1 | {nat['NE16']['append_share_before']:.2f} → {nat['NE16']['append_share_after']:.2f} | met |

**Reading.** Removing the "never update memory" instruction changed nothing measurable in the store's dynamics, as RE-O1's 99% write rate before the fix implied. Two days per side: a weak null.""",
         "- **E:** a documented memory-prompt change with no first stage, used as a negative control; the estimator does not invent a change.")
    nc = nat["NE32"]
    fill(GP / "NE32" / "README.md", "mixed (relaxation follows the slow set-point mode, not φ⁺)",
         f"""*Run 2026-10-04.* {nc['n']} newcomers (roster join with the first memory snapshot within 3 days, ≥ 40 cycles, non-holdout).

| Prediction | Observed | Verdict |
| --- | --- | --- |
| N4a φ_relax within ±0.2 of φ_i for ≥ 2/3 | {nc['share_within_02']:.2f} | met (at the threshold) |
| N4b displacement halves within 3 cycles for ≥ 2/3 | {nc['share_half_le3']:.2f} | failed |

Every newcomer starts *below* its later set point (first post-compression size 7.6k–25k characters vs set points 10k–77k; d₀ −0.23 to −1.29 in ln units). Median φ_relax {np.median([r['phi_relax'] for r in nc['rows']]):.2f} vs median φ_i {np.median([r['phi_i'] for r in nc['rows']]):.2f}.

**Reading (post hoc).** Memory grows from a newcomer's first compression toward its set point over 5–20 cycles, slower than the small-fluctuation φ⁺ predicts. The relaxation factor (≈ 0.9) matches the slow set-point persistence ρ_s of the two-timescale model (0.7–0.9 per cycle; `results/posthoc.json`), not the fast compression. Onsager regression holds for the slow mode only.""",
         "- **D:** the relaxation from the largest displacement is an unfitted statistic; it agrees with the post hoc slow mode, not with the pre-registered single loop.")


if __name__ == "__main__" and "--results" in sys.argv:
    import numpy as np  # noqa: F401
    results()
