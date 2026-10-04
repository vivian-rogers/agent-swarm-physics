# H61 × G38: Choose a charity and raise as much money as you can for it (2026-04-02 → 2026-04-27)

**Verdict:** supported
**Role:** replication
**Period:** regime III · mode C · 12 agents · non-holdout days only (held-out days masked with `holdout_mask`).

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
**supported.** 7194 agent-seeded ideas (uncensored), 6625 on 15 forward-chained test days; 1402 test ideas reached a second agent within 24 h (base rate 0.212).

| Prediction | Observed | Reference | Verdict |
| --- | --- | --- | --- |
| P1 ΔLL(F − B4) > 0, CI > 0 | 6.33 [3.01, 9.72] millinats/idea; vs B3 5.84 [2.03, 9.60]; gte specificity 6.45 [3.22, 9.82] | synthetic null size 0.07 | pass |
| P2 AUC_F > AUC_B1 | F 0.801, B1 0.675, B2 0.780, B4 0.789; Spearman ρ with reach F 0.439 vs B1 0.267 | class only | pass |
| P3 focus < 0; in-degree CI ∋ 0; receptive > 0 | focus -0.26 [-0.35, -0.16]; in-degree +0.01 [-0.18, +0.20]; receptive +0.15 [+0.07, +0.23]; specificity -0.04 [-0.12, +0.05]; length -0.20 [-0.31, -0.10]; addressed -0.07 [-0.15, +0.01]; threaded +0.01 [-0.06, +0.08] (standardised log-odds, in-sample) | 0 | descriptive |
| P4 top-decile lift for Y ≥ 2 | 3.52 (Y3: 5.66) | 1 | pass |
| P5 G_read > G_unread | G_read 0.121 vs G_unread 0.119; difference 0.002 [-0.133, 0.111] | synthetic: centred on 0 (SD 0.03) | pass |

Data: `data/processed/H61-contagiousness-at-first-use/G38/` (`ideas.parquet`, `pred_y.parquet`); numbers from `analysis/explore.py` → `results/periods.json`.

## Scorecard (period-specific axes)
C (adequacy): F vs the strongest baseline B4 on held-out days, ΔLL 6.33 [3.01, 9.72]. D (unfitted): held-out ranking, AUC 0.801, lift 3.52. H (rivals): class-only AUC 0.675, poster-only 0.780. E, G: not informed by this replication.

## Notes
- Ideas whose 24-h window runs past the last non-holdout agent message are dropped (censoring).
