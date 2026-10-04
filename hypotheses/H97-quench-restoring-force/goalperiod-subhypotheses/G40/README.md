# H97 × G40: connect worlds into a 3D universe (kickoff 2026-05-04)

**Verdict:** supported
**Role:** replication
**Period:** regime III · mode C · 15 agents with ≥ 4 statements on #39's last day and on day 1 · 1 room(s). Transition #39 → #40; the kickoff boundary is the object (exception (c)).

## Why this period
One eligible kickoff transition (both neighbours non-holdout, same regime). Common estimator, templated rule.

## Prediction
*Templated from the card (written 2026-10-04 ~20:25 UTC, amended ~20:48 UTC before any real-data statistic), labelled as such.*
Extra forgetting Δρ = ρ0 − ρ_kick > 0 (the kickoff erases more of each agent's relative position than an ordinary day), with Δρ∥ > 0. Rule: supported if Δρ's 90% CI (jackknife SE) is above 0 and Δρ∥ > 0; failed if Δρ ≤ 0; mixed otherwise.

## Result
| Statistic | bge-small | gte-modernbert | agent-centered (bge) |
| --- | --- | --- | --- |
| kickoff memory ρ_kick | +0.69 ± 0.06 | +0.68 ± 0.07 | +0.69 ± 0.06 |
| placebo memory ρ0 (median) | +0.83 | +0.82 | +0.82 |
| extra forgetting Δρ | +0.14 ± 0.06 | +0.14 ± 0.07 | +0.13 ± 0.06 |
| Δρ along k̂ (∥) | +0.36 | +0.08 | +0.29 |
| Δρ transverse (⊥) | +0.13 | +0.13 | +0.13 |
| isotropy β∥ − β⊥ | -0.17 ± 0.20 | -0.00 ± 0.22 | -0.02 ± 0.17 |
| overshoot intercept a (plateau target) | +0.13 ± 0.03 | +0.15 ± 0.03 | +0.16 ± 0.03 |

Verdict reason: Δρ 90% CI above 0 and Δρ∥ > 0. Placebo boundaries: 7. Within-transition reliability of χ^mem (upper bound): 0.91.
Data: `data/processed/H97-quench-restoring-force/G40/results.json`; all configurations in `NE34/transitions_all_configs.parquet`.

## Scorecard (period-specific axes)
- C: Δρ beats the placebo-day null.
- D: the intercept a is an unfitted statistic of the HH-literal law (0 under the law).

## Notes
- Holdout masked (`holdout_mask`); #23 excluded throughout.
