# H111 × G51: goal period #51

**Verdict:** supported
**Role:** replication (+ NE43 native on 51f/51g/51h, separate folder) (exploratory)
**Period:** goal #51 · regime III · mean present N 27.1 · units 51a, 51c, 51d, 51e, 51f, 51g, 51h, 51i, 51j, 51k, 51l · 44 non-holdout days.

## Why this period
Eligible for the replication layer: H67 measured a read-out loop gain g_lag for every unit of this period, so the sum rule gives a parameter-free prediction here.

## Prediction
*Written 2026-10-04 21:41 UTC, before running on this period (after Amendment A1). No H111 statistic seen.*
The card's per-period rule on the random-effects pooled r_F = Φ_obs(10)/Φ_pred(g_lag): supported if r_F ∈ [0.8, 1.2]; failed if r_F ≥ 2 or ≤ 0.5; mixed otherwise; descriptive with fewer than 40 usable windows or a Φ CI wider than 1.0. Regime III: the sum rule predicts Φ ≈ 1/(1 − g_lag)² (table). The card gives the HH's ±20% band credence 0.20 and the kill (Φ ≥ 2 Φ_pred) credence 0.35.

| Unit | H67 g_lag [95%] | ≈ 1/(1 − g_lag)² (room-adjusted value computed in the run) |
| --- | --- | --- |
| 51a | 0.129 [0.063, 0.202] | 1.32 |
| 51c | 0.160 [0.118, 0.207] | 1.42 |
| 51d | 0.075 [0.022, 0.127] | 1.17 |
| 51e | 0.127 [0.047, 0.215] | 1.31 |
| 51f | 0.123 [0.040, 0.205] | 1.30 |
| 51g | 0.147 [0.118, 0.180] | 1.37 |
| 51h | 0.292 [0.197, 0.393] | 2.00 |
| 51i | 0.156 [0.020, 0.316] | 1.40 |
| 51j | 0.196 [0.128, 0.251] | 1.55 |
| 51k | 0.019 [-0.092, 0.141] | 1.04 |
| 51l | 0.152 [0.020, 0.223] | 1.39 |

## Result
*Run 2026-10-04 ~21:45 UTC (non-holdout units; per-call clock, Amendment A1).* Period pool (random effects over units): **Φ(10) = 1.40 [1.30, 1.50]**, Φ_pred = 1.39, **r_F = 1.03 [0.94, 1.14]**; 1441 usable 10-min windows. Verdict by the card's rule: **supported**.

| Unit | windows (10 min) | Φ(10) [95%] per-call | Φ(10) wall | Φ_pred(g_lag) | r_F [95%] | Φ(5) → Φ(30) | Φ untrimmed |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 51a | 74 | 1.24 [0.92, 1.68] | 1.16 | 1.31 | 0.94 [0.66, 1.34] | 1.18 → 1.06 | 1.24 |
| 51c | 191 | 1.29 [1.06, 1.57] | 1.23 | 1.41 | 0.92 [0.73, 1.13] | 1.22 → 1.10 | 1.35 |
| 51d | 130 | 1.37 [1.06, 1.71] | 1.40 | 1.17 | 1.17 [0.89, 1.54] | 1.32 → 0.94 | 1.41 |
| 51e | 103 | 1.64 [1.26, 2.12] | 1.73 | 1.31 | 1.25 [0.89, 1.72] | 1.53 → 1.96 | 1.77 |
| 51f | 182 | 1.46 [1.15, 1.74] | 1.30 | 1.30 | 1.13 [0.85, 1.43] | 1.39 → 1.49 | 1.52 |
| 51g | 523 | 1.45 [1.27, 1.66] | 1.54 | 1.36 | 1.06 [0.91, 1.25] | 1.31 → 1.86 | 1.36 |
| 51h | 114 | 1.53 [1.17, 1.96] | 1.66 | 1.96 | 0.78 [0.52, 1.11] | 1.36 → 1.23 | 1.28 |
| 51i | 47 | 1.34 [0.73, 1.89] | 1.36 | 1.40 | 0.96 [0.43, 1.52] | 1.11 → 1.62 | 1.37 |
| 51j | 39 | 1.37 [1.03, 1.76] | 1.41 | 1.54 | 0.89 [0.65, 1.18] | 1.42 → 1.34 | 1.44 |
| 51k | 19 | 1.71 [0.98, 2.11] | 1.58 | 1.04 | 1.65 [0.96, 2.27] | 1.79 → 4.04 | 1.35 |
| 51l | 19 | 1.17 [0.79, 1.70] | 1.58 | 1.39 | 0.85 [0.53, 1.34] | 1.48 → 0.44 | 0.95 |

Data: `data/processed/H111-talk-fano-sum-rule/results/units.parquet`, `units_wall.parquet`, `periods.parquet`.

## Scorecard (period-specific axes)
C (Φ vs the block-shift null), D (the sum rule is unfitted).

## Notes
