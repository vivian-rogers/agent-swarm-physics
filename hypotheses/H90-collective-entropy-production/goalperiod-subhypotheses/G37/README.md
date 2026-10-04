# H90 × G37: Pick your own goal (2026-03-30 → 04-01)

**Verdict:** mixed (underpowered at the G51 effect size; "failed" under the A1 rule)
**Role:** replication (exploratory)
**Period:** regime III · 12 agents over the period (mean 12.0 day-present) · 3 trimmed talk days (708 trimmed minutes), 3 behavior days (122 trimmed 5-min steps) · 568 agent messages naming a peer, 70 named ordered pairs.

## Why this period
- First fully regime-III goal; a free week. Smallest replication unit (3 days).

## Prediction
*Written 2026-10-04 ~20:15 UTC (card), with amendments A1 (synthetic, before real data) and A2/A3 (dated on the card), before running on this period.*
- P1: ρ_coll < 0.1 in behavior and activity where Σ̂₁₊all's CI excludes 0.
- P2 (read after A1 as lead–lag): σ_coll(talk) over the block-shift null.
- P3 (after A1 the coupling test): Δ_addr(talk) = σ_nam − σ_un > 0 against the shift null.
- Synthetic size class: N 12 × 3 days (below the S40 synthetic size); Δ_addr power at J = 1 is 1.00, at G51's effect size (J ≈ 0.28) ≤ 0.05 (A3, post hoc).

## Result
*Run 2026-10-04 ~21:45 UTC (`analysis/run.py`; data `data/processed/H90-collective-entropy-production/G37/results.json`; figure `../../figures/summary_obs.pdf`).* Units: 10⁻³ nats per system step (1 min for talk/activity, 5 min for behavior); 95% day-bootstrap CIs; p against 100 (talk) / 50 block shifts.

| Quantity | Talk | Behavior | Activity |
| --- | --- | --- | --- |
| Σ̂₁ single-agent | -0.05 [-0.18, -0.02] | -154.26 [-375.70, -66.26] | +0.13 [-0.27, +0.57] |
| Σσ_i (marginals fitted alone) | -0.04 | -120.53 | +0.16 |
| σ_coll (all partners) | -0.16 [-5.05, +7.93], p 0.24 | -47.45 [-91.64, -30.03], p 0.98 | -1.52 [-3.34, -0.25], p 0.98 |
| σ_nam (named partners) | +0.46 [-0.87, +3.68], p 0.25 | -58.29 [-313.65, -15.17], p 0.78 | -1.59 [-4.70, -0.32], p 0.49 |
| σ_un (unnamed partners) | -4.44 [-17.66, +2.20], p 0.62 | -86.50 [-134.51, -86.50], p 1.00 | -0.80 [-4.22, +0.01], p 0.59 |
| Δ_addr = σ_nam − σ_un | +4.90 [+1.45, +16.95], p 0.26 | +28.21 [-207.16, +119.34], p 0.14 | -0.80 [-4.39, +3.90], p 0.55 |
| ρ_coll | undefined (Σ̂₁₊all ≤ 0) | undefined (Σ̂₁₊all ≤ 0) | undefined (Σ̂₁₊all ≤ 0) |
| exact-dual companion σ_nam | +0.44 | -59.86 | -1.59 |
| block-flip floor of Σ̂₁ (mean) | -0.03 | -82.14 | +0.02 |

H50's J₁ for this period: 0.097. Talk σ_nam per agent-hour: +0.0023 nats.

## Scorecard (period-specific axes)
- C: nothing beats the shift null in talk; behavior and activity are at the floor.
- F: power at G51's effect size is ≤ 0.05: a null here is inconclusive, not a refutation.
