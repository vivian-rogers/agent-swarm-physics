# H105 × G11: free week

**Verdict:** descriptive
**Role:** replication
**Period:** regime I · mode F · 7 agents with ≥ 6 eligible windows in F and A · F = #10 (2025-08-20 … 2025-08-22), A = unit 11 days 2+ (2025-08-26 … 2025-08-29).

## Why this period
One eligible kickoff transition (P6); F is the previous goal's tail.

## Prediction
*Templated from the card (written 2026-10-04 ~20:27 UTC), labelled as such.* P1: the tilt-predicted variance matches the observed (90% block-bootstrap CI of ρ_V contains 0 and |ρ_V| < ln 1.5). P2 (pairs): logit-shift slope s ≈ 1. **Amendment 1 (~20:51 UTC, before real data):** P1 and P3 are not identifiable at village sampling, so this folder is descriptive; the rule's outcome is reported.

## Result
| Statistic | bge-small | gte-modernbert |
| --- | --- | --- |
| occupancy p_F (free / previous) | 0.271 | – |
| occupancy p_A (assigned) | 0.040 | – |
| loop gain g₂ in F | 0.03 | – |
| loop gain g₂ in A | -0.02 | – |
| observed growth ln(V_A/V_F) | -1.59 | – |
| tilt-predicted growth | -1.32 | – |
| ρ_V = ln(V_A obs / pred) | -0.27 | – |
| ρ_V 90% CI | [-0.64, -0.31] | – |
| P1 rule outcome | inconclusive | – |

Data: `data/processed/H105-two-state-goal-order/NE34/kickoffs.parquet`.

## Scorecard (period-specific axes)
- D: the variance prediction is unfitted but not identifiable here (Amendment 1).

## Notes
- Holdout masked; #23 excluded.
