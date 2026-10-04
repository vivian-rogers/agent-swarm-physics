# H111 × G06: goal period #6

**Verdict:** supported
**Role:** replication (exploratory)
**Period:** goal #6 · regime I · mean present N 4.0 · units 6a, 6b · 15 non-holdout days.

## Why this period
Eligible for the replication layer: H67 measured a read-out loop gain g_lag for every unit of this period, so the sum rule gives a parameter-free prediction here.

## Prediction
*Written 2026-10-04 21:41 UTC, before running on this period (after Amendment A1). No H111 statistic seen.*
The card's per-period rule on the random-effects pooled r_F = Φ_obs(10)/Φ_pred(g_lag): supported if r_F ∈ [0.8, 1.2]; failed if r_F ≥ 2 or ≤ 0.5; mixed otherwise; descriptive with fewer than 40 usable windows or a Φ CI wider than 1.0. g_lag ≈ 0 in regime I, so the sum rule predicts Φ ≈ 1; the card expects an excess (P4: Φ(10) > 1.2, a field).

| Unit | H67 g_lag [95%] | ≈ 1/(1 − g_lag)² (room-adjusted value computed in the run) |
| --- | --- | --- |
| 6a | 0.002 [-0.075, 0.106] | 1.00 |
| 6b | -0.009 [-0.040, 0.018] | 0.98 |

## Result
*Run 2026-10-04 ~21:45 UTC (non-holdout units; per-call clock, Amendment A1).* Period pool (random effects over units): **Φ(10) = 1.00 [0.67, 1.32]**, Φ_pred = 0.99, **r_F = 1.03 [0.73, 1.45]**; 173 usable 10-min windows. Verdict by the card's rule: **supported**.

| Unit | windows (10 min) | Φ(10) [95%] per-call | Φ(10) wall | Φ_pred(g_lag) | r_F [95%] | Φ(5) → Φ(30) | Φ untrimmed |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 6a | 99 | 0.82 [0.51, 1.06] | 1.45 | 1.00 | 0.82 [0.48, 1.11] | 1.03 → – | 0.82 |
| 6b | 74 | 1.15 [0.88, 1.32] | 1.05 | 0.98 | 1.17 [0.89, 1.38] | 1.14 → 1.24 | 1.13 |

Data: `data/processed/H111-talk-fano-sum-rule/results/units.parquet`, `units_wall.parquet`, `periods.parquet`.

## Scorecard (period-specific axes)
C (Φ vs the block-shift null), D (the sum rule is unfitted).

## Notes
