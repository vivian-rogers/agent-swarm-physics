# H117 × NE16: memory-instruction fix (#36, 2026-03-26)

**Verdict:** mixed
**Role:** exploratory (replication)
**Period:** regime III · #36 · ~11 eligible agents · #best/#rest (fixed) · before 03-24, 03-25 | after 03-26, 03-27.

## Why this period
A scaffold fix (memory updates unblocked) two days after the regime-III boundary, with fixed rooms and roster. Little leverage on memory (RE-O1), so a small field step is expected.

## Prediction
*Written 2026-10-04 22:06 UTC, before running on this period.*
- Q p > 0.05 [0.7]; F p < 0.10 [0.3] (small first stage expected); Q_R (E2) p > 0.05 [0.65].
- Verdict rule (card): **supported** if Q has placebo p > 0.05 and F has p < 0.10; **failed** if Q p < 0.05; **mixed** if Q p > 0.05 and F p ≥ 0.10 (no field step to test against).

## Result
*Run 2026-10-04 22:43–22:46 UTC (exploratory, non-holdout).*

| Statistic | Observed | Null (placebo pool) | Verdict |
| --- | --- | --- | --- |
| Q (13 fixed pairs, 9 agents) | 0.37 | p 0.96 | within |
| F | 1.50 | p 0.85 | no field step |
| Q_R (E2, 9 recipients) | 1.53 | p 0.44 | within |
| J^R − J^U (before / after) | 0.80 ± 0.22 / 0.64 ± 0.15 | — | read > in-flight on both sides |

Pool: regime III, k = 2, 26 splits (Q median 0.60, 95th pct 0.95; F 90th pct 5.5). Mixed (no first stage, as expected for a fix with little leverage).

## Scorecard (period-specific axes)
C: passes. D: E2 read > in-flight on both sides. E: no first stage.

## Notes
