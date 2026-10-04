# H97 × G38: charity fundraiser (year 2) (kickoff 2026-04-02)

**Verdict:** supported
**Role:** replication
**Period:** regime III · mode C · 12 agents with ≥ 4 statements on #37's last day and on day 1 · 2 room(s). Transition #37 → #38; the kickoff boundary is the object (exception (c)).

## Why this period
One eligible kickoff transition (both neighbours non-holdout, same regime). Common estimator, templated rule.

## Prediction
*Templated from the card (written 2026-10-04 ~20:25 UTC, amended ~20:48 UTC before any real-data statistic), labelled as such.*
Extra forgetting Δρ = ρ0 − ρ_kick > 0 (the kickoff erases more of each agent's relative position than an ordinary day), with Δρ∥ > 0. Rule: supported if Δρ's 90% CI (jackknife SE) is above 0 and Δρ∥ > 0; failed if Δρ ≤ 0; mixed otherwise.

## Result
| Statistic | bge-small | gte-modernbert | agent-centered (bge) |
| --- | --- | --- | --- |
| kickoff memory ρ_kick | +0.41 ± 0.09 | +0.36 ± 0.13 | +0.44 ± 0.08 |
| placebo memory ρ0 (median) | +0.84 | +0.86 | +0.85 |
| extra forgetting Δρ | +0.43 ± 0.09 | +0.50 ± 0.13 | +0.41 ± 0.09 |
| Δρ along k̂ (∥) | +0.21 | +1.20 | +0.40 |
| Δρ transverse (⊥) | +0.42 | +0.47 | +0.40 |
| isotropy β∥ − β⊥ | +1.54 ± 0.43 | -0.88 ± 0.34 | +0.83 ± 0.76 |
| overshoot intercept a (plateau target) | +0.06 ± 0.05 | +0.05 ± 0.05 | +0.03 ± 0.05 |

Verdict reason: Δρ 90% CI above 0 and Δρ∥ > 0. Placebo boundaries: 13. Within-transition reliability of χ^mem (upper bound): 0.90.
Data: `data/processed/H97-quench-restoring-force/G38/results.json`; all configurations in `NE34/transitions_all_configs.parquet`.

## Scorecard (period-specific axes)
- C: Δρ beats the placebo-day null.
- D: the intercept a is an unfitted statistic of the HH-literal law (0 under the law).

## Notes
- Holdout masked (`holdout_mask`); #23 excluded throughout.
