# H29 × G38: Choose a charity and raise as much money as you can for it (2026-04-02 → 2026-04-24)

**Verdict:** failed
**Role:** exploratory (counted; the largest two-room unit)
**Period:** regime III · mode C · 14 recipients in the network · #best (~4) / #rest (~10); joins 04-17, 04-22 · 17 non-holdout days.

## Why this period
17 days of a shared objective in two rooms: the best-powered unit of the two-room era. H18 and H22 both found their clearest two-room signals here.

## Prediction
*Written 2026-10-04 ~02:25 UTC, before running on this period.* Card predictions P1–P10 as they apply here:

P1: κ > 0 with CI excluding 0 (credence 0.6). P2: invisible-placebo contamination ≥ 50% of the field-corrected pull. P3: net pull falls with k (slope < 0). P4: N_D (self-loops) = root SCCs ≈ 2; LSB drivers not split-half stable (Jaccard < 0.3). P5: split-half Spearman of D_k ≥ 0.4. P6: cross-fitted ρ(D_k, H_k) > 0. P7b: top driver in #rest (larger room). P7c: per-recipient pull higher in #best. P9: 15 named human messages: descriptive only.

## Result
| Prediction | Observed | Null / reference | Verdict |
| --- | --- | --- | --- |
| P1 net pull κ (pre-registered invisible placebo) > 0 | κ = -0.0631 [-0.0806, -0.0414]; field-corrected visible pull 0.0475, invisible-placebo pull 0.1105 | 0 | fail (negative) |
| *post hoc* visibility jump at matched time-to-reply | -0.0141 [-0.0443, 0.0240]; like-for-like: named -0.067 [-0.147, 0.009], unnamed -0.002 [-0.045, 0.047] | 0 | not detected |
| P5 split-half Spearman of D_k | pre-registered -0.21; post hoc -0.31; message volume 0.97 | synthetic true model 0.3–0.85 | fail |
| P6 held-out V2: ρ(D_k, H_k) | pre 0.28, post hoc -0.08; volume -0.31, out-strength -0.01 | validator split-half 0.18 | > 0 (uninformative where the validator does not replicate) |
| P4 structural drivers | LSB N_D 12/12 (significant edges 0/62); post hoc dense network N_D (self-loops) 2; split-half Jaccard 0.92 | rooms 2 | uninformative |
| P10 named vs unnamed | field-corrected pull named 0.075 vs unnamed 0.046 | ratio ≥ 2 | fail |
| Driver ranking (post hoc network) | top 3: Claude Sonnet 4.5, Claude Haiku 4.5, Claude Opus 4.6; highest volume: GPT-5.4 | ρ(D, volume) -0.24 | — |
| Scaling inputs | N = 12, E* = 151 (post hoc), median E = 204 | — | — |
| P7b/c rooms | top driver in larger room: True (post hoc True); room 3 (n=7): κ -0.059, post hoc jump -0.012; room 2 (n=5): κ -0.071, post hoc jump -0.028 | — | — |
| P9a humans named vs bystanders | 0.070 (n = 6 rows) vs 0.032 (n = 82) | — | pass |

Figures: `../../figures/h29_summary.pdf` (all periods). Data: `data/processed/H29-driver-nodes/G38/` (`results.json` pre-registered pipeline, `results_posthoc.json` Amendment 2, `agents*.parquet`).

## Scorecard (period-specific axes)
- **C** (beats nulls, held-out days): pre-registered κ fails; post hoc boundary test does not pass; ranking split-half -0.21 / -0.31.
- **D** (unfitted): held-out spread V2 0.28 (validator replicates at 0.18).
- **G** (ground truth): naming effect not significant (the H04 named-agent structure).

## Notes
- 2026-10-04: pre-registered pipeline (`explore.py`) and Amendment 2 (`posthoc.py`, post hoc) run. Invisible rows from call windows > 30 s: 0.45 (the H18 visibility rule misclassifies messages that arrive during a PAUSE or a long tool call).
