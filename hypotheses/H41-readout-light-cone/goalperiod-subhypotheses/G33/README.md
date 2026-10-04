# H41 × G33: Discuss, debate, and act on your views about the recent Pentagon-AI company news (2026-03-02 → 2026-03-04)

**Verdict:** supported
**Verdict (1b):** supported (unchanged; one agent's room was unknown in round 1; J_in 1.87 [1.31, 2.75], J_mh 2.9 [2.3, 4.1])
**Role:** replication (exploratory)
**Period:** regime II · up to 11 agents · rooms [0] · 3 non-holdout days · units 33.

## Why this period
A replication point for the common estimator (layer 1): every eligible goal period gets the same statistics, so periods are comparable points on a phase diagram, not independent tests.

## Prediction
*Written 2026-10-04 06:16 UTC, before running on this period (templated replication prediction, layer 1; the card's P1–P8 with amendments A1–A5 as they apply here).*
- **P1 / A1 (gating):** J_in = h(first post-entry talk call) / h(in-flight talk call) > 1, day-bootstrap lower CI > 1 (if powered: ≥ 100 in-room pre-entry at-risk calls, ≥ 20 in-room adoptions at o = 1).
- **P2:** robust acausal share A_rob ≤ 0.05 and A (best) ≤ 0.08; for the verdict (A4) the within-room A_rob must meet the 0.05 bound.
- **P3 (reported, not in the verdict; A3):** A among early adoptions below the time-shuffled null.
- **P4:** one room: static hops h = 1 for almost all adopters, so V ≈ A.
- **P5:** median cycles per hop ≥ 10 receiving calls; talk calls per hop 1–2.
- **P6:** where ≥ 200 hop events: b > 0 (CI excluding 0), b ∈ [0.5, 1.5], c > −0.2.
- **P7:** ≥ 50% of robustly acausal adoptions have an identified channel.
- **P8:** h(in-flight) ≤ h(o = 1)/3 (the same J_in, read as rooms vs interaction graph).
- **Verdict rule (A4):** supported = J_in lower CI > 1 and within-room A_rob within the bound; failed = J_in powered with CI including 1 or below; mixed = J_in passes but within-room A_rob exceeds the bound; n/a = J_in not powered.

## Result
Run 2026-10-04 (`analysis/explore.py`; data `data/processed/H41-readout-light-cone/G33/`). 3815 novel items, 1767 adoptions.

| Test | Observed | Null / reference | Verdict |
| --- | --- | --- | --- |
| P1/A1 J_in (in-flight vs first post-entry talk call) | 1.88 [1.30, 3.29]; h(in-flight) 0.0107 (n 1775), h(o=1) 0.0206 (n 34098) | field synthetic J_in 0.4–0.6 | pass |
| A6 (post hoc) delay-matched J_mh | 3.03 [2.19, 5.48]; lenient cone 2.48; by class U/D/N/W: – / ∞ / 2.95 / ∞ | field synthetic 0.8–1.2 | pass |
| P2 acausal share A (best) / A_rob | 0.011 [0.007, 0.019] / 0.008; within-room A_rob 0.008 | bound 0.05 | pass |
| P3 early A vs time-shuffled null (A3: not in verdict) | 0.018 vs 0.417 | null | below |
| P4 static V = P(n < h), parts h=1&n=0 / 2≤h<∞ / h=∞ | 0.011 = 0.011 / 0.000 / 0.000; cross-room share 0.000 |  |  |
| P5 cycles per hop (receiving / talk calls) | 20 / 2.0 (n 1747); v = 0.050 hops per call |  |  |
| P6 cadence b, volume c | b 0.74 [0.26, 2.65], c -0.53 [-1.10, -0.09] (n 1589) | R4: b≈0, c<0 |  |
| P7 identified channels (robust acausal) | 1.00 of 14 | in-cone controls 0.98 |  |

Verdict by the pre-registered rule A4 (J_in): **supported**. Post-hoc verdict with the delay-matched J_mh (A6): **supported**.

## Scorecard (period-specific axes)
- C (adequacy): J_in beats the field/room null (in-flight hazard).
- D (unfitted): acausal share 0.011; cycles per hop 20.

## Notes
- Data: `data/processed/H41-readout-light-cone/G33/`.
