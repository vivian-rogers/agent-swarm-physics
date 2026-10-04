# H111 × G44: goal period #44

**Verdict:** descriptive
**Role:** replication (exploratory)
**Period:** goal #44 · regime III · mean present N 17.0 · units 44b · 2 non-holdout days.

## Why this period
Eligible for the replication layer: H67 measured a read-out loop gain g_lag for every unit of this period, so the sum rule gives a parameter-free prediction here.

## Prediction
*Written 2026-10-04 21:41 UTC, before running on this period (after Amendment A1). No H111 statistic seen.*
The card's per-period rule on the random-effects pooled r_F = Φ_obs(10)/Φ_pred(g_lag): supported if r_F ∈ [0.8, 1.2]; failed if r_F ≥ 2 or ≤ 0.5; mixed otherwise; descriptive with fewer than 40 usable windows or a Φ CI wider than 1.0. Regime III: the sum rule predicts Φ ≈ 1/(1 − g_lag)² (table). The card gives the HH's ±20% band credence 0.20 and the kill (Φ ≥ 2 Φ_pred) credence 0.35.

| Unit | H67 g_lag [95%] | ≈ 1/(1 − g_lag)² (room-adjusted value computed in the run) |
| --- | --- | --- |
| 44b | 0.234 [0.122, 0.320] | 1.71 |

## Result
*Run 2026-10-04 ~21:45 UTC (non-holdout units; per-call clock, Amendment A1).* Period pool (random effects over units): **Φ(10) = 1.53 [0.17, 2.89]**, Φ_pred = 1.65, **r_F = 0.92 [0.02, 36.92]**; 5 usable 10-min windows. Verdict by the card's rule: **descriptive**.

| Unit | windows (10 min) | Φ(10) [95%] per-call | Φ(10) wall | Φ_pred(g_lag) | r_F [95%] | Φ(5) → Φ(30) | Φ untrimmed |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 44b | 5 | 1.53 [0.02, 1.72] | 0.92 | 1.65 | 0.92 [0.01, 1.21] | 0.95 → – | 0.92 |

Data: `data/processed/H111-talk-fano-sum-rule/results/units.parquet`, `units_wall.parquet`, `periods.parquet`.

## Scorecard (period-specific axes)
C (Φ vs the block-shift null), D (the sum rule is unfitted).

## Notes
