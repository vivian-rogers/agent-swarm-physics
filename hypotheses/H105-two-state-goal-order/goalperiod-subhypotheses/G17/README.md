# H105 × G17: personal websites

**Verdict:** descriptive
**Role:** replication
**Period:** regime I · mode I · 7 agents with ≥ 6 eligible windows in F and A · F = #16 (2025-10-06 … 2025-10-10), A = unit 17 days 2+ (2025-10-14 … 2025-10-17).

## Why this period
A free → assigned pair named in HH130 (primary).

## Prediction
*Templated from the card (written 2026-10-04 ~20:27 UTC), labelled as such.* P1: the tilt-predicted variance matches the observed (90% block-bootstrap CI of ρ_V contains 0 and |ρ_V| < ln 1.5). P2 (pairs): logit-shift slope s ≈ 1. **Amendment 1 (~20:51 UTC, before real data):** P1 and P3 are not identifiable at village sampling, so this folder is descriptive; the rule's outcome is reported.

## Result
| Statistic | bge-small | gte-modernbert |
| --- | --- | --- |
| occupancy p_F (free / previous) | 0.025 | 0.029 |
| occupancy p_A (assigned) | 0.272 | 0.327 |
| loop gain g₂ in F | -0.04 | 0.06 |
| loop gain g₂ in A | 0.22 | 0.33 |
| observed growth ln(V_A/V_F) | 2.41 | 2.50 |
| tilt-predicted growth | 1.88 | 2.52 |
| ρ_V = ln(V_A obs / pred) | 0.53 | -0.02 |
| ρ_V 90% CI | [0.20, 0.92] | [-0.80, 0.24] |
| P1 rule outcome | failed | supported |
| logit slope s (P2) | 0.38 | 0.29 |
| s 90% CI | [-0.27, 5.45] | [-0.70, 1.55] |

Calibrated (matched parametric bootstrap, 200 runs each): real ρ_V at the 0.57 quantile of the tilt (H) and 0.39 of R5; slope s at 0.46 of H and 0.64 of R2 → calibrated P2: **inconclusive**. Matched latent parameters: {'P0': 0.01, 'J': 4.5, 'LAM': 2.0, 'fit_loss': 0.011897551545903714, 'pA_gap': 0.03191137566137564}.

Day trajectory in A (p_d, V_d obs / tilt-pred): 10-14 0.32, 0.022/0.021; 10-15 0.23, 0.033/0.018; 10-16 0.13, 0.021/0.013; 10-17 0.41, 0.059/0.023.
Transverse control (50 directions ⊥ ĝ): median p⊥ 0.024 (F) → 0.022 (A); median ρ_V⊥ -0.03.

Data: `data/processed/H105-two-state-goal-order/NE34/pairs_all_configs.parquet`, `G17/results.json`.

## Scorecard (period-specific axes)
- D: the variance prediction is unfitted but not identifiable here (Amendment 1).

## Notes
- Holdout masked; #23 excluded.
