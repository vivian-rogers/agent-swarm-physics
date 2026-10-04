# H61 × G20: Start a Substack and join the blogosphere (2025-11-17 → 2025-12-01)

**Verdict:** failed
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
**failed.** 2854 agent-seeded ideas (uncensored), 2657 on 8 forward-chained test days; 396 test ideas reached a second agent within 24 h (base rate 0.149).

| Prediction | Observed | Reference | Verdict |
| --- | --- | --- | --- |
| P1 ΔLL(F − B4) > 0, CI > 0 | -6.42 [-15.60, 2.49] millinats/idea; vs B3 -6.73 [-17.21, 2.90]; gte specificity -8.45 [-18.42, 1.12] | synthetic null size 0.07 | fail |
| P2 AUC_F > AUC_B1 | F 0.627, B1 0.501, B2 0.620, B4 0.623; Spearman ρ with reach F 0.160 vs B1 0.000 | class only | pass |
| P3 focus < 0; in-degree CI ∋ 0; receptive > 0 | focus +0.01 [-0.15, +0.17]; in-degree +0.33 [+0.15, +0.51]; receptive +0.04 [-0.09, +0.17]; specificity -0.09 [-0.21, +0.04]; length -0.11 [-0.29, +0.06]; addressed -0.06 [-0.19, +0.06]; threaded +0.14 [+0.03, +0.25] (standardised log-odds, in-sample) | 0 | descriptive |
| P4 top-decile lift for Y ≥ 2 | 2.04 (Y3: 2.80) | 1 | pass |
| P5 G_read > G_unread | not testable (238 read-5, 12 unread-5 events) | synthetic: centred on 0 (SD 0.03) | n/a |

Data: `data/processed/H61-contagiousness-at-first-use/G20/` (`ideas.parquet`, `pred_y.parquet`); numbers from `analysis/explore.py` → `results/periods.json`.

## Scorecard (period-specific axes)
C (adequacy): F vs the strongest baseline B4 on held-out days, ΔLL -6.42 [-15.60, 2.49]. D (unfitted): held-out ranking, AUC 0.627, lift 2.04. H (rivals): class-only AUC 0.501, poster-only 0.620. E, G: not informed by this replication.

## Notes
- Ideas whose 24-h window runs past the last non-holdout agent message are dropped (censoring).
