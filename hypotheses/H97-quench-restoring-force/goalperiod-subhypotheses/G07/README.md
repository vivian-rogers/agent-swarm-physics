# H97 × G07: holiday (human helpers B) (kickoff 2025-07-16)

**Verdict:** descriptive
**Role:** replication
**Period:** regime I · mode F · 4 agents with ≥ 4 statements on #6's last day and on day 1 · 1 room(s). Transition #6 → #7; the kickoff boundary is the object (exception (c)).

## Why this period
One eligible kickoff transition (both neighbours non-holdout, same regime). Common estimator, templated rule.

## Prediction
*Templated from the card (written 2026-10-04 ~20:25 UTC, amended ~20:48 UTC before any real-data statistic), labelled as such.*
Extra forgetting Δρ = ρ0 − ρ_kick > 0 (the kickoff erases more of each agent's relative position than an ordinary day), with Δρ∥ > 0. Rule: supported if Δρ's 90% CI (jackknife SE) is above 0 and Δρ∥ > 0; failed if Δρ ≤ 0; mixed otherwise.

## Result
| Statistic | bge-small | gte-modernbert | agent-centered (bge) |
| --- | --- | --- | --- |
| kickoff memory ρ_kick | +0.35 ± 0.19 | +0.27 ± 0.08 | +0.14 ± 0.21 |
| placebo memory ρ0 (median) | – | – | – |
| extra forgetting Δρ | – | – | – |
| Δρ along k̂ (∥) | – | – | – |
| Δρ transverse (⊥) | – | – | – |
| isotropy β∥ − β⊥ | -0.30 ± 0.76 | +0.17 ± 0.39 | -0.44 ± 2.09 |
| overshoot intercept a (plateau target) | +0.00 ± 0.04 | -0.08 ± 0.05 | +0.01 ± 0.17 |

Verdict reason: N < 5 or no placebo boundary: no test. Placebo boundaries: 0. Within-transition reliability of χ^mem (upper bound): –.
Data: `data/processed/H97-quench-restoring-force/G07/results.json`; all configurations in `NE34/transitions_all_configs.parquet`.

## Scorecard (period-specific axes)
- C: not tested.
- D: the intercept a is an unfitted statistic of the HH-literal law (0 under the law).

## Notes
- Holdout masked (`holdout_mask`); #23 excluded throughout.
