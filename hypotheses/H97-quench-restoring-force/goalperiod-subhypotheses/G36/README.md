# H97 × G36: interact with outside agents (kickoff 2026-03-23)

**Verdict:** supported
**Role:** replication
**Period:** regime II · mode C · 12 agents with ≥ 4 statements on #35's last day and on day 1 · 2 room(s). Transition #35 → #36; the kickoff boundary is the object (exception (c)).

## Why this period
One eligible kickoff transition (both neighbours non-holdout, same regime). Common estimator, templated rule.

## Prediction
*Templated from the card (written 2026-10-04 ~20:25 UTC, amended ~20:48 UTC before any real-data statistic), labelled as such.*
Extra forgetting Δρ = ρ0 − ρ_kick > 0 (the kickoff erases more of each agent's relative position than an ordinary day), with Δρ∥ > 0. Rule: supported if Δρ's 90% CI (jackknife SE) is above 0 and Δρ∥ > 0; failed if Δρ ≤ 0; mixed otherwise.

## Result
| Statistic | bge-small | gte-modernbert | agent-centered (bge) |
| --- | --- | --- | --- |
| kickoff memory ρ_kick | +0.26 ± 0.06 | +0.26 ± 0.05 | +0.50 ± 0.07 |
| placebo memory ρ0 (median) | +0.63 | +0.63 | +0.66 |
| extra forgetting Δρ | +0.37 ± 0.07 | +0.37 ± 0.07 | +0.16 ± 0.07 |
| Δρ along k̂ (∥) | +0.50 | +0.27 | +0.73 |
| Δρ transverse (⊥) | +0.37 | +0.38 | +0.15 |
| isotropy β∥ − β⊥ | +0.03 ± 0.57 | +0.33 ± 0.23 | -0.55 ± 0.59 |
| overshoot intercept a (plateau target) | +0.18 ± 0.10 | +0.31 ± 0.02 | +0.09 ± 0.11 |

Verdict reason: Δρ 90% CI above 0 and Δρ∥ > 0. Placebo boundaries: 6. Within-transition reliability of χ^mem (upper bound): 0.81.
Data: `data/processed/H97-quench-restoring-force/G36/results.json`; all configurations in `NE34/transitions_all_configs.parquet`.

## Scorecard (period-specific axes)
- C: Δρ beats the placebo-day null.
- D: the intercept a is an unfitted statistic of the HH-literal law (0 under the law).

## Notes
- Holdout masked (`holdout_mask`); #23 excluded throughout.
