# H36 × NE42: merge into #universe-coordination (05-04) and split back (05-11)

**Verdict:** descriptive
**Verdict (1b):** descriptive
**Role:** exploratory (round 1, non-holdout)
**Period:** #39–#41 (2026-05-04 merge with the #40 kickoff; 2026-05-11 split with the #41 kickoff)

## Why this test
An A-B-A of room structure; both steps coincide with goal kickoffs.

## Prediction
*Written 2026-10-04 01:51 UTC, before computing any statistic on real data.* P4 (descriptive): the merge raises activity χ/I (z ≥ 2 on day 0) [0.35]; the split lowers them (z ≤ −1) [0.4]. If the merge alarms and the split does not, that is the sign pattern of a coupling change (S1 vs S2).

**Verdict rule:** Descriptive (two goal-confounded events): verdict 'descriptive'; sign pattern reported.

## Result
<!-- RESULT -->
| Event | day 0 | Z_phys −1 / 0 / +1 / +2 / +3 | Z_I d0 | Z_χ d0 | Z_C d0 | Z_act d0 | Z_cont d0 | R1 d0 | alarm |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| NE42a (merge into #universe-coordination) | 2026-05-04 | -0.07 / 0.84 / -0.20 / 0.42 / 0.38 | 1.01 | 1.55 | -0.05 | -0.61 | 2.83 | 5.17 | no |
| NE42b (split back to #best/#rest) | 2026-05-11 | 0.55 / -0.67 / 2.36 / -0.01 / 1.09 | 1.45 | -1.12 | -2.33 | -3.00 | 3.15 | 9.02 | yes |

**Prediction check:** the merge did **not** raise activity χ/I (Z_act −0.61 on day 0; predicted z ≥ 2 [0.35]); the split lowered activity (Z_act −3.0, predicted ≤ −1 [0.4]: held) but the combined score still alarmed on day +1 through content (Z_cont 3.15 on day 0) and R1 jumped at both steps (5.2, 9.0). The S1/S2 sign pattern of a coupling change is absent; both steps look like content field changes (they coincide with the #40 and #41 kickoffs).
<!-- /RESULT -->

## Round 1b (improved data, 2026-10-04)
<!-- R1B -->
Round 1b tables (bge-small, restatements removed, fixed activity table):

| Event | day 0 | Z_phys −1 / 0 / +1 / +2 / +3 | Z_I d0 | Z_χ d0 | Z_C d0 | Z_act d0 | Z_cont d0 | R1 d0 | alarm |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| NE42a (merge into #universe-coordination) | 2026-05-04 | -0.62 / 1.55 / 0.14 / -0.36 / 1.05 | 1.91 | 1.72 | 1.01 | 0.56 | 2.98 | 3.88 | no |
| NE42b (split back to #best/#rest) | 2026-05-11 | 1.45 / 1.79 / 1.53 / 0.04 / 0.99 | 2.08 | 1.91 | 1.39 | 0.98 | 2.97 | 8.61 | no |

gte-modernbert:

| Event | day 0 | Z_phys −1 / 0 / +1 / +2 / +3 | Z_I d0 | Z_χ d0 | Z_C d0 | Z_act d0 | Z_cont d0 | R1 d0 | alarm |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| NE42a (merge into #universe-coordination) | 2026-05-04 | -0.87 / 1.33 / 0.14 / 1.31 / 1.28 | 2.33 | 1.71 | -0.06 | 0.56 | 2.69 | 1.93 | no |
| NE42b (split back to #best/#rest) | 2026-05-11 | 1.94 / 1.64 / 1.61 / 0.12 / 1.56 | 2.07 | 1.61 | 1.24 | 0.98 | 2.66 | 10.41 | no |
<!-- /R1B -->
