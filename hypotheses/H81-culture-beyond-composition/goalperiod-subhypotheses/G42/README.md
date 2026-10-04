# H81 × G42: goal period #42 (2026-05-18 → 2026-05-22, non-holdout days)

**Verdict:** descriptive
**Role:** replication
**Period:** regime III · 16 eligible agents · 1 calendar-week block(s). Splits inside the period: 42b (roster_join:Gemini 3.5 Flash).

## Why this period
Every non-holdout goal period of regimes I and III is a replication point for the equal-time collective share κ and a node of the regime-level cross-goal slow-mode analysis (the card's exception (c)).

## Prediction
*Written 2026-10-04 20:05 UTC in the card (P1), before any real-data statistic; this folder was generated after the run.*
- P1 (descriptive): κ above its sign-flip band (field leakage and contemporaneous convergence make it positive). Not a culture claim.
- The slow-mode predictions (P2, P3) are regime-level; this period's neighbour similarities are listed for reference.

## Result
| Quantity | bge | gte |
| --- | --- | --- |
| κ (equal time) [95% jackknife] | +0.415 ± 0.134 | +0.452 ± 0.137 |
| sign-flip null band | [-0.042, 0.129] | [-0.043, 0.118] |
| excess variance ratio ‖u‖² / floor | 7.23 | 7.78 |
| mean similarity to blocks of other goals ≤ 14 d away (pairs) | +0.005 (3) | +0.024 (3) |
| mean similarity to blocks of other goals ≥ 42 d away (pairs) | -0.243 (13) | -0.261 (13) |

P1 here: κ above the band in both models. Data: `data/processed/H81-culture-beyond-composition/replication/` (`kappa.parquet`, `pairs_<model>_<regime>.parquet`).

## Scorecard (period-specific axes)
- C: κ against the sign-flip null (equal time only). The period's role in D (slow mode) is through the regime-level pairs.

## Notes
- κ includes field leakage beyond the projected directions and contemporaneous convergence; it is an upper bound on equal-time collective order.
