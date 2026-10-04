# H105 × G25: digital museum of 2025

**Verdict:** descriptive
**Role:** replication
**Period:** regime I · mode C · 10 agents with ≥ 6 eligible windows in F and A · F = #24 (2025-12-22 … 2025-12-26), A = unit 25 days 2+ (2025-12-30 … 2026-01-02).

## Why this period
One eligible kickoff transition (P6); F is the previous goal's tail.

## Prediction
*Templated from the card (written 2026-10-04 ~20:27 UTC), labelled as such.* P1: the tilt-predicted variance matches the observed (90% block-bootstrap CI of ρ_V contains 0 and |ρ_V| < ln 1.5). P2 (pairs): logit-shift slope s ≈ 1. **Amendment 1 (~20:51 UTC, before real data):** P1 and P3 are not identifiable at village sampling, so this folder is descriptive; the rule's outcome is reported.

## Result
| Statistic | bge-small | gte-modernbert |
| --- | --- | --- |
| occupancy p_F (free / previous) | 0.012 | – |
| occupancy p_A (assigned) | 0.434 | – |
| loop gain g₂ in F | 0.07 | – |
| loop gain g₂ in A | 0.71 | – |
| observed growth ln(V_A/V_F) | 4.24 | – |
| tilt-predicted growth | 5.32 | – |
| ρ_V = ln(V_A obs / pred) | -1.08 | – |
| ρ_V 90% CI | [-1.12, 3.30] | – |
| P1 rule outcome | inconclusive | – |

Data: `data/processed/H105-two-state-goal-order/NE34/kickoffs.parquet`.

## Scorecard (period-specific axes)
- D: the variance prediction is unfitted but not identifiable here (Amendment 1).

## Notes
- Holdout masked; #23 excluded.
