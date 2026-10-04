# H111 × G26: goal period #26

**Verdict:** descriptive
**Role:** replication (exploratory)
**Period:** goal #26 · regime I · mean present N 10.0 · units 26 · 5 non-holdout days.

## Why this period
Eligible for the replication layer: H67 measured a read-out loop gain g_lag for every unit of this period, so the sum rule gives a parameter-free prediction here.

## Prediction
*Written 2026-10-04 21:41 UTC, before running on this period (after Amendment A1). No H111 statistic seen.*
The card's per-period rule on the random-effects pooled r_F = Φ_obs(10)/Φ_pred(g_lag): supported if r_F ∈ [0.8, 1.2]; failed if r_F ≥ 2 or ≤ 0.5; mixed otherwise; descriptive with fewer than 40 usable windows or a Φ CI wider than 1.0. g_lag ≈ 0 in regime I, so the sum rule predicts Φ ≈ 1; the card expects an excess (P4: Φ(10) > 1.2, a field).

| Unit | H67 g_lag [95%] | ≈ 1/(1 − g_lag)² (room-adjusted value computed in the run) |
| --- | --- | --- |
| 26 | 0.012 [-0.053, 0.083] | 1.02 |

## Result
*Run 2026-10-04 ~21:45 UTC (non-holdout units; per-call clock, Amendment A1).* Period pool (random effects over units): **Φ(10) = 2.07 [1.25, 2.89]**, Φ_pred = 1.02, **r_F = 2.02 [1.30, 3.12]**; 63 usable 10-min windows. Verdict by the card's rule: **descriptive**.

| Unit | windows (10 min) | Φ(10) [95%] per-call | Φ(10) wall | Φ_pred(g_lag) | r_F [95%] | Φ(5) → Φ(30) | Φ untrimmed |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 26 | 63 | 2.07 [1.23, 2.90] | 2.36 | 1.02 | 2.02 [1.18, 2.87] | 1.71 → 2.35 | 1.66 |

Data: `data/processed/H111-talk-fano-sum-rule/results/units.parquet`, `units_wall.parquet`, `periods.parquet`.

## Scorecard (period-specific axes)
C (Φ vs the block-shift null), D (the sum rule is unfitted).

## Notes
