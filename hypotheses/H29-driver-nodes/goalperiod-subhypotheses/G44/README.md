# H29 × G44: Finetune your leader! (2026-05-26 → 2026-05-29)

**Verdict:** failed
**Role:** exploratory (counted)
**Period:** regime III · mode C · 17 recipients in the network · #best / #rest; Opus 4.8 and the temporary fine-tuned leader join 05-28 (NE31) · 4 non-holdout days.

## Why this period
Only #best had the shared objective; the most human messages of regime III before the holdout (59; 19 named). The temporary leader (agent 28) is present on 2 days.

## Prediction
*Written 2026-10-04 ~02:25 UTC, before running on this period.* Card predictions P1–P10 as they apply here:

P1: κ > 0 (credence 0.5). P5: split-half < 0.4 (4 days). P6: ρ > 0 weak. P7b: top driver in the larger room. P9: human named-vs-bystander pull, descriptive (19 named messages). The temporary leader is not predicted to be a top driver (2 days, 27 messages; H23 found no transmission of plans).

## Result
| Prediction | Observed | Null / reference | Verdict |
| --- | --- | --- | --- |
| P1 net pull κ (pre-registered invisible placebo) > 0 | κ = -0.0203 [-0.0284, -0.0120]; field-corrected visible pull 0.0514, invisible-placebo pull 0.0717 | 0 | fail (negative) |
| *post hoc* visibility jump at matched time-to-reply | 0.0037 [-0.0214, 0.0371]; like-for-like: named 0.031 [-0.041, 0.099], unnamed -0.008 [-0.031, 0.025] | 0 | not detected |
| P5 split-half Spearman of D_k | pre-registered 0.26; post hoc -0.09; message volume 0.94 | synthetic true model 0.3–0.85 | fail |
| P6 held-out V2: ρ(D_k, H_k) | pre 0.44, post hoc 0.13; volume -0.22, out-strength -0.04 | validator split-half 0.10 | > 0 (uninformative where the validator does not replicate) |
| P4 structural drivers | LSB N_D 8/15 (significant edges 22/100); post hoc dense network N_D (self-loops) 3; split-half Jaccard 0.30 | rooms 2 | uninformative |
| P10 named vs unnamed | field-corrected pull named 0.099 vs unnamed 0.045 | ratio ≥ 2 | pass |
| Driver ranking (post hoc network) | top 3: DeepSeek-V3.2, Claude Opus 4.7, Claude Opus 4.5; highest volume: DeepSeek-V3.2 | ρ(D, volume) 0.55 | — |
| Scaling inputs | N = 15, E* = 292 (post hoc), median E = 518 | — | — |
| P7b/c rooms | top driver in larger room: False (post hoc True); room 3 (n=9): κ -0.026, post hoc jump -0.003; room 2 (n=6): κ 0.049, post hoc jump 0.087 | — | — |
| P9a humans named vs bystanders | 0.035 (n = 15 rows) vs 0.012 (n = 237) | — | pass |

Figures: `../../figures/h29_summary.pdf` (all periods). Data: `data/processed/H29-driver-nodes/G44/` (`results.json` pre-registered pipeline, `results_posthoc.json` Amendment 2, `agents*.parquet`).

## Scorecard (period-specific axes)
- **C** (beats nulls, held-out days): pre-registered κ fails; post hoc boundary test does not pass; ranking split-half 0.26 / -0.09.
- **D** (unfitted): held-out spread V2 0.44 (validator replicates at 0.10).
- **G** (ground truth): naming effect not significant (the H04 named-agent structure).

## Notes
- 2026-10-04: pre-registered pipeline (`explore.py`) and Amendment 2 (`posthoc.py`, post hoc) run. Invisible rows from call windows > 30 s: 0.39 (the H18 visibility rule misclassifies messages that arrive during a PAUSE or a long tool call).
