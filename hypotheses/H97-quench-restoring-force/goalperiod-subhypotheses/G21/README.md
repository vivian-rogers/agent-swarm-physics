# H97 × G21: AI forecasts (kickoff 2025-12-01)

**Verdict:** supported
**Role:** replication
**Period:** regime I · mode I · 8 agents with ≥ 4 statements on #20's last day and on day 1 · 1 room(s). Transition #20 → #21; the kickoff boundary is the object (exception (c)).

## Why this period
One eligible kickoff transition (both neighbours non-holdout, same regime). Common estimator, templated rule.

## Prediction
*Templated from the card (written 2026-10-04 ~20:25 UTC, amended ~20:48 UTC before any real-data statistic), labelled as such.*
Extra forgetting Δρ = ρ0 − ρ_kick > 0 (the kickoff erases more of each agent's relative position than an ordinary day), with Δρ∥ > 0. Rule: supported if Δρ's 90% CI (jackknife SE) is above 0 and Δρ∥ > 0; failed if Δρ ≤ 0; mixed otherwise.

## Result
| Statistic | bge-small | gte-modernbert | agent-centered (bge) |
| --- | --- | --- | --- |
| kickoff memory ρ_kick | +0.28 ± 0.05 | +0.29 ± 0.07 | +0.22 ± 0.04 |
| placebo memory ρ0 (median) | +0.64 | +0.64 | +0.62 |
| extra forgetting Δρ | +0.35 ± 0.08 | +0.35 ± 0.10 | +0.41 ± 0.08 |
| Δρ along k̂ (∥) | +0.70 | +0.55 | +0.62 |
| Δρ transverse (⊥) | +0.34 | +0.35 | +0.40 |
| isotropy β∥ − β⊥ | -0.24 ± 0.67 | -0.15 ± 1.13 | -0.17 ± 0.39 |
| overshoot intercept a (plateau target) | +0.18 ± 0.04 | +0.19 ± 0.05 | +0.18 ± 0.03 |

Verdict reason: Δρ 90% CI above 0 and Δρ∥ > 0. Placebo boundaries: 8. Within-transition reliability of χ^mem (upper bound): 0.62.
Data: `data/processed/H97-quench-restoring-force/G21/results.json`; all configurations in `NE34/transitions_all_configs.parquet`.

## Scorecard (period-specific axes)
- C: Δρ beats the placebo-day null.
- D: the intercept a is an unfitted statistic of the HH-literal law (0 under the law).

## Notes
- Holdout masked (`holdout_mask`); #23 excluded throughout.
