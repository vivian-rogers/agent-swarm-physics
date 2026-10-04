# H90 × G39: Build your own interactive world (2026-04-27 → 05-01)

**Verdict:** mixed (underpowered at the G51 effect size; "failed" under the A1 rule)
**Role:** replication (exploratory)
**Period:** regime III · 15 agents over the period (mean 14.8 day-present) · 5 trimmed talk days (808 trimmed minutes), 5 behavior days (164 trimmed 5-min steps) · 473 agent messages naming a peer, 93 named ordered pairs.

## Why this period
- One agent per world: individual objectives, little reason to coordinate. A low-coupling baseline.

## Prediction
*Written 2026-10-04 ~20:15 UTC (card), with amendments A1 (synthetic, before real data) and A2/A3 (dated on the card), before running on this period.*
- P1: ρ_coll < 0.1 in behavior and activity where Σ̂₁₊all's CI excludes 0.
- P2 (read after A1 as lead–lag): σ_coll(talk) over the block-shift null.
- P3 (after A1 the coupling test): Δ_addr(talk) = σ_nam − σ_un > 0 against the shift null.
- Synthetic size class: S40; Δ_addr power at J = 1 is 1.00, at G51's effect size (J ≈ 0.28) 0.05 (A3, post hoc).

## Result
*Run 2026-10-04 ~21:45 UTC (`analysis/run.py`; data `data/processed/H90-collective-entropy-production/G39/results.json`; figure `../../figures/summary_obs.pdf`).* Units: 10⁻³ nats per system step (1 min for talk/activity, 5 min for behavior); 95% day-bootstrap CIs; p against 100 (talk) / 50 block shifts.

| Quantity | Talk | Behavior | Activity |
| --- | --- | --- | --- |
| Σ̂₁ single-agent | -0.17 [-3.91, -0.11] | +29.20 [-209.00, +73.16] | -0.03 [-1.04, +0.36] |
| Σσ_i (marginals fitted alone) | -0.17 | +22.97 | -0.03 |
| σ_coll (all partners) | -3.03 [-44.45, +6.75], p 0.50 | -5.80 [-222.69, +8.49], p 0.71 | +0.14 [-1.69, +2.43], p 0.24 |
| σ_nam (named partners) | -10.24 [-88.34, +5.19], p 0.74 | -13.55 [-133.27, +2.36], p 0.82 | +0.72 [-2.29, +3.55], p 0.24 |
| σ_un (unnamed partners) | -10.79 [-30.86, +4.46], p 0.92 | -9.59 [-410.42, +11.26], p 0.75 | -1.58 [-4.48, -1.29], p 0.96 |
| Δ_addr = σ_nam − σ_un | +0.55 [-73.55, +21.49], p 0.37 | -3.96 [-73.89, +302.42], p 0.73 | +2.30 [+0.53, +7.01], p 0.06 |
| ρ_coll | undefined (Σ̂₁₊all ≤ 0) | -0.248 | 1.226 |
| exact-dual companion σ_nam | -10.59 | -13.22 | +0.72 |
| block-flip floor of Σ̂₁ (mean) | -0.23 | -29.79 | +0.03 |
| size-matched (12 agents) σ_nam | -7.03 | -7.62 | +0.31 |
| σ_nam without the kickoff day | -9.77 | -12.88 | +0.20 |

H50's J₁ for this period: 0.026. Talk σ_nam per agent-hour: -0.0415 nats.

## Scorecard (period-specific axes)
- C: nothing beats the shift null in talk; behavior and activity are at the floor.
- F: power at G51's effect size is 0.05: a null here is inconclusive, not a refutation.
