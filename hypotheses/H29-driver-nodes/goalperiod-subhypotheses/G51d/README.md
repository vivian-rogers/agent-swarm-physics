# H29 × G51d: Each agent: Maximize your assigned goal! (after #focus) (2026-08-25 → 2026-09-02)

**Verdict:** mixed
**Verdict (1b):** mixed (r1 mixed; gte mixed)
**Role:** exploratory (counted)
**Period:** regime III · mode P · 29 recipients in the network · #general · 7 non-holdout days.

## Why this period
7 days, 29 agents, one room.

## Prediction
*Written 2026-10-04 ~02:25 UTC, before running on this period.* Card predictions P1–P10 as they apply here:

P1: κ > 0 (credence 0.6). P5: split-half ≥ 0.2. P6: ρ > 0.

## Result
| Prediction | Observed | Null / reference | Verdict |
| --- | --- | --- | --- |
| P1 net pull κ (pre-registered invisible placebo) > 0 | κ = -0.0133 [-0.0243, -0.0042]; field-corrected visible pull 0.0061, invisible-placebo pull 0.0193 | 0 | fail (negative) |
| *post hoc* visibility jump at matched time-to-reply | 0.0331 [0.0195, 0.0438]; like-for-like: named 0.087 [0.060, 0.112], unnamed 0.018 [0.007, 0.029] | 0 | influence detected |
| P5 split-half Spearman of D_k | pre-registered 0.05; post hoc -0.18; message volume 0.88 | synthetic true model 0.3–0.85 | fail |
| P6 held-out V2: ρ(D_k, H_k) | pre 0.14, post hoc -0.11; volume -0.28, out-strength -0.00 | validator split-half 0.23 | > 0 (uninformative where the validator does not replicate) |
| P4 structural drivers | LSB N_D 16/20 (significant edges 7/367); post hoc dense network N_D (self-loops) 1; split-half Jaccard 0.40 | rooms 1 | uninformative |
| P10 named vs unnamed | field-corrected pull named 0.061 vs unnamed 0.004 | ratio ≥ 2 | pass |
| Driver ranking (post hoc network) | top 3: Gemini 2.5 Pro, Claude Opus 4.8, Claude Fable 5.1; highest volume: DeepSeek-V3.2 | ρ(D, volume) 0.34 | — |
| Scaling inputs | N = 20, E* = 74.8 (post hoc), median E = 887 | — | — |
| P9a humans named vs bystanders | 0.019 (n = 6 rows) vs 0.030 (n = 131) | — | fail |

Figures: `../../figures/h29_summary.pdf` (all periods). Data: `data/processed/H29-driver-nodes/G51d/` (`results.json` pre-registered pipeline, `results_posthoc.json` Amendment 2, `agents*.parquet`).

## Scorecard (period-specific axes)
- **C** (beats nulls, held-out days): pre-registered κ fails; post hoc boundary test passes; ranking split-half 0.05 / -0.18.
- **D** (unfitted): held-out spread V2 0.14 (validator replicates at 0.23).
- **G** (ground truth): naming effect present (the H04 named-agent structure).

## Notes
- 2026-10-04: pre-registered pipeline (`explore.py`) and Amendment 2 (`posthoc.py`, post hoc) run. Invisible rows from call windows > 30 s: 0.69 (the H18 visibility rule misclassifies messages that arrive during a PAUSE or a long tool call).

## Round 1b (improved data, 2026-10-04)
Context-ledger visibility (DQ1) instead of H18's call-start rule; both embedding models; the DQ2 reply-graph network. Numbers in `data/processed/H29-driver-nodes/r1b/G51d/` (bge) and `r1b_gte/G51d/` (gte). Rule unchanged.

| Statistic | Round 1 | Round 1b bge | Round 1b gte |
| --- | --- | --- | --- |
| κ (pre-registered) | -0.013 [-0.024, -0.004] | -0.013 [-0.023, -0.003] | -0.017 [-0.026, -0.006] |
| boundary jump (matched age) | 0.033 [0.019, 0.044] | 0.020 [0.005, 0.033] | 0.017 [0.012, 0.022] |
| named like-for-like | 0.087 [0.060, 0.112] | 0.056 [0.001, 0.130] | 0.068 [0.032, 0.136] |
| unnamed like-for-like | 0.018 [0.007, 0.029] | 0.012 [-0.003, 0.024] | 0.007 [0.003, 0.011] |
| split-half D (pre-registered / post hoc) | 0.05 / -0.18 | 0.32 / 0.42 | 0.18 / 0.30 |
| held-out V2 ρ(D, H) (pre-registered / post hoc) | 0.14 / -0.11 | -0.25 / -0.18 | -0.17 / -0.02 |
| reply network: split-half D^rep · held-out ρ(D^rep, H) | – | 0.82 · 0.23 | 0.81 · 0.06 |
| reply-parent premium (matched age) | – | 0.159 [0.144, 0.175] | 0.167 [0.145, 0.188] |
