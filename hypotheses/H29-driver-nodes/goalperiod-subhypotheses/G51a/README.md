# H29 × G51a: Each agent: Maximize your assigned goal! (roles start) (2026-07-06 → 2026-07-08)

**Verdict:** descriptive
**Verdict (1b):** descriptive (r1 descriptive; gte descriptive)
**Role:** exploratory (descriptive: 3 days)
**Period:** regime III · mode P · 21 recipients in the network · #general · 3 non-holdout days.

## Why this period
First three days of private roles; one room of 21; heavy volume (69k visible rows).

## Prediction
*Written 2026-10-04 ~02:25 UTC, before running on this period.* Card predictions P1–P10 as they apply here:

P1: κ > 0 (credence 0.6; volume). P4: one room → N_D (self-loops) = 1. P5/P6: 2 + 1 days, not counted.

## Result
| Prediction | Observed | Null / reference | Verdict |
| --- | --- | --- | --- |
| P1 net pull κ (pre-registered invisible placebo) > 0 | κ = -0.0126 [-0.0225, -0.0075]; field-corrected visible pull 0.0092, invisible-placebo pull 0.0217 | 0 | fail (negative) |
| *post hoc* visibility jump at matched time-to-reply | 0.0331 [0.0304, 0.0468]; like-for-like: named 0.081 [0.025, 0.102], unnamed 0.021 [0.018, 0.030] | 0 | influence detected |
| P5 split-half Spearman of D_k | pre-registered 0.14; post hoc 0.49; message volume 0.65 | synthetic true model 0.3–0.85 | fail |
| P6 held-out V2: ρ(D_k, H_k) | pre -0.24, post hoc -0.20; volume -0.22, out-strength -0.33 | validator split-half -0.38 | ≤ 0 (uninformative where the validator does not replicate) |
| P4 structural drivers | LSB N_D 14/19 (significant edges 10/342); post hoc dense network N_D (self-loops) 1; split-half Jaccard 0.53 | rooms 1 | uninformative |
| P10 named vs unnamed | field-corrected pull named 0.074 vs unnamed 0.006 | ratio ≥ 2 | pass |
| Driver ranking (post hoc network) | top 3: DeepSeek-V3.2, GLM-5.2, GPT-5.4; highest volume: DeepSeek-V3.2 | ρ(D, volume) 0.81 | — |
| Scaling inputs | N = 19, E* = 39 (post hoc), median E = 905 | — | — |
| P9a humans named vs bystanders | 0.109 (n = 12 rows) vs -0.006 (n = 248) | — | pass |

Figures: `../../figures/h29_summary.pdf` (all periods). Data: `data/processed/H29-driver-nodes/G51a/` (`results.json` pre-registered pipeline, `results_posthoc.json` Amendment 2, `agents*.parquet`).

## Scorecard (period-specific axes)
- **C** (beats nulls, held-out days): pre-registered κ fails; post hoc boundary test passes; ranking split-half 0.14 / 0.49.
- **D** (unfitted): held-out spread V2 -0.24 (validator replicates at -0.38).
- **G** (ground truth): naming effect present (the H04 named-agent structure).

## Notes
- 2026-10-04: pre-registered pipeline (`explore.py`) and Amendment 2 (`posthoc.py`, post hoc) run. Invisible rows from call windows > 30 s: 0.56 (the H18 visibility rule misclassifies messages that arrive during a PAUSE or a long tool call).

## Round 1b (improved data, 2026-10-04)
Context-ledger visibility (DQ1) instead of H18's call-start rule; both embedding models; the DQ2 reply-graph network. Numbers in `data/processed/H29-driver-nodes/r1b/G51a/` (bge) and `r1b_gte/G51a/` (gte). Rule unchanged.

| Statistic | Round 1 | Round 1b bge | Round 1b gte |
| --- | --- | --- | --- |
| κ (pre-registered) | -0.013 [-0.023, -0.007] | -0.006 [-0.010, -0.001] | -0.004 [-0.006, -0.003] |
| boundary jump (matched age) | 0.033 [0.030, 0.047] | 0.018 [0.007, 0.040] | 0.013 [0.006, 0.035] |
| named like-for-like | 0.081 [0.025, 0.102] | 0.043 [0.029, 0.075] | 0.042 [0.033, 0.055] |
| unnamed like-for-like | 0.021 [0.018, 0.030] | 0.013 [0.005, 0.030] | 0.007 [-0.001, 0.030] |
| split-half D (pre-registered / post hoc) | 0.14 / 0.49 | 0.05 / 0.27 | 0.27 / 0.30 |
| held-out V2 ρ(D, H) (pre-registered / post hoc) | -0.24 / -0.20 | -0.13 / -0.18 | -0.08 / -0.08 |
| reply network: split-half D^rep · held-out ρ(D^rep, H) | – | 0.57 · -0.22 | 0.59 · -0.17 |
| reply-parent premium (matched age) | – | 0.180 [0.169, 0.199] | 0.204 [0.197, 0.214] |
