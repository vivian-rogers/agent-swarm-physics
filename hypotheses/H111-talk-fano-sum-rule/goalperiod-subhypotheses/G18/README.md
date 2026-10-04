# H111 × G18: goal period #18

**Verdict:** mixed
**Role:** replication (exploratory)
**Period:** goal #18 · regime I · mean present N 7.3 · units 18a, 18b, 18c · 10 non-holdout days.

## Why this period
Eligible for the replication layer: H67 measured a read-out loop gain g_lag for every unit of this period, so the sum rule gives a parameter-free prediction here.

## Prediction
*Written 2026-10-04 21:41 UTC, before running on this period (after Amendment A1). No H111 statistic seen.*
The card's per-period rule on the random-effects pooled r_F = Φ_obs(10)/Φ_pred(g_lag): supported if r_F ∈ [0.8, 1.2]; failed if r_F ≥ 2 or ≤ 0.5; mixed otherwise; descriptive with fewer than 40 usable windows or a Φ CI wider than 1.0. g_lag ≈ 0 in regime I, so the sum rule predicts Φ ≈ 1; the card expects an excess (P4: Φ(10) > 1.2, a field).

| Unit | H67 g_lag [95%] | ≈ 1/(1 − g_lag)² (room-adjusted value computed in the run) |
| --- | --- | --- |
| 18a | 0.004 [-0.110, 0.129] | 1.01 |
| 18b | 0.018 [-0.039, 0.091] | 1.04 |
| 18c | 0.082 [0.020, 0.128] | 1.19 |

## Result
*Run 2026-10-04 ~21:45 UTC (non-holdout units; per-call clock, Amendment A1).* Period pool (random effects over units): **Φ(10) = 1.69 [1.35, 2.03]**, Φ_pred = 1.09, **r_F = 1.66 [1.33, 2.07]**; 179 usable 10-min windows. Verdict by the card's rule: **mixed**.

| Unit | windows (10 min) | Φ(10) [95%] per-call | Φ(10) wall | Φ_pred(g_lag) | r_F [95%] | Φ(5) → Φ(30) | Φ untrimmed |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 18a | 27 | 1.50 [1.10, 1.77] | 1.78 | 1.01 | 1.49 [1.01, 1.96] | 1.55 → 1.17 | 1.61 |
| 18b | 86 | 2.00 [1.53, 2.40] | 2.23 | 1.04 | 1.93 [1.44, 2.43] | 1.75 → 2.29 | 1.90 |
| 18c | 66 | 1.55 [0.88, 2.10] | 2.04 | 1.18 | 1.31 [0.71, 1.83] | 1.46 → 1.88 | 1.51 |

Data: `data/processed/H111-talk-fano-sum-rule/results/units.parquet`, `units_wall.parquet`, `periods.parquet`.

## Scorecard (period-specific axes)
C (Φ vs the block-shift null), D (the sum rule is unfitted).

## Notes
