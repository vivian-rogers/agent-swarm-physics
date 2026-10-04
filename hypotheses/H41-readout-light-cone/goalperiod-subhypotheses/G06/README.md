# H41 × G06: Create your own merch store. Whichever agent's store makes the most profit wins! (2025-06-26 → 2025-07-15)

**Verdict:** supported
**Role:** replication (exploratory)
**Period:** regime I · up to 4 agents · rooms [0] · 15 non-holdout days · units 6a, 6b.

## Why this period
A replication point for the common estimator (layer 1): every eligible goal period gets the same statistics, so periods are comparable points on a phase diagram, not independent tests.

## Prediction
*Written 2026-10-04 06:16 UTC, before running on this period (templated replication prediction, layer 1; the card's P1–P8 with amendments A1–A5 as they apply here).*
- **P1 / A1 (gating):** J_in = h(first post-entry talk call) / h(in-flight talk call) > 1, day-bootstrap lower CI > 1 (if powered: ≥ 100 in-room pre-entry at-risk calls, ≥ 20 in-room adoptions at o = 1).
- **P2:** robust acausal share A_rob ≤ 0.10 and A (best) ≤ 0.15; for the verdict (A4) the within-room A_rob must meet the 0.10 bound.
- **P3 (reported, not in the verdict; A3):** A among early adoptions below the time-shuffled null.
- **P4:** one room: static hops h = 1 for almost all adopters, so V ≈ A.
- **P5:** median cycles per hop ≤ 5 receiving calls; talk calls per hop 1–2.
- **P6:** where ≥ 200 hop events: b > 0 (CI excluding 0), b ∈ [0.5, 1.5], c > −0.2.
- **P7:** ≥ 50% of robustly acausal adoptions have an identified channel.
- **P8:** h(in-flight) ≤ h(o = 1)/3 (the same J_in, read as rooms vs interaction graph).
- **Verdict rule (A4):** supported = J_in lower CI > 1 and within-room A_rob within the bound; failed = J_in powered with CI including 1 or below; mixed = J_in passes but within-room A_rob exceeds the bound; n/a = J_in not powered.

## Result
Run 2026-10-04 (`analysis/explore.py`; data `data/processed/H41-readout-light-cone/G06/`). 1232 novel items, 165 adoptions.

| Test | Observed | Null / reference | Verdict |
| --- | --- | --- | --- |
| P1/A1 J_in (in-flight vs first post-entry talk call) | 3.98 [1.83, 6.80]; h(in-flight) 0.0000 (n 229), h(o=1) 0.0085 (n 3636) | field synthetic J_in 0.4–0.6 | pass |
| A6 (post hoc) delay-matched J_mh | ∞ [–, –]; lenient cone ∞; by class U/D/N/W: – / ∞ / ∞ / – | field synthetic 0.8–1.2 | fail |
| P2 acausal share A (best) / A_rob | 0.000 [0.000, 0.000] / 0.000; within-room A_rob 0.000 | bound 0.10 | pass |
| P3 early A vs time-shuffled null (A3: not in verdict) | 0.000 vs 0.396 | null | below |
| P4 static V = P(n < h), parts h=1&n=0 / 2≤h<∞ / h=∞ | 0.000 = 0.000 / 0.000 / 0.000; cross-room share 0.000 |  |  |
| P5 cycles per hop (receiving / talk calls) | 108 / 13.0 (n 146); v = 0.009 hops per call |  |  |
| P6 cadence b, volume c | b -0.65 [-7.01, 1.07], c 0.54 [-0.30, 1.32] (n 157) | R4: b≈0, c<0 |  |
| P7 identified channels (robust acausal) | – of 0 | in-cone controls 0.56 | non-specific |

Verdict by the pre-registered rule A4 (J_in): **supported**. Post-hoc verdict with the delay-matched J_mh (A6): **supported**.

## Scorecard (period-specific axes)
- C (adequacy): J_in beats the field/room null (in-flight hazard).
- D (unfitted): acausal share 0.000; cycles per hop 108.

## Notes
- Data: `data/processed/H41-readout-light-cone/G06/`.
