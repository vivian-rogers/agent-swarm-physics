# H105 × G38: charity fundraiser (year 2)

**Verdict:** descriptive
**Role:** replication
**Period:** regime III · mode C · 12 agents with ≥ 6 eligible windows in F and A · F = #37 (2026-03-30 … 2026-04-01), A = unit 38a days 2+ (2026-04-03 … 2026-04-13).

## Why this period
A free → assigned pair named in HH130 (primary).

## Prediction
*Templated from the card (written 2026-10-04 ~20:27 UTC), labelled as such.* P1: the tilt-predicted variance matches the observed (90% block-bootstrap CI of ρ_V contains 0 and |ρ_V| < ln 1.5). P2 (pairs): logit-shift slope s ≈ 1. **Amendment 1 (~20:51 UTC, before real data):** P1 and P3 are not identifiable at village sampling, so this folder is descriptive; the rule's outcome is reported.

## Result
| Statistic | bge-small | gte-modernbert |
| --- | --- | --- |
| occupancy p_F (free / previous) | 0.045 | 0.053 |
| occupancy p_A (assigned) | 0.231 | 0.187 |
| loop gain g₂ in F | 0.22 | 0.35 |
| loop gain g₂ in A | 0.24 | -0.06 |
| observed growth ln(V_A/V_F) | 0.82 | 0.15 |
| tilt-predicted growth | 3.27 | 3.19 |
| ρ_V = ln(V_A obs / pred) | -2.45 | -3.04 |
| ρ_V 90% CI | [-2.88, 1.28] | [-3.00, 0.88] |
| P1 rule outcome | inconclusive | inconclusive |
| logit slope s (P2) | 2.53 | 0.18 |
| s 90% CI | [0.57, 9.42] | [-3.76, 2.28] |

Calibrated (matched parametric bootstrap, 200 runs each): real ρ_V at the 0.00 quantile of the tilt (H) and 0.00 of R5; slope s at 0.90 of H and 0.94 of R2 → calibrated P2: **inconclusive**. Matched latent parameters: {'P0': 0.01, 'J': 4.5, 'LAM': 1.75, 'fit_loss': 2.257050397988392, 'pA_gap': 0.09447311121418264}.

Day trajectory in A (p_d, V_d obs / tilt-pred): 04-03 0.20, 0.016/0.075; 04-06 0.10, 0.021/0.015; 04-07 0.24, 0.009/0.146; 04-08 0.28, 0.007/0.203; 04-09 0.26, 0.007/0.187; 04-10 0.31, 0.009/0.213; 04-13 0.23, 0.013/0.139.
Transverse control (50 directions ⊥ ĝ): median p⊥ 0.027 (F) → 0.022 (A); median ρ_V⊥ 0.04.

Data: `data/processed/H105-two-state-goal-order/NE34/pairs_all_configs.parquet`, `G38/results.json`.

## Scorecard (period-specific axes)
- D: the variance prediction is unfitted but not identifiable here (Amendment 1).

## Notes
- Holdout masked; #23 excluded.
