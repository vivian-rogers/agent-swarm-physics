# H120 × G38: #38 Charity drive (2026-04-02 → 04-24)

**Verdict:** failed
**Role:** exploratory (native (whole period; 38a; NE17 boundary) + replication (38a))
**Period:** regime III · 12 core agents · rooms #best/#rest · 17 days (4-h days; 04-16 window 7.6 h). Splits: 38a 04-02 → 04-13 (8 d), NE17 04-14 (38b), roster join 04-17 (38c), NE18 04-20 (38d), roster join 04-22 (38e).

## Why this period
The HH's test: the 17-day charity drive is the longest regime-III multi-week period before #51. 38a is the longest regime-III unit without a step change. NE17 is a boundary to rank.

## Prediction
*Written 2026-10-04 22:05 UTC, before running on this period.* Numbers in brackets are credences; verdict rules are in the main card.
- P1: no test rejects in the whole period [0.4]; HH kill = any Holm rejection.
- P2: no test rejects in 38a [0.6].
- P4: NE17 boundary in the top 20% of #38's day boundaries [0.3].
- P6: EP halves agree within the split null [0.65].

## Result
*Run 2026-10-04 (exploratory, non-holdout). Kinetic Ising (logistic) fit per core agent with weekday and session-length fields, ridge 1 on J; score tests calibrated by 1,000 random day splits (T1) and day-order permutations (T2); EP = corrected held-out Newton bound, nats per minute. Data: `data/processed/H120-period-ness-stationarity/results/results.json`.*

| Window, channel | N core, days | T1 split R (p) | T2 trend R (p) | min Holm (T1, T2) | EP drift ΔΣ (p) | Σ̂ [95%] | power at S2 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| G38 act | 11, 17 | 1.95 (0.002) | 2.22 (0.001) | 0.006 | -3.6e-04 (0.80) | -9.2e-06 [-4.3e-03, 5.0e-03] | 1.00 |
| G38 talk | 11, 17 | 2.18 (0.002) | 2.60 (0.001) | 0.006 | 9.0e-03 (0.47) | 8.7e-03 [-3.6e-03, 1.8e-02] | 0.43 |
| 38a act | 12, 8 | 1.28 (0.128) | 1.22 (0.161) | 0.639 | 4.5e-03 (0.29) | -1.7e-03 [-9.3e-03, 3.4e-03] | 0.85 |
| 38a talk | 12, 8 | 1.22 (0.027) | 1.08 (0.167) | 0.162 | 2.7e-02 (0.29) | 1.1e-05 [-3.4e-02, 1.8e-02] | 0.18 |

Whole period: drift in both channels (Holm ≤ 0.008), surviving weekday-stratified splits (p 0.004 / 0.002) and the first-day drop (p 0.003 / 0.017); J-only drift p ≤ 0.002 and pre-join (04-02 → 04-16) talk drift p ≤ 0.008 (post hoc). NE17 is not a special boundary (rank 0.36 / 0.21). 38a (8 days, no step inside): no drift (Holm ≥ 0.16), activity power 0.85, so stationary within the unit; talk inconclusive (power 0.18). EP: activity ≈ 0, talk 0.87×10⁻² [−0.36, 1.8]×10⁻² nats/min, no EP drift (unpowered). The HH kill fires: the period is not the stationary window. Figure: [`figures/boundary_profile.pdf`](figures/boundary_profile.pdf).


## Scorecard (period-specific axes)
B 1 (stationarity fails for the period, holds for 38a), C 2 (robust to stratification and day-1 drop), E 1 (NE17 not special), F 2 (activity power 1.00).

## Notes
