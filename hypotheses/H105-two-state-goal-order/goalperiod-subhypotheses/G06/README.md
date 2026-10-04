# H105 × G06: merch store competition

**Verdict:** descriptive
**Role:** replication
**Period:** regime I · mode K · 4 agents with ≥ 6 eligible windows in F and A · F = #5 (2025-06-19 … 2025-06-25), A = unit 6a days 2+ (2025-06-27 … 2025-07-02).

## Why this period
A secondary free → assigned pair (N = 4).

## Prediction
*Templated from the card (written 2026-10-04 ~20:27 UTC), labelled as such.* P1: the tilt-predicted variance matches the observed (90% block-bootstrap CI of ρ_V contains 0 and |ρ_V| < ln 1.5). P2 (pairs): logit-shift slope s ≈ 1. **Amendment 1 (~20:51 UTC, before real data):** P1 and P3 are not identifiable at village sampling, so this folder is descriptive; the rule's outcome is reported.

## Result
| Statistic | bge-small | gte-modernbert |
| --- | --- | --- |
| occupancy p_F (free / previous) | 0.025 | 0.025 |
| occupancy p_A (assigned) | 0.511 | 0.620 |
| loop gain g₂ in F | -0.08 | -0.08 |
| loop gain g₂ in A | 0.52 | 0.48 |
| observed growth ln(V_A/V_F) | 2.84 | 2.74 |
| tilt-predicted growth | 1.78 | 1.75 |
| ρ_V = ln(V_A obs / pred) | 1.06 | 0.99 |
| ρ_V 90% CI | [0.35, 1.36] | [0.27, 1.44] |
| P1 rule outcome | failed | failed |
| logit slope s (P2) | -0.43 | 0.41 |
| s 90% CI | [-26.95, 1.75] | [-3.48, 11.19] |

Day trajectory in A (p_d, V_d obs / tilt-pred): 06-27 0.81, 0.106/0.025; 06-29 0.39, 0.173/0.034; 06-30 0.44, 0.048/0.033; 07-01 0.50, 0.063/0.033; 07-02 0.50, 0.031/0.033.
Transverse control (50 directions ⊥ ĝ): median p⊥ 0.000 (F) → 0.000 (A); median ρ_V⊥ -0.04.

Data: `data/processed/H105-two-state-goal-order/NE34/pairs_all_configs.parquet`, `G06/results.json`.

## Scorecard (period-specific axes)
- D: the variance prediction is unfitted but not identifiable here (Amendment 1).

## Notes
- Holdout masked; #23 excluded.
