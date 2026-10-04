# H97 × G20: Substack blogs (kickoff 2025-11-17)

**Verdict:** supported
**Role:** replication
**Period:** regime I · mode I · 8 agents with ≥ 4 statements on #19's last day and on day 1 · 1 room(s). Transition #19 → #20; the kickoff boundary is the object (exception (c)).

## Why this period
One eligible kickoff transition (both neighbours non-holdout, same regime). Common estimator, templated rule.

## Prediction
*Templated from the card (written 2026-10-04 ~20:25 UTC, amended ~20:48 UTC before any real-data statistic), labelled as such.*
Extra forgetting Δρ = ρ0 − ρ_kick > 0 (the kickoff erases more of each agent's relative position than an ordinary day), with Δρ∥ > 0. Rule: supported if Δρ's 90% CI (jackknife SE) is above 0 and Δρ∥ > 0; failed if Δρ ≤ 0; mixed otherwise.

## Result
| Statistic | bge-small | gte-modernbert | agent-centered (bge) |
| --- | --- | --- | --- |
| kickoff memory ρ_kick | +0.36 ± 0.03 | +0.33 ± 0.07 | +0.29 ± 0.07 |
| placebo memory ρ0 (median) | +0.55 | +0.57 | +0.44 |
| extra forgetting Δρ | +0.18 ± 0.05 | +0.24 ± 0.09 | +0.14 ± 0.08 |
| Δρ along k̂ (∥) | +0.42 | +0.14 | +0.35 |
| Δρ transverse (⊥) | +0.17 | +0.22 | +0.14 |
| isotropy β∥ − β⊥ | -0.49 ± 1.16 | +0.46 ± 0.89 | -0.40 ± 1.24 |
| overshoot intercept a (plateau target) | +0.23 ± 0.09 | +0.25 ± 0.03 | +0.22 ± 0.09 |

Verdict reason: Δρ 90% CI above 0 and Δρ∥ > 0. Placebo boundaries: 13. Within-transition reliability of χ^mem (upper bound): 0.00.
Data: `data/processed/H97-quench-restoring-force/G20/results.json`; all configurations in `NE34/transitions_all_configs.parquet`.

## Scorecard (period-specific axes)
- C: Δρ beats the placebo-day null.
- D: the intercept a is an unfitted statistic of the HH-literal law (0 under the law).

## Notes
- Holdout masked (`holdout_mask`); #23 excluded throughout.
