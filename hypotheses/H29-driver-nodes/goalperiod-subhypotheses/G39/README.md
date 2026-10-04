# H29 × G39: Build your own interactive world! (2026-04-27 → 2026-05-01)

**Verdict:** mixed
**Role:** exploratory (counted)
**Period:** regime III · mode I · 14 recipients in the network · #best / #rest (reshuffled 04-27) · 5 non-holdout days.

## Why this period
Individual-objective week; few messages (5k visible rows). A low-coupling contrast.

## Prediction
*Written 2026-10-04 ~02:25 UTC, before running on this period.* Card predictions P1–P10 as they apply here:

P1: κ CI includes 0 (credence of a pass 0.35; individual objectives, low volume). P5: split-half < 0.4 (5 days). P6: ρ ≈ 0. P7b: top driver in the larger room.

## Result
| Prediction | Observed | Null / reference | Verdict |
| --- | --- | --- | --- |
| P1 net pull κ (pre-registered invisible placebo) > 0 | κ = 0.0082 [-0.0012, 0.0267]; field-corrected visible pull 0.0075, invisible-placebo pull -0.0007 | 0 | fail (n.s.) |
| *post hoc* visibility jump at matched time-to-reply | 0.0458 [0.0216, 0.0945]; like-for-like: named — [-0.056, 0.108], unnamed 0.034 [0.012, 0.053] | 0 | influence detected |
| P5 split-half Spearman of D_k | pre-registered 0.40; post hoc 0.55; message volume 0.67 | synthetic true model 0.3–0.85 | pass |
| P6 held-out V2: ρ(D_k, H_k) | pre 0.20, post hoc 0.09; volume -0.08, out-strength 0.34 | validator split-half -0.50 | > 0 (uninformative where the validator does not replicate) |
| P4 structural drivers | LSB N_D 6/11 (significant edges 9/62); post hoc dense network N_D (self-loops) 2; split-half Jaccard 0.00 | rooms 2 | uninformative |
| P10 named vs unnamed | field-corrected pull named 0.051 vs unnamed 0.006 | ratio ≥ 2 | pass |
| Driver ranking (post hoc network) | top 3: Claude Haiku 4.5, Claude Opus 4.5, GPT-5.5; highest volume: Claude Haiku 4.5 | ρ(D, volume) 0.47 | — |
| Scaling inputs | N = 11, E* = 70.8 (post hoc), median E = 191 | — | — |
| P7b/c rooms | top driver in larger room: True (post hoc True); room 3 (n=8): κ 0.008, post hoc jump 0.035; room 2 (n=3): κ 0.036, post hoc jump 0.166 | — | — |
| P9a humans named vs bystanders | 0.093 (n = 1 rows) vs -0.026 (n = 27) | — | descriptive (n < 5) |

Figures: `../../figures/h29_summary.pdf` (all periods). Data: `data/processed/H29-driver-nodes/G39/` (`results.json` pre-registered pipeline, `results_posthoc.json` Amendment 2, `agents*.parquet`).

## Scorecard (period-specific axes)
- **C** (beats nulls, held-out days): pre-registered κ fails; post hoc boundary test passes; ranking split-half 0.40 / 0.55.
- **D** (unfitted): held-out spread V2 0.20 (validator replicates at -0.50).
- **G** (ground truth): naming effect not significant (the H04 named-agent structure).

## Notes
- 2026-10-04: pre-registered pipeline (`explore.py`) and Amendment 2 (`posthoc.py`, post hoc) run. Invisible rows from call windows > 30 s: 0.27 (the H18 visibility rule misclassifies messages that arrive during a PAUSE or a long tool call).
