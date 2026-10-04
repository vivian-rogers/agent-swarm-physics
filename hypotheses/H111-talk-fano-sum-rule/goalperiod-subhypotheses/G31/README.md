# H111 × G31: goal period #31

**Verdict:** mixed
**Role:** replication (exploratory)
**Period:** goal #31 · regime I · mean present N 11.2 · units 31a, 31b, 31c, 31d · 5 non-holdout days.

## Why this period
Eligible for the replication layer: H67 measured a read-out loop gain g_lag for every unit of this period, so the sum rule gives a parameter-free prediction here.

## Prediction
*Written 2026-10-04 21:41 UTC, before running on this period (after Amendment A1). No H111 statistic seen.*
The card's per-period rule on the random-effects pooled r_F = Φ_obs(10)/Φ_pred(g_lag): supported if r_F ∈ [0.8, 1.2]; failed if r_F ≥ 2 or ≤ 0.5; mixed otherwise; descriptive with fewer than 40 usable windows or a Φ CI wider than 1.0. g_lag ≈ 0 in regime I, so the sum rule predicts Φ ≈ 1; the card expects an excess (P4: Φ(10) > 1.2, a field).

| Unit | H67 g_lag [95%] | ≈ 1/(1 − g_lag)² (room-adjusted value computed in the run) |
| --- | --- | --- |
| 31a | 0.024 [-0.022, 0.064] | 1.05 |
| 31b | -0.076 [-0.223, 0.041] | 0.86 |
| 31c | -0.042 [-0.091, 0.054] | 0.92 |
| 31d | -0.084 [-0.163, -0.025] | 0.85 |

## Result
*Run 2026-10-04 ~21:45 UTC (non-holdout units; per-call clock, Amendment A1).* Period pool (random effects over units): **Φ(10) = 1.44 [1.26, 1.61]**, Φ_pred = 0.94, **r_F = 1.65 [1.41, 1.93]**; 99 usable 10-min windows. Verdict by the card's rule: **mixed**.

| Unit | windows (10 min) | Φ(10) [95%] per-call | Φ(10) wall | Φ_pred(g_lag) | r_F [95%] | Φ(5) → Φ(30) | Φ untrimmed |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 31a | 38 | 1.80 [1.02, 2.46] | 1.79 | 1.05 | 1.71 [0.96, 2.49] | 1.85 → 3.23 | 2.07 |
| 31b | 16 | 1.36 [0.79, 1.60] | 1.55 | 0.86 | 1.58 [0.89, 2.16] | 1.28 → 2.32 | 2.32 |
| 31c | 22 | 1.31 [0.87, 1.69] | 0.84 | 0.92 | 1.43 [0.95, 1.89] | 1.06 → 1.62 | 1.12 |
| 31d | 23 | 1.47 [1.23, 1.67] | 0.94 | 0.85 | 1.73 [1.40, 2.11] | 1.14 → 1.99 | 1.28 |

Data: `data/processed/H111-talk-fano-sum-rule/results/units.parquet`, `units_wall.parquet`, `periods.parquet`.

## Scorecard (period-specific axes)
C (Φ vs the block-shift null), D (the sum rule is unfitted).

## Notes
