# H10 × G16: Choose your own goal! (2025-10-06 → 2025-10-10)

**Verdict:** descriptive (F1 ✗ by BIC, F2 ≈ 0.5, F3 ✓)
**Verdict (1b):** descriptive (both models)
**Role:** exploratory
**Period:** regime I · mode F · 7 agents · #general only · 5 active days (30 windows). No step change inside.

## Why this period
Free week before an individual-objective week (#17, mode I): the cleanest test of P1, since each agent's push should depend on its own fluctuations and not on coordination. In H10 a free week supplies the field-free distribution P_F(m) along the *next* week's goal direction; the test itself is the transition, in [`../NE34/`](../NE34/README.md) (exception (c)).

## Prediction
*Written 2026-10-03, before running on this period.* Card observables along ĝ of #17 (personal websites), segment = all active days.
- **F1, single well.** The noise-deconvolved per-agent and swarm F̂(m) along ĝ_next are unimodal; the pooled standardized skewness |γ_F| < 1. (A double well here would mean the free week already splits into on- and off-goal states.)
- **F2, weak coupling.** Mean-field loop gain along ĝ_next g_F < 0.5 (as in H01 P9, H02, H05).
- **F3, stationarity (axis B).** No trend in the daily mean of δm along ĝ_next (day-block slope CI contains 0); signal variance not dominated by a single day.
- **Verdict rule:** descriptive (this period carries no test of its own). It is set to "descriptive" once F1–F3 are reported; a failure of F3 is a caveat on the pair test.

## Result
Run 2026-10-03 (along ĝ₁₇, n = 32, 7 agents, 30 windows).

| Prediction | Observed (90% CI) | Reference | Verdict |
| --- | --- | --- | --- |
| F1 single well, \|γ\| < 1 | γ = −0.30, excess kurtosis −0.5; BIC prefers 2 components | Gaussian | ✗ by BIC (skew OK) |
| F2 g < 0.5 | g = 0.51 [0.03, 0.69]; g⊥ = 0.42 | | ✗ (point estimate at the threshold; CI wide) |
| F3 no drift | slope −0.000 [−0.016, 0.016] | 0 | ✓ |

Data: `data/processed/H10-goals-are-legendre-pushes/G16/period.json`. Figure: [`figures/shape_and_drift.pdf`](figures/shape_and_drift.pdf) (standardized agent-window deviations along ĝ and the daily mean alignment). Card: [`../../README.md`](../../README.md); the pair test is in [`../NE34/`](../NE34/README.md).

## Scorecard (period-specific axes)
- **B:** stationarity holds along ĝ₁₇.
- **C/D:** none.

## Notes

## Round 1b (improved data, 2026-10-04)
*Inputs: shared goal fields (`goal_fields`; H10's own goal and kickoff vectors already matched them to cos ≥ 0.9999999, so bge numbers are unchanged), the second embedding model gte-modernbert, DQ5 restatement dedupe and style-residualized vectors. Data: `data/processed/H10-goals-are-legendre-pushes/r1b/<config>/`. Role: replication (the round-1 estimator, unchanged).*

bge identical (γ −0.30, g 0.51, stationary). gte: γ −0.24, single well, g 0.37 [−0.25, 0.58], stationary (+0.003/day).
