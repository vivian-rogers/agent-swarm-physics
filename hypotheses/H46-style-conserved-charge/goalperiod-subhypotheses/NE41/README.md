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

## Round 2 (2026-10-05)
**Round-2 result:** the erasure effect on style survives genre and position control (R1-P1 passed); function words move less (R3-P2 passed, marginal); the OU drift-and-reset form fails (R2 kill fired), a reset-and-hold offset fits (post hoc).
*Pre-registered in the card (Round 2, 2026-10-05 02:44 UTC), synthetic validation and amendments R2-A1..A5 before this run; `analysis/r2_run.py` → `data/processed/H46-style-conserved-charge/r2/`. Non-reserved data.*
- **Predictions (R1-P1, R3-P2, R2-P1..P3):** T_s(gp) ≥ 0.54 with cluster CI > ½; function words T_fw ≤ 0.53 or CI ∋ ½; variance growth Δ̄ > 0, ΔC(1) > 0 with OU decay, self-pull within > erased.
- **Estimator change (R2-A5):** pair distances are scaled by the agent × unit median within-pair distance (most pairs fall into agent-free strata; unscaled null T is 0.507 for style, 0.530 for function words).

| Channel (forced pairs, scaled) | T [agent-cluster 95% CI] | unscaled (round-1 method) | voluntary |
| --- | --- | --- | --- |
| style, round-1 type control (tc) | 0.547 [0.522, 0.566] | 0.564 | 0.549 |
| style, genre-controlled (g) | 0.545 [0.520, 0.563] | 0.560 | 0.546 |
| **style, genre + position (gp)** | **0.546 [0.522, 0.564]** | 0.561 | 0.546 |
| style gp, genre-matched strata | 0.545 [0.519, 0.566] | – | 0.539 |
| function words (≥ 10 tokens) | 0.528 [0.501, 0.553] | 0.558 | 0.518 |
| content bge | 0.513 [0.485, 0.537] | 0.515 | 0.517 |
| content gte (second model) | 0.510 [0.487, 0.535] | – | 0.511 |

- **Per unit (gp, forced, ≥ 30 pairs):** 36c 0.63, 37 0.63, 38a 0.61, 38b 0.71, 39 0.56, 40 0.58, 41 0.61, 42b 0.60, 44a 0.51, 44b 0.47, 51a 0.52, 51b 0.46, 51c 0.53, 51d 0.52, 51e 0.53, 51f 0.55, 51g1 0.55, 51g2 0.48, 51h 0.48, 51i 0.58, 51j 0.48, 51k 0.56, 51l 0.53. Two-room periods #36–#42: 0.56–0.71; #44 and #51: 0.46–0.58.
- **Per unit (function words):** 36c 0.51, 37 0.56, 38a 0.54, 38b 0.60, 39 0.62, 40 0.65, 41 0.58, 42b 0.52, 44a 0.41, 44b 0.52, 51a 0.49, 51b 0.55, 51c 0.51, 51d 0.49, 51e 0.53, 51f 0.53, 51g1 0.53, 51g2 0.44, 51h 0.45, 51i 0.56, 51j 0.53, 51k 0.62, 51l 0.51.
- **Drift and reset (R2, regime III pooled, gp):** variance growth Δ̄ 0.25 [-0.16, 0.59] (fails); ΔC(1) 0.70 [0.26, 1.11] (> 0), but ΔC(l) does not decay over l = 1…8 (φ_C 1.14 > 1); self-pull ρ in context 0.36 vs erased 0.22, difference 0.145 [0.086, 0.184].
- **Post hoc (PH-R2a):** ΔC(1) is already 0.64 [0.35, 0.95] for the first message after a reset: the context state is set at the segment start and held, as in a synthetic per-segment offset (≈ 4–5% of the per-message style variance), not grown from zero.
- **Post hoc (PH-R3b), per lab, gp:** Anthropic 0.54, OpenAI 0.55, Google 0.62, DeepSeek 0.61, other 0.53 (Anthropic CI includes ½).
