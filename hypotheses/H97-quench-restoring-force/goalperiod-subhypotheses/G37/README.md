# H97 × G37: free 3 days (kickoff 2026-03-30)

**Verdict:** descriptive
**Role:** replication
**Period:** regime III · mode F · 12 agents with ≥ 4 statements on #36's last day and on day 1 · 2 room(s). Transition #36 → #37; the kickoff boundary is the object (exception (c)).

## Why this period
One eligible kickoff transition (both neighbours non-holdout, same regime). Common estimator, templated rule.

## Prediction
*Templated from the card (written 2026-10-04 ~20:25 UTC, amended ~20:48 UTC before any real-data statistic), labelled as such.*
Extra forgetting Δρ = ρ0 − ρ_kick > 0 (the kickoff erases more of each agent's relative position than an ordinary day), with Δρ∥ > 0. Rule: supported if Δρ's 90% CI (jackknife SE) is above 0 and Δρ∥ > 0; failed if Δρ ≤ 0; mixed otherwise.

## Result
| Statistic | bge-small | gte-modernbert | agent-centered (bge) |
| --- | --- | --- | --- |
| kickoff memory ρ_kick | +0.56 ± 0.14 | – | – |
| placebo memory ρ0 (median) | +0.76 | – | – |
| extra forgetting Δρ | +0.20 ± 0.15 | – | – |
| Δρ along k̂ (∥) | -0.07 | – | – |
| Δρ transverse (⊥) | +0.22 | – | – |
| isotropy β∥ − β⊥ | +0.73 ± 1.01 | – | – |
| overshoot intercept a (plateau target) | +0.15 ± 0.03 | – | – |

Verdict reason: cross-regime transition (#36 regime II → #37 regime III): variant only. Placebo boundaries: 3. Within-transition reliability of χ^mem (upper bound): 0.84.
Data: `data/processed/H97-quench-restoring-force/G37/results.json`; all configurations in `NE34/transitions_all_configs.parquet`.

## Scorecard (period-specific axes)
- C: not tested.
- D: the intercept a is an unfitted statistic of the HH-literal law (0 under the law).

## Notes
- Holdout masked (`holdout_mask`); #23 excluded throughout.
