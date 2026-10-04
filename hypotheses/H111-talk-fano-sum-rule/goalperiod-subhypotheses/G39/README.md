# H111 × G39: goal period #39

**Verdict:** supported
**Role:** replication (+ NE42 native, separate folder) (exploratory)
**Period:** goal #39 · regime III · mean present N 14.8 · units 39 · 5 non-holdout days.

## Why this period
Eligible for the replication layer: H67 measured a read-out loop gain g_lag for every unit of this period, so the sum rule gives a parameter-free prediction here.

## Prediction
*Written 2026-10-04 21:41 UTC, before running on this period (after Amendment A1). No H111 statistic seen.*
The card's per-period rule on the random-effects pooled r_F = Φ_obs(10)/Φ_pred(g_lag): supported if r_F ∈ [0.8, 1.2]; failed if r_F ≥ 2 or ≤ 0.5; mixed otherwise; descriptive with fewer than 40 usable windows or a Φ CI wider than 1.0. Regime III: the sum rule predicts Φ ≈ 1/(1 − g_lag)² (table). The card gives the HH's ±20% band credence 0.20 and the kill (Φ ≥ 2 Φ_pred) credence 0.35.

| Unit | H67 g_lag [95%] | ≈ 1/(1 − g_lag)² (room-adjusted value computed in the run) |
| --- | --- | --- |
| 39 | 0.144 [0.073, 0.219] | 1.37 |

## Result
*Run 2026-10-04 ~21:45 UTC (non-holdout units; per-call clock, Amendment A1).* Period pool (random effects over units): **Φ(10) = 1.12 [0.71, 1.53]**, Φ_pred = 1.35, **r_F = 0.83 [0.54, 1.27]**; 66 usable 10-min windows. Verdict by the card's rule: **supported**.

| Unit | windows (10 min) | Φ(10) [95%] per-call | Φ(10) wall | Φ_pred(g_lag) | r_F [95%] | Φ(5) → Φ(30) | Φ untrimmed |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 39 | 66 | 1.12 [0.72, 1.49] | 1.06 | 1.35 | 0.83 [0.52, 1.17] | 1.15 → 1.48 | 1.07 |

Data: `data/processed/H111-talk-fano-sum-rule/results/units.parquet`, `units_wall.parquet`, `periods.parquet`.

## Scorecard (period-specific axes)
C (Φ vs the block-shift null), D (the sum rule is unfitted).

## Notes
