# H139 × NE41: forced context erasures at the 41-turn cap (regime III, from 2026-03-24)

**Verdict:** descriptive. N1 is untestable (S1 fired in every unit; S3 failed); R_slow 1.06 [0.98, 1.14] is reported descriptively.
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
*Run 2026-10-07 14:32 UTC (exploratory, non-reserved). Pairs at lags 1–7 (R_fast) and 32–255 calls (R_slow) crossing a forced reset vs within a segment, matched per agent-day and lag bin, in all 15 testable regime-III units. N1 is untestable: S1 fired in every unit, and the synthetic S3 failed (R_fast separates a context-held kick from a well-held one in 37–59% of replicates, not ≥ 80%).*

| Unit | R_fast | R_slow |
| --- | --- | --- |
| 37 | -1.90 | 1.32 |
| 38a | 3.30 | 1.18 |
| 38b | 0.25 | 0.87 |
| 38e | -2.14 | 0.57 |
| 39 | -37.75 | 1.25 |
| 40 | -4.75 | 1.00 |
| 41 | 1.44 | 1.50 |
| 42b | 1.55 | 1.78 |
| 51a | -0.59 | 1.12 |
| 51c | -0.51 | 0.97 |
| 51d | -5.47 | 1.71 |
| 51e | 0.17 | 1.11 |
| 51f | -10.34 | 1.12 |
| 51g | 1.05 | 0.95 |
| 51h | 0.77 | 1.31 |

| Prediction | Observed | Verdict |
| --- | --- | --- |
| N1 R_fast < 0.5 and R_slow ≥ 0.8 | R_fast pooled 1.28 [0.58, 1.98]; R_slow pooled 1.06 [0.98, 1.14] (I² 0.12) | untestable; descriptive |

Descriptive reading: the slow part of own content passes a forced erasure unchanged (R_slow ≈ 1), as H130's R_C 1.03 found in #51 alone. Synthetic check of R_fast at a resolvable size (A = 3, added): it separates the two worlds only in 51g.

## Scorecard (period-specific axes)
E 1 (slow part passes erasures, descriptive; fast part untestable). H 0.

## Notes
- Pairs crossing a voluntary consolidation (`reset_consol` without `reset_forced`) are a secondary arm: the agent chose the timing, so it is not an exogenous cut.
