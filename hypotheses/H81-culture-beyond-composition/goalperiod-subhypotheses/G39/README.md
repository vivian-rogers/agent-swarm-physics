# H81 × G39: goal period #39 (2026-04-27 → 2026-05-01, non-holdout days)

**Verdict:** descriptive
**Role:** replication
**Period:** regime III · 15 eligible agents · 1 calendar-week block(s). Splits inside the period: none.

## Why this period
Every non-holdout goal period of regimes I and III is a replication point for the equal-time collective share κ and a node of the regime-level cross-goal slow-mode analysis (the card's exception (c)).

## Prediction
*Written 2026-10-04 20:05 UTC in the card (P1), before any real-data statistic; this folder was generated after the run.*
- P1 (descriptive): κ above its sign-flip band (field leakage and contemporaneous convergence make it positive). Not a culture claim.
- The slow-mode predictions (P2, P3) are regime-level; this period's neighbour similarities are listed for reference.

## Result
| Quantity | bge | gte |
| --- | --- | --- |
| κ (equal time) [95% jackknife] | +0.249 ± 0.098 | +0.278 ± 0.106 |
| sign-flip null band | [-0.040, 0.079] | [-0.043, 0.080] |
| excess variance ratio ‖u‖² / floor | 4.49 | 4.90 |
| mean similarity to blocks of other goals ≤ 14 d away (pairs) | +0.058 (4) | +0.084 (4) |
| mean similarity to blocks of other goals ≥ 42 d away (pairs) | -0.310 (9) | -0.146 (9) |

P1 here: κ above the band in both models. Data: `data/processed/H81-culture-beyond-composition/replication/` (`kappa.parquet`, `pairs_<model>_<regime>.parquet`).

## Scorecard (period-specific axes)
- C: κ against the sign-flip null (equal time only). The period's role in D (slow mode) is through the regime-level pairs.

## Notes
- κ includes field leakage beyond the projected directions and contemporaneous convergence; it is an upper bound on equal-time collective order.
