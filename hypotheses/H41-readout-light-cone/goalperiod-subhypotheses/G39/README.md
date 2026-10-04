# H41 × G39: Build your own interactive world! (2026-04-27 → 2026-05-01)

**Verdict:** failed
**Role:** replication (exploratory)
**Period:** regime III · up to 15 agents · rooms [2, 3] · 5 non-holdout days · units 39.

## Why this period
A replication point for the common estimator (layer 1): every eligible goal period gets the same statistics, so periods are comparable points on a phase diagram, not independent tests.

## Prediction
*Written 2026-10-04 06:16 UTC, before running on this period (templated replication prediction, layer 1; the card's P1–P8 with amendments A1–A5 as they apply here).*
- **P1 / A1 (gating):** J_in = h(first post-entry talk call) / h(in-flight talk call) > 1, day-bootstrap lower CI > 1 (if powered: ≥ 100 in-room pre-entry at-risk calls, ≥ 20 in-room adoptions at o = 1).
- **P2:** robust acausal share A_rob ≤ 0.05 and A (best) ≤ 0.08; for the verdict (A4) the within-room A_rob must meet the 0.05 bound.
- **P3 (reported, not in the verdict; A3):** A among early adoptions below the time-shuffled null.
- **P4:** two rooms: ≥ 90% of cross-room adopters unreachable on the pre-item read-out graph (h = ∞, W = 4 h), so V − A ≈ the cross-room share.
- **P5:** median cycles per hop ≥ 10 receiving calls; talk calls per hop 1–2.
- **P6:** where ≥ 200 hop events: b > 0 (CI excluding 0), b ∈ [0.5, 1.5], c > −0.2.
- **P7:** ≥ 50% of robustly acausal adoptions have an identified channel.
- **P8:** h(in-flight) ≤ h(o = 1)/3 (the same J_in, read as rooms vs interaction graph).
- **Verdict rule (A4):** supported = J_in lower CI > 1 and within-room A_rob within the bound; failed = J_in powered with CI including 1 or below; mixed = J_in passes but within-room A_rob exceeds the bound; n/a = J_in not powered.

## Result
Run 2026-10-04 (`analysis/explore.py`; data `data/processed/H41-readout-light-cone/G39/`). 3172 novel items, 317 adoptions.

| Test | Observed | Null / reference | Verdict |
| --- | --- | --- | --- |
| P1/A1 J_in (in-flight vs first post-entry talk call) | 1.50 [0.38, 8.20]; h(in-flight) 0.0023 (n 429), h(o=1) 0.0052 (n 23236) | field synthetic J_in 0.4–0.6 | fail |
| A6 (post hoc) delay-matched J_mh | 2.59 [0.66, 3.65]; lenient cone 1.41; by class U/D/N/W: – / 0.94 / ∞ / ∞ | field synthetic 0.8–1.2 | fail |
| P2 acausal share A (best) / A_rob | 0.032 [0.009, 0.081] / 0.032; within-room A_rob 0.010 | bound 0.05 | pass |
| P3 early A vs time-shuffled null (A3: not in verdict) | 0.025 vs 0.352 | null | below |
| P4 static V = P(n < h), parts h=1&n=0 / 2≤h<∞ / h=∞ | 0.025 = 0.006 / 0.000 / 0.019; cross-room share 0.022 |  |  |
| P5 cycles per hop (receiving / talk calls) | 62 / 3.0 (n 306); v = 0.016 hops per call |  |  |
| P6 cadence b, volume c | b -0.33 [-1.16, 0.27], c -1.06 [-1.67, -0.11] (n 293) | R4: b≈0, c<0 |  |
| P7 identified channels (robust acausal) | 1.00 of 10 | in-cone controls 0.79 |  |

Verdict by the pre-registered rule A4 (J_in): **failed**. Post-hoc verdict with the delay-matched J_mh (A6): **failed**.

## Scorecard (period-specific axes)
- C (adequacy): J_in does not beat the field/room null (in-flight hazard).
- D (unfitted): acausal share 0.032; cycles per hop 62.

## Notes
- Data: `data/processed/H41-readout-light-cone/G39/`.
