# H120 × G08: #8 (2025-07-18 → 08-12)

**Verdict:** failed
**Role:** exploratory (replication)
**Period:** regime I · 4 agents · one room · 18 days (3-h days). No split.

## Why this period
A long regime-I period with no step change.

## Prediction
*Written 2026-10-04 22:05 UTC, before running on this period.* Numbers in brackets are credences; verdict rules are in the main card.
- No drift test rejects [0.55].

## Result
*Run 2026-10-04 (exploratory, non-holdout). Kinetic Ising (logistic) fit per core agent with weekday and session-length fields, ridge 1 on J; score tests calibrated by 1,000 random day splits (T1) and day-order permutations (T2); EP = corrected held-out Newton bound, nats per minute. Data: `data/processed/H120-period-ness-stationarity/results/results.json`.*

| Window, channel | N core, days | T1 split R (p) | T2 trend R (p) | min Holm (T1, T2) | EP drift ΔΣ (p) | Σ̂ [95%] | power at S2 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 8 act | 4, 18 | 0.99 (0.475) | 0.98 (0.488) | 1.000 | 6.9e-05 (0.78) | -9.4e-05 [-4.4e-04, 2.1e-04] | 0.55 |
| 8 talk | 4, 18 | 1.63 (0.091) | 2.27 (0.008) | 0.048 | -3.2e-03 (0.18) | -1.3e-03 [-3.8e-03, 1.3e-03] | 0.33 |

Activity is stationary (R 0.99). Talk trends (R 2.27, p 0.008, Holm 0.048), surviving the first-day drop (p 0.02); talk power is only 0.33, so the rejection is real but the channel cannot be called stationary either way. Verdict failed (a Holm rejection), borderline.


## Scorecard (period-specific axes)
C 1 (calibrated test), F 1 (power at this skeleton: see table).

## Notes
