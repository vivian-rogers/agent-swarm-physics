# H90 × G38: Choose a charity and raise money (two rooms) (2026-04-02 → 04-24)

**Verdict:** mixed (replication underpowered; native N1 rooms: supported, weak)
**Role:** replication + native (exploratory)
**Period:** regime III · 14 agents over the period (mean 12.4 day-present) · 17 trimmed talk days (3337 trimmed minutes), 17 behavior days (649 trimmed 5-min steps) · 2829 agent messages naming a peer, 78 named ordered pairs.

## Why this period
- 17-day two-room period (#best / #rest) with per-agent goal overrides; the second-largest sample. Also hosts native N1 (rooms route reading).

## Prediction
*Written 2026-10-04 ~20:15 UTC (card), with amendments A1 (synthetic, before real data) and A2/A3 (dated on the card), before running on this period.*
- P1: ρ_coll < 0.1 in behavior and activity where Σ̂₁₊all's CI excludes 0.
- P2 (read after A1 as lead–lag): σ_coll(talk) over the block-shift null.
- P3 (after A1 the coupling test): Δ_addr(talk) = σ_nam − σ_un > 0 against the shift null.
- Synthetic size class: S38 (N 13 × 16 days); Δ_addr power at J = 1 is 1.00, at G51's effect size (J ≈ 0.28) 0.45 (A3, post hoc).

## Result
*Run 2026-10-04 ~21:45 UTC (`analysis/run.py`; data `data/processed/H90-collective-entropy-production/G38/results.json`; figure `../../figures/summary_obs.pdf`).* Units: 10⁻³ nats per system step (1 min for talk/activity, 5 min for behavior); 95% day-bootstrap CIs; p against 100 (talk) / 50 block shifts.

| Quantity | Talk | Behavior | Activity |
| --- | --- | --- | --- |
| Σ̂₁ single-agent | -0.01 [-0.12, +0.11] | +14.77 [-22.70, +43.32] | +0.15 [-0.03, +0.35] |
| Σσ_i (marginals fitted alone) | -0.01 | +12.88 | +0.15 |
| σ_coll (all partners) | +0.25 [-2.30, +1.95], p 0.23 | +0.42 [-4.60, +3.54], p 0.24 | +0.03 [-0.29, +0.24], p 0.31 |
| σ_nam (named partners) | +0.92 [-4.36, +5.65], p 0.21 | -1.33 [-10.33, +6.39], p 0.57 | -0.20 [-0.79, +0.19], p 0.57 |
| σ_un (unnamed partners) | -1.30 [-4.36, +1.40], p 0.93 | +3.47 [-5.15, +11.16], p 0.04 | -0.27 [-0.62, -0.03], p 0.96 |
| Δ_addr = σ_nam − σ_un | +2.22 [-5.08, +8.49], p 0.08 | -4.80 [-18.38, +6.98], p 0.92 | +0.07 [-0.49, +0.59], p 0.29 |
| ρ_coll | 1.055 | 0.028 | 0.144 |
| exact-dual companion σ_nam | +0.92 | -1.31 | -0.20 |
| block-flip floor of Σ̂₁ (mean) | -0.02 | -4.94 | +0.03 |
| size-matched (12 agents) σ_nam | +0.49 | -0.68 | -0.14 |
| σ_nam without the kickoff day | -0.18 | -0.24 | -0.22 |

H50's J₁ for this period: 0.009. Talk σ_nam per agent-hour: +0.0044 nats.

## Scorecard (period-specific axes)
- C: nothing beats the shift null in talk; behavior and activity are at the floor.
- F: power at G51's effect size is 0.45: a null here is inconclusive, not a refutation.

## Native N1: rooms route reading
*Prediction (card, 2026-10-04 ~20:15 UTC):* σ_same(talk) > σ_cross(talk), and σ_cross inside its shift null. Credence 0.45.

| Channel | σ_same (10⁻³) | p_shift | σ_cross (10⁻³) | p_shift | Verdict |
| --- | --- | --- | --- | --- | --- |
| talk | +1.65 [-2.76, +5.32] | 0.030 | -0.71 [-3.65, +3.32] | 0.66 | supported by the rule (bootstrap CI of σ_same spans 0) |
| behavior | -2.84 | 0.80 | +3.10 | 0.039 | opposite sign (descriptive) |

Rooms: #best (2) and #rest (3) on every day (midpoint of the day window, `rooms_timeline`). Native verdict: **supported (weak)**: same-room talk partners carry a lead–lag that cross-room partners do not, at p 0.03 against the shift null; the day bootstrap does not exclude 0.
