# H97 × G18: reduce global poverty (kickoff 2025-10-20)

**Verdict:** failed
**Role:** replication
**Period:** regime I · mode C · 7 agents with ≥ 4 statements on #17's last day and on day 1 · 1 room(s). Transition #17 → #18; the kickoff boundary is the object (exception (c)).

## Why this period
One eligible kickoff transition (both neighbours non-holdout, same regime). Common estimator, templated rule.

## Prediction
*Templated from the card (written 2026-10-04 ~20:25 UTC, amended ~20:48 UTC before any real-data statistic), labelled as such.*
Extra forgetting Δρ = ρ0 − ρ_kick > 0 (the kickoff erases more of each agent's relative position than an ordinary day), with Δρ∥ > 0. Rule: supported if Δρ's 90% CI (jackknife SE) is above 0 and Δρ∥ > 0; failed if Δρ ≤ 0; mixed otherwise.

## Result
| Statistic | bge-small | gte-modernbert | agent-centered (bge) |
| --- | --- | --- | --- |
| kickoff memory ρ_kick | +0.54 ± 0.07 | +0.47 ± 0.06 | +0.53 ± 0.09 |
| placebo memory ρ0 (median) | +0.54 | +0.55 | +0.51 |
| extra forgetting Δρ | -0.01 ± 0.08 | +0.08 ± 0.07 | -0.02 ± 0.10 |
| Δρ along k̂ (∥) | +0.44 | +1.28 | +0.06 |
| Δρ transverse (⊥) | -0.01 | +0.07 | -0.02 |
| isotropy β∥ − β⊥ | -0.73 ± 0.74 | -0.83 ± 0.48 | -0.07 ± 0.80 |
| overshoot intercept a (plateau target) | +0.18 ± 0.03 | +0.29 ± 0.03 | +0.16 ± 0.04 |

Verdict reason: Δρ ≤ 0. Placebo boundaries: 10. Within-transition reliability of χ^mem (upper bound): 0.86.
Data: `data/processed/H97-quench-restoring-force/G18/results.json`; all configurations in `NE34/transitions_all_configs.parquet`.

## Scorecard (period-specific axes)
- C: not beyond the placebo null at this N.
- D: the intercept a is an unfitted statistic of the HH-literal law (0 under the law).

## Notes
- Holdout masked (`holdout_mask`); #23 excluded throughout.
