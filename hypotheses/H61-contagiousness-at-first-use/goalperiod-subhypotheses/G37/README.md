# H61 × G37: Pick your own goal! (2026-03-30 → 2026-04-02)

**Verdict:** n/a
**Role:** replication
**Period:** regime III · mode F · 13 agents · non-holdout days only (held-out days masked with `holdout_mask`).

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
**n/a.** 145 test ideas, 33 that reached a second agent (eligibility: ≥ 300 and ≥ 20).

## Scorecard (period-specific axes)
Not informative (ineligible).

## Notes
- Ideas whose 24-h window runs past the last non-holdout agent message are dropped (censoring).
