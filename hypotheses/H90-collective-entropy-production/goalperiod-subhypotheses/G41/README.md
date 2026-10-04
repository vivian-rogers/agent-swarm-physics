# H90 × G41: Perform novel research (2026-05-11 → 05-15)

**Verdict:** mixed (no address contrast; one single-channel behavior exceedance, p 0.02)
**Role:** replication (exploratory)
**Period:** regime III · 15 agents over the period (mean 15.0 day-present) · 5 trimmed talk days (1026 trimmed minutes), 5 behavior days (189 trimmed 5-min steps) · 2846 agent messages naming a peer, 133 named ordered pairs.

## Why this period
- Individual research projects; H50's J₁ is not significant here.

## Prediction
*Written 2026-10-04 ~20:15 UTC (card), with amendments A1 (synthetic, before real data) and A2/A3 (dated on the card), before running on this period.*
- P1: ρ_coll < 0.1 in behavior and activity where Σ̂₁₊all's CI excludes 0.
- P2 (read after A1 as lead–lag): σ_coll(talk) over the block-shift null.
- P3 (after A1 the coupling test): Δ_addr(talk) = σ_nam − σ_un > 0 against the shift null.
- Synthetic size class: S40; Δ_addr power at J = 1 is 1.00, at G51's effect size (J ≈ 0.28) 0.05 (A3, post hoc).

## Result
*Run 2026-10-04 ~21:45 UTC (`analysis/run.py`; data `data/processed/H90-collective-entropy-production/G41/results.json`; figure `../../figures/summary_obs.pdf`).* Units: 10⁻³ nats per system step (1 min for talk/activity, 5 min for behavior); 95% day-bootstrap CIs; p against 100 (talk) / 50 block shifts.

| Quantity | Talk | Behavior | Activity |
| --- | --- | --- | --- |
| Σ̂₁ single-agent | +0.10 [-0.41, +0.62] | -34.20 [-179.87, +26.16] | -0.04 [-0.79, +0.39] |
| Σσ_i (marginals fitted alone) | +0.11 | -21.39 | -0.05 |
| σ_coll (all partners) | -0.41 [-10.55, +5.71], p 0.38 | +4.39 [-22.39, +14.12], p 0.02 | +0.16 [-0.50, +0.70], p 0.18 |
| σ_nam (named partners) | -4.12 [-16.33, -0.69], p 0.78 | -8.66 [-65.23, +6.36], p 0.90 | -0.39 [-3.17, +0.38], p 0.57 |
| σ_un (unnamed partners) | -1.25 [-20.51, +2.33], p 0.51 | +7.42 [-30.28, +22.02], p 0.10 | -0.82 [-4.68, +4.41], p 0.96 |
| Δ_addr = σ_nam − σ_un | -2.88 [-15.37, +12.95], p 0.58 | -16.08 [-43.95, +24.34], p 0.96 | +0.43 [-5.17, +4.48], p 0.31 |
| ρ_coll | undefined (Σ̂₁₊all ≤ 0) | undefined (Σ̂₁₊all ≤ 0) | 1.301 |
| exact-dual companion σ_nam | -4.13 | -8.83 | -0.39 |
| block-flip floor of Σ̂₁ (mean) | +0.06 | -24.59 | -0.05 |
| size-matched (12 agents) σ_nam | -3.08 | -6.02 | -0.42 |
| σ_nam without the kickoff day | -1.00 | -9.39 | -1.03 |

H50's J₁ for this period: 0.024. Talk σ_nam per agent-hour: -0.0165 nats.

## Scorecard (period-specific axes)
- C: nothing beats the shift null in talk; isolated single-channel exceedances (p ≈ 0.02) are expected at the multiplicity of 8 periods × 3 channels × 2 sets.
- F: power at G51's effect size is 0.05: a null here is inconclusive, not a refutation.
