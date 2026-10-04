# H23 × G44: Finetune your leader! (2026-05-26 → 2026-05-29)

**Verdict:** mixed
**Verdict (1b):** mixed (unchanged; copy_info and DQ6 checkpoints identical; P3a fails in both embedding models)
**Role:** exploratory
**Period:** regime III · mode C in #best (shared objective: fine-tune a leader), #rest free · 16 agents (+2 joined: Opus 4.8, the temporary leader) · rooms #best/#rest · 4 active days. Splits inside the period: the temporary leader ran four checkpoints (Qwen v3 05-26; Qwen v10 05-28 17:04; Kimi v2 / v4-curated56 05-28 20:04 / 20:07; **Kimi v7-aug-64 05-29 18:24:51**, the weights later used in #45). Only the last segment is the unit of analysis here.

## Why this period
The only non-holdout period with the fine-tuned leader in it, and the period in which its corpus was built, so corpus and live output can be compared directly. Goal-period ranking: model 08 first (`../../../hypohypotheses/goal-periods.md`; card: [`../../README.md`](../../README.md), #44).

## Prediction
*Written 2026-10-03, before any statistic was computed on real data; after reading the #44 #best transcript for the pipeline reconstruction (not blind; exploratory).* The card's P1–P4 applied to the 16 v7-aug-64 messages (05-29 18:24:51–20:27 UTC), controls = the 45 other agent messages in #best from 05-29 18:24:51 to 21:05 UTC (Kimi K2.6: 6), corpus = 31 recovered v7-aug-64 targets.
- **P1** corpus-distinctive n-gram rate: leader > controls (one-sided permutation p < 0.10) and > Kimi K2.6; bigram copy fraction: leader > controls.
- **P2** directive share: leader ≤ corpus − 0.25; JSD(leader, corpus) > 95th percentile of corpus self-resampling at n = 16; corpus → leader channel: excess c_plan ≤ 0.10 and I_transform > null (p < 0.10; expected underpowered).
- **P3** d_m = cos(z, z̄_C) − cos(z, z̄_B): leader > Kimi K2.6 and > controls (p < 0.10); Kimi field passes the split-half invariance check; then cos(h_L, h_C) > cos(h_L, h_K).
- **P4** R1 rejected if P1a and P3a hold; R2 rejected if the leader's conversational copy and lexical context copy ≤ the village's and its plan profile is closer to the corpus than to its contexts.
Decision rule: supported = predicted direction and p < 0.10; failed = opposite direction; else inconclusive.

## Result
*Run 2026-10-03 (`../../analysis/g44.py`; numbers in `data/processed/H23-leader-distillation-copy/G44/results.json`, `verdicts.json`, `results_sensitivity.json`, `hand_coding_sensitivity.json`). Figures: `figures/g44_lexical.pdf`, `figures/g44_plans.pdf`, `figures/g44_embedding.pdf`.*

| Prediction | Observed (95% CI) | Null / reference | Verdict |
| --- | --- | --- | --- |
| P1a corpus-distinctive n-grams | leader 14.2 [10.8, 18.1] per 100 tokens | controls 10.0 (p = 0.011); Kimi same window 12.1 (n = 6, p = 0.27); Kimi field 9.5 (p = 0.03); offline student 33.1 | supported |
| P1b corpus bigram copy | 0.064 [0.048, 0.083] | controls 0.055 (p = 0.17); corpus self-copy 0.33 | inconclusive |
| P2a plans not copied | directive share 0.62 (coder), 0.25 (hand, post hoc) | corpus 1.00; JSD 0.35 vs self p95 0.06 | supported |
| P2b plans transformed | excess plan copy −0.04; I_transform −0.03 bits (p = 0.65) | perfect-copy reference 0.23 / 0.19 bits | failed (not transmitted) |
| P3a closer to corpus than base | d 0.094 [0.019, 0.172] | controls 0.096 (p = 0.51); Kimi same window −0.03 (p = 0.08) | failed |
| P3b / P3c field level | Kimi split-half cos 0.53 < cross-agent max 0.64 | | invariance failed; P3c not evaluated |
| P4 rivals | R1 not rejected; R2 fits plans better than the corpus (JSD 0.15 vs 0.35) | | rivals stand |

Sensitivities: adding the 18 unplaced base-Kimi samples to the corpus (markers 16.7 vs 12.2, p = 0.01) or the two sibling Kimi checkpoints' messages (15.4 vs 10.0, p = 0.002) leaves every verdict unchanged, except P3a moving from failed to inconclusive. Negative control: the Qwen v10 checkpoint (different base, not trained on this corpus) shows no excess corpus vocabulary (13.5 vs 14.9, p = 0.71).

## Scorecard (period-specific axes)
- **C 1:** the vocabulary effect beats the same-window speaker null and the base-field null, not the same-window base (n = 6); plans and embedding do not beat their nulls.
- **D 1:** P2a held; the transformation signature is absent; lexical positive and negative controls behave.
- **E 0:** the in-period checkpoint switches were used only as a post hoc negative control.
- **G 1:** pipeline facts verified against commands and outputs; the embedding instrument fails its positive control.

## Notes
- 2026-10-03: plan acts in `messages.parquet` were first built with coder v1; rebuilt with the frozen v3 before the reported run.
- 2026-10-03: 3 of the 16 messages narrate the leader's own screen-mirror loop as if it were another agent; 6 contain status lines about a blocked push or pending tests, which the coder reads as GATE.
- 2026-10-03: the leader's 05-29 messages are interleaved with its own hands-on work in the training repo (89 bash turns). One of its turns printed a diff of the scenario-draft file (19:55:48 UTC, inputs only), after 15 of its 16 messages.
