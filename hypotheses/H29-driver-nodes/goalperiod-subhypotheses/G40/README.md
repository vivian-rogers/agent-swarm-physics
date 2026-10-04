# H29 × G40: Connect your worlds into a 3D universe! (2026-05-04 → 2026-05-08)

**Verdict:** failed
**Role:** exploratory (counted)
**Period:** regime III · mode C · 14 recipients in the network · merged into #universe-coordination (one room) · 5 non-holdout days.

## Why this period
Shared objective in one merged room (16.9k visible rows). H12 found its strongest collective mode in #40, partly self-repetition.

## Prediction
*Written 2026-10-04 ~02:25 UTC, before running on this period.* Card predictions P1–P10 as they apply here:

P1: κ > 0 (credence 0.5). P4: one room → N_D (self-loops) = 1. P5: split-half ≥ 0.2 (5 days). P6: ρ > 0. P7b: n/a (one room).

## Result
| Prediction | Observed | Null / reference | Verdict |
| --- | --- | --- | --- |
| P1 net pull κ (pre-registered invisible placebo) > 0 | κ = -0.0033 [-0.0171, 0.0155]; field-corrected visible pull 0.0241, invisible-placebo pull 0.0273 | 0 | fail (n.s.) |
| *post hoc* visibility jump at matched time-to-reply | 0.0164 [-0.0248, 0.0470]; like-for-like: named -0.054 [-0.158, 0.184], unnamed 0.015 [-0.038, 0.042] | 0 | not detected |
| P5 split-half Spearman of D_k | pre-registered 0.01; post hoc 0.17; message volume 0.83 | synthetic true model 0.3–0.85 | fail |
| P6 held-out V2: ρ(D_k, H_k) | pre -0.08, post hoc 0.04; volume 0.15, out-strength 0.13 | validator split-half -0.01 | ≤ 0 (uninformative where the validator does not replicate) |
| P4 structural drivers | LSB N_D 7/12 (significant edges 12/132); post hoc dense network N_D (self-loops) 1; split-half Jaccard 0.67 | rooms 1 | uninformative |
| P10 named vs unnamed | field-corrected pull named 0.072 vs unnamed 0.021 | ratio ≥ 2 | pass |
| Driver ranking (post hoc network) | top 3: Claude Opus 4.5, DeepSeek-V3.2, GPT-5.4; highest volume: DeepSeek-V3.2 | ρ(D, volume) 0.58 | — |
| Scaling inputs | N = 12, E* = 61.6 (post hoc), median E = 239 | — | — |
| P9a humans named vs bystanders | — (n = 0 rows) vs — (n = 0) | — | descriptive (n < 5) |

Figures: `../../figures/h29_summary.pdf` (all periods). Data: `data/processed/H29-driver-nodes/G40/` (`results.json` pre-registered pipeline, `results_posthoc.json` Amendment 2, `agents*.parquet`).

## Scorecard (period-specific axes)
- **C** (beats nulls, held-out days): pre-registered κ fails; post hoc boundary test does not pass; ranking split-half 0.01 / 0.17.
- **D** (unfitted): held-out spread V2 -0.08 (validator replicates at -0.01).
- **G** (ground truth): naming effect not significant (the H04 named-agent structure).

## Notes
- 2026-10-04: pre-registered pipeline (`explore.py`) and Amendment 2 (`posthoc.py`, post hoc) run. Invisible rows from call windows > 30 s: 0.24 (the H18 visibility rule misclassifies messages that arrive during a PAUSE or a long tool call).
