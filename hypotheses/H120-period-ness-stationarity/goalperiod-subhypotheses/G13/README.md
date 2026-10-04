# H120 × G13: #13 (2025-09-08 → 09-19)

**Verdict:** mixed
**Role:** exploratory (replication)
**Period:** regime I · 6 agents · one room · 10 days (3-h days).

## Why this period
A 10-day regime-I period.

## Prediction
*Written 2026-10-04 22:05 UTC, before running on this period.* Numbers in brackets are credences; verdict rules are in the main card.
- No drift test rejects [0.6]; power likely < 0.8.

## Result
*Run 2026-10-04 (exploratory, non-holdout). Kinetic Ising (logistic) fit per core agent with weekday and session-length fields, ridge 1 on J; score tests calibrated by 1,000 random day splits (T1) and day-order permutations (T2); EP = corrected held-out Newton bound, nats per minute. Data: `data/processed/H120-period-ness-stationarity/results/results.json`.*

| Window, channel | N core, days | T1 split R (p) | T2 trend R (p) | min Holm (T1, T2) | EP drift ΔΣ (p) | Σ̂ [95%] | power at S2 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 13 act | 6, 10 | 1.07 (0.419) | 1.03 (0.400) | 1.000 | -2.0e-03 (0.04) | -5.1e-04 [-2.1e-03, 9.9e-04] | 0.45 |
| 13 talk | 6, 10 | 0.99 (0.453) | 0.96 (0.487) | 1.000 | 4.7e-03 (0.11) | -8.6e-04 [-7.9e-03, 3.3e-03] | 0.43 |

No test rejects; power 0.45 / 0.43: inconclusive (mixed).


## Scorecard (period-specific axes)
C 1 (calibrated test), F 1 (power at this skeleton: see table).

## Notes
