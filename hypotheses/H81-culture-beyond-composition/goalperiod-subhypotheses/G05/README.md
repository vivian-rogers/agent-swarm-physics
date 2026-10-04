# H81 × G05: goal period #5 (2025-06-19 → 2025-06-25, non-holdout days)

**Verdict:** descriptive
**Role:** replication
**Period:** regime I · 4 eligible agents · 2 calendar-week block(s). Splits inside the period: none.

## Why this period
Every non-holdout goal period of regimes I and III is a replication point for the equal-time collective share κ and a node of the regime-level cross-goal slow-mode analysis (the card's exception (c)).

## Prediction
*Written 2026-10-04 20:05 UTC in the card (P1), before any real-data statistic; this folder was generated after the run.*
- P1 (descriptive): κ above its sign-flip band (field leakage and contemporaneous convergence make it positive). Not a culture claim.
- The slow-mode predictions (P2, P3) are regime-level; this period's neighbour similarities are listed for reference.

## Result
| Quantity | bge | gte |
| --- | --- | --- |
| κ (equal time) [95% jackknife] | +0.387 ± 0.215 | +0.406 ± 0.143 |
| sign-flip null band | [-0.146, 0.330] | [-0.152, 0.378] |
| excess variance ratio ‖u‖² / floor | 2.16 | 2.22 |
| mean similarity to blocks of other goals ≤ 14 d away (pairs) | +0.298 (8) | +0.197 (8) |
| mean similarity to blocks of other goals ≥ 42 d away (pairs) | -0.055 (50) | -0.057 (50) |

P1 here: κ above the band in both models. Data: `data/processed/H81-culture-beyond-composition/replication/` (`kappa.parquet`, `pairs_<model>_<regime>.parquet`).

## Scorecard (period-specific axes)
- C: κ against the sign-flip null (equal time only). The period's role in D (slow mode) is through the regime-level pairs.

## Notes
- κ includes field leakage beyond the projected directions and contemporaneous convergence; it is an upper bound on equal-time collective order.
