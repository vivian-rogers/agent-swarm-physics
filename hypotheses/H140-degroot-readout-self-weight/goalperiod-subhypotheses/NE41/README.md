# H140 × NE41: forced context erasures at the 41-turn cap (regime III, from 2026-03-24)

**Verdict:** pending
**Role:** exploratory (native N1)
**Period:** every non-reserved regime-III unit (#37–#42, #44, 51a–51l). The cap erases the context at a time set by the scaffold, not the agent (`natural-experiments.md`: ~18.6k forced vs ~12.2k voluntary events on non-reserved days).

## Why this natural experiment
A forced erasure drops the agent's own share of its context to near 0 at an exogenous time: the first post-reset call holds one own turn and whatever items arrive. HH383 then predicts that the agent's pre-reset content loses its weight in the next statement, so the statement moves toward what it reads. R-well (H130) predicts no change.

## Prediction
*Written 2026-10-07 ~10:50 UTC, before running. Seen beforehand (this native is not blind): content does not move at forced erasures (H46: T 0.51 in both models); own content memory survives (H130: R_C 1.03 [0.95, 1.10]); pull toward new items does not rise after a wipe (H44: D −0.026 [−0.064, 0.012]; G51 −0.027 [−0.047, −0.007]).*
- **N1 (HH383):** Δŵ_self / Δs_self ∈ [0.5, 1.5] at the first post-reset talk call vs talk calls at segment position ≥ 5. Credence 0.1.
- Counts against: Δŵ_self CI includes 0 while Δs_self is large (R-well).
- Voluntary consolidations (`reset_consol` without `reset_forced`) are reported as a secondary arm (the agent chose the time).

## Result
Not run.

## Scorecard (period-specific axes)
E, H: not run (all 0).

## Notes
- Because the three prior results above were seen, a failure here is expected and is weak new evidence; a pass would be strong.
