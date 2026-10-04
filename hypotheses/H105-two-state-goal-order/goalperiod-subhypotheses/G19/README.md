# H105 × G19: daily puzzle game

**Verdict:** descriptive
**Role:** replication
**Period:** regime I · mode C · 7 agents with ≥ 6 eligible windows in F and A · F = #18 (2025-10-29 … 2025-10-31), A = unit 19a days 2+ (2025-11-04 … 2025-11-13).

## Why this period
One eligible kickoff transition (P6); F is the previous goal's tail.

## Prediction
*Templated from the card (written 2026-10-04 ~20:27 UTC), labelled as such.* P1: the tilt-predicted variance matches the observed (90% block-bootstrap CI of ρ_V contains 0 and |ρ_V| < ln 1.5). P2 (pairs): logit-shift slope s ≈ 1. **Amendment 1 (~20:51 UTC, before real data):** P1 and P3 are not identifiable at village sampling, so this folder is descriptive; the rule's outcome is reported.

## Result
| Statistic | bge-small | gte-modernbert |
| --- | --- | --- |
| occupancy p_F (free / previous) | 0.000 | – |
| occupancy p_A (assigned) | 0.045 | – |
| loop gain g₂ in F | – | – |
| loop gain g₂ in A | 0.28 | – |
| observed growth ln(V_A/V_F) | – | – |
| tilt-predicted growth | – | – |
| ρ_V = ln(V_A obs / pred) | 0.27 | – |
| ρ_V 90% CI | [0.16, 0.40] | – |
| P1 rule outcome | inconclusive | – |

Data: `data/processed/H105-two-state-goal-order/NE34/kickoffs.parquet`.

## Scorecard (period-specific axes)
- D: the variance prediction is unfitted but not identifiable here (Amendment 1).

## Notes
- Holdout masked; #23 excluded.
