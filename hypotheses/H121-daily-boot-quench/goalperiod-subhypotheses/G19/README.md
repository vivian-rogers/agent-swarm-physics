# H121 × G19: goal period #19

**Verdict:** descriptive
**Role:** replication (exploratory)
**Period:** goal #19 · regime I · mean N 7.5 · units 19a, 19b · 10 unit-days, 71 eligible agent-days (boot replicas).

## Why this period
Eligible for the replication layer: every non-holdout unit with eligible agent-days (≥ 30 receiving calls). Each agent-day is one replica of the daily boot quench.

## Prediction
*Written 2026-10-04 22:20 UTC, before running on this period (the card's rule, written 22:00 UTC).* H67's read-out gain for this period is g_lag = -0.003 [-0.032, 0.026], so mean-field Glauber predicts τ_boot = τ₀ × 1.00 (τ₀ = max(1, −1/ln ρ_self) calls, measured on this period's steady-state calls). **Supported** if the pooled K_boot = τ_boot/τ_pred (HH form) has its point estimate in [0.5, 2] with a CI overlapping the band and the one-exponential test passes; **failed** if K_boot's CI lies entirely outside [0.5, 2]; **mixed** otherwise; **descriptive** if < 8 eligible agent-days or τ_boot unresolved (CI spans > ×10). Card expectation (P1′, credence 0.7): K_boot > 2 (the boot outlives the call-clock prediction).

## Result
Period pool (random effects over units): **τ_boot = 36.9 [0.0, 86594.5] calls**; τ_pred (HH form, median over units) = 1.10 calls; **K_boot = 33.8 [0.0, 97619.7]**; m(0) − m_∞ amplitude A = -0.481, m_∞ = 0.811; one-exponential CV gain of the double exponential (median) = -0.019.

| Unit | agent-days | K_max | τ_boot calls [95%] | ρ_self | τ₀ | g_lag | τ_pred | K_boot [95%] | K_AR | CV gain (2-exp) | resolved days |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 19a | 63 | 355 | 0.6 [0.2, 1775.0] | 0.437 | 1.21 | 0.003 | 1.21 | 0.5 [0.2, 1502.7] | 0.5 | 0.036 | 2 |
| 19b | 8 | 321 | 1605.0 [0.2, 1605.0] | 0.258 | 1.00 | -0.019 | 0.98 | 1635.7 [0.2, 1726.7] | 1605.0 | -0.075 | 0 |

Data: `data/processed/H121-daily-boot-quench/results/units.parquet`, `days.parquet`.

*Post hoc (labelled; card "Post hoc")*: first-call excess over the k = 20–60 plateau e(0) = 0.45 [0.21, 0.61]; fast relaxation τ_fast = −1/ln[e(1)/e(0)] = 0.49 [0.00, 0.96] calls (K_fast = 0.41); slow excess over the steady state at k = 20–240: -0.02 [-0.34, 0.43].

## Scorecard (period-specific axes)
C, D (K_boot against the unfitted prediction).

## Notes
