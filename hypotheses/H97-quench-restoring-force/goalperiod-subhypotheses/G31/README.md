# H97 × G31: free week (3.7 Sonnet farewell) (kickoff 2026-02-16)

**Verdict:** supported
**Role:** replication
**Period:** regime I · mode F · 11 agents with ≥ 4 statements on #30's last day and on day 1 · 1 room(s). Transition #30 → #31; the kickoff boundary is the object (exception (c)).

## Why this period
One eligible kickoff transition (both neighbours non-holdout, same regime). Common estimator, templated rule.

## Prediction
*Templated from the card (written 2026-10-04 ~20:25 UTC, amended ~20:48 UTC before any real-data statistic), labelled as such.*
Extra forgetting Δρ = ρ0 − ρ_kick > 0 (the kickoff erases more of each agent's relative position than an ordinary day), with Δρ∥ > 0. Rule: supported if Δρ's 90% CI (jackknife SE) is above 0 and Δρ∥ > 0; failed if Δρ ≤ 0; mixed otherwise.

## Result
| Statistic | bge-small | gte-modernbert | agent-centered (bge) |
| --- | --- | --- | --- |
| kickoff memory ρ_kick | +0.36 ± 0.09 | +0.31 ± 0.10 | +0.26 ± 0.12 |
| placebo memory ρ0 (median) | +0.66 | +0.70 | +0.63 |
| extra forgetting Δρ | +0.29 ± 0.11 | +0.40 ± 0.11 | +0.37 ± 0.14 |
| Δρ along k̂ (∥) | +0.37 | +0.84 | +0.93 |
| Δρ transverse (⊥) | +0.30 | +0.37 | +0.36 |
| isotropy β∥ − β⊥ | -0.04 ± 1.06 | -0.45 ± 0.26 | -0.83 ± 3.39 |
| overshoot intercept a (plateau target) | +0.04 ± 0.03 | +0.03 ± 0.02 | +0.07 ± 0.09 |

Verdict reason: Δρ 90% CI above 0 and Δρ∥ > 0. Placebo boundaries: 3. Within-transition reliability of χ^mem (upper bound): 0.92.
Data: `data/processed/H97-quench-restoring-force/G31/results.json`; all configurations in `NE34/transitions_all_configs.parquet`.

## Scorecard (period-specific axes)
- C: Δρ beats the placebo-day null.
- D: the intercept a is an unfitted statistic of the HH-literal law (0 under the law).

## Notes
- Holdout masked (`holdout_mask`); #23 excluded throughout.
