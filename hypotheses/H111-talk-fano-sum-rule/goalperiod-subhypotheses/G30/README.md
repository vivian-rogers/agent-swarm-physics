# H111 × G30: goal period #30

**Verdict:** mixed
**Role:** replication (exploratory)
**Period:** goal #30 · regime I · mean present N 11.0 · units 30a, 30b · 5 non-holdout days.

## Why this period
Eligible for the replication layer: H67 measured a read-out loop gain g_lag for every unit of this period, so the sum rule gives a parameter-free prediction here.

## Prediction
*Written 2026-10-04 21:41 UTC, before running on this period (after Amendment A1). No H111 statistic seen.*
The card's per-period rule on the random-effects pooled r_F = Φ_obs(10)/Φ_pred(g_lag): supported if r_F ∈ [0.8, 1.2]; failed if r_F ≥ 2 or ≤ 0.5; mixed otherwise; descriptive with fewer than 40 usable windows or a Φ CI wider than 1.0. g_lag ≈ 0 in regime I, so the sum rule predicts Φ ≈ 1; the card expects an excess (P4: Φ(10) > 1.2, a field).

| Unit | H67 g_lag [95%] | ≈ 1/(1 − g_lag)² (room-adjusted value computed in the run) |
| --- | --- | --- |
| 30a | 0.021 [-0.091, 0.116] | 1.04 |
| 30b | -0.009 [-0.052, 0.034] | 0.98 |

## Result
*Run 2026-10-04 ~21:45 UTC (non-holdout units; per-call clock, Amendment A1).* Period pool (random effects over units): **Φ(10) = 1.86 [1.53, 2.19]**, Φ_pred = 0.99, **r_F = 1.84 [1.48, 2.27]**; 93 usable 10-min windows. Verdict by the card's rule: **mixed**.

| Unit | windows (10 min) | Φ(10) [95%] per-call | Φ(10) wall | Φ_pred(g_lag) | r_F [95%] | Φ(5) → Φ(30) | Φ untrimmed |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 30a | 14 | 1.93 [1.39, 2.20] | 1.97 | 1.04 | 1.86 [1.27, 2.32] | 1.74 → 2.98 | 2.31 |
| 30b | 79 | 1.79 [1.33, 2.26] | 1.66 | 0.98 | 1.82 [1.35, 2.34] | 1.58 → 1.70 | 2.26 |

Data: `data/processed/H111-talk-fano-sum-rule/results/units.parquet`, `units_wall.parquet`, `periods.parquet`.

## Scorecard (period-specific axes)
C (Φ vs the block-shift null), D (the sum rule is unfitted).

## Notes
