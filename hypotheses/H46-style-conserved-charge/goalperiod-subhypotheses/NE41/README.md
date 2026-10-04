# H46 × NE41: forced context erasures (turn level)

**Verdict:** failed
**Role:** native (exploratory)
**Events:** regime III non-holdout consolidations (DQ1 `context_ledger_turns`).

## Why this NE
Thousands of exogenously timed erasures of the context window, memory kept. If an agent's style is held in its context (self-imitation), an erasure resets it; if it is in the weights, nothing happens. Content, which lives in the context, should move.

## Prediction
*Written 2026-10-04 05:45 UTC, before running on these events (card P2).*
- **Design:** consecutive eligible chat messages of one agent on one PT day (regime III, non-holdout). *Forced* pairs straddle exactly one forced consolidation (DQ1 rule: the closed segment has 41–42 records), *voluntary* pairs one voluntary consolidation, *within* pairs no reset. Each crossing pair is ranked among within pairs of the same agent, unit and time-gap bin (0.25 decades), which removes the recency confound.
- **Prediction:** content moves beyond within-context pairs (T_c in 0.53–0.65); style conserved (|T_s − ½| ≤ 0.03; turn-level margin 0.05). Voluntary consolidations shift content more than forced ones.
- *Falsifier:* T_s ≥ 0.55 with p < 0.05 (in-context self-imitation: style is partly held by the context window, R1).

## Result
*Run 2026-10-04 06:08 UTC; `analysis/ne41.py` → `data/processed/H46-style-conserved-charge/NE41/ne41.json`.*

Pairs: 7,312 forced, 7,214 voluntary, 32,055 within (median gaps 638 s / 475 s / 90 s).

| Channel | forced: T [95% CI] | voluntary: T [95% CI] | forced, gap-unmatched |
| --- | --- | --- | --- |
| style, type-controlled (primary) | 0.564 [0.513, 0.609] | 0.535 [0.474, 0.585] | 0.526 |
| style, raw | 0.568 [0.525, 0.607] | 0.546 [0.490, 0.594] | 0.533 |
| content, style-residualized (primary) | 0.515 [0.486, 0.538] | 0.512 [0.479, 0.540] | 0.483 |
| content, raw whitened | 0.518 [0.487, 0.541] | 0.511 [0.478, 0.537] | 0.485 |

- **Per unit (forced, ≥ 30 pairs):** style T > ½ in 18/23 units (regime III two-room periods 0.49–0.64; late #51, 51h–51l, 0.45–0.57); content T > ½ in 17/23 (content moves in #36–#42, 0.53–0.61, but not in #51, 0.42–0.54, which holds most pairs).
- **All messages (no self-repeat removal):** forced style 0.581, content 0.523.
- **Holm (six classes):** style p = < 0.001, content p = < 0.001; content's agent-cluster CI includes ½, so by Amendment 2 content does not move.
- **Pre-registered verdict:** **broken**: style moves across a forced erasure (falsifier T_s ≥ 0.55 hit), content does not.
- **Post hoc (PH3): style drifts inside a context and resets at erasure.** Excess squared distance of a message's style to the agent's unit mean, by its position since the last reset, within segments of ≥ 7 messages: pos 1 -2.31 (± 0.57), pos 2 -1.61 (± 0.58), pos 3 -0.69 (± 0.58), pos 4-6 -0.02 (± 0.35), pos 7+ +1.12 (± 0.39). Content shows only a small first-message dip (-0.018 in 1 − cos).
- **Post hoc (PH2):** the excess sits in conversational-register features: at 14%, emdash 13%, emoji 12%, ques 12%, excl 11%, bullet_share 10%.

## Scorecard (period-specific axes)
- **E (interventional):** 1. Exogenously timed erasures are the cleanest intervention here; the prediction (style conserved) failed, which is informative: style is partly held by the context window.
- **F:** 1 (gap-matched estimator validated on an OU recency confound; Amendment 2).
- **B:** in-context drift (PH3) is a Markov-order statement: style depends on context length, not only on the agent.

## Notes
- 2026-10-04 06:02 UTC, Amendment 2 (after the synthetic validation, before this run): the gap strata are 0.05 decades, not the 0.25 written in the prediction above. With 0.25-decade bins a pure recency process (no jump) gave T_c = 0.509 and false "content moves" in 58–70% of synthetic replicates; with 0.05-decade bins T_c = 0.499 and 0/30. "Moves" also requires the agent-cluster bootstrap lower bound > ½.
