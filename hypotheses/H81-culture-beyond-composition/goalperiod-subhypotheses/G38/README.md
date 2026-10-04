# H81 × G38: goal period #38 (2026-04-02 → 2026-04-24, non-holdout days)

**Verdict:** descriptive
**Role:** replication
**Period:** regime III · 14 eligible agents · 4 calendar-week block(s). Splits inside the period: 38b (ne:NE17), 38c (roster_join:Claude Opus 4.7), 38d (ne:NE18), 38e (roster_join:Kimi K2.6).

## Why this period
Every non-holdout goal period of regimes I and III is a replication point for the equal-time collective share κ and a node of the regime-level cross-goal slow-mode analysis (the card's exception (c)).

## Prediction
*Written 2026-10-04 20:05 UTC in the card (P1), before any real-data statistic; this folder was generated after the run.*
- P1 (descriptive): κ above its sign-flip band (field leakage and contemporaneous convergence make it positive). Not a culture claim.
- The slow-mode predictions (P2, P3) are regime-level; this period's neighbour similarities are listed for reference.

## Result
| Quantity | bge | gte |
| --- | --- | --- |
| κ (equal time) [95% jackknife] | +0.170 ± 0.121 | +0.175 ± 0.114 |
| sign-flip null band | [-0.034, 0.055] | [-0.034, 0.047] |
| excess variance ratio ‖u‖² / floor | 2.99 | 3.06 |
| mean similarity to blocks of other goals ≤ 14 d away (pairs) | -0.004 (7) | -0.005 (7) |
| mean similarity to blocks of other goals ≥ 42 d away (pairs) | -0.043 (41) | -0.010 (41) |

P1 here: κ above the band in both models. Data: `data/processed/H81-culture-beyond-composition/replication/` (`kappa.parquet`, `pairs_<model>_<regime>.parquet`).

## Scorecard (period-specific axes)
- C: κ against the sign-flip null (equal time only). The period's role in D (slow mode) is through the regime-level pairs.

## Notes
- κ includes field leakage beyond the projected directions and contemporaneous convergence; it is an upper bound on equal-time collective order.
