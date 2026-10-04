# H117 × NE43: bookends stop (08-05) and nudger off (08-20), #51

**Verdict:** mixed
**Role:** exploratory (replication + native)
**Period:** regime III · #51 (51f | 51g; 51g | 51h) · ~25 eligible agents · #general plus #focus from 08-05 · NE43a: 08-03, 08-04 | 08-05, 08-06 · NE43b: 08-18, 08-19 | 08-21, 08-24.

## Why this period
Two removals of an operator drive inside one goal: the daily pause/resume bookends (a synchronizing field) and the nudger (a field on idle agents). The #focus room opens on 08-05 (Gemini 2.5 Pro, Claude Opus 4.8 leave #general) and closes on 08-24, so the same boundary carries switched pairs: a built-in positive control.

## Prediction
*Written 2026-10-04 22:06 UTC, before running on this period.*
- NE43a replication: fixed-pair Q p > 0.05 [0.65]; F p < 0.10 [0.5]. NE43b replication: fixed-pair Q p > 0.05 [0.7]; F p < 0.10 [0.4]. Verdict rule (card): **supported** if Q has placebo p > 0.05 and F has p < 0.10; **failed** if Q p < 0.05; **mixed** if Q p > 0.05 and F p ≥ 0.10 (no field step to test against).
- Native (#focus): switched-pair Q (#focus members × #general stayers) exceeds the fixed-pair Q at NE43a [0.45]; supported if it does and the fixed pairs pass; failed if the switched pairs move no more than the fixed pairs while the fixed pairs pass (then Q cannot see a known adjacency change: the test has no power).

## Result
*Run 2026-10-04 22:43–22:46 UTC (exploratory, non-holdout).*

| Statistic | Observed | Null (placebo pool) | Verdict |
| --- | --- | --- | --- |
| NE43a Q (121 fixed pairs, 18 agents) | 0.61 | p 0.41 | within |
| NE43a F | 3.13 | p 0.56 | no field step |
| NE43a Q_R | 1.20 | p 0.70 | within |
| NE43a k = 3 Q (154 pairs) | 0.65 | p 0.50 | within |
| NE43b Q (56 fixed pairs, 14 agents) | 0.86 | p 0.11 | within |
| NE43b F | 4.00 | p 0.37 | no field step |
| NE43b Q_R | 3.78 | p 0.11 | within |
| **Native:** #focus switched-pair Q (32 pairs) | 0.93 (Gemini 2.5 Pro 1.08, Opus 4.8 0.77) | vs fixed 0.61; vs placebo Q p 0.11 | switched > fixed, weak |

Both replication rows mixed (no first stage beyond day-to-day changes). Native: supported by its rule (switched-pair Q exceeds fixed-pair Q and the fixed pairs pass), but the switched-pair Q is not beyond the placebo pool (p 0.11), so the positive control is weak: Q barely sees a known adjacency cut for two low-talk agents.

## Scorecard (period-specific axes)
E: weak positive control (switched pairs move more than fixed ones, p 0.11). G: the known cut is only weakly visible.

## Notes
