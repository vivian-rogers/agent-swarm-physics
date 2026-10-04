# H09 × NE43: the drive is withdrawn inside #51 (bookends stop after 08-04, nudges after 08-20)

**Verdict:** n/a
**Verdict (1b):** mixed (the gate is unchanged; overall acting fell more than nudges explain)
**Role:** native
**Period:** #51, non-holdout. Day-matched windows: 07-27 → 08-04 (both drives on), 08-06 → 08-20 (bookends off), 08-21 → 09-04 (nudges off too).

## Why this period
It is the only non-holdout withdrawal of the operator's drives at a fixed goal. If the regime-III timer gate is internal, it should not move.

## Prediction
Written 2026-10-04 08:40 UTC (card, N1):
- (a) P(act | no new item) at post-pause calls changes by less than 20% (|log ratio| < 0.18) at each step;
- (b) after the nudger stops, overall P(act) falls by no more than the nudge-accounting bound + 0.02.

## Result (`analysis/r1b_gate.py`; `data/processed/H09-swarm-thermodynamics/r1b/r1b_gate.json`)
| Window | Gates | P(act) | P(act given no new item) | Nudge share | Mention share |
| --- | --- | --- | --- | --- | --- |
| 07-27 → 08-04 | 3,785 | 0.65 | 0.92 | 0.045 | 0.19 |
| 08-06 → 08-20 | 7,474 | 0.73 | 0.79 | 0.038 | 0.15 |
| 08-21 → 09-04 | 6,064 | 0.69 | 0.84 | 0 | 0.12 |

- (a) Agent-matched log ratio: bookends step −0.011 [−0.08, 0.05] (13 agents); nudger step −0.047 [−0.12, 0.01] (16 agents). **Pass.**
- (b) Drop 0.036 vs bound 0.013. **Fail.** Mentions also fell after the nudger stopped, so the nudger accounting misses part of the change.

The raw no-news rates move (0.92 → 0.79) only through roster composition; within agents the rate is flat.
