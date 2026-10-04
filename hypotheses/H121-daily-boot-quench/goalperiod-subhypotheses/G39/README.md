# H121 × G39: goal period #39

**Verdict:** descriptive
**Role:** replication (exploratory)
**Period:** goal #39 · regime III · mean N 14.8 · units 39 · 5 unit-days, 74 eligible agent-days (boot replicas). NE42 native in `../NE42/`.

## Why this period
Eligible for the replication layer: every non-holdout unit with eligible agent-days (≥ 30 receiving calls). Each agent-day is one replica of the daily boot quench.

## Prediction
*Written 2026-10-04 22:20 UTC, before running on this period (the card's rule, written 22:00 UTC).* H67's read-out gain for this period is g_lag = 0.144 [0.066, 0.223], so mean-field Glauber predicts τ_boot = τ₀ × 1.17 (τ₀ = max(1, −1/ln ρ_self) calls, measured on this period's steady-state calls). **Supported** if the pooled K_boot = τ_boot/τ_pred (HH form) has its point estimate in [0.5, 2] with a CI overlapping the band and the one-exponential test passes; **failed** if K_boot's CI lies entirely outside [0.5, 2]; **mixed** otherwise; **descriptive** if < 8 eligible agent-days or τ_boot unresolved (CI spans > ×10). Card expectation (P1′, credence 0.7): K_boot > 2 (the boot outlives the call-clock prediction).

## Result
Period pool (random effects over units): **τ_boot = 0.7 [0.1, 4.2] calls**; τ_pred (HH form, median over units) = 1.17 calls; **K_boot = 0.6 [0.1, 3.6]**; m(0) − m_∞ amplitude A = +0.112, m_∞ = 0.024; one-exponential CV gain of the double exponential (median) = -0.002.

| Unit | agent-days | K_max | τ_boot calls [95%] | ρ_self | τ₀ | g_lag | τ_pred | K_boot [95%] | K_AR | CV gain (2-exp) | resolved days |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 39 | 74 | 370 | 0.7 [0.2, 18.7] | -0.045 | 1.00 | 0.144 | 1.17 | 0.6 [0.2, 16.2] | 0.7 | -0.002 | 0 |

Data: `data/processed/H121-daily-boot-quench/results/units.parquet`, `days.parquet`.

*Post hoc (labelled; card "Post hoc")*: first-call excess over the k = 20–60 plateau e(0) = 0.11 [-0.03, 0.25]; fast relaxation τ_fast = −1/ln[e(1)/e(0)] = 0.77 [0.00, 2.60] calls (K_fast = 0.66); slow excess over the steady state at k = 20–240: -0.04 [-0.24, 0.19].

## Scorecard (period-specific axes)
C, D (K_boot against the unfitted prediction).

## Notes
