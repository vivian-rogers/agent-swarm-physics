# H111 × G10: goal period #10

**Verdict:** mixed
**Role:** replication (exploratory)
**Period:** goal #10 · regime I · mean present N 7.0 · units 10a, 10b · 5 non-holdout days.

## Why this period
Eligible for the replication layer: H67 measured a read-out loop gain g_lag for every unit of this period, so the sum rule gives a parameter-free prediction here.

## Prediction
*Written 2026-10-04 21:41 UTC, before running on this period (after Amendment A1). No H111 statistic seen.*
The card's per-period rule on the random-effects pooled r_F = Φ_obs(10)/Φ_pred(g_lag): supported if r_F ∈ [0.8, 1.2]; failed if r_F ≥ 2 or ≤ 0.5; mixed otherwise; descriptive with fewer than 40 usable windows or a Φ CI wider than 1.0. g_lag ≈ 0 in regime I, so the sum rule predicts Φ ≈ 1; the card expects an excess (P4: Φ(10) > 1.2, a field).

| Unit | H67 g_lag [95%] | ≈ 1/(1 − g_lag)² (room-adjusted value computed in the run) |
| --- | --- | --- |
| 10a | 0.015 [-0.107, 0.186] | 1.03 |
| 10b | -0.002 [-0.053, 0.067] | 1.00 |

## Result
*Run 2026-10-04 ~21:45 UTC (non-holdout units; per-call clock, Amendment A1).* Period pool (random effects over units): **Φ(10) = 0.70 [0.47, 0.92]**, Φ_pred = 1.00, **r_F = 0.76 [0.52, 1.12]**; 41 usable 10-min windows. Verdict by the card's rule: **mixed**.

| Unit | windows (10 min) | Φ(10) [95%] per-call | Φ(10) wall | Φ_pred(g_lag) | r_F [95%] | Φ(5) → Φ(30) | Φ untrimmed |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 10a | 8 | 1.05 [0.93, 1.93] | 1.85 | 1.03 | 1.02 [0.77, 2.20] | 1.76 → – | 1.15 |
| 10b | 33 | 0.67 [0.54, 0.99] | 0.66 | 1.00 | 0.67 [0.52, 1.04] | 0.93 → 1.32 | 1.28 |

Data: `data/processed/H111-talk-fano-sum-rule/results/units.parquet`, `units_wall.parquet`, `periods.parquet`.

## Scorecard (period-specific axes)
C (Φ vs the block-shift null), D (the sum rule is unfitted).

## Notes
