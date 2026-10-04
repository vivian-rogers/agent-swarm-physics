# H30 × G05: Holiday: do whatever you like! Next goal will begin soon (2025-06-19 → 2025-06-26)

**Verdict:** mixed — content 0.023*, named 0.046; human activity ≈ 0; low power
**Role:** exploratory
**Period:** regime I · mode F · 4 agents at start · 5 active days.

## Why this period
Regime I holiday week with very dense human chat (≈ 176 messages/day over 5 days): many kicks per day, few days.

## Prediction
*Written 2026-10-03, before running on this period.*

- P3: χ_act(H_men) > χ_act(H_und), ratio ≥ 2; χ_act(H_und) > 0 (CI excluding 0 counts toward the 2-of-3 rule over G04–G06).
- P4: χ_con(H_und or H_men) > 0 with CI excluding 0, size 0.02–0.10; H_men ≥ H_und.
- P6: the daily human *content* gauge has permutation-calibrated R₁ < 0.5; the activity heterogeneity test is not run (dense chat, A1).
- Against: χ_con ≤ 0 or χ_act(H_men) ≤ χ_act(H_und).

## Result
Days: 5; kicks by class: {'H_men': 151, 'H_und': 3329}; content pairs with statements on both sides: 3352.

| Prediction | Observed | Null / reference | Verdict |
| --- | --- | --- | --- |
| P3 χ_act(H_men) vs χ_act(H_und), min per message-recipient | H_men -0.96 [-1.63, -0.46]; H_und -0.06 [-0.68, 0.21]; ratio 14.89 | day-swap H_und 0.02 [-0.11, 0.16] | failed |
| P4 χ_con(H_und), cosine | 0.023 [0.019, 0.027] (n = 3206; matched 0.028 [0.021, 0.034]) | pseudo-true null 0.001 [-0.002, 0.005] | supported |
| P4 χ_con(H_men), cosine | 0.046 [0.035, 0.054] (n = 146; matched 0.073 [0.049, 0.098]) | pseudo-true null -0.008 [-0.022, 0.007] | supported |
| P6 daily χ_con(H_und) stability | perm p (msg) 0.395 (kick-level 0.265); R₁(perm, msg) 0.04; lag-1 -0.56; 5 days, median 557 pairs/day | constant χ | supported (R₁ < 0.5) |
| P6 daily χ_con(H_men) stability | perm p (msg) 0.784 (kick-level 0.794); R₁(perm, msg) 0.00; lag-1 -0.17; 5 days, median 33 pairs/day | constant χ | supported (R₁ < 0.5) |

Daily gauge: `data/processed/H30-operator-susceptibility/G05/daily.parquet`; figure: `figures/daily_gauge.pdf`.

## Scorecard (period-specific axes)
- C: χ_act does not beat the day-swap / zero null at the period level.
- D: the bystander (N_by / H_und) response and the pre-window placebo are unfitted checks of the mapping (see rows P2, P11).
- F: estimator validated on synthetic swarms at this period's sampling class (card, Synthetic validation).

## Notes
- 2026-10-03: folder and prediction written before the run (card Amendment A1 applies).
- 2026-10-03: round-1 results filled in from `results.json`.
- 2026-10-03: round-1 results filled in from `results.json`.
- 2026-10-03: round-1 results filled in from `results.json`.
