# H81 × G30: goal period #30 (2026-02-09 → 2026-02-13, non-holdout days)

**Verdict:** descriptive
**Role:** replication
**Period:** regime I · 11 eligible agents · 1 calendar-week block(s). Splits inside the period: 30b (ne:NE10).

## Why this period
Every non-holdout goal period of regimes I and III is a replication point for the equal-time collective share κ and a node of the regime-level cross-goal slow-mode analysis (the card's exception (c)).

## Prediction
*Written 2026-10-04 20:05 UTC in the card (P1), before any real-data statistic; this folder was generated after the run.*
- P1 (descriptive): κ above its sign-flip band (field leakage and contemporaneous convergence make it positive). Not a culture claim.
- The slow-mode predictions (P2, P3) are regime-level; this period's neighbour similarities are listed for reference.

## Result
| Quantity | bge | gte |
| --- | --- | --- |
| κ (equal time) [95% jackknife] | +0.723 ± 0.067 | +0.789 ± 0.057 |
| sign-flip null band | [-0.077, 0.272] | [-0.084, 0.287] |
| excess variance ratio ‖u‖² / floor | 8.23 | 8.89 |
| mean similarity to blocks of other goals ≤ 14 d away (pairs) | +0.327 (1) | +0.098 (1) |
| mean similarity to blocks of other goals ≥ 42 d away (pairs) | -0.065 (37) | -0.076 (37) |

P1 here: κ above the band in both models. Data: `data/processed/H81-culture-beyond-composition/replication/` (`kappa.parquet`, `pairs_<model>_<regime>.parquet`).

## Scorecard (period-specific axes)
- C: κ against the sign-flip null (equal time only). The period's role in D (slow mode) is through the regime-level pairs.

## Notes
- κ includes field leakage beyond the projected directions and contemporaneous convergence; it is an upper bound on equal-time collective order.
