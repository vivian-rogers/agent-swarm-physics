# H117 × NE07: "don't do nothing" prompt (#21, 2025-12-04)

**Verdict:** mixed
**Role:** exploratory (replication)
**Period:** regime I · #21 · ~8 eligible agents · one room · before 12-02, 12-03 | after 12-04, 12-05. DeepSeek joins 12-04 and drops out by eligibility.

## Why this period
A prompt field aimed at waiting loops (activity field), mid-goal, no room change.

## Prediction
*Written 2026-10-04 22:06 UTC, before running on this period.*
- Q p > 0.05 [0.7]; F p < 0.10 [0.5]; D_F ≤ placebo 95th percentile [0.65].
- Verdict rule (card): **supported** if Q has placebo p > 0.05 and F has p < 0.10; **failed** if Q p < 0.05; **mixed** if Q p > 0.05 and F p ≥ 0.10 (no field step to test against).

## Result
*Run 2026-10-04 22:43–22:46 UTC (exploratory, non-holdout).*

| Statistic | Observed | Null (placebo pool) | Verdict |
| --- | --- | --- | --- |
| Q (28 fixed pairs, 8 agents) | 1.37 | p 0.071 | within (near the edge) |
| F | 2.14 | p 0.52 | no field step |
| D_F | 0.50 | p 0.071 | within |
| Q-naive | 1.36 | p 0.31 | within |

Pool: regime I, k = 2, 83 splits (Q median 0.70, 95th pct 1.43; F 90th pct 6.6). Mixed (no first stage).

## Scorecard (period-specific axes)
C: passes narrowly. E: no first stage.

## Notes
