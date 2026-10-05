# H36 × NE17: outreach approval (2026-04-14, inside #38)

**Verdict:** failed
**Verdict (1b):** failed
**Role:** replication (exploratory) (round 1, non-holdout)
**Period:** inside #38 (2026-04-02 → 04-27)

## Why this test
A scaffold change that degrades one external action for outreach-heavy agents; mid-goal, no confound.

## Prediction
*Written 2026-10-04 01:51 UTC, before computing any statistic on real data.* P5: no alarm (hit only at chance) [0.7]: a small-dose change to one tool.

**Verdict rule:** Supported if Z_phys ≥ 2.0 on any of days −1..+1; failed otherwise.

## Result
<!-- RESULT -->
| Event | day 0 | Z_phys −1 / 0 / +1 / +2 / +3 | Z_I d0 | Z_χ d0 | Z_C d0 | Z_act d0 | Z_cont d0 | R1 d0 | alarm |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| NE17 (NE17) | 2026-04-14 | -0.60 / -1.18 / -0.39 / -0.55 / -0.47 | -0.44 | -0.95 | -2.15 | -0.21 | -2.22 | -0.72 | no |

**Prediction check:** no alarm, as predicted (Z_phys −1.18 on day 0). The H36 verdict is 'failed' because the alarm missed a catalogued transition; the miss is the expected behavior for a small-dose tool change.
<!-- /RESULT -->

## Round 1b (improved data, 2026-10-04)
<!-- R1B -->
Round 1b tables (bge-small, restatements removed, fixed activity table):

| Event | day 0 | Z_phys −1 / 0 / +1 / +2 / +3 | Z_I d0 | Z_χ d0 | Z_C d0 | Z_act d0 | Z_cont d0 | R1 d0 | alarm |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| NE17 (NE17) | 2026-04-14 | 0.19 / -0.58 / -0.55 / 0.09 / -0.33 | -0.28 | -0.03 | -1.41 | 0.54 | -1.96 | -0.73 | no |

gte-modernbert:

| Event | day 0 | Z_phys −1 / 0 / +1 / +2 / +3 | Z_I d0 | Z_χ d0 | Z_C d0 | Z_act d0 | Z_cont d0 | R1 d0 | alarm |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| NE17 (NE17) | 2026-04-14 | -0.11 / 0.14 / -0.34 / -0.08 / -0.49 | -0.02 | 0.52 | -0.09 | 0.54 | -0.45 | -0.75 | no |
<!-- /R1B -->

## Round 2 (2026-10-05)
<!-- R2 -->
Scaffold detector R5 (card: Round 2; prediction P5.3 for NE14b: not separately predicted).

| Channel | z on day 0 |
| --- | --- |
| z_R5 (alarm ≥ 4) | 0.53 |
| tool mix | -1.25 |
| bash grammar | -1.34 |
| context-boundary rate (abs) | 0.53 |
| schema diff S (H74, shared) | 8 |
| H74 mix M | 0.41 |

Data: `data/processed/H36-reorganization-alarm/r2/scaffold_days.parquet`.
<!-- /R2 -->
