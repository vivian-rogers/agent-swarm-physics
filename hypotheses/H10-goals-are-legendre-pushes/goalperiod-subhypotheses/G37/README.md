# H10 × G37: Pick your own goal! (2026-03-30 → 2026-04-01)

**Verdict:** descriptive (F1 ✓, F2 ✗, F3 ✓)
**Verdict (1b):** descriptive (both models)
**Role:** exploratory
**Period:** regime III · mode F · 12 agents (Claude Code agent not present) · #best / #rest · 3 active days (27 windows); statements are sparse (median 3 per agent-window).

## Why this period
The only non-holdout regime-III free week; it precedes a collaborative week (#38, mode C), where rival R5 (coupling change) predicts the loop gain should rise. In H10 a free week supplies the field-free distribution P_F(m) along the *next* week's goal direction; the test itself is the transition, in [`../NE34/`](../NE34/README.md) (exception (c)).

## Prediction
*Written 2026-10-03, before running on this period.* Card observables along ĝ of #38 (charity fundraiser), segment = all active days.
- **F1, single well.** The noise-deconvolved per-agent and swarm F̂(m) along ĝ_next are unimodal; the pooled standardized skewness |γ_F| < 1. (A double well here would mean the free week already splits into on- and off-goal states.)
- **F2, weak coupling.** Mean-field loop gain along ĝ_next g_F < 0.5 (as in H01 P9, H02, H05).
- **F3, stationarity (axis B).** No trend in the daily mean of δm along ĝ_next (day-block slope CI contains 0); signal variance not dominated by a single day.
- **Verdict rule:** descriptive (this period carries no test of its own). It is set to "descriptive" once F1–F3 are reported; a failure of F3 is a caveat on the pair test.

## Result
Run 2026-10-03 (along ĝ₃₈, n = 32, 12 agents, 24 windows; statements sparse).

| Prediction | Observed (90% CI) | Reference | Verdict |
| --- | --- | --- | --- |
| F1 single well, \|γ\| < 1 | γ = −0.11; BIC prefers 1 component | Gaussian | ✓ |
| F2 g < 0.5 | g = 0.62 [0.34, 0.70]; g⊥ = 0.56 | | ✗ |
| F3 no drift | slope 0.009 [−0.008, 0.024] | 0 | ✓ |

Data: `data/processed/H10-goals-are-legendre-pushes/G37/period.json`. Figure: [`figures/shape_and_drift.pdf`](figures/shape_and_drift.pdf) (standardized agent-window deviations along ĝ and the daily mean alignment). Card: [`../../README.md`](../../README.md); the pair test is in [`../NE34/`](../NE34/README.md).

## Scorecard (period-specific axes)
- **B:** stationarity holds; the excess-kurtosis estimate (−5.0) is unreliable at median 3 statements per agent-window (noise correction dominates).
- **C/D:** none.

## Notes

## Round 1b (improved data, 2026-10-04)
*Inputs: shared goal fields (`goal_fields`; H10's own goal and kickoff vectors already matched them to cos ≥ 0.9999999, so bge numbers are unchanged), the second embedding model gte-modernbert, DQ5 restatement dedupe and style-residualized vectors. Data: `data/processed/H10-goals-are-legendre-pushes/r1b/<config>/`. Role: replication (the round-1 estimator, unchanged).*

bge identical (γ −0.11, unimodal, g 0.62). gte: γ +0.35, unimodal, g 0.48 [0.19, 0.72], stationary.
