# H97 × G39: build your own interactive world (kickoff 2026-04-27)

**Verdict:** supported
**Role:** replication
**Period:** regime III · mode I · 13 agents with ≥ 4 statements on #38's last day and on day 1 · 2 room(s). Transition #38 → #39; the kickoff boundary is the object (exception (c)).

## Why this period
One eligible kickoff transition (both neighbours non-holdout, same regime). Common estimator, templated rule.

## Prediction
*Templated from the card (written 2026-10-04 ~20:25 UTC, amended ~20:48 UTC before any real-data statistic), labelled as such.*
Extra forgetting Δρ = ρ0 − ρ_kick > 0 (the kickoff erases more of each agent's relative position than an ordinary day), with Δρ∥ > 0. Rule: supported if Δρ's 90% CI (jackknife SE) is above 0 and Δρ∥ > 0; failed if Δρ ≤ 0; mixed otherwise.

## Result
| Statistic | bge-small | gte-modernbert | agent-centered (bge) |
| --- | --- | --- | --- |
| kickoff memory ρ_kick | +0.23 ± 0.07 | +0.37 ± 0.07 | +0.25 ± 0.05 |
| placebo memory ρ0 (median) | +0.84 | +0.83 | +0.84 |
| extra forgetting Δρ | +0.60 ± 0.07 | +0.47 ± 0.07 | +0.59 ± 0.05 |
| Δρ along k̂ (∥) | +0.34 | +0.06 | +0.41 |
| Δρ transverse (⊥) | +0.61 | +0.48 | +0.60 |
| isotropy β∥ − β⊥ | +0.33 ± 0.47 | +0.55 ± 0.22 | +0.14 ± 0.49 |
| overshoot intercept a (plateau target) | +0.17 ± 0.07 | +0.31 ± 0.08 | +0.14 ± 0.08 |

Verdict reason: Δρ 90% CI above 0 and Δρ∥ > 0. Placebo boundaries: 15. Within-transition reliability of χ^mem (upper bound): 0.86.
Data: `data/processed/H97-quench-restoring-force/G39/results.json`; all configurations in `NE34/transitions_all_configs.parquet`.

## Scorecard (period-specific axes)
- C: Δρ beats the placebo-day null.
- D: the intercept a is an unfitted statistic of the HH-literal law (0 under the law).

## Notes
- Holdout masked (`holdout_mask`); #23 excluded throughout.
