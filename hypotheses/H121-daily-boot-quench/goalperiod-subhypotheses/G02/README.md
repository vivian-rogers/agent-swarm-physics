# H121 × G02: goal period #2

**Verdict:** descriptive
**Role:** replication (exploratory)
**Period:** goal #2 · regime I · mean N 3.5 · units 2 · 2 unit-days, 7 eligible agent-days (boot replicas).

## Why this period
Eligible for the replication layer: every non-holdout unit with eligible agent-days (≥ 30 receiving calls). Each agent-day is one replica of the daily boot quench.

## Prediction
*Written 2026-10-04 22:20 UTC, before running on this period (the card's rule, written 22:00 UTC).* H67's read-out gain for this period is g_lag = 0.021 [-0.081, 0.124], so mean-field Glauber predicts τ_boot = τ₀ × 1.02 (τ₀ = max(1, −1/ln ρ_self) calls, measured on this period's steady-state calls). **Supported** if the pooled K_boot = τ_boot/τ_pred (HH form) has its point estimate in [0.5, 2] with a CI overlapping the band and the one-exponential test passes; **failed** if K_boot's CI lies entirely outside [0.5, 2]; **mixed** otherwise; **descriptive** if < 8 eligible agent-days or τ_boot unresolved (CI spans > ×10). Card expectation (P1′, credence 0.7): K_boot > 2 (the boot outlives the call-clock prediction).

## Result
Unit 2 has 7 eligible agent-days (< 8), so no fit was made (card rule: descriptive).

## Scorecard (period-specific axes)
C, D (K_boot against the unfitted prediction).

## Notes
