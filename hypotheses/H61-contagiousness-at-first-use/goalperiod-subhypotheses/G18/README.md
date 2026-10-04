# H61 × G18: Reduce global poverty as much as you can (2025-10-20 → 2025-11-03)

**Verdict:** failed
**Role:** replication
**Period:** regime I · mode C · 7 agents · non-holdout days only (held-out days masked with `holdout_mask`).

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
**failed.** 2976 agent-seeded ideas (uncensored), 2865 on 8 forward-chained test days; 558 test ideas reached a second agent within 24 h (base rate 0.195).

| Prediction | Observed | Reference | Verdict |
| --- | --- | --- | --- |
| P1 ΔLL(F − B4) > 0, CI > 0 | -37.17 [-125.82, 22.10] millinats/idea; vs B3 -31.95 [-125.02, 36.84]; gte specificity -56.94 [-163.50, 14.94] | synthetic null size 0.07 | fail |
| P2 AUC_F > AUC_B1 | F 0.512, B1 0.559, B2 0.522, B4 0.546; Spearman ρ with reach F 0.026 vs B1 0.082 | class only | fail |
| P3 focus < 0; in-degree CI ∋ 0; receptive > 0 | focus +0.33 [+0.10, +0.55]; in-degree -0.72 [-1.05, -0.39]; receptive -0.29 [-0.39, -0.18]; specificity +0.09 [-0.02, +0.20]; length -0.37 [-0.60, -0.15]; addressed +0.09 [-0.03, +0.21]; threaded +0.16 [+0.05, +0.27] (standardised log-odds, in-sample) | 0 | descriptive |
| P4 top-decile lift for Y ≥ 2 | 1.69 (Y3: 2.28) | 1 | fail |
| P5 G_read > G_unread | G_read 0.067 vs G_unread 0.062; difference 0.005 [-0.217, 0.221] | synthetic: centred on 0 (SD 0.03) | pass |

Data: `data/processed/H61-contagiousness-at-first-use/G18/` (`ideas.parquet`, `pred_y.parquet`); numbers from `analysis/explore.py` → `results/periods.json`.

## Scorecard (period-specific axes)
C (adequacy): F vs the strongest baseline B4 on held-out days, ΔLL -37.17 [-125.82, 22.10]. D (unfitted): held-out ranking, AUC 0.512, lift 1.69. H (rivals): class-only AUC 0.559, poster-only 0.522. E, G: not informed by this replication.

## Notes
- Ideas whose 24-h window runs past the last non-holdout agent message are dropped (censoring).
