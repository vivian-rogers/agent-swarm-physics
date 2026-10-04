# H97 × G41: novel research (kickoff 2026-05-11)

**Verdict:** supported
**Role:** replication
**Period:** regime III · mode I · 15 agents with ≥ 4 statements on #40's last day and on day 1 · 2 room(s). Transition #40 → #41; the kickoff boundary is the object (exception (c)).

## Why this period
One eligible kickoff transition (both neighbours non-holdout, same regime). Common estimator, templated rule.

## Prediction
*Templated from the card (written 2026-10-04 ~20:25 UTC, amended ~20:48 UTC before any real-data statistic), labelled as such.*
Extra forgetting Δρ = ρ0 − ρ_kick > 0 (the kickoff erases more of each agent's relative position than an ordinary day), with Δρ∥ > 0. Rule: supported if Δρ's 90% CI (jackknife SE) is above 0 and Δρ∥ > 0; failed if Δρ ≤ 0; mixed otherwise.

## Result
| Statistic | bge-small | gte-modernbert | agent-centered (bge) |
| --- | --- | --- | --- |
| kickoff memory ρ_kick | +0.40 ± 0.13 | +0.40 ± 0.12 | +0.45 ± 0.10 |
| placebo memory ρ0 (median) | +0.81 | +0.84 | +0.81 |
| extra forgetting Δρ | +0.42 ± 0.14 | +0.43 ± 0.12 | +0.36 ± 0.11 |
| Δρ along k̂ (∥) | +0.56 | +0.51 | +0.59 |
| Δρ transverse (⊥) | +0.41 | +0.43 | +0.35 |
| isotropy β∥ − β⊥ | -0.17 ± 0.12 | -0.08 ± 0.15 | -0.19 ± 0.24 |
| overshoot intercept a (plateau target) | +0.14 ± 0.02 | +0.12 ± 0.02 | +0.14 ± 0.03 |

Verdict reason: Δρ 90% CI above 0 and Δρ∥ > 0. Placebo boundaries: 7. Within-transition reliability of χ^mem (upper bound): 0.99.
Data: `data/processed/H97-quench-restoring-force/G41/results.json`; all configurations in `NE34/transitions_all_configs.parquet`.

## Scorecard (period-specific axes)
- C: Δρ beats the placebo-day null.
- D: the intercept a is an unfitted statistic of the HH-literal law (0 under the law).

## Notes
- Holdout masked (`holdout_mask`); #23 excluded throughout.
