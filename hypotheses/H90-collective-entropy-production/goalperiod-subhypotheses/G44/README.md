# H90 × G44: Fine-tune your leader (#best) / pick your own goals (#rest) (2026-05-26 → 05-29)

**Verdict:** mixed (underpowered at the G51 effect size; "failed" under the A1 rule)
**Role:** replication (exploratory)
**Period:** regime III · 18 agents over the period (mean 17.0 day-present) · 3 trimmed talk days (408 trimmed minutes), 3 behavior days (46 trimmed 5-min steps) · 2094 agent messages naming a peer, 116 named ordered pairs.

## Why this period
- Two room kickoffs on the same days; the trimmed window is short (9 five-minute steps a day), so behavior is near-unusable.

## Prediction
*Written 2026-10-04 ~20:15 UTC (card), with amendments A1 (synthetic, before real data) and A2/A3 (dated on the card), before running on this period.*
- P1: ρ_coll < 0.1 in behavior and activity where Σ̂₁₊all's CI excludes 0.
- P2 (read after A1 as lead–lag): σ_coll(talk) over the block-shift null.
- P3 (after A1 the coupling test): Δ_addr(talk) = σ_nam − σ_un > 0 against the shift null.
- Synthetic size class: N 18 × 3 days, 9 trimmed 5-min steps per day (below S40); Δ_addr power at J = 1 is 1.00, at G51's effect size (J ≈ 0.28) ≤ 0.05 (A3, post hoc).

## Result
*Run 2026-10-04 ~21:45 UTC (`analysis/run.py`; data `data/processed/H90-collective-entropy-production/G44/results.json`; figure `../../figures/summary_obs.pdf`).* Units: 10⁻³ nats per system step (1 min for talk/activity, 5 min for behavior); 95% day-bootstrap CIs; p against 100 (talk) / 50 block shifts.

| Quantity | Talk | Behavior | Activity |
| --- | --- | --- | --- |
| Σ̂₁ single-agent | -0.54 [-5.41, -0.54] | -211.04 [-8492.73, -60.66] | -1.06 [-7.37, +0.21] |
| Σσ_i (marginals fitted alone) | -0.51 | -229.65 | -1.06 |
| σ_coll (all partners) | -6.71 [-69.96, -6.71], p 0.76 | -83.92 [-6940.16, -83.92], p 0.16 | -2.35 [-19.30, -0.23], p 0.92 |
| σ_nam (named partners) | +2.70 [-137.96, +2.70], p 0.30 | -302.15 [-10844.70, -302.15], p 0.63 | -10.03 [-67.81, -10.03], p 1.00 |
| σ_un (unnamed partners) | -20.43 [-121.69, -18.45], p 0.90 | -309.58 [-22033.84, -309.58], p 0.55 | +0.30 [-8.04, +2.19], p 0.12 |
| Δ_addr = σ_nam − σ_un | +23.12 [-39.98, +23.12], p 0.13 | +7.43 [-48.33, +11189.14], p 0.67 | -10.33 [-59.78, -10.33], p 1.00 |
| ρ_coll | undefined (Σ̂₁₊all ≤ 0) | undefined (Σ̂₁₊all ≤ 0) | undefined (Σ̂₁₊all ≤ 0) |
| exact-dual companion σ_nam | +2.78 | -349.87 | -10.00 |
| block-flip floor of Σ̂₁ (mean) | -0.96 | -644.64 | -0.90 |
| size-matched (12 agents) σ_nam | -0.90 | -185.43 | -3.74 |

H50's J₁ for this period: 0.025. Talk σ_nam per agent-hour: +0.0095 nats.

## Scorecard (period-specific axes)
- C: nothing beats the shift null in talk; behavior and activity are at the floor.
- F: power at G51's effect size is ≤ 0.05: a null here is inconclusive, not a refutation.
