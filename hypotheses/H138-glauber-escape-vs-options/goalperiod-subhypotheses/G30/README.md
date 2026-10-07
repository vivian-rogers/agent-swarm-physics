# H138 × G30: replication unit (2026-02-09 → 2026-02-16)

**Verdict:** failed
**Role:** exploratory (replication)
**Period:** regime I · mode C · 12 agents · 5 days. No split used (whole period, as in H11/H129).

## Why this period
Attention channel only: 140 attention leaves (testable, ≥ 25); 17 work leaves (below 25: work channel descriptive). It adds one unit to the attention replication layer.

## Prediction
*Written 2026-10-07 (round 1, after the synthetic check and before any real-data hazard statistic). Seen: the structural leave counts above; no hazard, elasticity or q-by-leave statistic. Copied from the card's replication layer.*
- **P1 (replication, attention, secondary channel):** ε̂_q > 0 with 95% CI above 0. Credence 0.3; read against the label-noise world W4.
- **P3 (lead placebo, attention):** ε̂_q − ε̂_lead > 0 with CI above 0. Credence 0.25.
- Counts against: ε̂_q CI includes 0 with synthetic power ≥ 0.8 at ε_q = 0.5 (pooled).

## Result
*Round 1, 2026-10-07 (exploration). Estimator: cloglog hazard per own call, agent effects, active-time spline, agent-cluster sandwich (card Amendment A1). Power from the real-skeleton synthetic (W1 worlds, 200 replicates).*

| Channel · unit | Leaves | ε̂_q [95% CI] | permutation p | ε̂_q − ε̂_lead [boot CI] | ε̂_Z | power at ε 0.5 / 1 | Verdict |
| --- | --- | --- | --- | --- | --- | --- | --- |
| work · 30 | 17 | not testable (< 25 leaves) | — | — | — | — | — |
| attention · 30 | 140 | −0.38 [−0.69, −0.07] | 0.519 | −0.43 [−0.87, −0.06] | 0.47 [0.13, 0.81] | 0.38 / 0.83 | P1 fails (CI below 0) |

- Period verdict: **failed**. The attention CI lies below 0 (sign reversed).
- The attention CI lies below 0: more open options go with fewer leaves, against the prediction. The unit power at ε_q = 0.5 is 0.38, so this is one unit of the pooled attention negative (−0.28 [−0.42, −0.15], 31 units).
- Data: `data/processed/H138-glauber-escape-vs-options/G30/`, results in `results/results.json`.

## Scorecard (period-specific axes)
C 0 (the Glauber term does not beat ε_q = 0 here); H 0 (R-finish not beaten; lead placebo unpowered).

## Notes
- Leave counts are structural (from `scheme/build.py`, counts.json) and set testability only.
