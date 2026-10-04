# H111 × G19: goal period #19

**Verdict:** mixed
**Role:** replication (exploratory)
**Period:** goal #19 · regime I · mean present N 7.5 · units 19a, 19b · 10 non-holdout days.

## Why this period
Eligible for the replication layer: H67 measured a read-out loop gain g_lag for every unit of this period, so the sum rule gives a parameter-free prediction here.

## Prediction
*Written 2026-10-04 21:41 UTC, before running on this period (after Amendment A1). No H111 statistic seen.*
The card's per-period rule on the random-effects pooled r_F = Φ_obs(10)/Φ_pred(g_lag): supported if r_F ∈ [0.8, 1.2]; failed if r_F ≥ 2 or ≤ 0.5; mixed otherwise; descriptive with fewer than 40 usable windows or a Φ CI wider than 1.0. g_lag ≈ 0 in regime I, so the sum rule predicts Φ ≈ 1; the card expects an excess (P4: Φ(10) > 1.2, a field).

| Unit | H67 g_lag [95%] | ≈ 1/(1 − g_lag)² (room-adjusted value computed in the run) |
| --- | --- | --- |
| 19a | 0.003 [-0.029, 0.039] | 1.01 |
| 19b | -0.019 [-0.061, 0.063] | 0.96 |

## Result
*Run 2026-10-04 ~21:45 UTC (non-holdout units; per-call clock, Amendment A1).* Period pool (random effects over units): **Φ(10) = 1.53 [1.29, 1.76]**, Φ_pred = 1.00, **r_F = 1.55 [1.31, 1.84]**; 205 usable 10-min windows. Verdict by the card's rule: **mixed**.

| Unit | windows (10 min) | Φ(10) [95%] per-call | Φ(10) wall | Φ_pred(g_lag) | r_F [95%] | Φ(5) → Φ(30) | Φ untrimmed |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 19a | 186 | 1.55 [1.21, 1.87] | 1.78 | 1.01 | 1.54 [1.19, 1.86] | 1.55 → 1.41 | 1.55 |
| 19b | 19 | 1.51 [1.02, 1.69] | 2.42 | 0.96 | 1.57 [1.11, 1.86] | 1.27 → 2.20 | 1.54 |

Data: `data/processed/H111-talk-fano-sum-rule/results/units.parquet`, `units_wall.parquet`, `periods.parquet`.

## Scorecard (period-specific axes)
C (Φ vs the block-shift null), D (the sum rule is unfitted).

## Notes
