# H97 × G25: digital museum of 2025 (kickoff 2025-12-29)

**Verdict:** supported
**Role:** replication
**Period:** regime I · mode C · 10 agents with ≥ 4 statements on #24's last day and on day 1 · 1 room(s). Transition #24 → #25; the kickoff boundary is the object (exception (c)).

## Why this period
One eligible kickoff transition (both neighbours non-holdout, same regime). Common estimator, templated rule.

## Prediction
*Templated from the card (written 2026-10-04 ~20:25 UTC, amended ~20:48 UTC before any real-data statistic), labelled as such.*
Extra forgetting Δρ = ρ0 − ρ_kick > 0 (the kickoff erases more of each agent's relative position than an ordinary day), with Δρ∥ > 0. Rule: supported if Δρ's 90% CI (jackknife SE) is above 0 and Δρ∥ > 0; failed if Δρ ≤ 0; mixed otherwise.

## Result
| Statistic | bge-small | gte-modernbert | agent-centered (bge) |
| --- | --- | --- | --- |
| kickoff memory ρ_kick | +0.35 ± 0.07 | +0.45 ± 0.05 | +0.32 ± 0.09 |
| placebo memory ρ0 (median) | +0.73 | +0.71 | +0.67 |
| extra forgetting Δρ | +0.38 ± 0.10 | +0.26 ± 0.08 | +0.35 ± 0.11 |
| Δρ along k̂ (∥) | +1.33 | +0.87 | +1.00 |
| Δρ transverse (⊥) | +0.34 | +0.22 | +0.32 |
| isotropy β∥ − β⊥ | -0.75 ± 0.29 | -0.49 ± 0.57 | -0.68 ± 0.50 |
| overshoot intercept a (plateau target) | -0.01 ± 0.02 | +0.10 ± 0.04 | -0.01 ± 0.03 |

Verdict reason: Δρ 90% CI above 0 and Δρ∥ > 0. Placebo boundaries: 7. Within-transition reliability of χ^mem (upper bound): 0.89.
Data: `data/processed/H97-quench-restoring-force/G25/results.json`; all configurations in `NE34/transitions_all_configs.parquet`.

## Scorecard (period-specific axes)
- C: Δρ beats the placebo-day null.
- D: the intercept a is an unfitted statistic of the HH-literal law (0 under the law).

## Notes
- Holdout masked (`holdout_mask`); #23 excluded throughout.
