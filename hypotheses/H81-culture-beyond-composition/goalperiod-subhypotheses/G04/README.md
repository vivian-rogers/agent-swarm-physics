# H81 × G04: goal period #4 (2025-05-15 → 2025-06-18, non-holdout days)

**Verdict:** descriptive
**Role:** replication
**Period:** regime I · 5 eligible agents · 6 calendar-week block(s). Splits inside the period: 4b (roster_join:o4-mini; roster_leave:GPT-4.1), 4c (roster_join:Claude Opus 4; roster_leave:o4-mini), 4d (outage:300min).

## Why this period
Every non-holdout goal period of regimes I and III is a replication point for the equal-time collective share κ and a node of the regime-level cross-goal slow-mode analysis (the card's exception (c)).

## Prediction
*Written 2026-10-04 20:05 UTC in the card (P1), before any real-data statistic; this folder was generated after the run.*
- P1 (descriptive): κ above its sign-flip band (field leakage and contemporaneous convergence make it positive). Not a culture claim.
- The slow-mode predictions (P2, P3) are regime-level; this period's neighbour similarities are listed for reference.

## Result
| Quantity | bge | gte |
| --- | --- | --- |
| κ (equal time) [95% jackknife] | +0.556 ± 0.247 | +0.660 ± 0.169 |
| sign-flip null band | [-0.154, 0.197] | [-0.174, 0.229] |
| excess variance ratio ‖u‖² / floor | 2.76 | 3.09 |
| mean similarity to blocks of other goals ≤ 14 d away (pairs) | +0.225 (9) | +0.270 (9) |
| mean similarity to blocks of other goals ≥ 42 d away (pairs) | -0.067 (172) | -0.076 (172) |

P1 here: κ above the band in both models. Data: `data/processed/H81-culture-beyond-composition/replication/` (`kappa.parquet`, `pairs_<model>_<regime>.parquet`).

## Scorecard (period-specific axes)
- C: κ against the sign-flip null (equal time only). The period's role in D (slow mode) is through the regime-level pairs.

## Notes
- κ includes field leakage beyond the projected directions and contemporaneous convergence; it is an upper bound on equal-time collective order.
