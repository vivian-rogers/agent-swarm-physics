# H140 × G41: regime-III shared-goal period #41 (2026-05-11 → 05-15)

**Verdict:** mixed
**Role:** exploratory (replication)
**Period:** regime III · computer-use context segments · 15 agents · two rooms (NE42 split) · 5 days; synthetic skeleton. Fit units: unit 41 (`period_units`).

## Why this period
A non-reserved regime-III period with context segments, so s_self exists. It is one more point for the replication layer (O1–O4). Units with < 300 scored talk calls enter only through the random-effects pool (card, exception (d)).

## Prediction
*Copied from the card and dated 2026-10-07 08:55 UTC (system clock), before running on this period. Seen: H113's #41 values (card "What I had seen"); the synthetic results on skeletons 51c, 51g, #38, #41 (no real H140 statistic).*
- **P1:** ŵ₁ ∈ [0.5, 1.5] with CI above 0. Credence 0.15.
- **P2:** â ∈ [0.15, 0.40], CI excluding 1 (scored only if the read − in-flight contrast CI > 0 and r < 0.7). Credence 0.6.
- **P3:** ŵ₂ (call-gap term) > 0 with CI. Credence 0.5.
- **P4:** γ̂_F / γ̂₁ ≤ 0.5 and read − in-flight contrast > 0. Credence 0.65.
- Counts against: the card's kill clauses on this unit (per-unit verdicts are descriptive for the kill; the pool decides).

## Result
Data: `data/processed/H140-degroot-readout-self-weight/G41/`, results `results/units_G41.json`. Run 2026-10-07 (exploration data; reserved days never enter the scheme). Estimator: Amendment A1 spec (primary) and the registered spec; agent-day cluster bootstrap, 300 draws.

| Prediction | Observed (bge; gte) | Verdict |
| --- | --- | --- |
| P1 ŵ₁ ∈ [0.5, 1.5], CI > 0 | 0.29 [−0.21, 0.83]; 0.32 [−0.06, 0.74] (433 rows). Registered 0.16 [−0.17, 0.62] | failed (CI includes 0) |
| P2 â ∈ [0.15, 0.40], CI excludes 1 | 0.26 [−0.04, 0.58] (identified: contrast 0.094 [0.048, 0.137], r 0.42); gte 0.22 [−0.19, 0.54] (identified) | supported |
| P3 ŵ₂ > 0 (registered) | 0.84 [−1.33, 2.63] | failed |
| P4 γ̂_F/γ̂₁ ≤ 0.5, contrast > 0 | −0.09; contrast > 0 | supported |

- N2 permutation null: mean 0.15 (sd 0.19); observed 0.29, p = 0.45.

## Scorecard (period-specific axes)
C 1 (read beats in-flight), D 0, H 1 (beats R-linear and R-convergence; not R-well).
