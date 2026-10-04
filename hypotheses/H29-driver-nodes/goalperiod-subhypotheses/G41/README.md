# H29 × G41: Perform novel research! (2026-05-11 → 2026-05-15)

**Verdict:** failed
**Verdict (1b):** failed (r1 failed; gte failed)
**Role:** replication (exploratory (counted))
**Period:** regime III · mode I · 14 recipients in the network · #best / #rest (split back 05-11) · 5 non-holdout days.

## Why this period
Individual research in two rooms with the same task (H01's exception: no room field). 14.3k visible rows.

## Prediction
*Written 2026-10-04 ~02:25 UTC, before running on this period.* Card predictions P1–P10 as they apply here:

P1: κ > 0 (credence 0.45). P5: split-half ≥ 0.2. P6: ρ > 0 (weak). P7b: top driver in the larger room. P7c: pull higher in the smaller room.

## Result
| Prediction | Observed | Null / reference | Verdict |
| --- | --- | --- | --- |
| P1 net pull κ (pre-registered invisible placebo) > 0 | κ = -0.0372 [-0.0513, -0.0201]; field-corrected visible pull 0.0651, invisible-placebo pull 0.1023 | 0 | fail (negative) |
| *post hoc* visibility jump at matched time-to-reply | -0.0217 [-0.0566, 0.0287]; like-for-like: named -0.023 [-0.053, -0.001], unnamed -0.024 [-0.062, 0.032] | 0 | not detected |
| P5 split-half Spearman of D_k | pre-registered 0.51; post hoc -0.04; message volume 0.95 | synthetic true model 0.3–0.85 | pass |
| P6 held-out V2: ρ(D_k, H_k) | pre 0.01, post hoc 0.07; volume -0.24, out-strength 0.00 | validator split-half 0.60 | > 0 (uninformative where the validator does not replicate) |
| P4 structural drivers | LSB N_D 13/14 (significant edges 1/102); post hoc dense network N_D (self-loops) 2; split-half Jaccard 0.57 | rooms 2 | uninformative |
| P10 named vs unnamed | field-corrected pull named 0.108 vs unnamed 0.060 | ratio ≥ 2 | fail |
| Driver ranking (post hoc network) | top 3: Claude Sonnet 4.5, Claude Opus 4.7, Claude Opus 4.5; highest volume: GPT-5.4 | ρ(D, volume) 0.27 | — |
| Scaling inputs | N = 14, E* = 212 (post hoc), median E = 423 | — | — |
| P7b/c rooms | top driver in larger room: True (post hoc True); room 3 (n=10): κ -0.037, post hoc jump -0.026; room 2 (n=4): κ -0.026, post hoc jump 0.008 | — | — |
| P9a humans named vs bystanders | 0.081 (n = 2 rows) vs 0.019 (n = 39) | — | descriptive (n < 5) |

Figures: `../../figures/h29_summary.pdf` (all periods). Data: `data/processed/H29-driver-nodes/G41/` (`results.json` pre-registered pipeline, `results_posthoc.json` Amendment 2, `agents*.parquet`).

## Scorecard (period-specific axes)
- **C** (beats nulls, held-out days): pre-registered κ fails; post hoc boundary test does not pass; ranking split-half 0.51 / -0.04.
- **D** (unfitted): held-out spread V2 0.01 (validator replicates at 0.60).
- **G** (ground truth): naming effect not significant (the H04 named-agent structure).

## Notes
- 2026-10-04: pre-registered pipeline (`explore.py`) and Amendment 2 (`posthoc.py`, post hoc) run. Invisible rows from call windows > 30 s: 0.43 (the H18 visibility rule misclassifies messages that arrive during a PAUSE or a long tool call).

## Round 1b (improved data, 2026-10-04)
Context-ledger visibility (DQ1) instead of H18's call-start rule; both embedding models; the DQ2 reply-graph network. Numbers in `data/processed/H29-driver-nodes/r1b/G41/` (bge) and `r1b_gte/G41/` (gte). Rule unchanged.

| Statistic | Round 1 | Round 1b bge | Round 1b gte |
| --- | --- | --- | --- |
| κ (pre-registered) | -0.037 [-0.051, -0.020] | -0.035 [-0.039, -0.020] | -0.031 [-0.034, -0.017] |
| boundary jump (matched age) | -0.022 [-0.057, 0.029] | -0.000 [-0.024, 0.036] | 0.018 [-0.008, 0.067] |
| named like-for-like | -0.023 [-0.053, -0.001] | -0.002 [-0.060, 0.082] | 0.056 [0.000, 0.154] |
| unnamed like-for-like | -0.024 [-0.062, 0.032] | -0.001 [-0.021, 0.042] | 0.007 [-0.024, 0.062] |
| split-half D (pre-registered / post hoc) | 0.51 / -0.04 | 0.20 / 0.26 | -0.18 / 0.19 |
| held-out V2 ρ(D, H) (pre-registered / post hoc) | 0.01 / 0.07 | 0.28 / -0.14 | 0.19 / 0.16 |
| reply network: split-half D^rep · held-out ρ(D^rep, H) | – | 0.59 · 0.63 | 0.57 · 0.31 |
| reply-parent premium (matched age) | – | 0.142 [0.133, 0.153] | 0.159 [0.148, 0.173] |
