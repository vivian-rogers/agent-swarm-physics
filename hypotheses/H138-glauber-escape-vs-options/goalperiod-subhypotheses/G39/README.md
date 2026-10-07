# H138 × G39: replication unit (2026-04-27 → 2026-05-04)

**Verdict:** descriptive
**Role:** exploratory (replication)
**Period:** regime III · mode I · 15 agents · 5 days. No split used (whole period, as in H11/H129).

## Why this period
Attention channel only: 63 attention leaves (testable, ≥ 25); 4 work leaves (below 25: work channel descriptive). It adds one unit to the attention replication layer.

## Prediction
*Written 2026-10-07 (round 1, after the synthetic check and before any real-data hazard statistic). Seen: the structural leave counts above; no hazard, elasticity or q-by-leave statistic. Copied from the card's replication layer.*
- **P1 (replication, attention, secondary channel):** ε̂_q > 0 with 95% CI above 0. Credence 0.3; read against the label-noise world W4.
- **P3 (lead placebo, attention):** ε̂_q − ε̂_lead > 0 with CI above 0. Credence 0.25.
- Counts against: ε̂_q CI includes 0 with synthetic power ≥ 0.8 at ε_q = 0.5 (pooled).

## Result
*Round 1, 2026-10-07 (exploration). Estimator: cloglog hazard per own call, agent effects, active-time spline, agent-cluster sandwich (card Amendment A1). Power from the real-skeleton synthetic (W1 worlds, 200 replicates).*

| Channel · unit | Leaves | ε̂_q [95% CI] | permutation p | ε̂_q − ε̂_lead [boot CI] | ε̂_Z | power at ε 0.5 / 1 | Verdict |
| --- | --- | --- | --- | --- | --- | --- | --- |
| work · 39 | 4 | not testable (< 25 leaves) | — | — | — | — | — |
| attention · 39 | 63 | 1.81 [−2.20, 5.82] | 0.404 | 1.94 [−1.38, 7.12] | −0.09 [−0.59, 0.41] | 0.06 / 0.11 | P1 fails; unpowered |

- Period verdict: **descriptive**. No unit has a CI above 0, and the unit power at ε_q = 0.5 is below 0.8, so a null here is unpowered.
- Data: `data/processed/H138-glauber-escape-vs-options/G39/`, results in `results/results.json`.

## Scorecard (period-specific axes)
C 0 (the Glauber term does not beat ε_q = 0 here); H 0 (R-finish not beaten; lead placebo unpowered).

## Notes
- Leave counts are structural (from `scheme/build.py`, counts.json) and set testability only.
