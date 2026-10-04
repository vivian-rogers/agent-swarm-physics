# H109 × NE41: forced context erasures at the 41-call cap (regime III, non-holdout multi-room periods)

**Verdict:** failed
**Role:** exploratory (native)
**Period:** regime III · the scoped multi-room periods (G36–G44, 51g) · NE41 forced erasures (exogenous timing) and voluntary consolidations (agent-chosen).

## Why this period
NE41 is the scrambling intervention itself. This folder holds the two native contrasts that are about the erasure rather than one period: forced vs voluntary erasures, and the random-effects summary of δ_F across periods (named exception (d): per-period CIs are wide; partial pooling reported next to the per-period estimates).

## Prediction
*Written 2026-10-04 21:31 UTC, before running.*
- P1 pooled: δ_F ≥ 0.30 with CI > 0 under HH339; my expectation is the kill: the random-effects δ_F's CI upper bound < 0.30 with synthetic power ≥ 0.8 [0.75].
- P5: δ_V within 0.15 of δ_F [0.5].
- P4 (R-fast): any drop concentrates in statements produced before any room item was read [0.5].
- P6 (self-copy): δ_F(no dedupe) − δ_F(dedupe) ≥ 0 [0.6].
- Counts against my expectation: a pooled δ_F ≥ 0.30 with CI lower > 0 in both models.

## Result
*Run 2026-10-04 (`analysis/run.py`, `analysis/report.py`; non-holdout).*

| Statistic (pooled over 8 periods) | bge | gte |
| --- | --- | --- |
| δ_F random-effects mean [95% CI] | -0.08 [-0.23, 0.06] (I² 0.35) | -0.07 [-0.17, 0.03] |
| δ_V voluntary, RE | -0.04 [-0.13, 0.06] (I² 0.00) | -0.08 [-0.19, 0.02] |
| δ_K kickoff, RE | 0.08 [-0.12, 0.28] (I² 0.00) | -0.03 [-0.20, 0.13] |
| δ_F direct pooled stratified | -0.12 [-0.21, -0.03] | -0.08 [-0.16, -0.00] |
| δ_F RE, no dedupe | -0.08 [-0.16, 0.00] | -0.10 [-0.17, -0.03] |
| δ_F RE, copies dropped | -0.07 [-0.16, 0.02] | -0.09 [-0.18, 0.01] |
| δ_F RE, first statement only | -0.08 [-0.20, 0.05] | -0.04 [-0.14, 0.06] |
| δ_F RE, no agent constant / white32 (bge) | -0.08 [-0.25, 0.10] / -0.07 [-0.18, 0.04] | – |
| R-fast: δ_F for post statements with R = 0 (n F) | -0.10 [-0.24, 0.02] (300) | -0.05 [-0.17, 0.07] |
| R-fast: δ_F for post statements with R > 0 (n F) | -0.11 [-0.19, -0.03] (3330) | -0.08 [-0.15, 0.01] |
| κ_R after forced erasures [CI]; κ_R − κ_U [CI] | 0.019 [0.003, 0.034]; 0.025 [0.003, 0.046] | 0.017 [0.001, 0.033]; 0.026 [0.004, 0.050] |
| κ_R after voluntary erasures [CI]; κ_R − κ_U [CI] | 0.033 [0.015, 0.049]; 0.042 [0.019, 0.063] | 0.025 [0.004, 0.044]; 0.034 [0.007, 0.060] |
| synthetic null 95th pct of κ_R; κ_R − κ_U (A1) | 0.014; 0.020 | 0.018; 0.023 |

**Verdict:** failed (HH339's kill fires: the pooled δ_F CI upper bound is below 0.30 in both models, synthetic power 1.00). P5 holds (δ_V within 0.15 of δ_F). Reading adds a small pull (κ_R ≈ 0.02 per e-fold of items, above the null 95th percentile in bge, at it in gte), but no drop exists for it to recover.

## Scorecard (period-specific axes)
- **C:** W-boundary placebo; kickoff control; posted-unread placebo.
- **E:** 3,477 forced erasures (exogenous) and 2,559 voluntary.
- **F:** pooled power 1.00 at δ = 0.30; size 0.00.
- **H:** R-art / R-prior (no drop) beat R-ctx; R-fast and R-loop moot.

## Notes
- 2026-10-04 21:31 UTC: folder and prediction written before any H109 statistic.
