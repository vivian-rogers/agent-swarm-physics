# H121 × G04: goal period #4

**Verdict:** descriptive
**Role:** replication (exploratory)
**Period:** goal #4 · regime I · mean N 4.0 · units 4a, 4b, 4c · 25 unit-days, 100 eligible agent-days (boot replicas).

## Why this period
Eligible for the replication layer: every non-holdout unit with eligible agent-days (≥ 30 receiving calls). Each agent-day is one replica of the daily boot quench.

## Prediction
*Written 2026-10-04 22:20 UTC, before running on this period (the card's rule, written 22:00 UTC).* H67's read-out gain for this period is g_lag = 0.011 [-0.023, 0.046], so mean-field Glauber predicts τ_boot = τ₀ × 1.01 (τ₀ = max(1, −1/ln ρ_self) calls, measured on this period's steady-state calls). **Supported** if the pooled K_boot = τ_boot/τ_pred (HH form) has its point estimate in [0.5, 2] with a CI overlapping the band and the one-exponential test passes; **failed** if K_boot's CI lies entirely outside [0.5, 2]; **mixed** otherwise; **descriptive** if < 8 eligible agent-days or τ_boot unresolved (CI spans > ×10). Card expectation (P1′, credence 0.7): K_boot > 2 (the boot outlives the call-clock prediction).

## Result
Period pool (random effects over units): **τ_boot = 24.1 [0.0, 19036.8] calls**; τ_pred (HH form, median over units) = 1.36 calls; **K_boot = 17.3 [0.0, 8095.3]**; m(0) − m_∞ amplitude A = +0.364, m_∞ = 0.064; one-exponential CV gain of the double exponential (median) = -0.003.

| Unit | agent-days | K_max | τ_boot calls [95%] | ρ_self | τ₀ | g_lag | τ_pred | K_boot [95%] | K_AR | CV gain (2-exp) | resolved days |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 4a | 20 | 221 | 1105.0 [0.2, 1105.0] | 0.559 | 1.72 | -0.007 | 1.71 | 647.5 [0.1, 776.2] | 657.0 | 0.018 | 0 |
| 4c | 76 | 244 | 1.2 [0.3, 1220.0] | 0.226 | 1.00 | 0.021 | 1.02 | 1.1 [0.3, 1167.7] | 1.2 | -0.024 | 0 |

Data: `data/processed/H121-daily-boot-quench/results/units.parquet`, `days.parquet`.

*Post hoc (labelled; card "Post hoc")*: first-call excess over the k = 20–60 plateau e(0) = 0.29 [0.20, 0.38]; fast relaxation τ_fast = −1/ln[e(1)/e(0)] = 0.50 [0.00, 1.21] calls (K_fast = 0.43); slow excess over the steady state at k = 20–240: 0.07 [-0.06, 0.22].

## Scorecard (period-specific axes)
C, D (K_boot against the unfitted prediction).

## Notes
