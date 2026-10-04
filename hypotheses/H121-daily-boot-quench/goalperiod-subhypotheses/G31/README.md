# H121 × G31: goal period #31

**Verdict:** descriptive
**Role:** replication (exploratory)
**Period:** goal #31 · regime I · mean N 11.2 · units 31a, 31b, 31c, 31d · 5 unit-days, 56 eligible agent-days (boot replicas).

## Why this period
Eligible for the replication layer: every non-holdout unit with eligible agent-days (≥ 30 receiving calls). Each agent-day is one replica of the daily boot quench.

## Prediction
*Written 2026-10-04 22:20 UTC, before running on this period (the card's rule, written 22:00 UTC).* H67's read-out gain for this period is g_lag = -0.035 [-0.094, 0.025], so mean-field Glauber predicts τ_boot = τ₀ × 0.97 (τ₀ = max(1, −1/ln ρ_self) calls, measured on this period's steady-state calls). **Supported** if the pooled K_boot = τ_boot/τ_pred (HH form) has its point estimate in [0.5, 2] with a CI overlapping the band and the one-exponential test passes; **failed** if K_boot's CI lies entirely outside [0.5, 2]; **mixed** otherwise; **descriptive** if < 8 eligible agent-days or τ_boot unresolved (CI spans > ×10). Card expectation (P1′, credence 0.7): K_boot > 2 (the boot outlives the call-clock prediction).

## Result
Period pool (random effects over units): **τ_boot = 5.6 [0.8, 41.3] calls**; τ_pred (HH form, median over units) = 0.94 calls; **K_boot = 5.8 [0.8, 42.3]**; m(0) − m_∞ amplitude A = -0.057, m_∞ = 0.080; one-exponential CV gain of the double exponential (median) = 0.007.

| Unit | agent-days | K_max | τ_boot calls [95%] | ρ_self | τ₀ | g_lag | τ_pred | K_boot [95%] | K_AR | CV gain (2-exp) | resolved days |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 31a | 22 | 400 | 17.9 [0.2, 72.1] | 0.242 | 1.00 | 0.024 | 1.02 | 17.5 [0.2, 69.0] | 17.9 | 0.010 | 0 |
| 31b | 12 | 390 | 0.2 [0.2, 1950.0] | 0.265 | 1.00 | -0.076 | 0.93 | 0.2 [0.2, 2108.3] | 0.2 | 0.015 | 0 |
| 31c | 11 | 400 | 13.8 [8.9, 2000.0] | 0.210 | 1.00 | -0.042 | 0.96 | 14.4 [9.1, 2149.8] | 13.8 | 0.004 | 0 |
| 31d | 11 | 400 | 9.7 [0.2, 2000.0] | 0.209 | 1.00 | -0.084 | 0.92 | 10.5 [0.2, 2266.9] | 9.7 | 0.003 | 0 |

Data: `data/processed/H121-daily-boot-quench/results/units.parquet`, `days.parquet`.

*Post hoc (labelled; card "Post hoc")*: first-call excess over the k = 20–60 plateau e(0) = 0.06 [-0.07, 0.24]; fast relaxation τ_fast = −1/ln[e(1)/e(0)] = 0.00 [0.00, 0.61] calls (K_fast = 0.00); slow excess over the steady state at k = 20–240: 0.04 [-0.04, 0.11].

## Scorecard (period-specific axes)
C, D (K_boot against the unfitted prediction).

## Notes
