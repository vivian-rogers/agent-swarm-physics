# H97 × G17: personal websites (kickoff 2025-10-13)

**Verdict:** mixed
**Role:** replication
**Period:** regime I · mode I · 7 agents with ≥ 4 statements on #16's last day and on day 1 · 1 room(s). Transition #16 → #17; the kickoff boundary is the object (exception (c)).

## Why this period
One eligible kickoff transition (both neighbours non-holdout, same regime). Common estimator, templated rule.

## Prediction
*Templated from the card (written 2026-10-04 ~20:25 UTC, amended ~20:48 UTC before any real-data statistic), labelled as such.*
Extra forgetting Δρ = ρ0 − ρ_kick > 0 (the kickoff erases more of each agent's relative position than an ordinary day), with Δρ∥ > 0. Rule: supported if Δρ's 90% CI (jackknife SE) is above 0 and Δρ∥ > 0; failed if Δρ ≤ 0; mixed otherwise.

## Result
| Statistic | bge-small | gte-modernbert | agent-centered (bge) |
| --- | --- | --- | --- |
| kickoff memory ρ_kick | +0.46 ± 0.16 | +0.57 ± 0.13 | +0.34 ± 0.19 |
| placebo memory ρ0 (median) | +0.56 | +0.55 | +0.52 |
| extra forgetting Δρ | +0.10 ± 0.16 | -0.02 ± 0.14 | +0.19 ± 0.19 |
| Δρ along k̂ (∥) | +0.81 | +0.21 | +0.75 |
| Δρ transverse (⊥) | +0.06 | -0.02 | +0.16 |
| isotropy β∥ − β⊥ | -0.79 ± 0.90 | +0.36 ± 0.63 | -0.36 ± 0.93 |
| overshoot intercept a (plateau target) | -0.01 ± 0.11 | +0.13 ± 0.10 | +0.02 ± 0.13 |

Verdict reason: Δρ > 0 but its 90% CI includes 0. Placebo boundaries: 7. Within-transition reliability of χ^mem (upper bound): 0.98.
Data: `data/processed/H97-quench-restoring-force/G17/results.json`; all configurations in `NE34/transitions_all_configs.parquet`.

## Scorecard (period-specific axes)
- C: not beyond the placebo null at this N.
- D: the intercept a is an unfitted statistic of the HH-literal law (0 under the law).

## Notes
- Holdout masked (`holdout_mask`); #23 excluded throughout.
