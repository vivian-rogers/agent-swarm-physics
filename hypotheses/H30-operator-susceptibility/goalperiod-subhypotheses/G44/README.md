# H30 × G44: Finetune your leader! (2026-05-26 → 2026-06-01)

**Verdict:** mixed — nudge -0.32 min (n 24); content 0.016; low power
**Verdict (1b):** mixed (r1 mixed; fixed bins, receiving call)
**Role:** exploratory
**Period:** regime III · mode C · 16 agents at start · 4 active days.

## Why this period
Regime III, 4 days, 27 nudges and 59 human messages (the fine-tuned-leader week, non-holdout).

## Prediction
*Written 2026-10-03, before running on this period.*

- P1: χ_act(N_tgt) point estimate > 0.
- P3: χ_act(H_men) > χ_act(H_und); per-recipient human χ_act below regime I's.
- P4: χ_con(H_und) > 0 (point; CI may include 0 with 4 days).

## Result
Days: 4; kicks by class: {'H_und': 284, 'H_men': 15, 'N_by': 217, 'N_tgt': 32}; content pairs with statements on both sides: 494.

| Prediction | Observed | Null / reference | Verdict |
| --- | --- | --- | --- |
| P1 χ_act(N_tgt), min per nudge (pre-registered model) | -0.32 [-1.19, 0.70] (n = 24); with day FE (A2) -0.21 [-1.41, 0.54]: first nudge in 30 min -0.11 [-1.53, 0.80], repeat 0.07 [-6.00, 1.53], outage-masked -0.21 [-1.41, 0.54], swarm lull 0.00 [CI unstable: too few days] vs not 0.13 [-0.63, 0.89] | day-swap 0.09 [-0.90, 1.50] | failed (point ≤ 0) |
| P2 χ_act(N_by) per bystander; χ_coll per nudge (pre-registered model) | 0.46 [0.05, 1.44]; χ_coll 2.69 [-0.60, 9.95] (6.5 bystanders/nudge); with day FE 0.73 [0.49, 0.97], χ_coll 4.57 [2.62, 6.76]; day FE within swarm lulls -0.45 [CI unstable: too few days] / outside 0.96 [0.88, 1.04] | day-swap 0.06 [-0.77, 0.96] | failed |
| P3 χ_act(H_men) vs χ_act(H_und), min per message-recipient | H_men -0.72 [-3.97, 1.08]; H_und 0.62 [0.23, 3.15]; ratio -1.15 | day-swap H_und -0.07 [-0.49, 0.34] | partly (H_und > 0, ratio < 2) |
| P4 χ_con(H_und), cosine | 0.016 [-0.041, 0.030] (n = 261; matched 0.017 [-0.048, 0.035]) | pseudo-true null 0.012 [0.011, 0.017] | not supported (CI includes 0) |
| P4 χ_con(H_men), cosine | 0.043 [-0.027, 0.069] (n = 15; matched -0.003 [-0.023, 0.028]) | pseudo-true null 0.007 [-0.040, 0.049] | not supported (CI includes 0) |
| P6 daily χ_con(H_und) stability | perm p (msg) 0.124 (kick-level 0.018); R₁(perm, msg) 0.24; lag-1 –; 4 days, median 42 pairs/day | constant χ | supported (R₁ < 0.5) |

Daily gauge: `data/processed/H30-operator-susceptibility/G44/daily.parquet`; figure: `figures/daily_gauge.pdf`.

## Scorecard (period-specific axes)
- C: χ_act does not beat the day-swap / zero null at the period level.
- D: the bystander (N_by / H_und) response and the pre-window placebo are unfitted checks of the mapping (see rows P2, P11).
- F: estimator validated on synthetic swarms at this period's sampling class (card, Synthetic validation).

## Notes
- 2026-10-03: folder and prediction written before the run (card Amendment A1 applies).
- 2026-10-03: round-1 results filled in from `results.json`.
- 2026-10-03: round-1 results filled in from `results.json`.
- 2026-10-03: round-1 results filled in from `results.json`.

## Round 1b (improved data, 2026-10-04)
Fixed activity bins, leading-@ nudge target, kicks at the DQ1 receiving call, past-only kick adjustment with a day fixed effect, content also with gte-modernbert. Numbers in `data/processed/H30-operator-susceptibility/r1b/G44/results.json`; verdict rule unchanged.

| Statistic | Round 1 | Round 1b |
| --- | --- | --- |
| χ_act(N_tgt), level model (r1: no FE; 1b: day FE, past-only) | -0.32 [-1.19, 0.70] (n 24) | 0.01 [-0.83, 1.65] (n 21) |
| χ_act(N_tgt) with day FE / without | -0.21 [-1.41, 0.54] | 0.32 [-0.51, 1.98] (no FE) |
| first / repeat nudge | -0.11 [-1.53, 0.80] / 0.07 [-6.00, 1.53] | 0.10 [-0.37, 1.59] / -2.90 [-5.16, 0.19] |
| bystander χ_act(N_by) | 0.46 [0.05, 1.44] | 0.07 [-0.26, 0.89] |
| χ_con(H_und) bge (gte) | 0.016 [-0.041, 0.030] | 0.012 [-0.037, 0.023] (0.016 [-0.052, 0.026]) |
| χ_con(H_men) bge (gte) | 0.043 [-0.027, 0.069] | 0.039 [-0.020, 0.057] (-0.030 [-0.065, 0.044]) |
| χ_act(H_und) | 0.62 [0.23, 3.15] | 0.01 [-0.90, 0.65] |

Round-1b prediction rows: P1 supported (point > 0); P2 supported; P3 partly (H_men > H_und, H_und CI includes 0); P4 not supported (CI includes 0); P4 not supported (CI includes 0); P6 supported (R₁ < 0.5).
