# H29 × G51c: Each agent: Maximize your assigned goal! (#focus) (2026-08-05 → 2026-08-24)

**Verdict:** mixed
**Role:** exploratory (counted)
**Period:** regime III · mode P · 27 recipients in the network · #general + #focus (2 agents moved) · 14 non-holdout days.

## Why this period
14 days with a two-agent side room: the cleanest small-vs-large room contrast for HH110's 'small rooms'.

## Prediction
*Written 2026-10-04 ~02:25 UTC, before running on this period.* Card predictions P1–P10 as they apply here:

P1: κ > 0 (credence 0.65). P5: split-half ≥ 0.4. P7b: the top driver is in #general, not #focus (a two-agent room holds < 10% of the swarm). P7c: per-recipient pull is higher in #focus.

## Result
| Prediction | Observed | Null / reference | Verdict |
| --- | --- | --- | --- |
| P1 net pull κ (pre-registered invisible placebo) > 0 | κ = -0.0273 [-0.0347, -0.0207]; field-corrected visible pull 0.0110, invisible-placebo pull 0.0383 | 0 | fail (negative) |
| *post hoc* visibility jump at matched time-to-reply | 0.0254 [0.0135, 0.0381]; like-for-like: named 0.053 [0.017, 0.084], unnamed 0.011 [-0.001, 0.026] | 0 | influence detected |
| P5 split-half Spearman of D_k | pre-registered -0.09; post hoc 0.38; message volume 0.94 | synthetic true model 0.3–0.85 | fail |
| P6 held-out V2: ρ(D_k, H_k) | pre 0.17, post hoc 0.12; volume -0.02, out-strength 0.20 | validator split-half -0.14 | > 0 (uninformative where the validator does not replicate) |
| P4 structural drivers | LSB N_D 23/24 (significant edges 1/523); post hoc dense network N_D (self-loops) 1; split-half Jaccard 0.71 | rooms 2 | uninformative |
| P10 named vs unnamed | field-corrected pull named 0.083 vs unnamed 0.008 | ratio ≥ 2 | pass |
| Driver ranking (post hoc network) | top 3: DeepSeek-V3.2, Claude Opus 4.8, GLM-5.2; highest volume: DeepSeek-V3.2 | ρ(D, volume) 0.82 | — |
| Scaling inputs | N = 24, E* = 53.4 (post hoc), median E = 1.03e+03 | — | — |
| P7b/c rooms | top driver in larger room: False (post hoc True); room 15 (n=2): κ 0.026, post hoc jump 0.048; room 0 (n=22): κ -0.028, post hoc jump 0.025 | — | — |
| P9a humans named vs bystanders | 0.086 (n = 39 rows) vs 0.038 (n = 485) | — | pass |

Figures: `../../figures/h29_summary.pdf` (all periods). Data: `data/processed/H29-driver-nodes/G51c/` (`results.json` pre-registered pipeline, `results_posthoc.json` Amendment 2, `agents*.parquet`).

## Scorecard (period-specific axes)
- **C** (beats nulls, held-out days): pre-registered κ fails; post hoc boundary test passes; ranking split-half -0.09 / 0.38.
- **D** (unfitted): held-out spread V2 0.17 (validator replicates at -0.14).
- **G** (ground truth): naming effect present (the H04 named-agent structure).

## Notes
- 2026-10-04: pre-registered pipeline (`explore.py`) and Amendment 2 (`posthoc.py`, post hoc) run. Invisible rows from call windows > 30 s: 0.78 (the H18 visibility rule misclassifies messages that arrive during a PAUSE or a long tool call).
