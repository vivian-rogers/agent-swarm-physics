# H41 × G36: Interact with other AI agents outside the Village! (2026-03-23 → 2026-03-27)

**Verdict:** supported
**Role:** replication (exploratory)
**Period:** regime II/III · up to 12 agents · rooms [2, 3] · 5 non-holdout days · units 36a, 36b, 36c.

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
Run 2026-10-04 (`analysis/explore.py`; data `data/processed/H41-readout-light-cone/G36/`). 4037 novel items, 1386 adoptions.

| Test | Observed | Null / reference | Verdict |
| --- | --- | --- | --- |
| P1/A1 J_in (in-flight vs first post-entry talk call) | 6.55 [2.75, 26.05]; h(in-flight) 0.0025 (n 399), h(o=1) 0.0245 (n 15033) | field synthetic J_in 0.4–0.6 | pass |
| A6 (post hoc) delay-matched J_mh | 25.44 [6.70, 42.92]; lenient cone ∞; by class U/D/N/W: ∞ / ∞ / 16.81 / ∞ | field synthetic 0.8–1.2 | pass |
| P2 acausal share A (best) / A_rob | 0.272 [0.184, 0.346] / 0.271; within-room A_rob 0.000 | bound 0.05 | fail |
| P3 early A vs time-shuffled null (A3: not in verdict) | 0.143 vs 0.467 | null | below |
| P4 static V = P(n < h), parts h=1&n=0 / 2≤h<∞ / h=∞ | 0.098 = 0.001 / 0.001 / 0.096; cross-room share 0.328 |  |  |
| P5 cycles per hop (receiving / talk calls) | 46 / 2.0 (n 1174); v = 0.022 hops per call |  |  |
| P6 cadence b, volume c | b 1.62 [-0.07, 2.74], c 0.15 [-0.51, 1.77] (n 1146) | R4: b≈0, c<0 |  |
| P7 identified channels (robust acausal) | 0.98 of 376 | in-cone controls 0.98 | non-specific |

Verdict by the pre-registered rule A4 (J_in): **supported**. Post-hoc verdict with the delay-matched J_mh (A6): **supported**.

## Scorecard (period-specific axes)
- C (adequacy): J_in beats the field/room null (in-flight hazard).
- D (unfitted): acausal share 0.272; cycles per hop 46.

## Notes
- Data: `data/processed/H41-readout-light-cone/G36/`.
