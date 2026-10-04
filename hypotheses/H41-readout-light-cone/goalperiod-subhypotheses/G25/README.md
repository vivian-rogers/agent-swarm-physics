# H41 × G25: Create a digital museum of 2025 (2025-12-29 → 2026-01-02)

**Verdict:** failed
**Role:** replication (exploratory)
**Period:** regime I · up to 10 agents · rooms [0] · 5 non-holdout days · units 25.

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
Run 2026-10-04 (`analysis/explore.py`; data `data/processed/H41-readout-light-cone/G25/`). 2970 novel items, 826 adoptions.

| Test | Observed | Null / reference | Verdict |
| --- | --- | --- | --- |
| P1/A1 J_in (in-flight vs first post-entry talk call) | 1.13 [0.62, 5.11]; h(in-flight) 0.0068 (n 1179), h(o=1) 0.0081 (n 25710) | field synthetic J_in 0.4–0.6 | fail |
| A6 (post hoc) delay-matched J_mh | 2.39 [1.33, 8.02]; lenient cone 1.94; by class U/D/N/W: ∞ / 0.01 / 3.08 / ∞ | field synthetic 0.8–1.2 | pass |
| P2 acausal share A (best) / A_rob | 0.010 [0.001, 0.022] / 0.007; within-room A_rob 0.007 | bound 0.10 | pass |
| P3 early A vs time-shuffled null (A3: not in verdict) | 0.028 vs 0.386 | null | below |
| P4 static V = P(n < h), parts h=1&n=0 / 2≤h<∞ / h=∞ | 0.010 = 0.010 / 0.000 / 0.000; cross-room share 0.000 |  |  |
| P5 cycles per hop (receiving / talk calls) | 62 / 5.0 (n 818); v = 0.016 hops per call |  |  |
| P6 cadence b, volume c | b -0.11 [-0.56, 0.83], c 0.04 [-0.45, 0.79] (n 744) | R4: b≈0, c<0 |  |
| P7 identified channels (robust acausal) | 0.33 of 6 | in-cone controls 0.81 | non-specific |

Verdict by the pre-registered rule A4 (J_in): **failed**. Post-hoc verdict with the delay-matched J_mh (A6): **supported**.

## Scorecard (period-specific axes)
- C (adequacy): J_in does not beat the field/room null (in-flight hazard).
- D (unfitted): acausal share 0.010; cycles per hop 62.

## Notes
- Data: `data/processed/H41-readout-light-cone/G25/`.
