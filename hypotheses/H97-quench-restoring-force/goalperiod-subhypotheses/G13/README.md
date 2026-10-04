# H97 × G13: human-subjects experiment (kickoff 2025-09-08)

**Verdict:** supported
**Role:** replication
**Period:** regime I · mode C · 6 agents with ≥ 4 statements on #12's last day and on day 1 · 1 room(s). Transition #12 → #13; the kickoff boundary is the object (exception (c)).

## Why this period
One eligible kickoff transition (both neighbours non-holdout, same regime). Common estimator, templated rule.

## Prediction
*Templated from the card (written 2026-10-04 ~20:25 UTC, amended ~20:48 UTC before any real-data statistic), labelled as such.*
Extra forgetting Δρ = ρ0 − ρ_kick > 0 (the kickoff erases more of each agent's relative position than an ordinary day), with Δρ∥ > 0. Rule: supported if Δρ's 90% CI (jackknife SE) is above 0 and Δρ∥ > 0; failed if Δρ ≤ 0; mixed otherwise.

## Result
| Statistic | bge-small | gte-modernbert | agent-centered (bge) |
| --- | --- | --- | --- |
| kickoff memory ρ_kick | +0.54 ± 0.08 | +0.52 ± 0.05 | +0.34 ± 0.11 |
| placebo memory ρ0 (median) | +0.75 | +0.74 | +0.67 |
| extra forgetting Δρ | +0.21 ± 0.08 | +0.22 ± 0.05 | +0.33 ± 0.12 |
| Δρ along k̂ (∥) | +0.79 | -0.04 | +1.41 |
| Δρ transverse (⊥) | +0.19 | +0.22 | +0.30 |
| isotropy β∥ − β⊥ | -0.24 ± 1.16 | +1.01 ± 0.35 | -0.71 ± 1.45 |
| overshoot intercept a (plateau target) | +0.07 ± 0.15 | +0.14 ± 0.02 | +0.00 ± 0.17 |

Verdict reason: Δρ 90% CI above 0 and Δρ∥ > 0. Placebo boundaries: 11. Within-transition reliability of χ^mem (upper bound): 0.60.
Data: `data/processed/H97-quench-restoring-force/G13/results.json`; all configurations in `NE34/transitions_all_configs.parquet`.

## Scorecard (period-specific axes)
- C: Δρ beats the placebo-day null.
- D: the intercept a is an unfitted statistic of the HH-literal law (0 under the law).

## Notes
- Holdout masked (`holdout_mask`); #23 excluded throughout.
