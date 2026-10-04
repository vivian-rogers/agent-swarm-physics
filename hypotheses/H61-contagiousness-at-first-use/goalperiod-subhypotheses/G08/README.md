# H61 × G08: Design the AI Village benchmark for open-ended goal pursuit – and test yourselves on it! (2025-07-18 → 2025-08-13)

**Verdict:** supported
**Role:** replication
**Period:** regime I · mode C · 4 agents · non-holdout days only (held-out days masked with `holdout_mask`).

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
**supported.** 1515 agent-seeded ideas (uncensored), 1357 on 15 forward-chained test days; 56 test ideas reached a second agent within 24 h (base rate 0.041).

| Prediction | Observed | Reference | Verdict |
| --- | --- | --- | --- |
| P1 ΔLL(F − B4) > 0, CI > 0 | 11.82 [3.14, 21.36] millinats/idea; vs B3 15.34 [6.23, 23.95]; gte specificity 13.51 [2.60, 23.18] | synthetic null size 0.07 | pass |
| P2 AUC_F > AUC_B1 | F 0.629, B1 0.575, B2 0.492, B4 0.500; Spearman ρ with reach F 0.089 vs B1 0.051 | class only | pass |
| P3 focus < 0; in-degree CI ∋ 0; receptive > 0 | focus -0.11 [-0.41, +0.20]; in-degree +0.40 [+0.11, +0.69]; receptive +0.43 [+0.03, +0.82]; specificity -0.07 [-0.34, +0.21]; length -0.06 [-0.38, +0.25]; addressed +0.02 [-0.21, +0.24]; threaded +0.46 [+0.26, +0.65] (standardised log-odds, in-sample) | 0 | descriptive |
| P4 top-decile lift for Y ≥ 2 | 1.78 (Y3: 1.43) | 1 | fail |
| P5 G_read > G_unread | not testable (0 read-5, 0 unread-5 events) | synthetic: centred on 0 (SD 0.03) | n/a |

Data: `data/processed/H61-contagiousness-at-first-use/G08/` (`ideas.parquet`, `pred_y.parquet`); numbers from `analysis/explore.py` → `results/periods.json`.

## Scorecard (period-specific axes)
C (adequacy): F vs the strongest baseline B4 on held-out days, ΔLL 11.82 [3.14, 21.36]. D (unfitted): held-out ranking, AUC 0.629, lift 1.78. H (rivals): class-only AUC 0.575, poster-only 0.492. E, G: not informed by this replication.

## Notes
- Ideas whose 24-h window runs past the last non-holdout agent message are dropped (censoring).
