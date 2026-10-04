# H120 × G51: #51 main body (2026-07-06 → 09-04; the tail 09-07 → 09-18 is held out)

**Verdict:** supported
**Role:** exploratory (native (main body; 08-05 and 08-24 boundaries) + replication (51g))
**Period:** regime III · 21–32 agents (core = present on ≥ 90% of days) · #general, plus #focus 08-05 → 08-21 · 45 days (8-h days). Splits: units 51a–51l (roster joins, NE32, NE38, room changes, NE33).

## Why this period
The HH's second test: the longest period, predicted to drift (H91). The two room/drive boundaries (08-05 and 08-24) are known steps to rank. 51g (13 days) is the replication unit.

## Prediction
*Written 2026-10-04 22:05 UTC, before running on this period.* Numbers in brackets are credences; verdict rules are in the main card.
- P3: T1 or T2 rejects in activity [0.7] and talk [0.5]; R_split ≥ 1.5 in activity [0.6].
- P4: 08-05 or 08-24 in the top 20% of boundaries [0.55].
- P5 (51g): no rejection [0.5].
- P6: EP drifts (T3 rejects) [0.4].

## Result
*Run 2026-10-04 (exploratory, non-holdout). Kinetic Ising (logistic) fit per core agent with weekday and session-length fields, ridge 1 on J; score tests calibrated by 1,000 random day splits (T1) and day-order permutations (T2); EP = corrected held-out Newton bound, nats per minute. Data: `data/processed/H120-period-ness-stationarity/results/results.json`.*

| Window, channel | N core, days | T1 split R (p) | T2 trend R (p) | min Holm (T1, T2) | EP drift ΔΣ (p) | Σ̂ [95%] | power at S2 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 51main act | 25, 41 | 2.17 (0.001) | 2.26 (0.001) | 0.006 | -2.3e-03 (0.21) | 7.6e-05 [-3.1e-03, 1.3e-03] | 1.00 |
| 51main talk | 25, 41 | 2.14 (0.001) | 2.28 (0.001) | 0.006 | 4.3e-03 (0.45) | 1.0e-02 [2.4e-03, 1.3e-02] | 1.00 |
| 51g act | 27, 13 | 1.53 (0.001) | 1.52 (0.001) | 0.006 | -1.3e-02 (0.02) | -6.5e-03 [-1.8e-02, -3.1e-03] | 1.00 |
| 51g talk | 27, 13 | 1.68 (0.005) | 1.62 (0.002) | 0.008 | 5.8e-03 (0.79) | 4.1e-03 [-2.2e-02, 1.0e-02] | 0.80 |

Main body (07-10 → 09-04, 41 days; the first four days drop because agents that joined on 07-09 are core): drift in both channels (p 0.001), as predicted. The 08-05 boundary (#focus room, bookend stop) ranks in the top 13% for activity (talk 0.21); 08-24 does not (0.74 / 0.55). Base rates move most (h-only R 4.6 / 4.9, post hoc), but J alone also drifts (R 2.18 / 1.46). Talk EP is positive, 1.0×10⁻² [0.24, 1.3]×10⁻² nats/min, with no detected drift (unpowered). 51g (13 days, one unit): drifts too (Holm ≤ 0.015), so the replication prediction P5 fails here; its EP rejection rests on negative bounds and is not read as an arrow of time. Figure: [`figures/boundary_profile.pdf`](figures/boundary_profile.pdf).


## Scorecard (period-specific axes)
C 2, E 1 (08-05 top 13%), F 2 (power 1.00 both channels), G 1 (one known step ranks high, one does not).

## Notes
