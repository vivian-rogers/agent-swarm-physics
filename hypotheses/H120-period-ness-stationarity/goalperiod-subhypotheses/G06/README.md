# H120 × G06: #6 (2025-06-26 → 07-15)

**Verdict:** mixed
**Role:** exploratory (replication (unit 6b))
**Period:** regime I · 4 agents · one room · unit 6b: 2025-07-03 → 07-15, 9 days (after NE02).

## Why this period
A 9-day regime-I unit.

## Prediction
*Written 2026-10-04 22:05 UTC, before running on this period.* Numbers in brackets are credences; verdict rules are in the main card.
- No drift test rejects [0.6]; power likely < 0.8 (inconclusive).

## Result
*Run 2026-10-04 (exploratory, non-holdout). Kinetic Ising (logistic) fit per core agent with weekday and session-length fields, ridge 1 on J; score tests calibrated by 1,000 random day splits (T1) and day-order permutations (T2); EP = corrected held-out Newton bound, nats per minute. Data: `data/processed/H120-period-ness-stationarity/results/results.json`.*

| Window, channel | N core, days | T1 split R (p) | T2 trend R (p) | min Holm (T1, T2) | EP drift ΔΣ (p) | Σ̂ [95%] | power at S2 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 6b act | 4, 9 | 2.07 (0.060) | 2.31 (0.010) | 0.060 | 5.4e-04 (0.13) | -2.9e-05 [-9.4e-04, 4.0e-04] | 0.15 |
| 6b talk | 4, 9 | 1.34 (0.216) | 1.91 (0.047) | 0.235 | -7.6e-03 (0.43) | -3.3e-04 [-9.0e-03, 7.4e-03] | 0.30 |

Activity trend p 0.01 raw (Holm 0.06); power 0.15 / 0.30: inconclusive (mixed). Dropping the first day removes the trend (p 0.14).


## Scorecard (period-specific axes)
C 1 (calibrated test), F 1 (power at this skeleton: see table).

## Notes
