# H29 × G37: Pick your own goal! (2026-03-30 → 2026-04-01)

**Verdict:** descriptive
**Verdict (1b):** descriptive (r1 descriptive; gte descriptive)
**Role:** replication (exploratory (descriptive: 3 days))
**Period:** regime III · mode F · 10 recipients in the network · #best / #rest · 3 non-holdout days.

## Why this period
Free week at the start of regime III; two rooms. Too short for split halves; included to show what three days give.

## Prediction
*Written 2026-10-04 ~02:25 UTC, before running on this period.* Card predictions P1–P10 as they apply here:

P1: κ CI includes 0 (2.4k visible rows; low power). P4: structural N_D (self-loops) = root SCCs ≈ 2 (rooms). P5/P6: split halves of 2 + 1 days; no reliability expected (|ρ| < 0.4). P7b: the top driver is in the larger room (#rest).

## Result
| Prediction | Observed | Null / reference | Verdict |
| --- | --- | --- | --- |
| P1 net pull κ (pre-registered invisible placebo) > 0 | κ = -0.0061 [-0.0647, 0.0318]; field-corrected visible pull 0.1025, invisible-placebo pull 0.1086 | 0 | fail (n.s.) |
| *post hoc* visibility jump at matched time-to-reply | 0.0744 [-0.1283, 0.1652]; like-for-like: named -0.040 [-0.294, 0.078], unnamed 0.114 [-0.056, 0.163] | 0 | not detected |
| P5 split-half Spearman of D_k | pre-registered 0.17; post hoc 0.06; message volume 0.82 | synthetic true model 0.3–0.85 | fail |
| P6 held-out V2: ρ(D_k, H_k) | pre 0.17, post hoc 0.19; volume 0.32, out-strength 0.25 | validator split-half 0.40 | > 0 (uninformative where the validator does not replicate) |
| P4 structural drivers | LSB N_D 5/9 (significant edges 7/37); post hoc dense network N_D (self-loops) 1; split-half Jaccard 0.22 | rooms 2 | uninformative |
| P10 named vs unnamed | field-corrected pull named 0.170 vs unnamed 0.096 | ratio ≥ 2 | fail |
| Driver ranking (post hoc network) | top 3: GPT-5.4, Claude Opus 4.5, GPT-5.1; highest volume: GPT-5.4 | ρ(D, volume) 0.32 | — |
| Scaling inputs | N = 9, E* = 35.2 (post hoc), median E = 86 | — | — |
| P7b/c rooms | top driver in larger room: True (post hoc False); room 3 (n=6): κ -0.012, post hoc jump 0.051; room 2 (n=3): κ 0.051, post hoc jump 0.138 | — | — |
| P9a humans named vs bystanders | 0.039 (n = 1 rows) vs 0.071 (n = 3) | — | descriptive (n < 5) |

Figures: `../../figures/h29_summary.pdf` (all periods). Data: `data/processed/H29-driver-nodes/G37/` (`results.json` pre-registered pipeline, `results_posthoc.json` Amendment 2, `agents*.parquet`).

## Scorecard (period-specific axes)
- **C** (beats nulls, held-out days): pre-registered κ fails; post hoc boundary test does not pass; ranking split-half 0.17 / 0.06.
- **D** (unfitted): held-out spread V2 0.17 (validator replicates at 0.40).
- **G** (ground truth): naming effect not significant (the H04 named-agent structure).

## Notes
- 2026-10-04: pre-registered pipeline (`explore.py`) and Amendment 2 (`posthoc.py`, post hoc) run. Invisible rows from call windows > 30 s: 0.69 (the H18 visibility rule misclassifies messages that arrive during a PAUSE or a long tool call).

## Round 1b (improved data, 2026-10-04)
Context-ledger visibility (DQ1) instead of H18's call-start rule; both embedding models; the DQ2 reply-graph network. Numbers in `data/processed/H29-driver-nodes/r1b/G37/` (bge) and `r1b_gte/G37/` (gte). Rule unchanged.

| Statistic | Round 1 | Round 1b bge | Round 1b gte |
| --- | --- | --- | --- |
| κ (pre-registered) | -0.006 [-0.065, 0.032] | 0.002 [-0.047, 0.028] | 0.025 [-0.035, 0.059] |
| boundary jump (matched age) | 0.074 [-0.128, 0.165] | 0.117 [-0.017, 0.155] | 0.139 [0.060, 0.178] |
| named like-for-like | -0.040 [-0.294, 0.078] | 0.083 [0.060, 0.127] | 0.132 [0.095, 0.191] |
| unnamed like-for-like | 0.114 [-0.056, 0.163] | 0.142 [0.004, 0.227] | 0.130 [-0.002, 0.185] |
| split-half D (pre-registered / post hoc) | 0.17 / 0.06 | 0.27 / 0.18 | -0.08 / 0.63 |
| held-out V2 ρ(D, H) (pre-registered / post hoc) | 0.17 / 0.19 | 0.15 / 0.34 | 0.35 / 0.61 |
| reply network: split-half D^rep · held-out ρ(D^rep, H) | – | 0.75 · -0.63 | 0.75 · -0.68 |
| reply-parent premium (matched age) | – | 0.176 [0.128, 0.195] | 0.199 [0.152, 0.223] |
