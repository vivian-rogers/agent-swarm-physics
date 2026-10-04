# H29 × G51e: Each agent: Maximize your assigned goal! (NE33 joins) (2026-09-03 → 2026-09-04)

**Verdict:** descriptive
**Role:** exploratory (descriptive: 2 days)
**Period:** regime III · mode P · 29 recipients in the network · #general · 2 non-holdout days.

## Why this period
Two days after a batch join of three agents; the holdout tail starts 09-07.

## Prediction
*Written 2026-10-04 ~02:25 UTC, before running on this period.* Card predictions P1–P10 as they apply here:

P1: κ > 0 (credence 0.5). No split-half statistics (1 + 1 days).

## Result
| Prediction | Observed | Null / reference | Verdict |
| --- | --- | --- | --- |
| P1 net pull κ (pre-registered invisible placebo) > 0 | κ = -0.0123 [-0.0164, -0.0101]; field-corrected visible pull 0.0022, invisible-placebo pull 0.0145 | 0 | fail (negative) |
| *post hoc* visibility jump at matched time-to-reply | 0.0127 [0.0102, 0.0151]; like-for-like: named 0.026 [0.013, 0.034], unnamed 0.009 [0.007, 0.012] | 0 | influence detected |
| P5 split-half Spearman of D_k | pre-registered -0.05; post hoc 0.33; message volume 0.77 | synthetic true model 0.3–0.85 | fail |
| P6 held-out V2: ρ(D_k, H_k) | pre 0.11, post hoc -0.07; volume 0.09, out-strength -0.05 | validator split-half 0.06 | > 0 (uninformative where the validator does not replicate) |
| P4 structural drivers | LSB N_D 6/21 (significant edges 40/385); post hoc dense network N_D (self-loops) 1; split-half Jaccard 1.00 | rooms 1 | uninformative |
| P10 named vs unnamed | field-corrected pull named 0.051 vs unnamed 0.000 | ratio ≥ 2 | pass |
| Driver ranking (post hoc network) | top 3: GPT-5.2, GPT-5.4, DeepSeek-V3.2; highest volume: DeepSeek-V4-Pro | ρ(D, volume) 0.37 | — |
| Scaling inputs | N = 21, E* = 127 (post hoc), median E = 2.4e+03 | — | — |
| P9a humans named vs bystanders | -0.238 (n = 2 rows) vs 0.024 (n = 90) | — | descriptive (n < 5) |

Figures: `../../figures/h29_summary.pdf` (all periods). Data: `data/processed/H29-driver-nodes/G51e/` (`results.json` pre-registered pipeline, `results_posthoc.json` Amendment 2, `agents*.parquet`).

## Scorecard (period-specific axes)
- **C** (beats nulls, held-out days): pre-registered κ fails; post hoc boundary test passes; ranking split-half -0.05 / 0.33.
- **D** (unfitted): held-out spread V2 0.11 (validator replicates at 0.06).
- **G** (ground truth): naming effect present (the H04 named-agent structure).

## Notes
- 2026-10-04: pre-registered pipeline (`explore.py`) and Amendment 2 (`posthoc.py`, post hoc) run. Invisible rows from call windows > 30 s: 0.61 (the H18 visibility rule misclassifies messages that arrive during a PAUSE or a long tool call).
