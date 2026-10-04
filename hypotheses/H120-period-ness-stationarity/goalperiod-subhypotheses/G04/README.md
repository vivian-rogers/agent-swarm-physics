# H120 × G04: #4 (2025-05-15 → 06-18)

**Verdict:** mixed
**Role:** exploratory (replication (unit 4c))
**Period:** regime I · 4 agents · one room · unit 4c: 2025-05-23 → 06-18, 19 days (2-h days; 06-18 outage day is its own unit 4d and is not in 4c).

## Why this period
The longest regime-I unit: 19 days with the same 4 agents and no step change.

## Prediction
*Written 2026-10-04 22:05 UTC, before running on this period.* Numbers in brackets are credences; verdict rules are in the main card.
- No drift test rejects (P5 share) [0.55]; power is likely below 0.8 at 4 agents × 2 h, in which case the verdict is inconclusive.

## Result
*Run 2026-10-04 (exploratory, non-holdout). Kinetic Ising (logistic) fit per core agent with weekday and session-length fields, ridge 1 on J; score tests calibrated by 1,000 random day splits (T1) and day-order permutations (T2); EP = corrected held-out Newton bound, nats per minute. Data: `data/processed/H120-period-ness-stationarity/results/results.json`.*

| Window, channel | N core, days | T1 split R (p) | T2 trend R (p) | min Holm (T1, T2) | EP drift ΔΣ (p) | Σ̂ [95%] | power at S2 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 4c act | 4, 18 | 1.01 (0.446) | 1.62 (0.129) | 0.584 | -7.3e-04 (0.17) | 3.2e-05 [-4.8e-04, 8.2e-04] | 0.65 |
| 4c talk | 4, 18 | 1.40 (0.139) | 1.60 (0.117) | 0.584 | 4.6e-03 (0.09) | 5.0e-04 [-2.7e-03, 4.0e-03] | 0.53 |

No test rejects, but activity power is 0.65 and talk power 0.53 at the drift that matters: inconclusive (written as mixed).


## Scorecard (period-specific axes)
C 1 (calibrated test), F 1 (power at this skeleton: see table).

## Notes
