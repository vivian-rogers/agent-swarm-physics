# H121 × G17: goal period #17

**Verdict:** descriptive
**Role:** replication (exploratory)
**Period:** goal #17 · regime I · mean N 7.0 · units 17 · 5 unit-days, 35 eligible agent-days (boot replicas).

## Why this period
Eligible for the replication layer: every non-holdout unit with eligible agent-days (≥ 30 receiving calls). Each agent-day is one replica of the daily boot quench.

## Prediction
*Written 2026-10-04 22:20 UTC, before running on this period (the card's rule, written 22:00 UTC).* H67's read-out gain for this period is g_lag = 0.038 [-0.075, 0.150], so mean-field Glauber predicts τ_boot = τ₀ × 1.04 (τ₀ = max(1, −1/ln ρ_self) calls, measured on this period's steady-state calls). **Supported** if the pooled K_boot = τ_boot/τ_pred (HH form) has its point estimate in [0.5, 2] with a CI overlapping the band and the one-exponential test passes; **failed** if K_boot's CI lies entirely outside [0.5, 2]; **mixed** otherwise; **descriptive** if < 8 eligible agent-days or τ_boot unresolved (CI spans > ×10). Card expectation (P1′, credence 0.7): K_boot > 2 (the boot outlives the call-clock prediction).

## Result
Period pool (random effects over units): **τ_boot = 1.1 [0.0, 719.8] calls**; τ_pred (HH form, median over units) = 1.04 calls; **K_boot = 1.1 [0.0, 691.1]**; m(0) − m_∞ amplitude A = +0.361, m_∞ = 0.191; one-exponential CV gain of the double exponential (median) = 0.081.

| Unit | agent-days | K_max | τ_boot calls [95%] | ρ_self | τ₀ | g_lag | τ_pred | K_boot [95%] | K_AR | CV gain (2-exp) | resolved days |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 17 | 35 | 215 | 1.1 [1.0, 1075.0] | 0.070 | 1.00 | 0.038 | 1.04 | 1.1 [0.9, 1134.3] | 1.1 | 0.081 | 0 |

Data: `data/processed/H121-daily-boot-quench/results/units.parquet`, `days.parquet`.

*Post hoc (labelled; card "Post hoc")*: first-call excess over the k = 20–60 plateau e(0) = 0.37 [0.22, 0.52]; fast relaxation τ_fast = −1/ln[e(1)/e(0)] = 1.61 [0.83, 7.12] calls (K_fast = 1.55); slow excess over the steady state at k = 20–240: -0.04 [-0.17, 0.11].

## Scorecard (period-specific axes)
C, D (K_boot against the unfitted prediction).

## Notes
