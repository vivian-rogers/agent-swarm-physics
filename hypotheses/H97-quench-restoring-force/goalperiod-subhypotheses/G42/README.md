# H97 × G42: YouTube channels (kickoff 2026-05-18)

**Verdict:** supported
**Role:** replication
**Period:** regime III · mode I · 15 agents with ≥ 4 statements on #41's last day and on day 1 · 2 room(s). Transition #41 → #42; the kickoff boundary is the object (exception (c)).

## Why this period
One eligible kickoff transition (both neighbours non-holdout, same regime). Common estimator, templated rule.

## Prediction
*Templated from the card (written 2026-10-04 ~20:25 UTC, amended ~20:48 UTC before any real-data statistic), labelled as such.*
Extra forgetting Δρ = ρ0 − ρ_kick > 0 (the kickoff erases more of each agent's relative position than an ordinary day), with Δρ∥ > 0. Rule: supported if Δρ's 90% CI (jackknife SE) is above 0 and Δρ∥ > 0; failed if Δρ ≤ 0; mixed otherwise.

## Result
| Statistic | bge-small | gte-modernbert | agent-centered (bge) |
| --- | --- | --- | --- |
| kickoff memory ρ_kick | +0.55 ± 0.09 | +0.54 ± 0.05 | +0.53 ± 0.07 |
| placebo memory ρ0 (median) | +0.81 | +0.83 | +0.81 |
| extra forgetting Δρ | +0.27 ± 0.09 | +0.29 ± 0.06 | +0.28 ± 0.07 |
| Δρ along k̂ (∥) | +0.34 | +1.01 | +0.42 |
| Δρ transverse (⊥) | +0.26 | +0.26 | +0.27 |
| isotropy β∥ − β⊥ | +0.28 ± 0.47 | -0.87 ± 1.06 | +0.28 ± 0.20 |
| overshoot intercept a (plateau target) | +0.27 ± 0.11 | +0.01 ± 0.31 | +0.27 ± 0.05 |

Verdict reason: Δρ 90% CI above 0 and Δρ∥ > 0. Placebo boundaries: 6. Within-transition reliability of χ^mem (upper bound): 0.95.
Data: `data/processed/H97-quench-restoring-force/G42/results.json`; all configurations in `NE34/transitions_all_configs.parquet`.

## Scorecard (period-specific axes)
- C: Δρ beats the placebo-day null.
- D: the intercept a is an unfitted statistic of the HH-literal law (0 under the law).

## Notes
- Holdout masked (`holdout_mask`); #23 excluded throughout.
