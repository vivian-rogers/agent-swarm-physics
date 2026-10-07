# H139 × NE41: forced context erasures at the 41-turn cap (regime III, from 2026-03-24)

**Verdict:** pending
**Role:** exploratory (native N1)
**Period:** every non-reserved regime-III unit (#37–#42, #44, 51a–51l). The cap erases the context at a time set by the scaffold, not the agent (~18.6k forced vs ~12.2k voluntary events, non-reserved; `natural-experiments.md`).

## Why this natural experiment
If the fast part of content is held in the context window (the context-held kick, H130's R1 world), it should vanish across a forced erasure while the slow, well-held part passes through. H130 found the slow part survives (R_C 1.03 [0.95, 1.10]) but could not measure the kick across an erasure (it had decayed before lag 4 of its dose design). An autocovariance at lags 1–7 calls across a reset can see the fast part directly.

## Prediction
*Written 2026-10-07 ~10:00 UTC, before running. Seen: H130's R_C and R_K; H44's coupling cut to pre-erasure items (ratio 0.60 [0.44, 0.81]) and no rise of content pull toward new items (D −0.026 [−0.064, 0.012]); H46's content T 0.51 at erasures.*
- **N1:** R_fast < 0.5 and R_slow ≥ 0.8. Credence 0.3.
- Counts against: R_fast ≥ 0.8 (the fast part is not context-held).
- If the fast part is below resolution in a unit (synthetic S1), N1 is untestable there.

## Result
Not run.

## Scorecard (period-specific axes)
E, H: not run (all 0).

## Notes
- Pairs crossing a voluntary consolidation (`reset_consol` without `reset_forced`) are a secondary arm: the agent chose the timing, so it is not an exogenous cut.
