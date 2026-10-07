# H140 × NE41: forced context erasures at the 41-turn cap (regime III, from 2026-03-24)

**Verdict:** mixed
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
Data: `data/processed/H140-degroot-readout-self-weight/G<NN>/` (rows with `pmode = xreset`), results `results/ne41.json`. Run 2026-10-07 on exploration data. **This native is not blind:** H46, H130 and H44 had already shown that content does not move at forced erasures (see Prediction).

Design: first talk call after a reset (no own statement yet in the new segment; p and its instrument z from the erased segment) vs talk calls at segment position ctx_pos ≥ 5 (p in context). Fit: A1 spec with a first-call indicator on p (`firstA1`). Units with ≥ 30 first calls; DL pool over units. Forced arm: 18 units, 1,783 first calls. Voluntary arm: 16 units, 1,999 first calls.

| Quantity | bge | gte | Verdict |
| --- | --- | --- | --- |
| Δs_self (first − control; call-weighted mean over units) | −0.099 | −0.099 | small: the call-entry share does not drop to ≈ 0 at a reset (ctx_pos and k_ctx both restart) |
| Δŵ_self (forced) | −0.028 [−0.085, 0.029] | −0.054 [−0.096, −0.012] | |
| **N1 ratio Δŵ_self / Δs_self ∈ [0.5, 1.5]** | 0.29 (CI from Δŵ: [−0.29, 0.86]) | 0.55 ([0.12, 0.97]) | **failed (bge) / supported (gte): mixed** |
| Self-weight on in-context p (control rows) | 0.96 [0.54, 1.38] | 0.74 [0.41, 1.08] | |
| Voluntary arm Δŵ_self | −0.024 [−0.067, 0.019] | −0.027 [−0.065, 0.012] | ratio 0.18 / 0.20 |

- The counts-against condition ("Δŵ_self CI includes 0 while Δs_self is large") cannot be applied cleanly: Δs_self is only −0.10, so the rule's lever is weak. The card assumed the self-share drops to near 0; under the call-entry definition it does not.
- **Post hoc reading (not a registered test):** content that the reset removed from the context keeps 97% (bge) or 93% (gte) of the weight of in-context content in the next statement (Δŵ −0.03/−0.05 against a base of 0.96/0.74). A literal DeGroot average over context contents would give erased content zero weight. This agrees with H130 (R_C 1.03) and H46: the self-weight lives outside the context window (R-well).

## Scorecard (period-specific axes)
E 1 (the erasure is exogenous; the result favours R-well, but the native is not blind and the registered ratio splits by model), H 1 (R-well beats HH383 on the post hoc reading).

## Notes
- Because the three prior results above were seen, a failure here is expected and is weak new evidence; a pass would be strong.
