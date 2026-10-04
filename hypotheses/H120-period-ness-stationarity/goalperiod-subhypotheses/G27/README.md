# H120 × G27: #27 (2026-01-12 → 01-23)

**Verdict:** failed
**Role:** exploratory (replication)
**Period:** regime I · 10 agents · one room · 10 days (4-h days).

## Why this period
The longest late regime-I period, with 10 agents.

## Prediction
*Written 2026-10-04 22:05 UTC, before running on this period.* Numbers in brackets are credences; verdict rules are in the main card.
- No drift test rejects [0.55].

## Result
*Run 2026-10-04 (exploratory, non-holdout). Kinetic Ising (logistic) fit per core agent with weekday and session-length fields, ridge 1 on J; score tests calibrated by 1,000 random day splits (T1) and day-order permutations (T2); EP = corrected held-out Newton bound, nats per minute. Data: `data/processed/H120-period-ness-stationarity/results/results.json`.*

| Window, channel | N core, days | T1 split R (p) | T2 trend R (p) | min Holm (T1, T2) | EP drift ΔΣ (p) | Σ̂ [95%] | power at S2 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 27 act | 10, 10 | 1.55 (0.014) | 1.71 (0.005) | 0.030 | -1.5e-03 (0.59) | 1.6e-03 [-2.0e-03, 4.4e-03] | 0.93 |
| 27 talk | 10, 10 | 1.45 (0.095) | 1.26 (0.180) | 0.380 | 1.1e-02 (0.14) | -6.7e-03 [-2.4e-02, -7.1e-04] | 0.42 |

Activity drifts (trend p 0.005, Holm 0.03; first-day drop p 0.05); J-only p ≤ 0.018 (post hoc). Activity power 0.93.


## Scorecard (period-specific axes)
C 1 (calibrated test), F 2 (power at this skeleton: see table).

## Notes
