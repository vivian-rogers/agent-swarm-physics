# H81 × G36: goal period #36 (2026-03-24 → 2026-03-27, non-holdout days)

**Verdict:** descriptive
**Role:** replication
**Period:** regime III · 12 eligible agents · 1 calendar-week block(s). Splits inside the period: 36b (ne:NE14; ne:NE41), 36c (ne:NE16).

## Why this period
Every non-holdout goal period of regimes I and III is a replication point for the equal-time collective share κ and a node of the regime-level cross-goal slow-mode analysis (the card's exception (c)).

## Prediction
*Written 2026-10-04 20:05 UTC in the card (P1), before any real-data statistic; this folder was generated after the run.*
- P1 (descriptive): κ above its sign-flip band (field leakage and contemporaneous convergence make it positive). Not a culture claim.
- The slow-mode predictions (P2, P3) are regime-level; this period's neighbour similarities are listed for reference.

## Result
| Quantity | bge | gte |
| --- | --- | --- |
| κ (equal time) [95% jackknife] | +0.431 ± 0.186 | +0.400 ± 0.198 |
| sign-flip null band | [-0.060, 0.174] | [-0.059, 0.176] |
| excess variance ratio ‖u‖² / floor | 5.74 | 5.40 |
| mean similarity to blocks of other goals ≤ 14 d away (pairs) | +0.175 (3) | +0.093 (3) |
| mean similarity to blocks of other goals ≥ 42 d away (pairs) | -0.221 (13) | -0.176 (13) |

P1 here: κ above the band in both models. Data: `data/processed/H81-culture-beyond-composition/replication/` (`kappa.parquet`, `pairs_<model>_<regime>.parquet`).

## Scorecard (period-specific axes)
- C: κ against the sign-flip null (equal time only). The period's role in D (slow mode) is through the regime-level pairs.

## Notes
- κ includes field leakage beyond the projected directions and contemporaneous convergence; it is an upper bound on equal-time collective order.
