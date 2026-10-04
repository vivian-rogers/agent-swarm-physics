# H105 × G40: connect worlds into a 3D universe

**Verdict:** descriptive
**Role:** replication
**Period:** regime III · mode C · 15 agents with ≥ 6 eligible windows in F and A · F = #39 (2026-04-27 … 2026-05-01), A = unit 40 days 2+ (2026-05-05 … 2026-05-08).

## Why this period
One eligible kickoff transition (P6); F is the previous goal's tail.

## Prediction
*Templated from the card (written 2026-10-04 ~20:27 UTC), labelled as such.* P1: the tilt-predicted variance matches the observed (90% block-bootstrap CI of ρ_V contains 0 and |ρ_V| < ln 1.5). P2 (pairs): logit-shift slope s ≈ 1. **Amendment 1 (~20:51 UTC, before real data):** P1 and P3 are not identifiable at village sampling, so this folder is descriptive; the rule's outcome is reported.

## Result
| Statistic | bge-small | gte-modernbert |
| --- | --- | --- |
| occupancy p_F (free / previous) | 0.400 | – |
| occupancy p_A (assigned) | 0.635 | – |
| loop gain g₂ in F | 0.48 | – |
| loop gain g₂ in A | 0.48 | – |
| observed growth ln(V_A/V_F) | -0.00 | – |
| tilt-predicted growth | 0.01 | – |
| ρ_V = ln(V_A obs / pred) | -0.01 | – |
| ρ_V 90% CI | [-0.50, 0.72] | – |
| P1 rule outcome | supported | – |

Data: `data/processed/H105-two-state-goal-order/NE34/kickoffs.parquet`.

## Scorecard (period-specific axes)
- D: the variance prediction is unfitted but not identifiable here (Amendment 1).

## Notes
- Holdout masked; #23 excluded.
