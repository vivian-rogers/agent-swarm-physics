# H111 × G36: goal period #36

**Verdict:** supported
**Role:** replication (+ NE14 native, separate folder) (exploratory)
**Period:** goal #36 · regime II · mean present N 12.0 · units 36a, 36b, 36c · 5 non-holdout days.

## Why this period
Eligible for the replication layer: H67 measured a read-out loop gain g_lag for every unit of this period, so the sum rule gives a parameter-free prediction here.

## Prediction
*Written 2026-10-04 21:41 UTC, before running on this period (after Amendment A1). No H111 statistic seen.*
The card's per-period rule on the random-effects pooled r_F = Φ_obs(10)/Φ_pred(g_lag): supported if r_F ∈ [0.8, 1.2]; failed if r_F ≥ 2 or ≤ 0.5; mixed otherwise; descriptive with fewer than 40 usable windows or a Φ CI wider than 1.0. g_lag ≈ 0 in regime II (H67), so the sum rule predicts Φ ≈ 1.

| Unit | H67 g_lag [95%] | ≈ 1/(1 − g_lag)² (room-adjusted value computed in the run) |
| --- | --- | --- |
| 36a | -0.060 [-0.146, 0.030] | 0.89 |
| 36b | 0.094 [0.053, 0.141] | 1.22 |
| 36c | 0.151 [0.104, 0.224] | 1.39 |

## Result
*Run 2026-10-04 ~21:45 UTC (non-holdout units; per-call clock, Amendment A1).* Period pool (random effects over units): **Φ(10) = 1.43 [1.10, 1.76]**, Φ_pred = 1.22, **r_F = 1.15 [0.90, 1.47]**; 103 usable 10-min windows. Verdict by the card's rule: **supported**.

| Unit | windows (10 min) | Φ(10) [95%] per-call | Φ(10) wall | Φ_pred(g_lag) | r_F [95%] | Φ(5) → Φ(30) | Φ untrimmed |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 36a | 17 | 1.36 [0.74, 2.30] | 1.09 | 0.89 | 1.53 [0.80, 2.64] | 0.82 → 0.37 | 0.94 |
| 36b | 43 | 1.10 [0.68, 1.97] | 1.33 | 1.21 | 0.91 [0.54, 1.65] | 1.11 → 0.74 | 1.06 |
| 36c | 43 | 1.57 [1.20, 1.99] | 1.45 | 1.36 | 1.15 [0.87, 1.57] | 1.51 → 1.55 | 1.59 |

Data: `data/processed/H111-talk-fano-sum-rule/results/units.parquet`, `units_wall.parquet`, `periods.parquet`.

## Scorecard (period-specific axes)
C (Φ vs the block-shift null), D (the sum rule is unfitted).

## Notes
