# H105 × NE38: a field on one spin (#51, Claude Opus 5 reassigned 2026-07-29)

**Verdict:** mixed
**Role:** native
**Period:** regime III · mode I/K · ~20 agents · rooms · pre 07-24 → 07-29 16:51 UTC, post 16:51 → 08-04 (inside 51e/51f).

## Why this period
A human changed one agent's private goal. In a coupled two-state model the other agents' occupancy along that agent's new direction rises by about J₂·v·Δp/N. A field on one spin is the cleanest test of coupling transfer in the record.

## Prediction
*Written 2026-10-04 ~20:41 UTC, before running on this unit.*
- **N3:** Opus 5's own occupancy along its new goal rises by > 0.3; the other agents' occupancy along Opus 5's new goal changes by less than 0.02 in absolute value, as a difference-in-differences against their change along the other agents' own-goal directions (placebo directions). Credence 0.65.
- Counts against: the others' change > 0.03 with a 90% CI that excludes 0.

## Result
| Statistic | bge-small | gte-modernbert |
| --- | --- | --- |
| Opus 5's occupancy along its new goal, pre → post | 0.00 → 0.96 | 0.00 → 0.98 |
| others' occupancy along Opus 5's new goal, pre → post | 0.069 → 0.073 | 0.022 → 0.069 |
| placebo change (others along other agents' goals), mean ± SD | −0.008 ± 0.012 | −0.005 ± 0.015 |
| DiD [90% block-bootstrap CI] | +0.012 [−0.006, +0.031] | +0.052 [+0.040, +0.070] |

**N3 mixed (model-dependent):** the field flips Opus 5's spin from 0 to ≈ 1 in both models (a complete one-spin quench, beyond p = ½). The others' occupancy along Opus 5's new direction does not move under bge (DiD +0.01, inside ±0.02) but rises by 0.05 under gte (CI excludes 0). A rise of 0.05 is larger than the mean-field transfer J₂·v·Δp/N ≈ 0.003 at the fitted couplings, so if real it is not coupling through occupancy; it may be the others writing about the new mathematician (talking about Opus 5's new work), which the gte direction picks up. Data: `data/processed/H105-two-state-goal-order/natives/NE38.json`.

## Scorecard (period-specific axes)
- E: a dated one-agent intervention (DQ6); the own-spin quench is unambiguous; transfer is model-dependent.
- G: the target is Opus 5's DQ6 role text.

## Notes
