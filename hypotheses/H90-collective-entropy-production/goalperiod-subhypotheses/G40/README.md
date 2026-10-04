# H90 × G40: Connect your worlds into a 3D universe (2026-05-04 → 05-08)

**Verdict:** mixed (no address contrast; one single-channel behavior exceedance, p 0.02)
**Role:** replication (exploratory)
**Period:** regime III · 15 agents over the period (mean 15.0 day-present) · 5 trimmed talk days (949 trimmed minutes), 5 behavior days (182 trimmed 5-min steps) · 1511 agent messages naming a peer, 135 named ordered pairs.

## Why this period
- One shared artifact and a dedicated coordination room: the most coordination-heavy 5-day week.

## Prediction
*Written 2026-10-04 ~20:15 UTC (card), with amendments A1 (synthetic, before real data) and A2/A3 (dated on the card), before running on this period.*
- P1: ρ_coll < 0.1 in behavior and activity where Σ̂₁₊all's CI excludes 0.
- P2 (read after A1 as lead–lag): σ_coll(talk) over the block-shift null.
- P3 (after A1 the coupling test): Δ_addr(talk) = σ_nam − σ_un > 0 against the shift null.
- Synthetic size class: S40; Δ_addr power at J = 1 is 1.00, at G51's effect size (J ≈ 0.28) 0.05 (A3, post hoc).

## Result
*Run 2026-10-04 ~21:45 UTC (`analysis/run.py`; data `data/processed/H90-collective-entropy-production/G40/results.json`; figure `../../figures/summary_obs.pdf`).* Units: 10⁻³ nats per system step (1 min for talk/activity, 5 min for behavior); 95% day-bootstrap CIs; p against 100 (talk) / 50 block shifts.

| Quantity | Talk | Behavior | Activity |
| --- | --- | --- | --- |
| Σ̂₁ single-agent | -0.19 [-3.36, +0.02] | -60.06 [-216.67, +10.85] | -0.35 [-273.09, +0.11] |
| Σσ_i (marginals fitted alone) | -0.19 | -56.09 | -0.34 |
| σ_coll (all partners) | -1.95 [-21.67, +2.75], p 0.52 | -3.43 [-29.27, -0.16], p 0.59 | -0.34 [-73.40, -0.19], p 0.78 |
| σ_nam (named partners) | -1.34 [-28.37, +7.35], p 0.40 | +7.89 [-77.28, +40.42], p 0.02 | -1.22 [-234.54, +1.73], p 0.67 |
| σ_un (unnamed partners) | -6.62 [-21.82, +10.55], p 0.83 | -0.97 [-62.32, +3.43], p 0.24 | -0.26 [-400.38, +0.62], p 0.55 |
| Δ_addr = σ_nam − σ_un | +5.28 [-29.79, +23.07], p 0.16 | +8.87 [-63.73, +43.48], p 0.14 | -0.95 [-5.96, +165.84], p 0.65 |
| ρ_coll | undefined (Σ̂₁₊all ≤ 0) | undefined (Σ̂₁₊all ≤ 0) | undefined (Σ̂₁₊all ≤ 0) |
| exact-dual companion σ_nam | -1.34 | +8.35 | -1.22 |
| block-flip floor of Σ̂₁ (mean) | -0.23 | -41.05 | -0.09 |
| size-matched (12 agents) σ_nam | -1.59 | +3.96 | -0.81 |
| σ_nam without the kickoff day | -8.62 | -2.18 | -1.19 |

H50's J₁ for this period: 0.01. Talk σ_nam per agent-hour: -0.0053 nats.

## Scorecard (period-specific axes)
- C: nothing beats the shift null in talk; isolated single-channel exceedances (p ≈ 0.02) are expected at the multiplicity of 8 periods × 3 channels × 2 sets.
- F: power at G51's effect size is 0.05: a null here is inconclusive, not a refutation.
