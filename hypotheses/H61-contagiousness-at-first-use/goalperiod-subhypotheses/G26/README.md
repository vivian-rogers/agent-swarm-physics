# H61 × G26: Elect a village leader. They choose this week’s goal! (2026-01-05 → 2026-01-12)

**Verdict:** failed
**Role:** native (with the replication estimator)
**Period:** regime I · mode C · 10 agents · non-holdout days only (held-out days masked with `holdout_mask`).

## Why this period
Replication layer: the common H61 estimator (forward-chained fitness model of idea spread at first use) on every period H34 analysed, so periods compare as points on a phase diagram. This period also hosts a native test (section below), with its own dated prediction.

## Native test: the elected leader's ideas (DQ6)
*Prediction written 2026-10-04 19:30 UTC, before any native statistic.* H34 found that the elected leader (agent 17, DQ6 `leader` term1 from 2026-01-05 19:35:22 UTC) seeds 7.5× more new markers per message and that each spreads less (P(s ≥ 2) ratio 0.36). Ideas seeded during the leader's term (to the end of the non-holdout period) by the leader vs by the other agents; logistic model for Y without poster terms.
- **N26-a (raw):** the leader's unadjusted odds ratio for Y is < 1 (expected 0.3–0.5).
- **N26-b (features explain it):** adjusted for class, focus, seed length, specificity, receptive fraction, addressed, threaded, kickoff day and room size, the leader OR rises to ≥ 0.7, or its 95% CI includes 1. **Counts against:** adjusted OR ≤ 0.5 with upper CI < 0.7 (authority, or something else about the leader, lowers fitness beyond the seed features).
- Credence 0.45. Verdict: supported = N26-a and N26-b pass; failed = N26-b fails; mixed = otherwise.

*Run 2026-10-04 after the prediction above.* Leader = agent 17; ideas seeded from 2026-01-05 19:35:22.589746+00:00 to the end of the non-holdout period: 1513 (696 by the leader, from 86 messages; 817 by the other agents, from 337 messages). Mean novel items per seeding item's message: leader 32.5, others 4.7.

| Prediction | Observed (OR, seed-message cluster bootstrap 95% CI) | Verdict |
| --- | --- | --- |
| N26-a raw OR < 1 | 0.22 [0.12, 0.39]; P(Y) leader 0.052 vs others 0.196 | pass |
| N26-b adjusted OR ≥ 0.7 or CI ∋ 1 | 0.28 [0.09, 0.53] (Wald [0.17, 0.48]) | fail |

**Native verdict: failed.**

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
**failed.** 1658 agent-seeded ideas (uncensored), 690 on 3 forward-chained test days; 116 test ideas reached a second agent within 24 h (base rate 0.168).

| Prediction | Observed | Reference | Verdict |
| --- | --- | --- | --- |
| P1 ΔLL(F − B4) > 0, CI > 0 | -19.41 [-38.68, -2.44] millinats/idea; vs B3 -22.86 [-41.97, -3.57]; gte specificity -13.86 [-32.11, 3.38] | synthetic null size 0.07 | fail |
| P2 AUC_F > AUC_B1 | F 0.621, B1 0.532, B2 0.625, B4 0.633; Spearman ρ with reach F 0.164 vs B1 0.047 | class only | pass |
| P3 focus < 0; in-degree CI ∋ 0; receptive > 0 | focus +0.25 [-0.09, +0.59]; in-degree -0.01 [-0.23, +0.21]; receptive -0.14 [-0.30, +0.03]; specificity -0.16 [-0.33, +0.00]; length -0.48 [-0.84, -0.12]; addressed -0.01 [-0.19, +0.17]; threaded +0.17 [+0.01, +0.34] (standardised log-odds, in-sample) | 0 | descriptive |
| P4 top-decile lift for Y ≥ 2 | 0.95 (Y3: 0.80) | 1 | fail |
| P5 G_read > G_unread | not testable (63 read-5, 5 unread-5 events) | synthetic: centred on 0 (SD 0.03) | n/a |

Data: `data/processed/H61-contagiousness-at-first-use/G26/` (`ideas.parquet`, `pred_y.parquet`); numbers from `analysis/explore.py` → `results/periods.json`.

Replication verdict for this period: **failed**.

## Scorecard (period-specific axes)
C (adequacy): F vs the strongest baseline B4 on held-out days, ΔLL -19.41 [-38.68, -2.44]. D (unfitted): held-out ranking, AUC 0.621, lift 0.95. H (rivals): class-only AUC 0.532, poster-only 0.625. E, G: not informed by this replication.

## Notes
- Ideas whose 24-h window runs past the last non-holdout agent message are dropped (censoring).
