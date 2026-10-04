# H111 × G13: goal period #13

**Verdict:** supported
**Role:** replication (exploratory)
**Period:** goal #13 · regime I · mean present N 6.0 · units 13 · 10 non-holdout days.

## Why this period
Eligible for the replication layer: H67 measured a read-out loop gain g_lag for every unit of this period, so the sum rule gives a parameter-free prediction here.

## Prediction
*Written 2026-10-04 21:41 UTC, before running on this period (after Amendment A1). No H111 statistic seen.*
The card's per-period rule on the random-effects pooled r_F = Φ_obs(10)/Φ_pred(g_lag): supported if r_F ∈ [0.8, 1.2]; failed if r_F ≥ 2 or ≤ 0.5; mixed otherwise; descriptive with fewer than 40 usable windows or a Φ CI wider than 1.0. g_lag ≈ 0 in regime I, so the sum rule predicts Φ ≈ 1; the card expects an excess (P4: Φ(10) > 1.2, a field).

| Unit | H67 g_lag [95%] | ≈ 1/(1 − g_lag)² (room-adjusted value computed in the run) |
| --- | --- | --- |
| 13 | -0.002 [-0.033, 0.032] | 1.00 |

## Result
*Run 2026-10-04 ~21:45 UTC (non-holdout units; per-call clock, Amendment A1).* Period pool (random effects over units): **Φ(10) = 1.19 [0.90, 1.48]**, Φ_pred = 1.00, **r_F = 1.20 [0.93, 1.54]**; 111 usable 10-min windows. Verdict by the card's rule: **supported**.

| Unit | windows (10 min) | Φ(10) [95%] per-call | Φ(10) wall | Φ_pred(g_lag) | r_F [95%] | Φ(5) → Φ(30) | Φ untrimmed |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 13 | 111 | 1.19 [0.91, 1.49] | 1.22 | 1.00 | 1.20 [0.90, 1.49] | 1.08 → 2.04 | 1.20 |

Data: `data/processed/H111-talk-fano-sum-rule/results/units.parquet`, `units_wall.parquet`, `periods.parquet`.

## Scorecard (period-specific axes)
C (Φ vs the block-shift null), D (the sum rule is unfitted).

## Notes
