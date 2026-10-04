# H117 × NE17: outreach approval (#38, 2026-04-14)

**Verdict:** failed
**Role:** exploratory (replication)
**Period:** regime III · #38 · ~12 eligible agents · #best/#rest (fixed) · before 04-10, 04-13 | after 04-14, 04-15.

## Why this period
The outreach approval system degrades external action mid-goal (dose: outreach-heavy agents), with rooms and roster fixed: a rule change that moves what agents do, not who reads whom.

## Prediction
*Written 2026-10-04 22:06 UTC, before running on this period.*
- Q p > 0.05 [0.7]; F p < 0.10 [0.45]; Q_R p > 0.05 [0.65]; D_F ≤ placebo 95th [0.65].
- Verdict rule (card): **supported** if Q has placebo p > 0.05 and F has p < 0.10; **failed** if Q p < 0.05; **mixed** if Q p > 0.05 and F p ≥ 0.10 (no field step to test against).

## Result
*Run 2026-10-04 22:43–22:46 UTC (exploratory, non-holdout).*

| Statistic | Observed | Null (placebo pool) | Verdict |
| --- | --- | --- | --- |
| Q (7 fixed pairs, 6 agents) | 1.54 | p 0.037 | **J moved** |
| D_F | 0.67 | p 0.037 | moved |
| Q-naive | 1.84 | p 0.037 | moved |
| Q_MF | 0.94 | p 0.41 | within |
| F | 2.56 | p 0.70 | no field step |
| Q_R (E2) | 2.08 | p 0.26 | within |
| mean J^s over fixed pairs | 0.05 → 0.40 | — | rise after the step |

Pool: regime III, k = 2, 26 splits (Q median 0.60, 95th pct 0.95; F 90th pct 5.5). Failed by the per-step rule (Q p < 0.05). The smallest skeleton in the set (6 agents, 7 fixed pairs). One of nine tests at p 0.037, with no first stage on F; read as a possible false positive or a real coupling rise after the outreach gate (agents redirected from email to chat), not as a field artifact (the field did not move).

## Scorecard (period-specific axes)
C: fails at this step. E: the coupling rose although talk rates did not shift: not the R-leak signature.

## Notes
- The failure is not the HH's failure mode: R-leak needs a field step, and F shows none here.
