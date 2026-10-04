# H111 × G40: goal period #40

**Verdict:** mixed
**Role:** replication (+ NE42 native, separate folder) (exploratory)
**Period:** goal #40 · regime III · mean present N 14.8 · units 40 · 5 non-holdout days.

## Why this period
Eligible for the replication layer: H67 measured a read-out loop gain g_lag for every unit of this period, so the sum rule gives a parameter-free prediction here.

## Prediction
*Written 2026-10-04 21:41 UTC, before running on this period (after Amendment A1). No H111 statistic seen.*
The card's per-period rule on the random-effects pooled r_F = Φ_obs(10)/Φ_pred(g_lag): supported if r_F ∈ [0.8, 1.2]; failed if r_F ≥ 2 or ≤ 0.5; mixed otherwise; descriptive with fewer than 40 usable windows or a Φ CI wider than 1.0. Regime III: the sum rule predicts Φ ≈ 1/(1 − g_lag)² (table). The card gives the HH's ±20% band credence 0.20 and the kill (Φ ≥ 2 Φ_pred) credence 0.35.

| Unit | H67 g_lag [95%] | ≈ 1/(1 − g_lag)² (room-adjusted value computed in the run) |
| --- | --- | --- |
| 40 | 0.003 [-0.106, 0.109] | 1.01 |

## Result
*Run 2026-10-04 ~21:45 UTC (non-holdout units; per-call clock, Amendment A1).* Period pool (random effects over units): **Φ(10) = 1.24 [0.88, 1.61]**, Φ_pred = 1.01, **r_F = 1.24 [0.84, 1.82]**; 106 usable 10-min windows. Verdict by the card's rule: **mixed**.

| Unit | windows (10 min) | Φ(10) [95%] per-call | Φ(10) wall | Φ_pred(g_lag) | r_F [95%] | Φ(5) → Φ(30) | Φ untrimmed |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 40 | 106 | 1.24 [0.90, 1.59] | 1.23 | 1.01 | 1.24 [0.82, 1.69] | 1.12 → 0.93 | 0.96 |

Data: `data/processed/H111-talk-fano-sum-rule/results/units.parquet`, `units_wall.parquet`, `periods.parquet`.

## Scorecard (period-specific axes)
C (Φ vs the block-shift null), D (the sum rule is unfitted).

## Notes
