# H61 × G35: Test your game to make it as fun and functional as you can! (2026-03-16 → 2026-03-23)

**Verdict:** supported
**Role:** native (with the replication estimator)
**Period:** regime II · mode C · 13 agents · non-holdout days only (held-out days masked with `holdout_mask`).

## Why this period
Replication layer: the common H61 estimator (forward-chained fitness model of idea spread at first use) on every period H34 analysed, so periods compare as points on a phase diagram. This period also hosts a native test (section below), with its own dated prediction.

## Native test: designated lead designers (DQ6)
*Prediction written 2026-10-04 19:30 UTC, before any native statistic.* DQ6 names two lead designers per day on 2026-03-16 to 03-18 (6 agent-days). Ideas seeded by an agent on its lead day vs ideas seeded on the same days by others. Two models: features without poster terms, and features + poster terms (the role effect within agent).
- **N35-a (raw):** unadjusted OR for Y of lead-day seeds vs others: 95% CI includes 1 (H34: 1.11 [0.82, 1.45]).
- **N35-b (role adds nothing beyond features and identity):** with features + poster terms, the lead-day OR has a 95% CI that includes 1. **Counts against:** OR > 1.5 with lower CI > 1.
- Credence 0.6. Verdict: supported = N35-b passes; failed = N35-b fails; mixed = N35-b passes but N35-a fails.

*Run 2026-10-04 after the prediction above.* Lead-designer days 2026-03-16 → 03-18: 1848 seeded ideas, 227 seeded by an agent on its lead day.

| Prediction | Observed (OR, seed-message cluster bootstrap 95% CI) | Verdict |
| --- | --- | --- |
| N35-a raw OR CI ∋ 1 | 1.22 [0.82, 1.70]; P(Y) lead 0.260 vs others 0.223 | pass |
| N35-b OR with features + poster terms, CI ∋ 1 | 1.39 [0.86, 2.35] (Wald [0.90, 2.14]) | pass |

**Native verdict: supported.**

## Prediction
*Written 2026-10-04 19:26 UTC, before running on this period* (after the card's predictions at 19:15 UTC and synthetic amendment A1; first written 19:26, rewritten with the native sections at 19:30 UTC; no H61 feature–outcome statistic had been computed for any period).

| # | Prediction here | Counts against |
| --- | --- | --- |
| P1 | Seed features forecast spread beyond the strongest baseline: ΔLL(F − B4) > 0 with lower 95% CI > 0 (B4 = class + poster + kickoff day + room size; A1) | CI includes 0 or ΔLL ≤ 0 |
| P2 | AUC of F for "reaches a second agent within 24 h" exceeds the class-only AUC | AUC_F ≤ AUC_B1 |
| P3 | Focus (log novel items in the seed message) < 0; poster reply in-degree CI includes 0; receptive fraction > 0 | focus ≥ 0 with CI; in-degree CI > 0 |
| P4 | Top-decile lift for Y ≥ 2 | lift < 1.5 |
| P5 | If ≥ 15 read-5 and ≥ 15 unread-5 events: the F − B1 AUC gain is larger for read-5 than for unread-5 adoption | gain for unread-5 ≥ gain for read-5 |

**Verdict rule (card, with A1):** supported = ΔLL(F − B4) lower 95% CI > 0 and top-decile lift for Y ≥ 1.5; failed = ΔLL(F − B4) ≤ 0; mixed = otherwise; n/a = < 300 test ideas or < 20 positive test ideas.

## Result (replication estimator)
**supported.** 2450 agent-seeded ideas (uncensored), 1682 on 3 forward-chained test days; 316 test ideas reached a second agent within 24 h (base rate 0.188).

| Prediction | Observed | Reference | Verdict |
| --- | --- | --- | --- |
| P1 ΔLL(F − B4) > 0, CI > 0 | -6.58 [-15.48, 2.10] millinats/idea; vs B3 -1.96 [-10.48, 6.87]; gte specificity -5.47 [-13.72, 3.22] | synthetic null size 0.07 | fail |
| P2 AUC_F > AUC_B1 | F 0.619, B1 0.539, B2 0.617, B4 0.627; Spearman ρ with reach F 0.165 vs B1 0.053 | class only | pass |
| P3 focus < 0; in-degree CI ∋ 0; receptive > 0 | focus +0.02 [-0.13, +0.16]; in-degree +0.15 [-0.00, +0.31]; receptive -0.01 [-0.13, +0.11]; specificity +0.00 [-0.10, +0.11]; length -0.26 [-0.41, -0.10]; addressed -0.04 [-0.16, +0.09]; threaded +0.06 [-0.06, +0.17] (standardised log-odds, in-sample) | 0 | descriptive |
| P4 top-decile lift for Y ≥ 2 | 2.09 (Y3: 2.68) | 1 | pass |
| P5 G_read > G_unread | not testable (178 read-5, 12 unread-5 events) | synthetic: centred on 0 (SD 0.03) | n/a |

Data: `data/processed/H61-contagiousness-at-first-use/G35/` (`ideas.parquet`, `pred_y.parquet`); numbers from `analysis/explore.py` → `results/periods.json`.

Replication verdict for this period: **failed**.

## Scorecard (period-specific axes)
C (adequacy): F vs the strongest baseline B4 on held-out days, ΔLL -6.58 [-15.48, 2.10]. D (unfitted): held-out ranking, AUC 0.619, lift 2.09. H (rivals): class-only AUC 0.539, poster-only 0.617. E, G: not informed by this replication.

## Notes
- Ideas whose 24-h window runs past the last non-holdout agent message are dropped (censoring).
