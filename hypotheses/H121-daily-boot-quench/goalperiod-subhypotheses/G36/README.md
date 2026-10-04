# H121 × G36: goal period #36

**Verdict:** descriptive
**Role:** replication (exploratory)
**Period:** goal #36 · regime II/III · mean N 12.0 · units 36a, 36b, 36c · 5 unit-days, 60 eligible agent-days (boot replicas). NE14 native in `../NE14/`.

## Why this period
Eligible for the replication layer: every non-holdout unit with eligible agent-days (≥ 30 receiving calls). Each agent-day is one replica of the daily boot quench.

## Prediction
*Written 2026-10-04 22:20 UTC, before running on this period (the card's rule, written 22:00 UTC).* H67's read-out gain for this period is g_lag = 0.068 [-0.030, 0.166], so mean-field Glauber predicts τ_boot = τ₀ × 1.07 (τ₀ = max(1, −1/ln ρ_self) calls, measured on this period's steady-state calls). **Supported** if the pooled K_boot = τ_boot/τ_pred (HH form) has its point estimate in [0.5, 2] with a CI overlapping the band and the one-exponential test passes; **failed** if K_boot's CI lies entirely outside [0.5, 2]; **mixed** otherwise; **descriptive** if < 8 eligible agent-days or τ_boot unresolved (CI spans > ×10). Card expectation (P1′, credence 0.7): K_boot > 2 (the boot outlives the call-clock prediction).

## Result
Period pool (random effects over units): **τ_boot = 19.7 [0.1, 2671.3] calls**; τ_pred (HH form, median over units) = 1.10 calls; **K_boot = 18.1 [0.2, 2065.0]**; m(0) − m_∞ amplitude A = +0.039, m_∞ = 0.046; one-exponential CV gain of the double exponential (median) = 0.006.

| Unit | agent-days | K_max | τ_boot calls [95%] | ρ_self | τ₀ | g_lag | τ_pred | K_boot [95%] | K_AR | CV gain (2-exp) | resolved days |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 36a | 12 | 400 | 1.2 [0.5, 2.5] | 0.122 | 1.00 | -0.060 | 0.94 | 1.2 [0.5, 2.7] | 1.2 | 0.007 | 0 |
| 36b | 24 | 400 | 19.4 [0.2, 2000.0] | -0.030 | 1.00 | 0.094 | 1.10 | 17.6 [0.2, 1857.6] | 19.4 | 0.006 | 0 |
| 36c | 24 | 400 | 2000.0 [0.2, 2000.0] | -0.061 | 1.00 | 0.151 | 1.18 | 1697.4 [0.2, 1765.1] | 2000.0 | -0.008 | 0 |

Data: `data/processed/H121-daily-boot-quench/results/units.parquet`, `days.parquet`.

*Post hoc (labelled; card "Post hoc")*: first-call excess over the k = 20–60 plateau e(0) = 0.16 [0.02, 0.34]; fast relaxation τ_fast = −1/ln[e(1)/e(0)] = 1.30 [0.00, 3.40] calls (K_fast = 1.18); slow excess over the steady state at k = 20–240: 0.13 [-0.12, 0.36].

## Scorecard (period-specific axes)
C, D (K_boot against the unfitted prediction).

## Notes
