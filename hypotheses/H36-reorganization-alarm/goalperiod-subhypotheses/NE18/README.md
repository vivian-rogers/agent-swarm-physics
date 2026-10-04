# H36 × NE18: history search returns verbatim segments (2026-04-20, inside #38)

**Verdict:** failed
**Role:** exploratory (round 1, non-holdout)
**Period:** inside #38 (2026-04-02 → 04-27)

## Why this test
A memory-access change for searchers; mid-goal, no confound.

## Prediction
*Written 2026-10-04 01:51 UTC, before computing any statistic on real data.* P5: no alarm [0.7].

**Verdict rule:** Supported if Z_phys ≥ 2.0 on any of days −1..+1; failed otherwise.

## Result
<!-- RESULT -->
| Event | day 0 | Z_phys −1 / 0 / +1 / +2 / +3 | Z_I d0 | Z_χ d0 | Z_C d0 | Z_act d0 | Z_cont d0 | R1 d0 | alarm |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| NE18 (NE18) | 2026-04-20 | -0.47 / 0.73 / -0.39 / -1.72 / 0.50 | 0.89 | 0.21 | 1.10 | 1.68 | -0.48 | -0.76 | no |

**Prediction check:** no alarm, as predicted (Z_phys 0.73 on day 0). As for NE17, the miss is expected.
<!-- /RESULT -->
