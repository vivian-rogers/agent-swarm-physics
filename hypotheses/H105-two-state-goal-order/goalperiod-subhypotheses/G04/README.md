# H105 × G04: story + 100-person in-person event

**Verdict:** descriptive
**Role:** replication
**Period:** regime I · mode C · 4 agents with ≥ 6 eligible windows in F and A · F = #3 (2025-05-12 … 2025-05-14), A = unit 4a days 2+ (2025-05-16 … 2025-05-21).

## Why this period
A secondary free → assigned pair (N = 4).

## Prediction
*Templated from the card (written 2026-10-04 ~20:27 UTC), labelled as such.* P1: the tilt-predicted variance matches the observed (90% block-bootstrap CI of ρ_V contains 0 and |ρ_V| < ln 1.5). P2 (pairs): logit-shift slope s ≈ 1. **Amendment 1 (~20:51 UTC, before real data):** P1 and P3 are not identifiable at village sampling, so this folder is descriptive; the rule's outcome is reported.

## Result
| Statistic | bge-small | gte-modernbert |
| --- | --- | --- |
| occupancy p_F (free / previous) | 0.021 | 0.090 |
| occupancy p_A (assigned) | 0.135 | 0.130 |
| loop gain g₂ in F | -0.14 | 0.54 |
| loop gain g₂ in A | 0.32 | 0.07 |
| observed growth ln(V_A/V_F) | 2.11 | -0.71 |
| tilt-predicted growth | 1.22 | 0.83 |
| ρ_V = ln(V_A obs / pred) | 0.89 | -1.54 |
| ρ_V 90% CI | [-0.10, 1.15] | [-1.83, -0.16] |
| P1 rule outcome | inconclusive | failed |
| logit slope s (P2) | 1.74 | 2.02 |
| s 90% CI | [1.05, 9.43] | [-3.18, 785.22] |

Day trajectory in A (p_d, V_d obs / tilt-pred): 05-16 0.23, 0.080/0.021; 05-19 0.25, 0.047/0.020; 05-20 0.06, 0.016/0.010; 05-21 0.00, 0.016/–.
Transverse control (50 directions ⊥ ĝ): median p⊥ 0.000 (F) → 0.016 (A); median ρ_V⊥ -0.07.

Data: `data/processed/H105-two-state-goal-order/NE34/pairs_all_configs.parquet`, `G04/results.json`.

## Scorecard (period-specific axes)
- D: the variance prediction is unfitted but not identifiable here (Amendment 1).

## Notes
- Holdout masked; #23 excluded.
