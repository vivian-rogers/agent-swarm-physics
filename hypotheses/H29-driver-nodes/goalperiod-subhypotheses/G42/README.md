# H29 × G42: Run your own Youtube channel! (2026-05-18 → 2026-05-22)

**Verdict:** failed
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
