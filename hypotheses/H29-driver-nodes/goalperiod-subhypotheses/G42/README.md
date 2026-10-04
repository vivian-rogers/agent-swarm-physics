# H29 × G42: Run your own Youtube channel! (2026-05-18 → 2026-05-22)

**Verdict:** failed
**Verdict (1b):** failed (r1 failed; gte failed)
**Role:** exploratory (counted)
**Period:** regime III · mode I · 15 recipients in the network · #best / #rest · 5 non-holdout days.

## Why this period
Individual objective, moderate volume (6.5k visible rows).

## Prediction
*Written 2026-10-04 ~02:25 UTC, before running on this period.* Card predictions P1–P10 as they apply here:

P1: κ CI includes 0 (pass credence 0.35). P5: split-half < 0.4. P6: ρ ≈ 0. P7b: larger room.

## Result
| Prediction | Observed | Null / reference | Verdict |
| --- | --- | --- | --- |
| P1 net pull κ (pre-registered invisible placebo) > 0 | κ = -0.0138 [-0.0290, -0.0015]; field-corrected visible pull 0.0196, invisible-placebo pull 0.0334 | 0 | fail (negative) |
| *post hoc* visibility jump at matched time-to-reply | 0.0380 [-0.0077, 0.0872]; like-for-like: named 0.093 [-0.085, 0.181], unnamed 0.040 [-0.015, 0.092] | 0 | not detected |
| P5 split-half Spearman of D_k | pre-registered 0.03; post hoc 0.52; message volume 0.87 | synthetic true model 0.3–0.85 | fail |
| P6 held-out V2: ρ(D_k, H_k) | pre 0.36, post hoc 0.08; volume 0.31, out-strength 0.16 | validator split-half -0.09 | > 0 (uninformative where the validator does not replicate) |
| P4 structural drivers | LSB N_D 11/13 (significant edges 4/74); post hoc dense network N_D (self-loops) 2; split-half Jaccard 0.64 | rooms 2 | uninformative |
| P10 named vs unnamed | field-corrected pull named 0.070 vs unnamed 0.012 | ratio ≥ 2 | pass |
| Driver ranking (post hoc network) | top 3: DeepSeek-V3.2, GPT-5.4, Gemini 3.1 Pro; highest volume: DeepSeek-V3.2 | ρ(D, volume) 0.37 | — |
| Scaling inputs | N = 13, E* = 115 (post hoc), median E = 361 | — | — |
| P7b/c rooms | top driver in larger room: True (post hoc True); room 3 (n=8): κ -0.017, post hoc jump 0.024; room 2 (n=5): κ 0.036, post hoc jump 0.130 | — | — |
| P9a humans named vs bystanders | -0.055 (n = 2 rows) vs -0.012 (n = 33) | — | descriptive (n < 5) |

Figures: `../../figures/h29_summary.pdf` (all periods). Data: `data/processed/H29-driver-nodes/G42/` (`results.json` pre-registered pipeline, `results_posthoc.json` Amendment 2, `agents*.parquet`).

## Scorecard (period-specific axes)
- **C** (beats nulls, held-out days): pre-registered κ fails; post hoc boundary test does not pass; ranking split-half 0.03 / 0.52.
- **D** (unfitted): held-out spread V2 0.36 (validator replicates at -0.09).
- **G** (ground truth): naming effect not significant (the H04 named-agent structure).

## Notes
- 2026-10-04: pre-registered pipeline (`explore.py`) and Amendment 2 (`posthoc.py`, post hoc) run. Invisible rows from call windows > 30 s: 0.40 (the H18 visibility rule misclassifies messages that arrive during a PAUSE or a long tool call).

## Round 1b (improved data, 2026-10-04)
Context-ledger visibility (DQ1) instead of H18's call-start rule; both embedding models; the DQ2 reply-graph network. Numbers in `data/processed/H29-driver-nodes/r1b/G42/` (bge) and `r1b_gte/G42/` (gte). Rule unchanged.

| Statistic | Round 1 | Round 1b bge | Round 1b gte |
| --- | --- | --- | --- |
| κ (pre-registered) | -0.014 [-0.029, -0.001] | -0.025 [-0.046, -0.006] | -0.022 [-0.060, 0.016] |
| boundary jump (matched age) | 0.038 [-0.008, 0.087] | -0.005 [-0.049, 0.054] | -0.028 [-0.097, 0.058] |
| named like-for-like | 0.093 [-0.085, 0.181] | 0.126 [-0.044, 0.235] | 0.153 [-0.017, 0.274] |
| unnamed like-for-like | 0.040 [-0.015, 0.092] | -0.059 [-0.125, 0.032] | -0.105 [-0.171, -0.049] |
| split-half D (pre-registered / post hoc) | 0.03 / 0.52 | -0.02 / 0.39 | 0.18 / -0.46 |
| held-out V2 ρ(D, H) (pre-registered / post hoc) | 0.36 / 0.08 | 0.14 / 0.16 | -0.13 / 0.05 |
| reply network: split-half D^rep · held-out ρ(D^rep, H) | – | 0.55 · -0.05 | 0.48 · -0.01 |
| reply-parent premium (matched age) | – | 0.159 [0.144, 0.165] | 0.187 [0.162, 0.199] |
