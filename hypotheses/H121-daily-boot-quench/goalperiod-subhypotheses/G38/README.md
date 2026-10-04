# H121 × G38: goal period #38

**Verdict:** descriptive
**Role:** replication (exploratory)
**Period:** goal #38 · regime III · mean N 12.6 · units 38a, 38b, 38c, 38d, 38e · 17 unit-days, 211 eligible agent-days (boot replicas).

## Why this period
Eligible for the replication layer: every non-holdout unit with eligible agent-days (≥ 30 receiving calls). Each agent-day is one replica of the daily boot quench.

## Prediction
*Written 2026-10-04 22:20 UTC, before running on this period (the card's rule, written 22:00 UTC).* H67's read-out gain for this period is g_lag = 0.066 [0.041, 0.090], so mean-field Glauber predicts τ_boot = τ₀ × 1.07 (τ₀ = max(1, −1/ln ρ_self) calls, measured on this period's steady-state calls). **Supported** if the pooled K_boot = τ_boot/τ_pred (HH form) has its point estimate in [0.5, 2] with a CI overlapping the band and the one-exponential test passes; **failed** if K_boot's CI lies entirely outside [0.5, 2]; **mixed** otherwise; **descriptive** if < 8 eligible agent-days or τ_boot unresolved (CI spans > ×10). Card expectation (P1′, credence 0.7): K_boot > 2 (the boot outlives the call-clock prediction).

## Result
Period pool (random effects over units): **τ_boot = 3.6 [0.4, 30.4] calls**; τ_pred (HH form, median over units) = 1.05 calls; **K_boot = 3.4 [0.4, 28.1]**; m(0) − m_∞ amplitude A = +0.116, m_∞ = 0.034; one-exponential CV gain of the double exponential (median) = -0.010.

| Unit | agent-days | K_max | τ_boot calls [95%] | ρ_self | τ₀ | g_lag | τ_pred | K_boot [95%] | K_AR | CV gain (2-exp) | resolved days |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 38a | 96 | 400 | 1.7 [0.4, 8.3] | -0.102 | 1.00 | 0.080 | 1.09 | 1.6 [0.3, 7.8] | 1.7 | -0.012 | 0 |
| 38b | 36 | 382 | 0.7 [0.2, 1675.7] | -0.035 | 1.00 | 0.039 | 1.04 | 0.7 [0.2, 1602.7] | 0.7 | 0.000 | 0 |
| 38c | 13 | 368 | 1840.0 [0.2, 1840.0] | -0.115 | 1.00 | 0.051 | 1.05 | 1745.8 [0.2, 1789.3] | 1840.0 | 0.005 | 0 |
| 38d | 25 | 337 | 323.6 [0.2, 1685.0] | -0.082 | 1.00 | 0.112 | 1.13 | 287.3 [0.2, 1580.2] | 323.6 | -0.014 | 0 |
| 38e | 41 | 388 | 1.3 [0.2, 1940.0] | -0.095 | 1.00 | 0.030 | 1.03 | 1.3 [0.2, 1894.8] | 1.3 | -0.010 | 0 |

Data: `data/processed/H121-daily-boot-quench/results/units.parquet`, `days.parquet`.

*Post hoc (labelled; card "Post hoc")*: first-call excess over the k = 20–60 plateau e(0) = 0.10 [0.06, 0.15]; fast relaxation τ_fast = −1/ln[e(1)/e(0)] = 1.43 [0.50, 13.83] calls (K_fast = 1.33); slow excess over the steady state at k = 20–240: 0.05 [-0.04, 0.16].

## Scorecard (period-specific axes)
C, D (K_boot against the unfitted prediction).

## Notes
