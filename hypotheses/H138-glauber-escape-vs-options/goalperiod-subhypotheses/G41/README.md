# H138 × G41: replication unit (2026-05-11 → 2026-05-18)

**Verdict:** supported
**Role:** exploratory (replication)
**Period:** regime III · mode I · 15 agents · 5 days. No split used (whole period, as in H11/H129).

## Why this period
A regime-III week with 35 work leaves (testable, ≥ 25) and 109 attention leaves. It adds one shared-goal work unit to the replication layer.

## Prediction
*Written 2026-10-07 (round 1, after the synthetic check and before any real-data hazard statistic). Seen: the structural leave counts above; no hazard, elasticity or q-by-leave statistic. Copied from the card's replication layer.*
- **P1 (replication, work):** ε̂_q > 0 with 95% CI above 0. Credence 0.25.
- **P3 (lead placebo, work):** ε̂_q − ε̂_lead > 0 with CI above 0. Credence 0.25.
- **Attention (secondary):** ε̂_q > 0 with CI above 0. Credence 0.3; read against the label-noise world W4.
- Counts against: ε̂_q CI includes 0 with synthetic power ≥ 0.8 at ε_q = 0.5 (pooled).

## Result
*Round 1, 2026-10-07 (exploration). Estimator: cloglog hazard per own call, agent effects, active-time spline, agent-cluster sandwich (card Amendment A1). Power from the real-skeleton synthetic (W1 worlds, 200 replicates).*

| Channel · unit | Leaves | ε̂_q [95% CI] | permutation p | ε̂_q − ε̂_lead [boot CI] | ε̂_Z | power at ε 0.5 / 1 | Verdict |
| --- | --- | --- | --- | --- | --- | --- | --- |
| work · 41 | 35 | 1.86 [0.25, 3.47] | 0.010 | 1.80 [0.33, 4.29] | 1.32 [0.33, 2.30] | 0.13 / 0.35 | P1 passes and P3 passes |
| attention · 41 | 109 | −0.51 [−1.28, 0.25] | 0.302 | −0.32 [−1.31, 0.32] | 0.25 [−0.36, 0.87] | 0.14 / 0.46 | P1 fails; unpowered |

- Period verdict: **supported**. P1 and P3 pass in the work channel.
- #41 is the only work unit of 13 with a CI above 0 (and permutation p 0.010). By chance about 0.3 of 13 units would show a CI above 0, and one other unit (51g) shows a CI below 0. So this unit alone is weak evidence for the hypothesis. The pooled work elasticity is −0.66 [−1.64, 0.32].
- Data: `data/processed/H138-glauber-escape-vs-options/G41/`, results in `results/results.json`.

## Scorecard (period-specific axes)
C 1 (ε̂_q beats 0 in this unit; permutation p 0.010); H 1 (the lead placebo is positive here, so R-coarrival does not explain this unit). Unit power is low (0.13 at ε 0.5), so the size of ε̂_q is uncertain.

## Notes
- Leave counts are structural (from `scheme/build.py`, counts.json) and set testability only.
