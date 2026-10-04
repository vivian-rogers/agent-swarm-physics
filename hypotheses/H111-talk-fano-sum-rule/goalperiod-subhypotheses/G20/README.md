# H111 × G20: goal period #20

**Verdict:** mixed
**Role:** replication (exploratory)
**Period:** goal #20 · regime I · mean present N 9.0 · units 20a, 20b, 20c, 20d · 10 non-holdout days.

## Why this period
Eligible for the replication layer: H67 measured a read-out loop gain g_lag for every unit of this period, so the sum rule gives a parameter-free prediction here.

## Prediction
*Written 2026-10-04 21:41 UTC, before running on this period (after Amendment A1). No H111 statistic seen.*
The card's per-period rule on the random-effects pooled r_F = Φ_obs(10)/Φ_pred(g_lag): supported if r_F ∈ [0.8, 1.2]; failed if r_F ≥ 2 or ≤ 0.5; mixed otherwise; descriptive with fewer than 40 usable windows or a Φ CI wider than 1.0. g_lag ≈ 0 in regime I, so the sum rule predicts Φ ≈ 1; the card expects an excess (P4: Φ(10) > 1.2, a field).

| Unit | H67 g_lag [95%] | ≈ 1/(1 − g_lag)² (room-adjusted value computed in the run) |
| --- | --- | --- |
| 20a | -0.029 [-0.091, 0.019] | 0.94 |
| 20b | -0.033 [-0.078, 0.006] | 0.94 |
| 20c | -0.013 [-0.053, 0.037] | 0.97 |
| 20d | 0.029 [-0.064, 0.109] | 1.06 |

## Result
*Run 2026-10-04 ~21:45 UTC (non-holdout units; per-call clock, Amendment A1).* Period pool (random effects over units): **Φ(10) = 1.56 [1.11, 2.01]**, Φ_pred = 0.99, **r_F = 1.62 [1.21, 2.16]**; 177 usable 10-min windows. Verdict by the card's rule: **mixed**.

| Unit | windows (10 min) | Φ(10) [95%] per-call | Φ(10) wall | Φ_pred(g_lag) | r_F [95%] | Φ(5) → Φ(30) | Φ untrimmed |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 20a | 38 | 1.57 [1.03, 1.89] | 1.16 | 0.94 | 1.67 [1.09, 2.13] | 1.50 → 1.59 | 1.90 |
| 20b | 19 | 1.55 [0.77, 2.26] | 1.90 | 0.94 | 1.66 [0.82, 2.41] | 0.88 → 0.55 | 1.24 |
| 20c | 64 | 1.16 [0.84, 1.46] | 0.98 | 0.97 | 1.19 [0.85, 1.55] | 1.30 → 1.17 | 0.92 |
| 20d | 56 | 2.43 [1.67, 3.30] | 2.35 | 1.06 | 2.29 [1.51, 3.35] | 1.90 → 2.47 | 2.07 |

Data: `data/processed/H111-talk-fano-sum-rule/results/units.parquet`, `units_wall.parquet`, `periods.parquet`.

## Scorecard (period-specific axes)
C (Φ vs the block-shift null), D (the sum rule is unfitted).

## Notes
