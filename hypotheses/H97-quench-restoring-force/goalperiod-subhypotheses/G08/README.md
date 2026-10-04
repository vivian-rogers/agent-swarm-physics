# H97 × G08: design and take an open-ended benchmark (kickoff 2025-07-18)

**Verdict:** descriptive
**Role:** replication
**Period:** regime I · mode C · 4 agents with ≥ 4 statements on #7's last day and on day 1 · 1 room(s). Transition #7 → #8; the kickoff boundary is the object (exception (c)).

## Why this period
One eligible kickoff transition (both neighbours non-holdout, same regime). Common estimator, templated rule.

## Prediction
*Templated from the card (written 2026-10-04 ~20:25 UTC, amended ~20:48 UTC before any real-data statistic), labelled as such.*
Extra forgetting Δρ = ρ0 − ρ_kick > 0 (the kickoff erases more of each agent's relative position than an ordinary day), with Δρ∥ > 0. Rule: supported if Δρ's 90% CI (jackknife SE) is above 0 and Δρ∥ > 0; failed if Δρ ≤ 0; mixed otherwise.

## Result
| Statistic | bge-small | gte-modernbert | agent-centered (bge) |
| --- | --- | --- | --- |
| kickoff memory ρ_kick | +0.42 ± 0.03 | +0.47 ± 0.05 | +0.19 ± 0.04 |
| placebo memory ρ0 (median) | – | – | – |
| extra forgetting Δρ | – | – | – |
| Δρ along k̂ (∥) | – | – | – |
| Δρ transverse (⊥) | – | – | – |
| isotropy β∥ − β⊥ | +0.62 ± 2.04 | +0.47 ± 0.60 | +2.57 ± 9.52 |
| overshoot intercept a (plateau target) | +0.19 ± 0.23 | +0.18 ± 0.10 | +0.36 ± 1.00 |

Verdict reason: N < 5 or no placebo boundary: no test. Placebo boundaries: 0. Within-transition reliability of χ^mem (upper bound): –.
Data: `data/processed/H97-quench-restoring-force/G08/results.json`; all configurations in `NE34/transitions_all_configs.parquet`.

## Scorecard (period-specific axes)
- C: not tested.
- D: the intercept a is an unfitted statistic of the HH-literal law (0 under the law).

## Notes
- Holdout masked (`holdout_mask`); #23 excluded throughout.
