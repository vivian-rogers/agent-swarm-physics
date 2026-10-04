# H30 × G06: Create your own merch store. Whichever agent's store makes the most profit wins! (2025-06-26 → 2025-07-16)

**Verdict:** mixed — content 0.012*, named 0.030; human activity ≈ 0
**Role:** exploratory
**Period:** regime I · mode K · 4 agents at start · 14 active days.

## Why this period
Regime I merch-store competition, 15 days, ≈ 30 human messages/day: a second long human-dense daily series.

## Prediction
*Written 2026-10-03, before running on this period.*

- P3: χ_act(H_men) > χ_act(H_und), ratio ≥ 2; χ_act(H_und) > 0 (CI excluding 0 counts toward the 2-of-3 rule over G04–G06).
- P4: χ_con(H_und or H_men) > 0 with CI excluding 0, size 0.02–0.10; H_men ≥ H_und.
- P6: the daily human *content* gauge has permutation-calibrated R₁ < 0.5; the activity heterogeneity test is not run (dense chat, A1).
- Against: χ_con ≤ 0 or χ_act(H_men) ≤ χ_act(H_und).

## Result
Days: 15; kicks by class: {'H_und': 1657, 'H_men': 67}; content pairs with statements on both sides: 1624.

| Prediction | Observed | Null / reference | Verdict |
| --- | --- | --- | --- |
| P3 χ_act(H_men) vs χ_act(H_und), min per message-recipient | H_men -0.67 [-1.77, 1.82]; H_und -0.31 [-0.80, 0.96]; ratio 2.13 | day-swap H_und -0.01 [-0.26, 0.19] | failed |
| P4 χ_con(H_und), cosine | 0.012 [0.005, 0.037] (n = 1562; matched 0.013 [0.005, 0.046]) | pseudo-true null -0.000 [-0.008, 0.006] | sign supported, size outside 0.02–0.10 |
| P4 χ_con(H_men), cosine | 0.030 [-0.027, 0.099] (n = 62; matched 0.062 [-0.008, 0.148]) | pseudo-true null 0.008 [-0.019, 0.023] | not supported (CI includes 0) |
| P6 daily χ_con(H_und) stability | perm p (msg) 0.002 (kick-level 0.002); R₁(perm, msg) 0.53; lag-1 -0.17; 9 days, median 92 pairs/day | constant χ | failed (R₁ ≥ 0.5) |
| P6 daily χ_con(H_men) stability | perm p (msg) 0.034 (kick-level 0.032); R₁(perm, msg) 0.49; lag-1 –; 4 days, median 16 pairs/day | constant χ | supported (R₁ < 0.5) |

Daily gauge: `data/processed/H30-operator-susceptibility/G06/daily.parquet`; figure: `figures/daily_gauge.pdf`.

## Scorecard (period-specific axes)
- C: χ_act does not beat the day-swap / zero null at the period level.
- D: the bystander (N_by / H_und) response and the pre-window placebo are unfitted checks of the mapping (see rows P2, P11).
- F: estimator validated on synthetic swarms at this period's sampling class (card, Synthetic validation).

## Notes
- 2026-10-03: folder and prediction written before the run (card Amendment A1 applies).
- 2026-10-03: round-1 results filled in from `results.json`.
- 2026-10-03: round-1 results filled in from `results.json`.
- 2026-10-03: round-1 results filled in from `results.json`.
