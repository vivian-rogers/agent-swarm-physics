# H121 × G10: goal period #10

**Verdict:** descriptive
**Role:** replication (exploratory)
**Period:** goal #10 · regime I · mean N 7.0 · units 10a, 10b · 5 unit-days, 35 eligible agent-days (boot replicas).

## Why this period
Eligible for the replication layer: every non-holdout unit with eligible agent-days (≥ 30 receiving calls). Each agent-day is one replica of the daily boot quench.

## Prediction
*Written 2026-10-04 22:20 UTC, before running on this period (the card's rule, written 22:00 UTC).* H67's read-out gain for this period is g_lag = 0.002 [-0.050, 0.054], so mean-field Glauber predicts τ_boot = τ₀ × 1.00 (τ₀ = max(1, −1/ln ρ_self) calls, measured on this period's steady-state calls). **Supported** if the pooled K_boot = τ_boot/τ_pred (HH form) has its point estimate in [0.5, 2] with a CI overlapping the band and the one-exponential test passes; **failed** if K_boot's CI lies entirely outside [0.5, 2]; **mixed** otherwise; **descriptive** if < 8 eligible agent-days or τ_boot unresolved (CI spans > ×10). Card expectation (P1′, credence 0.7): K_boot > 2 (the boot outlives the call-clock prediction).

## Result
Period pool (random effects over units): **τ_boot = 0.7 [0.0, 11.5] calls**; τ_pred (HH form, median over units) = 1.01 calls; **K_boot = 0.7 [0.0, 11.3]**; m(0) − m_∞ amplitude A = +0.379, m_∞ = 0.108; one-exponential CV gain of the double exponential (median) = 0.017.

| Unit | agent-days | K_max | τ_boot calls [95%] | ρ_self | τ₀ | g_lag | τ_pred | K_boot [95%] | K_AR | CV gain (2-exp) | resolved days |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 10a | 14 | 151 | 0.8 [0.2, 755.0] | 0.207 | 1.00 | 0.015 | 1.02 | 0.8 [0.2, 732.8] | 0.8 | -0.006 | 0 |
| 10b | 21 | 287 | 0.5 [0.2, 1435.0] | 0.236 | 1.00 | -0.002 | 1.00 | 0.5 [0.2, 1464.2] | 0.5 | 0.039 | 0 |

Data: `data/processed/H121-daily-boot-quench/results/units.parquet`, `days.parquet`.

*Post hoc (labelled; card "Post hoc")*: first-call excess over the k = 20–60 plateau e(0) = 0.39 [0.14, 0.60]; fast relaxation τ_fast = −1/ln[e(1)/e(0)] = 0.60 [0.00, 0.93] calls (K_fast = 0.60); slow excess over the steady state at k = 20–240: -0.01 [-0.13, 0.11].

## Scorecard (period-specific axes)
C, D (K_boot against the unfitted prediction).

## Notes
