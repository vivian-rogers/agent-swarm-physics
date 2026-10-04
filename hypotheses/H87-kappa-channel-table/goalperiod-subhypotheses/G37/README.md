# H87 × G37: the search row's own scramble (the 2026-03-31/04-01 outage)

**Verdict:** mixed (inconclusive: κ_Q not identified)
**Role:** native (exploratory)
**Period:** regime III · goal #37 (03-30 → 04-01) with H84's placebo panel (#36b–#42, #44); the replication point for #37 is below.

## Why this period
The search channel's only natural scramble outside the holdout. H84 measures its value; H87 converts it to κ_Q with the search row's information I_Q.

## Prediction
*Written 2026-10-04 ~20:07 UTC, before any outcome statistic.*
- ΔV_Q = −β_V4 × mean searcher dose (commits per 20 calls), from H84's G37 regression; I_Q from H84's replication (bits per search event, pooled over eligible periods).
- **P5:** κ_Q's CI includes 0.
- *Counts against:* κ_Q > 0 with CI excluding 0.
- Replication point (templated, card row R): supported if κ_C > 0 with CI excluding 0 and largest among identified rows; A1 applied to C (clarified after the run): mixed if the erasure cost is positive but I_C is not identified; failed otherwise.

## Result
*Assembled 2026-10-04 20:51 UTC from H84's G37 results (data reuse; `results.json` block `G37_Q`).*
- ΔV_Q = −0.03 commits per 20 calls at the mean searcher dose (placebo-SD interval [−1.04, +0.98]).
- I_Q = 0.012 bits [−0.011, +0.035] (H84's pooled replication over 7 periods); not identified under A1.
- κ_Q: n.i. P5 is met only in the weak sense that no finite κ_Q exists; the uniform-column search row agrees (I 0.001 bits; ΔV_rel −0.08 [−0.33, +0.47]).

**Reading.** The search channel is a near-zero row on both axes: about 0.01 bits, and its outage cost no measurable commits. The κ ratio is undefined, not small.

### Replication point for #37 (call scale; 359 F, 369 P; B = 200)
| Row | I (bits) [95% CI] | ΔV (commits per 20 calls) [95% CI] | ΔV_rel | κ |
| --- | --- | --- | --- | --- |
| C | 0.018 [-0.089, 0.125] | 0.022 [-0.032, 0.085] | 0.123 | n.i. |
| A | 0.058 [0.008, 0.118] | 0.003 [-0.846, 0.259] | 0.005 | n.i. |
| M | 0.045 [-0.013, 0.123] | -0.025 [-1.659, 0.369] | -0.126 | n.i. |
| G | 0.006 [-0.029, 0.047] | -0.030 [-0.544, 0.334] | -0.119 | n.i. |
| Q | -0.001 [-0.005, -0.000] | — — | — | n.i. |

Replication verdict: failed (erasure cost 0.12 [−0.20, +0.44] includes 0; I_C not identified). The three-day period has 359 forced erasures.

## Scorecard (period-specific axes)
- **E:** the outage is a natural scramble; it reached one agent fully (H84).
- **I:** #37 is the one period where the erasure cost is not distinguishable from 0.
