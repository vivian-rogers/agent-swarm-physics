# H130 × NE41: Forced context erasure at the 41-turn cap, inside #51 (non-holdout days 2026-07-06 → 2026-09-04)

**Verdict:** mixed
**Role:** exploratory
**Period:** regime III · #51 units 51a–51l · forced context segments of 40 calls (H44), so every lag longer than 40 calls crosses at least one forced erasure; lags of 4–39 calls cross one or none depending on the position in the segment, which the scaffold sets.

## Why this period
NE41 erases the context window at a time set by the scaffold, not the agent. The OU picture puts the agent's state in its well-anchored content (the statement it is producing tracks x_i, which persists). The rival R1 puts a read's kick in the context window: when the window is erased, the kick goes with it. At a matched lag of 4–39 calls, whether a forced erasure falls between two events is close to random. That is a quasi-intervention on the context channel inside one period.

## Prediction
*Written 2026-10-04 22:21–22:22 UTC, before running on this period.*
- **Estimator.** For lag bins 4–7, 8–15, 16–31 and 32–39 calls, split the O1 own-autocorrelation pairs and the O2 kick pairs by whether a forced reset (`reset_forced`) of the agent lies strictly between the two calls. Per bin: ratio R_C = C_cross/C_within and R_K = K_cross/K_within; pooled across bins by inverse-variance weighting on the log scale where both are positive, with agent-day bootstrap CIs (pooled #51 units).
- **OU prediction:** R_C ≥ 0.5 and R_K ≥ 0.5 (no step at the erasure beyond noise; ideal 1). **Credence 0.6** for R_C (H46: content does not move at erasures; H109: room alignment survives erasure), **0.4** for R_K (H08: erasure cuts coupling to pre-erasure senders by 18% ± 6% in talk).
- **Against (R1, context-held state):** R_K < 0.5 with CI below 0.5 (the kick is held in the context); R_C < 0.5 with CI below 0.5 (the agent's content persistence itself is context-held, which would make γ_auto a context rate rather than a well rate).
- Voluntary consolidations (`reset_consol` without `reset_forced`) are reported as a descriptive second arm (the agent chooses their timing, so they are not quasi-random).

**A1 note (22:48 UTC, before running):** R_C uses the drive-corrected autocorrelation and R_K the sender-specific dose coefficients (reads 4–15 and 16–39 calls before B, split by an intervening forced reset).

## Result
*Run 2026-10-04 23:10 UTC; pooled #51 non-holdout units, agent-day bootstrap stratified by unit (B = 200).*

| Statistic | bge | gte | OU prediction | Outcome |
| --- | --- | --- | --- | --- |
| R_C (own content memory across a forced erasure, lag 4–39 calls) | 1.03 [0.95, 1.10] | 1.00 [0.91, 1.07] | ≥ 0.5 | **supported** |
| R_K (kick across a forced erasure, lag 4–39 calls) | −0.45 [−2.22, 0.85] | 0.06 [−1.49, 2.09] | ≥ 0.5 | undefined |

The kick has decayed before lag 4 (within-segment dose coefficients 4–15 calls ≈ 0.0004, 16–39 ≈ 0), so the ratio has no denominator. The agent's own content memory crosses a context erasure unchanged: it is not held in the context window (H46, H109 agree). Where the fast kick lives (context or not) is not testable at this lag.

## Scorecard (period-specific axes)
E 1 (erasure leaves own memory intact; kick part unidentified).

## Notes
- 2026-10-04 22:21 UTC: folder created; prediction written before any H130 statistic.
- 2026-10-04 23:13 UTC: results added.
