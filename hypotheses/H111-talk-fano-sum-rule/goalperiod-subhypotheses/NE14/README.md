# H111 × NE14: regime II → III inside goal #36 (36a → 36b ∪ 36c, 2026-03-23 → 03-27)

**Verdict:** descriptive
**Role:** native (exploratory)
**Period:** goal #36 · 12 agents · two rooms · 36a regime II (1 day), 36b ∪ 36c regime III (4 days).

## Why this period
The regime boundary inside one goal at a fixed roster. H67 found read-out coupling switching on across it (g_lag −0.06 [−0.15, 0.03] → 0.12 [0.06, 0.17]) at a nearly fixed call interval (13.7 → 12.0 s). The sum rule predicts a rise of the collective Fano ratio by Φ_pred(0.12) − Φ_pred(−0.06) ≈ +0.35, with no free parameter. H38 found regime-III co-activation is mostly the runner's schedule, so the scheduler part should grow too.

## Prediction
*Written 2026-10-04 21:30 UTC, before running on this period. Seen: H67's and H99's NE14 results. No H111 statistic.*
- **N14a (sum rule):** trimmed Φ_obs(15) rises from 36a to 36b ∪ 36c by at least half the predicted rise. [0.35]
- **N14b (scheduler):** the untrimmed − trimmed gap of Φ(15) is larger in 36b ∪ 36c than in 36a. [0.55]
- **Caveat stated in advance:** 36a is one day; its CI (hour blocks) will be wide, so N14a may be uninformative.

## Result
*Run 2026-10-04 ~21:45 UTC.*

| Side | g_lag | Φ_pred | Φ(10) [95%] | untrimmed − trimmed (per-call / wall) |
| --- | --- | --- | --- | --- |
| 36a (regime II, 1 day, 17 windows) | -0.060 | 0.89 | 1.36 [0.74, 2.30] | -0.42 / -0.07 |
| 36b ∪ 36c (regime III, 4 days) | 0.09 / 0.15 | 1.29 | 1.42 [0.99, 1.85] | -0.01 / -0.08 |

- **N14a** (rise ≥ half the predicted 0.40): observed +0.05. Not met, but 36a's CI spans 0.74–2.30 (one day, 17 windows), as stated in advance. **Uninformative.**
- **N14b** (scheduler gap larger in regime III): per-call -0.42 → -0.01 (met nominally); wall clock -0.07 → -0.08 (not met). **Uninformative.**
- **Verdict:** descriptive. One regime-II day cannot resolve a 0.4 change in Φ.

## Scorecard (period-specific axes)
E: the change across the regime boundary.

## Notes
