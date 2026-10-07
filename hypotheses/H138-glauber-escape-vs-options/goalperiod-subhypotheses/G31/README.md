# H138 × G31: the free week before the room split (#31, 2026-02-16 → 2026-02-23)

**Verdict:** descriptive
**Role:** exploratory (replication)
**Period:** regime I · mode F (free) · 12 agents · one room · 5 days. No split inside the period.

## Why this period
The regime-I week with the most work-label switches outside #51 (130, H11 round 2). A free goal sets a weak goal field, so the options on offer have the most room to act. H129 found age-signed triple flows here (A_3 1.13 work), so hops are frequent enough for a per-call hazard.

## Prediction
*Written 2026-10-07 ~09:10 UTC, before running on this period. Seen: the switch total above; no q count and no hazard statistic.*
- **P1 (replication):** ε̂_q > 0 with 95% CI above 0 (work channel). Credence 0.3.
- **P3 (lead placebo):** ε̂_q − ε̂_lead > 0 with CI above 0. Credence 0.25 (H11: joins here are co-arrival).
- Counts against: ε̂_q CI includes 0 with synthetic power ≥ 0.8 at ε_q = 0.5 on this skeleton.
- Period verdict: supported if P1 and P3 pass; mixed if only P1 passes; failed if ε̂_q ≤ 0 with power; inconclusive otherwise.

## Result
*Round 1, 2026-10-07 (exploration). Estimator: cloglog hazard per own call, agent effects, active-time spline, agent-cluster sandwich (card Amendment A1). Power from the real-skeleton synthetic (W1 worlds, 200 replicates). The work power at ε_q = 0.5 is below 0.8 in every unit (card A2), so a work null is unpowered.*

| Channel · unit | Leaves | ε̂_q [95% CI] | permutation p | ε̂_q − ε̂_lead [boot CI] | ε̂_Z [CI] | β̂_own [CI] | power at ε 0.5 / 1 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| work · 31 | 69 | −0.07 [−1.23, 1.09] | 0.899 | 0.14 [−0.54, 1.30] | −1.14 [−2.82, 0.53] | −0.30 [−1.19, 0.60] | 0.14 / 0.34 |
| attention · 31 | 200 | −0.36 [−0.67, −0.05] | 0.053 | −0.28 [−0.55, 0.03] | −0.98 [−2.09, 0.13] | −0.19 [−0.76, 0.37] | 0.56 / 0.96 |

| Prediction | Observed | Verdict |
| --- | --- | --- |
| P1 (work): ε̂_q CI above 0 | −0.07 [−1.23, 1.09] | fails; unpowered (0.14) |
| P3 (work): ε̂_q − ε̂_lead CI above 0 | 0.14 [−0.54, 1.30] | fails; unpowered |
| Attention (secondary) | −0.36 [−0.67, −0.05] (CI below 0) | against the prediction |

- Period verdict: **descriptive** (the work test is unpowered; the period rule gives "inconclusive"). The secondary attention channel points the other way: more open options go with fewer leaves.
- Descriptive: work leaves 0.30 per 100 own calls; q̄ = 7.5 open options; 26% of work leaves go to a project born in the 2 h before. λ_own (H94, 31a) 1.2 nats; R_own 0.24.

## Scorecard (period-specific axes)
C 0 (ε̂_q does not beat 0; unpowered); D 0 (no unfitted check here); H 0 (R-finish not beaten).

## Notes
- Attention channel reported as secondary, with the label-noise world W4 as its size check.
