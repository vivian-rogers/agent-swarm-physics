# H81 × G31: goal period #31 (2026-02-16 → 2026-02-20, non-holdout days)

**Verdict:** descriptive
**Role:** replication
**Period:** regime I · 11 eligible agents · 1 calendar-week block(s). Splits inside the period: 31b (roster_join:Claude Sonnet 4.6), 31c (ne:NE29; roster_leave:Claude 3.7 Sonnet), 31d (ne:NE11).

## Why this period
Every non-holdout goal period of regimes I and III is a replication point for the equal-time collective share κ and a node of the regime-level cross-goal slow-mode analysis (the card's exception (c)).

## Prediction
*Written 2026-10-04 20:05 UTC in the card (P1), before any real-data statistic; this folder was generated after the run.*
- P1 (descriptive): κ above its sign-flip band (field leakage and contemporaneous convergence make it positive). Not a culture claim.
- The slow-mode predictions (P2, P3) are regime-level; this period's neighbour similarities are listed for reference.

## Result
| Quantity | bge | gte |
| --- | --- | --- |
| κ (equal time) [95% jackknife] | +0.642 ± 0.146 | +0.614 ± 0.149 |
| sign-flip null band | [-0.077, 0.289] | [-0.073, 0.246] |
| excess variance ratio ‖u‖² / floor | 7.42 | 7.14 |
| mean similarity to blocks of other goals ≤ 14 d away (pairs) | +0.327 (1) | +0.098 (1) |
| mean similarity to blocks of other goals ≥ 42 d away (pairs) | -0.063 (38) | -0.045 (38) |

P1 here: κ above the band in both models. Data: `data/processed/H81-culture-beyond-composition/replication/` (`kappa.parquet`, `pairs_<model>_<regime>.parquet`).

## Scorecard (period-specific axes)
- C: κ against the sign-flip null (equal time only). The period's role in D (slow mode) is through the regime-level pairs.

## Notes
- κ includes field leakage beyond the projected directions and contemporaneous convergence; it is an upper bound on equal-time collective order.
