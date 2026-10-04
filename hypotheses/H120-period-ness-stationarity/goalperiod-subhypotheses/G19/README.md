# H120 × G19: #19 (2025-11-03 → 11-14)

**Verdict:** failed
**Role:** exploratory (replication (unit 19a))
**Period:** regime I · 7 agents · one room · unit 19a: 11-03 → 11-13, 9 days (roster join 11-14 is unit 19b).

## Why this period
A 9-day regime-I unit.

## Prediction
*Written 2026-10-04 22:05 UTC, before running on this period.* Numbers in brackets are credences; verdict rules are in the main card.
- No drift test rejects [0.6].

## Result
*Run 2026-10-04 (exploratory, non-holdout). Kinetic Ising (logistic) fit per core agent with weekday and session-length fields, ridge 1 on J; score tests calibrated by 1,000 random day splits (T1) and day-order permutations (T2); EP = corrected held-out Newton bound, nats per minute. Data: `data/processed/H120-period-ness-stationarity/results/results.json`.*

| Window, channel | N core, days | T1 split R (p) | T2 trend R (p) | min Holm (T1, T2) | EP drift ΔΣ (p) | Σ̂ [95%] | power at S2 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 19a act | 7, 9 | 1.66 (0.015) | 1.76 (0.001) | 0.006 | -1.3e-03 (0.39) | 6.4e-04 [-8.2e-04, 2.9e-03] | 0.77 |
| 19a talk | 7, 9 | 1.64 (0.013) | 1.49 (0.043) | 0.065 | -5.7e-03 (0.23) | 2.3e-03 [-4.1e-03, 6.9e-03] | 0.45 |

Activity drifts (trend p 0.001, Holm 0.006; first-day drop p 0.017); J-only drift p ≤ 0.007 (post hoc). Activity power 0.77.


## Scorecard (period-specific axes)
C 1 (calibrated test), F 1 (power at this skeleton: see table).

## Notes
