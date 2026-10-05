# H41 × G42: Run your own Youtube channel! (2026-05-18 → 2026-05-22)

**Verdict:** failed
**Role:** replication (exploratory)
**Period:** regime III · up to 16 agents · rooms [2, 3] · 5 non-holdout days · units 42a, 42b.

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
Run 2026-10-04 (`analysis/explore.py`; data `data/processed/H41-readout-light-cone/G42/`). 3916 novel items, 638 adoptions.

| Test | Observed | Null / reference | Verdict |
| --- | --- | --- | --- |
| P1/A1 J_in (in-flight vs first post-entry talk call) | 1.54 [0.91, 10.31]; h(in-flight) 0.0061 (n 490), h(o=1) 0.0110 (n 24333) | field synthetic J_in 0.4–0.6 | fail |
| A6 (post hoc) delay-matched J_mh | 7.75 [3.21, 8.34]; lenient cone 3.52; by class U/D/N/W: – / – / 10.58 / 2.68 | field synthetic 0.8–1.2 | pass |
| P2 acausal share A (best) / A_rob | 0.053 [0.024, 0.072] / 0.053; within-room A_rob 0.007 | bound 0.05 | fail |
| P3 early A vs time-shuffled null (A3: not in verdict) | 0.012 vs 0.355 | null | below |
| P4 static V = P(n < h), parts h=1&n=0 / 2≤h<∞ / h=∞ | 0.071 = 0.005 / 0.000 / 0.066; cross-room share 0.056 |  |  |
| P5 cycles per hop (receiving / talk calls) | 26 / 2.0 (n 611); v = 0.038 hops per call |  |  |
| P6 cadence b, volume c | b -1.14 [-3.72, 1.33], c -0.95 [-1.50, -0.05] (n 585) | R4: b≈0, c<0 |  |
| P7 identified channels (robust acausal) | 0.88 of 34 | in-cone controls 0.78 |  |

Verdict by the pre-registered rule A4 (J_in): **failed**. Post-hoc verdict with the delay-matched J_mh (A6): **supported**.

## Scorecard (period-specific axes)
- C (adequacy): J_in does not beat the field/room null (in-flight hazard).
- D (unfitted): acausal share 0.053; cycles per hop 26.


## Round 2 (2026-10-05)
*Role unchanged. Predictions, nulls and kill rules are in the card's "Round 2" section (written 03:50 UTC before any round-2 statistic). Verdict lines above are round-1/1b and are not changed by round 2.*
- **R2:** 30 strata, 152 controls. Ordered-read share 0.43 vs 0.28. OR_ord 4.7 [1.7, ∞], OR_post 4.4 [1.7, 24], Λ 1.08 [0.55, 7.9]: shared-project field, no ordered excess.
- **R4:** names J_mh 10.6 [3.9, ∞] (2 in-flight adoptions); numbers not estimable.

## Notes
- Data: `data/processed/H41-readout-light-cone/G42/`.
