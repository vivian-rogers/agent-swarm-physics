# H121 × G51: goal period #51

**Verdict:** descriptive
**Role:** replication (exploratory)
**Period:** goal #51 · regime III · mean N 26.8 · units 51a, 51b, 51c, 51d, 51e, 51f, 51g, 51h, 51i, 51j, 51k, 51l · 45 unit-days, 1186 eligible agent-days (boot replicas). NE43 native in `../NE43/`.

## Why this period
Eligible for the replication layer: every non-holdout unit with eligible agent-days (≥ 30 receiving calls). Each agent-day is one replica of the daily boot quench.

## Prediction
*Written 2026-10-04 22:20 UTC, before running on this period (the card's rule, written 22:00 UTC).* H67's read-out gain for this period is g_lag = 0.142 [0.111, 0.174], so mean-field Glauber predicts τ_boot = τ₀ × 1.17 (τ₀ = max(1, −1/ln ρ_self) calls, measured on this period's steady-state calls). **Supported** if the pooled K_boot = τ_boot/τ_pred (HH form) has its point estimate in [0.5, 2] with a CI overlapping the band and the one-exponential test passes; **failed** if K_boot's CI lies entirely outside [0.5, 2]; **mixed** otherwise; **descriptive** if < 8 eligible agent-days or τ_boot unresolved (CI spans > ×10). Card expectation (P1′, credence 0.7): K_boot > 2 (the boot outlives the call-clock prediction).

## Result
Period pool (random effects over units): **τ_boot = 107.1 [14.2, 807.2] calls**; τ_pred (HH form, median over units) = 1.17 calls; **K_boot = 91.6 [12.2, 687.9]**; m(0) − m_∞ amplitude A = +0.017, m_∞ = 0.050; one-exponential CV gain of the double exponential (median) = -0.008.

| Unit | agent-days | K_max | τ_boot calls [95%] | ρ_self | τ₀ | g_lag | τ_pred | K_boot [95%] | K_AR | CV gain (2-exp) | resolved days |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 51a | 63 | 400 | 2.1 [1.2, 3.2] | 0.002 | 1.00 | 0.129 | 1.15 | 1.8 [1.0, 2.8] | 2.1 | 0.001 | 0 |
| 51b | 24 | 400 | 0.9 [0.2, 2000.0] | -0.062 | 1.00 | 0.142 | 1.17 | 0.8 [0.2, 1739.2] | 0.9 | -0.002 | 0 |
| 51c | 123 | 400 | 166.4 [1.2, 2000.0] | -0.082 | 1.00 | 0.160 | 1.19 | 139.7 [1.0, 1738.9] | 166.4 | -0.006 | 0 |
| 51d | 130 | 384 | 332.4 [1.9, 1920.0] | -0.073 | 1.00 | 0.075 | 1.08 | 307.4 [1.7, 1823.8] | 332.4 | 0.011 | 0 |
| 51e | 81 | 382 | 1910.0 [0.2, 1910.0] | -0.011 | 1.00 | 0.127 | 1.15 | 1667.0 [0.2, 1804.4] | 1910.0 | -0.039 | 0 |
| 51f | 135 | 235 | 1175.0 [6.7, 1175.0] | -0.036 | 1.00 | 0.123 | 1.14 | 1030.2 [5.5, 1113.3] | 1175.0 | -0.051 | 0 |
| 51g | 350 | 346 | 30.7 [0.6, 1730.0] | -0.002 | 1.00 | 0.147 | 1.17 | 26.2 [0.5, 1478.0] | 30.7 | -0.017 | 0 |
| 51h | 105 | 261 | 1305.0 [0.2, 1305.0] | -0.048 | 1.00 | 0.292 | 1.41 | 923.7 [0.1, 1029.7] | 1305.0 | 0.005 | 0 |
| 51i | 55 | 295 | 53.0 [0.2, 1475.0] | -0.013 | 1.00 | 0.156 | 1.18 | 44.7 [0.2, 1328.7] | 53.0 | -0.015 | 0 |
| 51j | 58 | 305 | 0.9 [0.2, 1525.0] | -0.013 | 1.00 | 0.196 | 1.24 | 0.7 [0.2, 1287.3] | 0.9 | -0.011 | 0 |
| 51k | 30 | 342 | 502.7 [1.3, 1710.0] | 0.116 | 1.00 | 0.019 | 1.02 | 493.1 [1.3, 1832.2] | 502.7 | -0.003 | 0 |
| 51l | 32 | 360 | 1800.0 [2.3, 1800.0] | 0.103 | 1.00 | 0.152 | 1.18 | 1526.1 [1.9, 1685.2] | 1800.0 | -0.050 | 0 |

Data: `data/processed/H121-daily-boot-quench/results/units.parquet`, `days.parquet`.

*Post hoc (labelled; card "Post hoc")*: first-call excess over the k = 20–60 plateau e(0) = 0.02 [-0.00, 0.05]; fast relaxation τ_fast = −1/ln[e(1)/e(0)] = n/a [0.12, 28.57] calls (K_fast = n/a); slow excess over the steady state at k = 20–240: 0.15 [0.06, 0.26].

## Scorecard (period-specific axes)
C, D (K_boot against the unfitted prediction).

## Notes
