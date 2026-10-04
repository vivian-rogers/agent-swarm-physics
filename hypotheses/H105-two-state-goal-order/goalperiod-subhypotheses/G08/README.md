# H105 × G08: design and take an open-ended benchmark

**Verdict:** descriptive
**Role:** replication
**Period:** regime I · mode C · 4 agents with ≥ 6 eligible windows in F and A · F = #7 (2025-07-16 … 2025-07-17), A = unit 8 days 2+ (2025-07-21 … 2025-08-12).

## Why this period
One eligible kickoff transition (P6); F is the previous goal's tail.

## Prediction
*Templated from the card (written 2026-10-04 ~20:27 UTC), labelled as such.* P1: the tilt-predicted variance matches the observed (90% block-bootstrap CI of ρ_V contains 0 and |ρ_V| < ln 1.5). P2 (pairs): logit-shift slope s ≈ 1. **Amendment 1 (~20:51 UTC, before real data):** P1 and P3 are not identifiable at village sampling, so this folder is descriptive; the rule's outcome is reported.

## Result
| Statistic | bge-small | gte-modernbert |
| --- | --- | --- |
| occupancy p_F (free / previous) | 0.031 | – |
| occupancy p_A (assigned) | 0.236 | – |
| loop gain g₂ in F | 0.00 | – |
| loop gain g₂ in A | 0.00 | – |
| observed growth ln(V_A/V_F) | 1.70 | – |
| tilt-predicted growth | 1.89 | – |
| ρ_V = ln(V_A obs / pred) | -0.19 | – |
| ρ_V 90% CI | [-0.39, -0.09] | – |
| P1 rule outcome | inconclusive | – |

Data: `data/processed/H105-two-state-goal-order/NE34/kickoffs.parquet`.

## Scorecard (period-specific axes)
- D: the variance prediction is unfitted but not identifiable here (Amendment 1).

## Notes
- Holdout masked; #23 excluded.
