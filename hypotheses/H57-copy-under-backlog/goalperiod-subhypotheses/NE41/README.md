# H57 × NE41: forced context erasures reset the context load (regime III, non-holdout)

**Verdict:** failed (at fixed backlog, statements right after a forced erasure copy neither less nor more than right before it; context load has no positive slope)
**Role:** native
**Period:** regime III non-holdout goal periods #36–#42, #44, #51 (units 51a–51l). At the 41-turn cap the scaffold erases the context window (memory kept) at a time set by the scaffold, not the agent: ~21k forced vs ~16k voluntary consolidations (DQ1 ledger, non-holdout).

## Why this period
The backlog k counts what arrived since the agent last spoke; the context load k_ctx counts everything in the window since the last reset. A forced erasure sets k_ctx to ≈ 0 at a quasi-random time while leaving the conversation (and k) untouched. If copying is a response to load on a bounded context, statements just after an erasure, at the same backlog, should copy less. If agents echo recent messages to re-orient after losing their context, they should copy more.

## Prediction
*Written 2026-10-04 07:09 UTC, before running H57 on these periods.*
- **N41a:** within agent × unit, comparing statements in the first three receiving calls after a forced erasure with those in the last three calls before one (same day), at fixed log k and the card's controls, the after-erasure coefficient on the chance-corrected echo (bge and gte) and marker near-copy is < 0 (random-effects pooled over periods).
- **N41b:** in all computer-use statements, the slope on log₂(1 + k_ctx) at fixed log k is > 0 (pooled).
- **Comparison:** voluntary consolidations (agent-timed) give the same contrast with a timing confound. A forced–voluntary difference would point to the agent choosing when to consolidate.
- **Against:** after-erasure coefficient ≥ 0 (> 0 = the reorientation reading).

## Result
*Run 2026-10-04 (non-holdout). Numbers: `data/processed/H57-copy-under-backlog/results/native_NE41.json`. Figure: [figures/ne41_after_before.pdf](figures/ne41_after_before.pdf).*

Statements in the first three receiving calls after a forced erasure vs the last three before one (same day), within agent × unit, at fixed log k and the card's controls; 9 regime-III periods (#51: 1,310 after, 1,401 before; the others 30–200 per side). Random-effects pooled over periods.

| Native prediction (dated) | Observed (pooled, 95% CI) | Verdict |
| --- | --- | --- |
| N41a: after-erasure coefficient < 0 (echo bge, gte; marker near-copy), chance-corrected | bge +0.0002 [−0.0001, +0.0004] (p 0.19; 7/9 periods > 0); gte +0.0002 [−0.0001, +0.0004]; marker +0.0016 [−0.0003, +0.0035] (p 0.095) | not met (null, leaning positive) |
| N41b: slope on log₂(1 + k_ctx) at fixed k > 0 | bge −0.0005 [−0.0014, +0.0004]; gte −0.0007 [−0.0012, −0.0002] (p 0.005); marker +0.0007 [−0.0062, +0.0076] | not met |
| Post hoc: raw echo, after − before | bge +0.0001 [−0.0038, +0.0039] (4 periods with any echo) | null |
| Post hoc: lag-matched count, after − before | forced +0.0001 (p 0.09); voluntary +0.0004 [+0.0002, +0.0005] (p 0.0003) | null for forced; tiny positive for voluntary |

**Reading.** Erasing the context window at a scaffold-set time leaves copying unchanged at the same backlog, and a fuller context (larger k_ctx) does not raise it. Context load is not what drives echo. The small positive contrasts (markers; voluntary consolidations) lean towards the reorientation reading (re-reading recent messages after losing context) but are not significant for forced erasures.

## Scorecard (period-specific axes)
- **E (interventional):** 0. The predicted load effect is absent across the quasi-random erasures.

## Notes
- Forced erasures (41-turn cap) have quasi-random timing; voluntary ones are agent-timed and serve only as a comparison.
