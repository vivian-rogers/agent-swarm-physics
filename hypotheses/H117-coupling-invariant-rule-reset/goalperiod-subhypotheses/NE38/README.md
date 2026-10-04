# H117 × NE38: one agent's role reassigned (#51, 2026-07-29)

**Verdict:** mixed
**Role:** exploratory (replication + native)
**Period:** regime III · #51 (units 51e | 51f) · ~25 eligible agents · one room (#general) · before 07-27, 07-28 | after 07-29, 07-30.

## Why this period
A human reassigns Claude Opus 5's role (word puzzles → mathematics): a field step on one agent while 20+ others keep theirs. Replication uses all fixed pairs; the native compares the reassigned agent's own row and column of J with every other agent's (H96 found its content quenches fastest).

## Prediction
*Written 2026-10-04 22:06 UTC, before running on this period.*
- Replication: Q p > 0.05 [0.7]; F p < 0.10 [0.35] (one agent's field). Verdict rule (card): **supported** if Q has placebo p > 0.05 and F has p < 0.10; **failed** if Q p < 0.05; **mixed** if Q p > 0.05 and F p ≥ 0.10 (no field step to test against).
- Native: the reassigned agent's row Q is not in the top 20% of agents [0.65]; its |Δh̄| ranks in the top 3 of all agents [0.45]. Native supported if both hold; failed if its row Q is the largest of all agents.

## Result
*Run 2026-10-04 22:43–22:46 UTC (exploratory, non-holdout).*

| Statistic | Observed | Null (placebo pool) | Verdict |
| --- | --- | --- | --- |
| Replication Q (171 fixed pairs, 19 agents) | 0.59 | p 0.52 | within |
| F | 3.80 | p 0.48 | no village-wide field step |
| Q_R (19 recipients) | 0.68 | p 0.93 | within |
| k = 3 sensitivity Q (231 pairs, 22 agents) | 0.66 | p 0.50 (9 k = 3 splits) | within |
| **Native:** reassigned agent's row Q | 0.86, rank 5 of 19 | top 20% = ranks 1–3 | not singled out |
| **Native:** reassigned agent's Δh̄ | −1.57 (z −5.6), rank 1 of 19 | — | its own field moved most |

Replication: mixed (no village-wide first stage, which is expected for a one-agent field). Native: **supported** (the targeted agent's field moved most while its couplings moved no more than other agents'). Power (Amendment 1, #51 skeleton): ±1.2 0.68 (k = 2), 0.63 (k = 3); ±0.6 0.50 / 0.78.

## Scorecard (period-specific axes)
E: the native is a single-agent field step with a clear first stage (z −5.6); its couplings stay at the null level. F: power 0.5–0.8.

## Notes
- Verdict line covers the replication row; the native verdict is supported.
