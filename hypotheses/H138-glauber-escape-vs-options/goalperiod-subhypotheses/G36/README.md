# H138 × G36: replication unit (2026-03-23 → 2026-03-30)

**Verdict:** descriptive
**Role:** exploratory (replication)
**Period:** regime II · mode C · 13 agents · 5 days. Split at the 2026-03-24 regime boundary into 36a (regime II) and 36bc (regime III).

## Why this period
Attention channel only: 36a 36, 36bc 159 attention leaves (testable, ≥ 25); 36a 4, 36bc 13 work leaves (below 25: work channel descriptive). It adds one unit to the attention replication layer.

## Prediction
*Written 2026-10-07 (round 1, after the synthetic check and before any real-data hazard statistic). Seen: the structural leave counts above; no hazard, elasticity or q-by-leave statistic. Copied from the card's replication layer.*
- **P1 (replication, attention, secondary channel):** ε̂_q > 0 with 95% CI above 0. Credence 0.3; read against the label-noise world W4.
- **P3 (lead placebo, attention):** ε̂_q − ε̂_lead > 0 with CI above 0. Credence 0.25.
- Counts against: ε̂_q CI includes 0 with synthetic power ≥ 0.8 at ε_q = 0.5 (pooled).

## Result
*Round 1, 2026-10-07 (exploration). Estimator: cloglog hazard per own call, agent effects, active-time spline, agent-cluster sandwich (card Amendment A1). Power from the real-skeleton synthetic (W1 worlds, 200 replicates).*

| Channel · unit | Leaves | ε̂_q [95% CI] | permutation p | ε̂_q − ε̂_lead [boot CI] | ε̂_Z | power at ε 0.5 / 1 | Verdict |
| --- | --- | --- | --- | --- | --- | --- | --- |
| work · 36a | 4 | not testable (< 25 leaves) | — | — | — | — | — |
| work · 36bc | 13 | not testable (< 25 leaves) | — | — | — | — | — |
| attention · 36a | 36 | −4.53 [−9.41, 0.35] | 0.005 | −10.92 [−70.27, 12.57] | −1.65 [−8.88, 5.57] | 0.12 / 0.14 | P1 fails; unpowered |
| attention · 36bc | 159 | −0.31 [−0.87, 0.24] | 0.407 | −0.16 [−0.81, 0.53] | −0.07 [−0.78, 0.63] | 0.30 / 0.71 | P1 fails; unpowered |

- Period verdict: **descriptive**. No unit has a CI above 0, and the unit power at ε_q = 0.5 is below 0.8, so a null here is unpowered.
- 36a is one day (regime II); its CI is wide. 36bc is regime III.
- Data: `data/processed/H138-glauber-escape-vs-options/G36/`, results in `results/results.json`.

## Scorecard (period-specific axes)
C 0 (the Glauber term does not beat ε_q = 0 here); H 0 (R-finish not beaten; lead placebo unpowered).

## Notes
- Leave counts are structural (from `scheme/build.py`, counts.json) and set testability only.
