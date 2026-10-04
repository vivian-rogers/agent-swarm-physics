# H61 × G21: Forecast the abilities and effects of AI (2025-12-01 → 2025-12-08)

**Verdict:** mixed
**Role:** replication
**Period:** regime I · mode I · 8 agents · non-holdout days only (held-out days masked with `holdout_mask`).

## Why this period
Replication layer: the common H61 estimator (forward-chained fitness model of idea spread at first use) on every period H34 analysed, so periods compare as points on a phase diagram.

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

## Result
**mixed.** 1542 agent-seeded ideas (uncensored), 1244 on 3 forward-chained test days; 156 test ideas reached a second agent within 24 h (base rate 0.125).

| Prediction | Observed | Reference | Verdict |
| --- | --- | --- | --- |
| P1 ΔLL(F − B4) > 0, CI > 0 | 23.31 [-12.35, 52.92] millinats/idea; vs B3 25.57 [-7.72, 57.02]; gte specificity 22.95 [-11.83, 54.17] | synthetic null size 0.07 | fail |
| P2 AUC_F > AUC_B1 | F 0.659, B1 0.508, B2 0.503, B4 0.555; Spearman ρ with reach F 0.183 vs B1 0.010 | class only | pass |
| P3 focus < 0; in-degree CI ∋ 0; receptive > 0 | focus -0.05 [-0.35, +0.24]; in-degree +0.07 [-0.17, +0.31]; receptive -0.09 [-0.30, +0.12]; specificity -0.02 [-0.20, +0.15]; length -0.79 [-1.14, -0.44]; addressed +0.03 [-0.14, +0.20]; threaded +0.09 [-0.07, +0.25] (standardised log-odds, in-sample) | 0 | descriptive |
| P4 top-decile lift for Y ≥ 2 | 2.25 (Y3: 2.47) | 1 | pass |
| P5 G_read > G_unread | not testable (25 read-5, 0 unread-5 events) | synthetic: centred on 0 (SD 0.03) | n/a |

Data: `data/processed/H61-contagiousness-at-first-use/G21/` (`ideas.parquet`, `pred_y.parquet`); numbers from `analysis/explore.py` → `results/periods.json`.

## Scorecard (period-specific axes)
C (adequacy): F vs the strongest baseline B4 on held-out days, ΔLL 23.31 [-12.35, 52.92]. D (unfitted): held-out ranking, AUC 0.659, lift 2.25. H (rivals): class-only AUC 0.508, poster-only 0.503. E, G: not informed by this replication.

## Notes
- Ideas whose 24-h window runs past the last non-holdout agent message are dropped (censoring).
