# H121 × G44: goal period #44

**Verdict:** descriptive
**Role:** replication (exploratory)
**Period:** goal #44 · regime III · mean N 16.5 · units 44a, 44b · 4 unit-days, 66 eligible agent-days (boot replicas).

## Why this period
Eligible for the replication layer: every non-holdout unit with eligible agent-days (≥ 30 receiving calls). Each agent-day is one replica of the daily boot quench.

## Prediction
*Written 2026-10-04 22:20 UTC, before running on this period (the card's rule, written 22:00 UTC).* H67's read-out gain for this period is g_lag = 0.234 [0.129, 0.340], so mean-field Glauber predicts τ_boot = τ₀ × 1.31 (τ₀ = max(1, −1/ln ρ_self) calls, measured on this period's steady-state calls). **Supported** if the pooled K_boot = τ_boot/τ_pred (HH form) has its point estimate in [0.5, 2] with a CI overlapping the band and the one-exponential test passes; **failed** if K_boot's CI lies entirely outside [0.5, 2]; **mixed** otherwise; **descriptive** if < 8 eligible agent-days or τ_boot unresolved (CI spans > ×10). Card expectation (P1′, credence 0.7): K_boot > 2 (the boot outlives the call-clock prediction).

## Result
Period pool (random effects over units): **τ_boot = 160.6 [6.1, 4198.4] calls**; τ_pred (HH form, median over units) = 1.31 calls; **K_boot = 123.0 [4.7, 3221.0]**; m(0) − m_∞ amplitude A = +0.039, m_∞ = 0.037; one-exponential CV gain of the double exponential (median) = -0.005.

| Unit | agent-days | K_max | τ_boot calls [95%] | ρ_self | τ₀ | g_lag | τ_pred | K_boot [95%] | K_AR | CV gain (2-exp) | resolved days |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 44a | 32 | 293 | 48.0 [0.5, 1465.0] | 0.170 | 1.00 | 0.234 | 1.31 | 36.7 [0.4, 1185.4] | 43.5 | -0.002 | 0 |
| 44b | 34 | 285 | 1425.0 [0.2, 1425.0] | -0.103 | 1.00 | 0.234 | 1.31 | 1091.3 [0.2, 1229.4] | 1425.0 | -0.009 | 0 |

Data: `data/processed/H121-daily-boot-quench/results/units.parquet`, `days.parquet`.

*Post hoc (labelled; card "Post hoc")*: first-call excess over the k = 20–60 plateau e(0) = -0.00 [-0.02, 0.03]; fast relaxation τ_fast = −1/ln[e(1)/e(0)] = n/a [0.00, 0.00] calls (K_fast = n/a); slow excess over the steady state at k = 20–240: 0.08 [-0.13, 0.42].

## Scorecard (period-specific axes)
C, D (K_boot against the unfitted prediction).

## Notes
