# H61 × G51: Each agent: Maximize your assigned goal! (2026-07-06 → 2026-09-20)

**Verdict:** supported
**Role:** replication
**Period:** regime III · mode I/K · 21 agents · non-holdout days only (held-out days masked with `holdout_mask`).

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
**supported.** 50471 agent-seeded ideas (uncensored), 47748 on 43 forward-chained test days; 7530 test ideas reached a second agent within 24 h (base rate 0.158).

| Prediction | Observed | Reference | Verdict |
| --- | --- | --- | --- |
| P1 ΔLL(F − B4) > 0, CI > 0 | 5.52 [4.05, 7.06] millinats/idea; vs B3 5.55 [3.96, 7.11]; gte specificity 5.16 [3.56, 6.85] | synthetic null size 0.07 | pass |
| P2 AUC_F > AUC_B1 | F 0.701, B1 0.584, B2 0.647, B4 0.685; Spearman ρ with reach F 0.254 vs B1 0.105 | class only | pass |
| P3 focus < 0; in-degree CI ∋ 0; receptive > 0 | focus -0.13 [-0.16, -0.09]; in-degree -0.07 [-0.13, -0.02]; receptive +0.00 [-0.02, +0.03]; specificity -0.11 [-0.14, -0.08]; length -0.24 [-0.28, -0.20]; addressed +0.16 [+0.12, +0.19]; threaded +0.10 [+0.07, +0.13] (standardised log-odds, in-sample) | 0 | descriptive |
| P4 top-decile lift for Y ≥ 2 | 2.54 (Y3: 2.82) | 1 | pass |
| P5 G_read > G_unread | G_read 0.124 vs G_unread 0.095; difference 0.028 [-0.062, 0.113] | synthetic: centred on 0 (SD 0.03) | pass |

Data: `data/processed/H61-contagiousness-at-first-use/G51/` (`ideas.parquet`, `pred_y.parquet`); numbers from `analysis/explore.py` → `results/periods.json`.

## Scorecard (period-specific axes)
C (adequacy): F vs the strongest baseline B4 on held-out days, ΔLL 5.52 [4.05, 7.06]. D (unfitted): held-out ranking, AUC 0.701, lift 2.54. H (rivals): class-only AUC 0.584, poster-only 0.647. E, G: not informed by this replication.

## Notes
- Ideas whose 24-h window runs past the last non-holdout agent message are dropped (censoring).
