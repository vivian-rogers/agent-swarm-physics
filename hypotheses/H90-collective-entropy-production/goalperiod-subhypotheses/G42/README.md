# H90 × G42: Run your own YouTube channel (2026-05-18 → 05-22)

**Verdict:** mixed (underpowered at the G51 effect size; "failed" under the A1 rule)
**Role:** replication (exploratory)
**Period:** regime III · 16 agents over the period (mean 15.6 day-present) · 5 trimmed talk days (1123 trimmed minutes), 5 behavior days (197 trimmed 5-min steps) · 1223 agent messages naming a peer, 91 named ordered pairs.

## Why this period
- Individual channels with a shared misreading of the brief (H26/H34): a content cascade week.

## Prediction
*Written 2026-10-04 ~20:15 UTC (card), with amendments A1 (synthetic, before real data) and A2/A3 (dated on the card), before running on this period.*
- P1: ρ_coll < 0.1 in behavior and activity where Σ̂₁₊all's CI excludes 0.
- P2 (read after A1 as lead–lag): σ_coll(talk) over the block-shift null.
- P3 (after A1 the coupling test): Δ_addr(talk) = σ_nam − σ_un > 0 against the shift null.
- Synthetic size class: S40; Δ_addr power at J = 1 is 1.00, at G51's effect size (J ≈ 0.28) 0.05 (A3, post hoc).

## Result
*Run 2026-10-04 ~21:45 UTC (`analysis/run.py`; data `data/processed/H90-collective-entropy-production/G42/results.json`; figure `../../figures/summary_obs.pdf`).* Units: 10⁻³ nats per system step (1 min for talk/activity, 5 min for behavior); 95% day-bootstrap CIs; p against 100 (talk) / 50 block shifts.

| Quantity | Talk | Behavior | Activity |
| --- | --- | --- | --- |
| Σ̂₁ single-agent | +0.25 [-0.26, +1.02] | +20.26 [-176.39, +32.08] | +0.23 [-0.19, +0.34] |
| Σσ_i (marginals fitted alone) | +0.27 | +14.85 | +0.22 |
| σ_coll (all partners) | +0.13 [-17.55, +7.83], p 0.29 | -6.48 [-96.04, +3.14], p 0.78 | -0.22 [-1.11, +0.19], p 0.65 |
| σ_nam (named partners) | -4.55 [-30.24, +6.58], p 0.78 | -11.08 [-157.67, +18.04], p 0.78 | -0.23 [-4.90, +5.69], p 0.43 |
| σ_un (unnamed partners) | -3.48 [-18.45, +8.26], p 0.61 | -9.75 [-121.50, +0.84], p 0.90 | -0.11 [-1.26, +0.19], p 0.43 |
| Δ_addr = σ_nam − σ_un | -1.06 [-23.25, +15.61], p 0.63 | -1.33 [-44.91, +28.52], p 0.55 | -0.12 [-5.05, +6.22], p 0.45 |
| ρ_coll | 0.343 | -0.471 | -18.868 |
| exact-dual companion σ_nam | -4.52 | -11.25 | -0.22 |
| block-flip floor of Σ̂₁ (mean) | +0.02 | -24.89 | +0.13 |
| size-matched (12 agents) σ_nam | -3.74 | -9.69 | -0.52 |
| σ_nam without the kickoff day | -4.02 | -6.49 | +2.07 |

H50's J₁ for this period: 0.022. Talk σ_nam per agent-hour: -0.0175 nats.

## Scorecard (period-specific axes)
- C: nothing beats the shift null in talk; behavior and activity are at the floor.
- F: power at G51's effect size is 0.05: a null here is inconclusive, not a refutation.
