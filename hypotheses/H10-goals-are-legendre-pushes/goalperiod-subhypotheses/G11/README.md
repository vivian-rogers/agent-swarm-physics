# H10 × G11: Pursue whatever you'd like to (2025-08-25 → 2025-08-29)

**Verdict:** descriptive (F1 ✗ by BIC, F2 ✗ marginal, F3 ✗ drift)
**Verdict (1b):** descriptive (both models)
**Role:** replication (exploratory)
**Period:** regime I · mode F · 7 agents · #general only · 5 active days (30 windows of 30 min). No step change inside.

## Why this period
Free week before an operator-set team debate (#12, mode M). Its fluctuations along ĝ₁₂ are the F(m) for the first exploratory pair. In H10 a free week supplies the field-free distribution P_F(m) along the *next* week's goal direction; the test itself is the transition, in [`../NE34/`](../NE34/README.md) (exception (c)).

## Prediction
*Written 2026-10-03, before running on this period.* Card observables along ĝ of #12 (debate teams), segment = all active days.
- **F1, single well.** The noise-deconvolved per-agent and swarm F̂(m) along ĝ_next are unimodal; the pooled standardized skewness |γ_F| < 1. (A double well here would mean the free week already splits into on- and off-goal states.)
- **F2, weak coupling.** Mean-field loop gain along ĝ_next g_F < 0.5 (as in H01 P9, H02, H05).
- **F3, stationarity (axis B).** No trend in the daily mean of δm along ĝ_next (day-block slope CI contains 0); signal variance not dominated by a single day.
- **Verdict rule:** descriptive (this period carries no test of its own). It is set to "descriptive" once F1–F3 are reported; a failure of F3 is a caveat on the pair test.

## Result
Run 2026-10-03 (along ĝ₁₂, n = 32, 7 agents, 30 windows).

| Prediction | Observed (90% CI) | Reference | Verdict |
| --- | --- | --- | --- |
| F1 single well, \|γ\| < 1 | γ = −0.51, excess kurtosis −1.5; BIC prefers 2 Gaussian components for the standardized deviations | Gaussian | ✗ (flat-topped / two-component; skew OK) |
| F2 g < 0.5 | g = 0.55 [0.21, 0.64]; transverse median g⊥ = 0.53 | H01 P9, H02/H05 loop gains | ✗ (marginal) |
| F3 no drift | daily slope −0.018 [−0.030, −0.006] per day | 0 | ✗ (alignment with ĝ₁₂ drifts *down* across the free week) |

Data: `data/processed/H10-goals-are-legendre-pushes/G11/period.json`. Figure: [`figures/shape_and_drift.pdf`](figures/shape_and_drift.pdf) (standardized agent-window deviations along ĝ and the daily mean alignment). Card: [`../../README.md`](../../README.md); the pair test is in [`../NE34/`](../NE34/README.md).

## Scorecard (period-specific axes)
- **B (stationarity):** fails for this segment (drift along ĝ₁₂).
- **C/D:** none (this period carries no test of its own).

## Notes
- 2026-10-03: the drift violates the stationarity assumption of the pair test's free-week F(m). The variance estimate along ĝ₁₂ includes this slow trend, which, if anything, *inflates* κ2^F (making the tilt's predicted variance larger, not smaller).

## Round 1b (improved data, 2026-10-04)
*Inputs: shared goal fields (`goal_fields`; H10's own goal and kickoff vectors already matched them to cos ≥ 0.9999999, so bge numbers are unchanged), the second embedding model gte-modernbert, DQ5 restatement dedupe and style-residualized vectors. Data: `data/processed/H10-goals-are-legendre-pushes/r1b/<config>/`. Role: replication (the round-1 estimator, unchanged).*

bge (shared goals) identical to round 1: γ −0.51, BIC prefers 2 components, g 0.55 [0.21, 0.64], drift −0.018/day [−0.032, −0.005]. gte: γ −0.48, single well (F1 ✓), g 0.41 [−1.64, 0.63], no drift (−0.001 [−0.020, +0.018]). The round-1 stationarity failure of #11 (F3) is not reproduced in gte.
