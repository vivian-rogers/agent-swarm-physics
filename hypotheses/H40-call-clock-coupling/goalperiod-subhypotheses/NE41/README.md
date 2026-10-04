# H40 × NE41: forced consolidation as an exogenous call gap (regime III, non-holdout: #37–#42, #44, #51 head)

**Verdict:** mixed
**Role:** native (exploratory)
**Period:** every regime-III non-holdout period; forced consolidations at the 41-turn cap (timing set by the scaffold). Gap at the call after a forced consolidation: median 160–190 s (q10 ≈ 80–110 s, q90 ≈ 290–410 s).

## Why this period
A forced consolidation is a summary call of a few minutes whose timing the scaffold, not the agent, sets. Messages arriving during it are read at the next call after a long exogenous gap. Wall clock: that call carries a catch-up burst proportional to the gap. Call clock: no burst.

## Prediction
*Written 2026-10-04 ~06:10 UTC (card N2), before any H40 statistic.* (i) η at post-forced-consolidation calls CI inside [−0.3, 0.3] (no catch-up); (ii) the ratio of P(reply within 10 calls of read-out) for messages that arrived during the forced consolidation (A) vs during the call before it (B) lies in [0.75, 1.33]. Confound: the context is erased at the same moment (H08: −18% to pre-erasure senders).

## Result
| Test | Observed (95% CI; random-effects over periods) | Prediction | Verdict |
| --- | --- | --- | --- |
| (i) η at later post-forced calls (5 periods with SE < 2) | +0.06 [−0.35, +0.47] | inside [−0.3, 0.3] | inconclusive (too few replies at those calls) |
| η₁: read-out wait at post-forced read-outs (8 periods) | −0.09 [−0.20, +0.01] | — | no catch-up with wait |
| Level of the post-forced read-out call vs a busy read-out (log hazard) | −0.82 [−1.01, −0.62] (× 0.44) | — | a dip, not a burst |
| (ii) A/B ratio, pooled (A: 1,273/102,254; B: 87/13,018) | 1.86 [1.50, 2.31] | [0.75, 1.33] | **failed** |
| per period A/B | 1.0–3.1 (G51 1.73, 1,011 replies) | | |

**Reading.** No catch-up: replies at the first call after a forced consolidation are 56% *lower* than at an ordinary read-out with the same batch and rank, and they do not rise with how long the message waited (η₁ −0.09). That is the opposite of the wall clock, consistent with H39/H15 (post-erasure re-orientation). The pre-registered A/B ratio failed: messages that arrived *during* the consolidation are answered more than those that arrived during the call before. Post hoc, B messages are older at read-out (median wait 200 s vs 100 s) and sit lower in the batch, so recency and burial (χ, rank) explain the direction; the ratio was not adjusted for rank.

Data: `native/N2_NE41.json`.

## Scorecard (period-specific axes)
- **E:** mixed: no catch-up (supports the call clock), raw ratio failed its band (recency, post hoc).
