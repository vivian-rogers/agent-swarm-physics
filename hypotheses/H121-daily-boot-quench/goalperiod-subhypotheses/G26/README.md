# H121 × G26: goal period #26

**Verdict:** supported
**Role:** replication (exploratory)
**Period:** goal #26 · regime I · mean N 10.0 · units 26 · 5 unit-days, 50 eligible agent-days (boot replicas).

## Why this period
Eligible for the replication layer: every non-holdout unit with eligible agent-days (≥ 30 receiving calls). Each agent-day is one replica of the daily boot quench.

## Prediction
*Written 2026-10-04 22:20 UTC, before running on this period (the card's rule, written 22:00 UTC).* H67's read-out gain for this period is g_lag = 0.012 [-0.055, 0.079], so mean-field Glauber predicts τ_boot = τ₀ × 1.01 (τ₀ = max(1, −1/ln ρ_self) calls, measured on this period's steady-state calls). **Supported** if the pooled K_boot = τ_boot/τ_pred (HH form) has its point estimate in [0.5, 2] with a CI overlapping the band and the one-exponential test passes; **failed** if K_boot's CI lies entirely outside [0.5, 2]; **mixed** otherwise; **descriptive** if < 8 eligible agent-days or τ_boot unresolved (CI spans > ×10). Card expectation (P1′, credence 0.7): K_boot > 2 (the boot outlives the call-clock prediction).

## Result
Period pool (random effects over units): **τ_boot = 1.9 [0.7, 5.6] calls**; τ_pred (HH form, median over units) = 1.01 calls; **K_boot = 1.9 [0.6, 5.6]**; m(0) − m_∞ amplitude A = +0.368, m_∞ = 0.132; one-exponential CV gain of the double exponential (median) = -0.084.

| Unit | agent-days | K_max | τ_boot calls [95%] | ρ_self | τ₀ | g_lag | τ_pred | K_boot [95%] | K_AR | CV gain (2-exp) | resolved days |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 26 | 50 | 193 | 1.9 [1.2, 12.2] | 0.339 | 1.00 | 0.012 | 1.01 | 1.9 [1.1, 12.2] | 1.9 | -0.084 | 1 |

Data: `data/processed/H121-daily-boot-quench/results/units.parquet`, `days.parquet`.

*Post hoc (labelled; card "Post hoc")*: first-call excess over the k = 20–60 plateau e(0) = 0.35 [0.24, 0.46]; fast relaxation τ_fast = −1/ln[e(1)/e(0)] = 3.01 [0.75, 18.78] calls (K_fast = 2.97); slow excess over the steady state at k = 20–240: -0.02 [-0.21, 0.18].

## Scorecard (period-specific axes)
C, D (K_boot against the unfitted prediction).

## Notes
