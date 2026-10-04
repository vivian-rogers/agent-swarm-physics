# H30 × G13: Design, run and write up a human subjects experiment (2025-09-08 → 2025-09-22)

**Verdict:** mixed — content 0.036*, named 0.066; human activity ≈ 0
**Verdict (1b):** mixed (r1 mixed; fixed bins, receiving call)
**Role:** exploratory
**Period:** regime I · mode C · 6 agents at start · 10 active days.

## Why this period
Regime I, 6 agents, a human-subjects experiment week with ≈ 5 human messages/day: a low-dose human period (10 days).

## Prediction
*Written 2026-10-03, before running on this period.*

- P3: χ_act(H_men) > χ_act(H_und), ratio ≥ 2; χ_act(H_und) > 0 (CI excluding 0 counts toward the 2-of-3 rule over G04–G06).
- P4: χ_con(H_und or H_men) > 0 with CI excluding 0, size 0.02–0.10; H_men ≥ H_und.
- P6: the daily human *content* gauge has permutation-calibrated R₁ < 0.5; the activity heterogeneity test is not run (dense chat, A1).
- Against: χ_con ≤ 0 or χ_act(H_men) ≤ χ_act(H_und).

## Result
Days: 10; kicks by class: {'H_und': 243, 'H_men': 33}; content pairs with statements on both sides: 250.

| Prediction | Observed | Null / reference | Verdict |
| --- | --- | --- | --- |
| P3 χ_act(H_men) vs χ_act(H_und), min per message-recipient | H_men -1.00 [-2.97, 0.01]; H_und -0.34 [-1.88, 0.89]; ratio 2.94 | day-swap H_und -0.05 [-0.63, 0.56] | failed |
| P4 χ_con(H_und), cosine | 0.036 [0.015, 0.046] (n = 217; matched 0.032 [0.011, 0.042]) | pseudo-true null 0.002 [-0.005, 0.024] | supported |
| P4 χ_con(H_men), cosine | 0.066 [0.053, 0.102] (n = 33; matched 0.069 [0.057, 0.107]) | pseudo-true null -0.014 [-0.043, 0.029] | supported |
| P6 daily χ_con(H_und) stability | perm p (msg) 0.739 (kick-level 0.517); R₁(perm, msg) 0.00; lag-1 0.29; 8 days, median 14 pairs/day | constant χ | supported (R₁ < 0.5) |
| P6 daily χ_con(H_men) stability | perm p (msg) 0.974 (kick-level 0.970); R₁(perm, msg) 0.00; lag-1 –; 4 days, median 4 pairs/day | constant χ | supported (R₁ < 0.5) |

Daily gauge: `data/processed/H30-operator-susceptibility/G13/daily.parquet`; figure: `figures/daily_gauge.pdf`.

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
Fixed activity bins, leading-@ nudge target, kicks at the DQ1 receiving call, past-only kick adjustment with a day fixed effect, content also with gte-modernbert. Numbers in `data/processed/H30-operator-susceptibility/r1b/G13/results.json`; verdict rule unchanged.

| Statistic | Round 1 | Round 1b |
| --- | --- | --- |
| χ_con(H_und) bge (gte) | 0.036 [0.015, 0.046] | 0.033 [0.012, 0.044] (0.034 [0.018, 0.063]) |
| χ_con(H_men) bge (gte) | 0.066 [0.053, 0.102] | 0.061 [0.045, 0.102] (0.074 [0.027, 0.098]) |
| χ_act(H_und) | -0.34 [-1.88, 0.89] | -0.47 [-1.14, 0.15] |

Round-1b prediction rows: P3 partly (H_men > H_und, H_und CI includes 0); P4 supported; P4 supported; P6 supported (R₁ < 0.5); P6 supported (R₁ < 0.5).
