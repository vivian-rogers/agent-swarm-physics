# H121 × G18: goal period #18

**Verdict:** descriptive
**Role:** replication (exploratory)
**Period:** goal #18 · regime I · mean N 7.3 · units 18a, 18b, 18c · 10 unit-days, 75 eligible agent-days (boot replicas).

## Why this period
Eligible for the replication layer: every non-holdout unit with eligible agent-days (≥ 30 receiving calls). Each agent-day is one replica of the daily boot quench.

## Prediction
*Written 2026-10-04 22:20 UTC, before running on this period (the card's rule, written 22:00 UTC).* H67's read-out gain for this period is g_lag = 0.048 [-0.000, 0.097], so mean-field Glauber predicts τ_boot = τ₀ × 1.05 (τ₀ = max(1, −1/ln ρ_self) calls, measured on this period's steady-state calls). **Supported** if the pooled K_boot = τ_boot/τ_pred (HH form) has its point estimate in [0.5, 2] with a CI overlapping the band and the one-exponential test passes; **failed** if K_boot's CI lies entirely outside [0.5, 2]; **mixed** otherwise; **descriptive** if < 8 eligible agent-days or τ_boot unresolved (CI spans > ×10). Card expectation (P1′, credence 0.7): K_boot > 2 (the boot outlives the call-clock prediction).

## Result
Period pool (random effects over units): **τ_boot = 53.1 [2.7, 1048.2] calls**; τ_pred (HH form, median over units) = 1.18 calls; **K_boot = 46.2 [2.4, 899.0]**; m(0) − m_∞ amplitude A = -0.134, m_∞ = 0.207; one-exponential CV gain of the double exponential (median) = 0.059.

| Unit | agent-days | K_max | τ_boot calls [95%] | ρ_self | τ₀ | g_lag | τ_pred | K_boot [95%] | K_AR | CV gain (2-exp) | resolved days |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 18a | 14 | 218 | 91.1 [0.2, 515.5] | 0.180 | 1.00 | 0.004 | 1.00 | 90.8 [0.2, 473.7] | 91.1 | 0.059 | 0 |
| 18b | 40 | 297 | 52.3 [0.2, 579.7] | 0.452 | 1.26 | 0.018 | 1.28 | 40.8 [0.2, 473.8] | 39.4 | 0.089 | 0 |
| 18c | 21 | 367 | 20.6 [0.2, 1835.0] | 0.396 | 1.08 | 0.082 | 1.18 | 17.5 [0.1, 1735.5] | 15.2 | -0.011 | 0 |

Data: `data/processed/H121-daily-boot-quench/results/units.parquet`, `days.parquet`.

*Post hoc (labelled; card "Post hoc")*: first-call excess over the k = 20–60 plateau e(0) = 0.38 [0.20, 0.57]; fast relaxation τ_fast = −1/ln[e(1)/e(0)] = 0.49 [0.00, 1.19] calls (K_fast = 0.41); slow excess over the steady state at k = 20–240: -0.07 [-0.36, 0.25].

## Scorecard (period-specific axes)
C, D (K_boot against the unfitted prediction).

## Notes
