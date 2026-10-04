# H61 × G39: Build your own interactive world! (2026-04-27 → 2026-05-04)

**Verdict:** mixed
**Role:** replication
**Period:** regime III · mode I · 15 agents · non-holdout days only (held-out days masked with `holdout_mask`).

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
**mixed.** 2368 agent-seeded ideas (uncensored), 2061 on 3 forward-chained test days; 112 test ideas reached a second agent within 24 h (base rate 0.054).

| Prediction | Observed | Reference | Verdict |
| --- | --- | --- | --- |
| P1 ΔLL(F − B4) > 0, CI > 0 | 6.17 [-8.06, 19.21] millinats/idea; vs B3 2.49 [-18.42, 18.36]; gte specificity -0.21 [-16.96, 14.32] | synthetic null size 0.07 | fail |
| P2 AUC_F > AUC_B1 | F 0.638, B1 0.513, B2 0.557, B4 0.571; Spearman ρ with reach F 0.109 vs B1 0.011 | class only | pass |
| P3 focus < 0; in-degree CI ∋ 0; receptive > 0 | focus -0.48 [-0.77, -0.18]; in-degree -0.03 [-0.33, +0.26]; receptive -0.14 [-0.31, +0.04]; specificity -0.31 [-0.53, -0.10]; length +0.34 [+0.01, +0.68]; addressed -0.06 [-0.28, +0.17]; threaded +0.16 [-0.01, +0.33] (standardised log-odds, in-sample) | 0 | descriptive |
| P4 top-decile lift for Y ≥ 2 | 2.23 (Y3: 5.30) | 1 | pass |
| P5 G_read > G_unread | not testable (36 read-5, 0 unread-5 events) | synthetic: centred on 0 (SD 0.03) | n/a |

Data: `data/processed/H61-contagiousness-at-first-use/G39/` (`ideas.parquet`, `pred_y.parquet`); numbers from `analysis/explore.py` → `results/periods.json`.

## Scorecard (period-specific axes)
C (adequacy): F vs the strongest baseline B4 on held-out days, ΔLL 6.17 [-8.06, 19.21]. D (unfitted): held-out ranking, AUC 0.638, lift 2.23. H (rivals): class-only AUC 0.513, poster-only 0.557. E, G: not informed by this replication.

## Notes
- Ideas whose 24-h window runs past the last non-holdout agent message are dropped (censoring).
