# H121 × G11: goal period #11

**Verdict:** descriptive
**Role:** replication (exploratory)
**Period:** goal #11 · regime I · mean N 7.0 · units 11 · 5 unit-days, 35 eligible agent-days (boot replicas).

## Why this period
Eligible for the replication layer: every non-holdout unit with eligible agent-days (≥ 30 receiving calls). Each agent-day is one replica of the daily boot quench.

## Prediction
*Written 2026-10-04 22:20 UTC, before running on this period (the card's rule, written 22:00 UTC).* H67's read-out gain for this period is g_lag = 0.027 [-0.026, 0.080], so mean-field Glauber predicts τ_boot = τ₀ × 1.03 (τ₀ = max(1, −1/ln ρ_self) calls, measured on this period's steady-state calls). **Supported** if the pooled K_boot = τ_boot/τ_pred (HH form) has its point estimate in [0.5, 2] with a CI overlapping the band and the one-exponential test passes; **failed** if K_boot's CI lies entirely outside [0.5, 2]; **mixed** otherwise; **descriptive** if < 8 eligible agent-days or τ_boot unresolved (CI spans > ×10). Card expectation (P1′, credence 0.7): K_boot > 2 (the boot outlives the call-clock prediction).

## Result
Period pool (random effects over units): **τ_boot = 153.0 [3.6, 6480.3] calls**; τ_pred (HH form, median over units) = 1.03 calls; **K_boot = 148.9 [3.5, 6265.1]**; m(0) − m_∞ amplitude A = -0.174, m_∞ = 0.262; one-exponential CV gain of the double exponential (median) = 0.062.

| Unit | agent-days | K_max | τ_boot calls [95%] | ρ_self | τ₀ | g_lag | τ_pred | K_boot [95%] | K_AR | CV gain (2-exp) | resolved days |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 11 | 35 | 284 | 153.0 [0.6, 1420.0] | 0.289 | 1.00 | 0.027 | 1.03 | 148.9 [0.6, 1350.8] | 153.0 | 0.062 | 0 |

Data: `data/processed/H121-daily-boot-quench/results/units.parquet`, `days.parquet`.

*Post hoc (labelled; card "Post hoc")*: first-call excess over the k = 20–60 plateau e(0) = 0.37 [0.20, 0.51]; fast relaxation τ_fast = −1/ln[e(1)/e(0)] = 0.53 [0.00, 1.02] calls (K_fast = 0.51); slow excess over the steady state at k = 20–240: -0.10 [-0.34, 0.15].

## Scorecard (period-specific axes)
C, D (K_boot against the unfitted prediction).

## Notes
