# H29 × G51b: Each agent: Maximize your assigned goal! (2026-07-09 → 2026-08-04)

**Verdict:** mixed
**Verdict (1b):** mixed (r1 mixed; gte mixed)
**Role:** replication (exploratory (counted))
**Period:** regime III · mode P · 27 recipients in the network · #general (isolated GPT-5.6 rooms 07-09/10) · 19 non-holdout days.

## Why this period
19 days, 27 agents, 319k visible rows: the best-powered unit overall, and the large-N end of the scaling test.

## Prediction
*Written 2026-10-04 ~02:25 UTC, before running on this period.* Card predictions P1–P10 as they apply here:

P1: κ > 0 with CI excluding 0 (credence 0.7). P3: slope < 0. P5: split-half ≥ 0.4. P6: ρ > 0, pooled with the rest ≥ 0.3. P8: E* at N = 27 above the two-room-era E* by ≈ (27/14)^2 ≈ 3.7 (η = 2).

## Result
| Prediction | Observed | Null / reference | Verdict |
| --- | --- | --- | --- |
| P1 net pull κ (pre-registered invisible placebo) > 0 | κ = -0.0185 [-0.0228, -0.0138]; field-corrected visible pull 0.0094, invisible-placebo pull 0.0279 | 0 | fail (negative) |
| *post hoc* visibility jump at matched time-to-reply | 0.0332 [0.0231, 0.0432]; like-for-like: named 0.084 [0.066, 0.105], unnamed 0.013 [0.004, 0.021] | 0 | influence detected |
| P5 split-half Spearman of D_k | pre-registered 0.17; post hoc 0.87; message volume 0.97 | synthetic true model 0.3–0.85 | fail |
| P6 held-out V2: ρ(D_k, H_k) | pre -0.32, post hoc 0.05; volume 0.11, out-strength -0.42 | validator split-half 0.45 | ≤ 0 (uninformative where the validator does not replicate) |
| P4 structural drivers | LSB N_D 23/26 (significant edges 5/648); post hoc dense network N_D (self-loops) 1; split-half Jaccard 0.88 | rooms 1 | uninformative |
| P10 named vs unnamed | field-corrected pull named 0.080 vs unnamed 0.006 | ratio ≥ 2 | pass |
| Driver ranking (post hoc network) | top 3: DeepSeek-V3.2, GPT-5.4, GLM-5.2; highest volume: DeepSeek-V3.2 | ρ(D, volume) 0.89 | — |
| Scaling inputs | N = 26, E* = 36.8 (post hoc), median E = 1.24e+03 | — | — |
| P9a humans named vs bystanders | 0.113 (n = 23 rows) vs 0.020 (n = 528) | — | pass |

Figures: `../../figures/h29_summary.pdf` (all periods). Data: `data/processed/H29-driver-nodes/G51b/` (`results.json` pre-registered pipeline, `results_posthoc.json` Amendment 2, `agents*.parquet`).

## Scorecard (period-specific axes)
- **C** (beats nulls, held-out days): pre-registered κ fails; post hoc boundary test passes; ranking split-half 0.17 / 0.87.
- **D** (unfitted): held-out spread V2 -0.32 (validator replicates at 0.45).
- **G** (ground truth): naming effect present (the H04 named-agent structure).

## Notes
- 2026-10-04: pre-registered pipeline (`explore.py`) and Amendment 2 (`posthoc.py`, post hoc) run. Invisible rows from call windows > 30 s: 0.70 (the H18 visibility rule misclassifies messages that arrive during a PAUSE or a long tool call).

## Round 1b (improved data, 2026-10-04)
Context-ledger visibility (DQ1) instead of H18's call-start rule; both embedding models; the DQ2 reply-graph network. Numbers in `data/processed/H29-driver-nodes/r1b/G51b/` (bge) and `r1b_gte/G51b/` (gte). Rule unchanged.

| Statistic | Round 1 | Round 1b bge | Round 1b gte |
| --- | --- | --- | --- |
| κ (pre-registered) | -0.019 [-0.023, -0.014] | -0.015 [-0.019, -0.010] | -0.016 [-0.022, -0.010] |
| boundary jump (matched age) | 0.033 [0.023, 0.043] | 0.023 [0.014, 0.033] | 0.029 [0.019, 0.042] |
| named like-for-like | 0.084 [0.066, 0.105] | 0.069 [0.051, 0.090] | 0.079 [0.053, 0.106] |
| unnamed like-for-like | 0.013 [0.004, 0.021] | 0.007 [-0.001, 0.017] | 0.013 [0.002, 0.025] |
| split-half D (pre-registered / post hoc) | 0.17 / 0.87 | 0.45 / 0.86 | 0.43 / 0.87 |
| held-out V2 ρ(D, H) (pre-registered / post hoc) | -0.32 / 0.05 | -0.08 / 0.05 | -0.09 / 0.06 |
| reply network: split-half D^rep · held-out ρ(D^rep, H) | – | 0.91 · 0.25 | 0.91 · 0.07 |
| reply-parent premium (matched age) | – | 0.166 [0.156, 0.175] | 0.193 [0.183, 0.203] |
