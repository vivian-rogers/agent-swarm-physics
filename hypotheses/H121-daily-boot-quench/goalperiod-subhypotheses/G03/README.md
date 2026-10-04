# H121 × G03: goal period #3

**Verdict:** descriptive
**Role:** replication (exploratory)
**Period:** goal #3 · regime I · mean N 4.0 · units 3 · 3 unit-days, 12 eligible agent-days (boot replicas).

## Why this period
Eligible for the replication layer: every non-holdout unit with eligible agent-days (≥ 30 receiving calls). Each agent-day is one replica of the daily boot quench.

## Prediction
*Written 2026-10-04 22:20 UTC, before running on this period (the card's rule, written 22:00 UTC).* H67's read-out gain for this period is g_lag = 0.017 [-0.090, 0.124], so mean-field Glauber predicts τ_boot = τ₀ × 1.02 (τ₀ = max(1, −1/ln ρ_self) calls, measured on this period's steady-state calls). **Supported** if the pooled K_boot = τ_boot/τ_pred (HH form) has its point estimate in [0.5, 2] with a CI overlapping the band and the one-exponential test passes; **failed** if K_boot's CI lies entirely outside [0.5, 2]; **mixed** otherwise; **descriptive** if < 8 eligible agent-days or τ_boot unresolved (CI spans > ×10). Card expectation (P1′, credence 0.7): K_boot > 2 (the boot outlives the call-clock prediction).

## Result
Period pool (random effects over units): **τ_boot = 77.1 [8.4, 707.0] calls**; τ_pred (HH form, median over units) = 1.24 calls; **K_boot = 62.2 [6.5, 594.7]**; m(0) − m_∞ amplitude A = -0.203, m_∞ = 0.609; one-exponential CV gain of the double exponential (median) = -0.041.

| Unit | agent-days | K_max | τ_boot calls [95%] | ρ_self | τ₀ | g_lag | τ_pred | K_boot [95%] | K_AR | CV gain (2-exp) | resolved days |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 3 | 12 | 214 | 77.1 [4.6, 117.2] | 0.440 | 1.22 | 0.017 | 1.24 | 62.2 [2.9, 86.2] | 60.3 | -0.041 | 0 |

Data: `data/processed/H121-daily-boot-quench/results/units.parquet`, `days.parquet`.

*Post hoc (labelled; card "Post hoc")*: first-call excess over the k = 20–60 plateau e(0) = 0.23 [-0.07, 0.48]; fast relaxation τ_fast = −1/ln[e(1)/e(0)] = n/a [n/a, n/a] calls (K_fast = n/a); slow excess over the steady state at k = 20–240: 0.26 [-0.26, 0.73].

## Scorecard (period-specific axes)
C, D (K_boot against the unfitted prediction).

## Notes
