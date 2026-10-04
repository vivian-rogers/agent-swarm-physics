# H81 × G21: goal period #21 (2025-12-01 → 2025-12-05, non-holdout days)

**Verdict:** descriptive
**Role:** replication
**Period:** regime I · 9 eligible agents · 1 calendar-week block(s). Splits inside the period: 21b (ne:NE07; roster_join:DeepSeek-V3.2).

## Why this period
Every non-holdout goal period of regimes I and III is a replication point for the equal-time collective share κ and a node of the regime-level cross-goal slow-mode analysis (the card's exception (c)).

## Prediction
*Written 2026-10-04 20:05 UTC in the card (P1), before any real-data statistic; this folder was generated after the run.*
- P1 (descriptive): κ above its sign-flip band (field leakage and contemporaneous convergence make it positive). Not a culture claim.
- The slow-mode predictions (P2, P3) are regime-level; this period's neighbour similarities are listed for reference.

## Result
| Quantity | bge | gte |
| --- | --- | --- |
| κ (equal time) [95% jackknife] | +0.613 ± 0.207 | +0.605 ± 0.192 |
| sign-flip null band | [-0.089, 0.302] | [-0.090, 0.324] |
| excess variance ratio ‖u‖² / floor | 5.90 | 5.84 |
| mean similarity to blocks of other goals ≤ 14 d away (pairs) | +0.075 (3) | +0.008 (3) |
| mean similarity to blocks of other goals ≥ 42 d away (pairs) | -0.081 (32) | -0.044 (32) |

P1 here: κ above the band in both models. Data: `data/processed/H81-culture-beyond-composition/replication/` (`kappa.parquet`, `pairs_<model>_<regime>.parquet`).

## Scorecard (period-specific axes)
- C: κ against the sign-flip null (equal time only). The period's role in D (slow mode) is through the regime-level pairs.

## Notes
- κ includes field leakage beyond the projected directions and contemporaneous convergence; it is an upper bound on equal-time collective order.
