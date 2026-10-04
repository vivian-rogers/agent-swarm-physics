# H97 × G27: Juice Shop hacking competition (kickoff 2026-01-12)

**Verdict:** supported
**Role:** replication
**Period:** regime I · mode K · 10 agents with ≥ 4 statements on #26's last day and on day 1 · 1 room(s). Transition #26 → #27; the kickoff boundary is the object (exception (c)).

## Why this period
One eligible kickoff transition (both neighbours non-holdout, same regime). Common estimator, templated rule.

## Prediction
*Templated from the card (written 2026-10-04 ~20:25 UTC, amended ~20:48 UTC before any real-data statistic), labelled as such.*
Extra forgetting Δρ = ρ0 − ρ_kick > 0 (the kickoff erases more of each agent's relative position than an ordinary day), with Δρ∥ > 0. Rule: supported if Δρ's 90% CI (jackknife SE) is above 0 and Δρ∥ > 0; failed if Δρ ≤ 0; mixed otherwise.

## Result
| Statistic | bge-small | gte-modernbert | agent-centered (bge) |
| --- | --- | --- | --- |
| kickoff memory ρ_kick | +0.16 ± 0.13 | +0.17 ± 0.10 | +0.23 ± 0.10 |
| placebo memory ρ0 (median) | +0.58 | +0.58 | +0.59 |
| extra forgetting Δρ | +0.43 ± 0.14 | +0.41 ± 0.10 | +0.35 ± 0.10 |
| Δρ along k̂ (∥) | +1.07 | -0.09 | +1.15 |
| Δρ transverse (⊥) | +0.40 | +0.42 | +0.32 |
| isotropy β∥ − β⊥ | -0.97 ± 1.47 | +1.15 ± 0.66 | -1.00 ± 1.08 |
| overshoot intercept a (plateau target) | -0.24 ± 0.57 | +0.56 ± 0.24 | -0.21 ± 0.42 |

Verdict reason: Δρ 90% CI above 0 and Δρ∥ > 0. Placebo boundaries: 12. Within-transition reliability of χ^mem (upper bound): 0.92.
Data: `data/processed/H97-quench-restoring-force/G27/results.json`; all configurations in `NE34/transitions_all_configs.parquet`.

## Scorecard (period-specific axes)
- C: Δρ beats the placebo-day null.
- D: the intercept a is an unfitted statistic of the HH-literal law (0 under the law).

## Notes
- Holdout masked (`holdout_mask`); #23 excluded throughout.
