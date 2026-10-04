# H30 × G04: Write a story and celebrate it with 100 people in person (2025-05-15 → 2025-06-19)

**Verdict:** mixed — content 0.030*, named 0.033; human activity ≈ 0
**Verdict (1b):** mixed (r1 mixed; fixed bins, receiving call)
**Role:** exploratory
**Period:** regime I · mode C · 4 agents at start · 25 active days.

## Why this period
Regime I, 4 agents, 2 h days, public chat: the densest human input in the data (≈ 69 human messages/day, 336 naming an agent). The best period for the human content gauge and a long (25-day) daily series.

## Prediction
*Written 2026-10-03, before running on this period.*

- P3: χ_act(H_men) > χ_act(H_und), ratio ≥ 2; χ_act(H_und) > 0 (CI excluding 0 counts toward the 2-of-3 rule over G04–G06).
- P4: χ_con(H_und or H_men) > 0 with CI excluding 0, size 0.02–0.10; H_men ≥ H_und.
- P6: the daily human *content* gauge has permutation-calibrated R₁ < 0.5; the activity heterogeneity test is not run (dense chat, A1).
- Against: χ_con ≤ 0 or χ_act(H_men) ≤ χ_act(H_und).

## Result
Days: 25; kicks by class: {'H_und': 6434, 'H_men': 345}; content pairs with statements on both sides: 6067.

| Prediction | Observed | Null / reference | Verdict |
| --- | --- | --- | --- |
| P3 χ_act(H_men) vs χ_act(H_und), min per message-recipient | H_men -0.42 [-1.11, 0.38]; H_und -0.21 [-0.64, 0.17]; ratio 2.03 | day-swap H_und -0.06 [-0.29, 0.12] | failed |
| P4 χ_con(H_und), cosine | 0.030 [0.025, 0.035] (n = 5730; matched 0.035 [0.029, 0.040]) | pseudo-true null -0.001 [-0.004, 0.001] | supported |
| P4 χ_con(H_men), cosine | 0.033 [0.021, 0.049] (n = 337; matched 0.043 [0.030, 0.060]) | pseudo-true null -0.004 [-0.013, 0.002] | supported |
| P6 daily χ_con(H_und) stability | perm p (msg) 0.004 (kick-level 0.002); R₁(perm, msg) 0.28; lag-1 0.20; 25 days, median 170 pairs/day | constant χ | supported (R₁ < 0.5) |
| P6 daily χ_con(H_men) stability | perm p (msg) 0.012 (kick-level 0.018); R₁(perm, msg) 0.38; lag-1 0.32; 23 days, median 13 pairs/day | constant χ | supported (R₁ < 0.5) |

Daily gauge: `data/processed/H30-operator-susceptibility/G04/daily.parquet`; figure: `figures/daily_gauge.pdf`.

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
Fixed activity bins, leading-@ nudge target, kicks at the DQ1 receiving call, past-only kick adjustment with a day fixed effect, content also with gte-modernbert. Numbers in `data/processed/H30-operator-susceptibility/r1b/G04/results.json`; verdict rule unchanged.

| Statistic | Round 1 | Round 1b |
| --- | --- | --- |
| χ_con(H_und) bge (gte) | 0.030 [0.025, 0.035] | 0.027 [0.022, 0.032] (0.028 [0.024, 0.033]) |
| χ_con(H_men) bge (gte) | 0.033 [0.021, 0.049] | 0.033 [0.020, 0.047] (0.044 [0.031, 0.060]) |
| χ_act(H_und) | -0.21 [-0.64, 0.17] | 0.15 [-0.09, 0.35] |

Round-1b prediction rows: P3 failed; P4 supported; P4 supported; P6 supported (R₁ < 0.5); P6 supported (R₁ < 0.5).
