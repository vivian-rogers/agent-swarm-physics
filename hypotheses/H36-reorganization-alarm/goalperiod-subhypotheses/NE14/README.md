# H36 × NE14: regime II→III boundary (perma-computer-use, 2026-03-24)

**Verdict:** failed
**Verdict (1b):** failed
**Role:** replication (exploratory) (round 1, non-holdout)
**Period:** inside #36 (2026-03-23 → 03-30); the NE14 rollout start (03-11) is in held-out #34

## Why this test
The largest scaffold change in the data: discrete sessions replaced by continuous computer use + CONSOLIDATE.

## Prediction
*Written 2026-10-04 01:51 UTC, before computing any statistic on real data.* P5: the alarm fires within ±1 day of 03-24 [0.6] (the activity grammar changes completely; expect the activity members to carry it).

**Verdict rule:** Supported if Z_phys ≥ 2.0 on any of days −1..+1; failed otherwise.

## Result
<!-- RESULT -->
| Event | day 0 | Z_phys −1 / 0 / +1 / +2 / +3 | Z_I d0 | Z_χ d0 | Z_C d0 | Z_act d0 | Z_cont d0 | R1 d0 | alarm |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| NE14b (NE14 regime II->III boundary (perma-computer-use)) | 2026-03-24 | 0.31 / -0.78 / -0.76 / -0.43 / -1.29 | -1.56 | -1.43 | 0.64 | -0.36 | -1.60 | 0.39 | no |

**Prediction check:** P5 predicted an alarm within ±1 day of 03-24 [0.6]: **failed**. Every family is near or below zero (Z_act −0.36, Z_cont −1.60). Likely reasons (post hoc): NE14 was rolled out by provider from 03-11 (held out), so 03-24 ends a gradual change rather than starting one; and the per-pair, surrogate-corrected statistics are designed to be invariant to the activity grammar.
<!-- /RESULT -->

## Round 1b (improved data, 2026-10-04)
<!-- R1B -->
Round 1b tables (bge-small, restatements removed, fixed activity table):

| Event | day 0 | Z_phys −1 / 0 / +1 / +2 / +3 | Z_I d0 | Z_χ d0 | Z_C d0 | Z_act d0 | Z_cont d0 | R1 d0 | alarm |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| NE14b (NE14 regime II->III boundary (perma-computer-use)) | 2026-03-24 | 0.19 / -0.96 / -0.80 / -0.07 / -0.85 | -1.32 | -1.82 | 0.28 | -0.68 | -1.45 | 0.39 | no |

gte-modernbert:

| Event | day 0 | Z_phys −1 / 0 / +1 / +2 / +3 | Z_I d0 | Z_χ d0 | Z_C d0 | Z_act d0 | Z_cont d0 | R1 d0 | alarm |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| NE14b (NE14 regime II->III boundary (perma-computer-use)) | 2026-03-24 | 0.07 / -1.02 / -0.67 / -0.12 / -0.79 | -1.45 | -1.77 | 0.17 | -0.68 | -1.61 | 0.48 | no |
<!-- /R1B -->
