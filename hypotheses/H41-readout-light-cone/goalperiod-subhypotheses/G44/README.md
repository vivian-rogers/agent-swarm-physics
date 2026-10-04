# H41 × G44: Finetune your leader! (2026-05-26 → 2026-05-29)

**Verdict:** failed
**Verdict (1b):** failed (unchanged; one agent's room fixed, 1.5% of calls; J_in 0.70 [0.36, 1.84], J_mh 1.47 [0.83, 4.18])
**Role:** replication (exploratory)
**Period:** regime III · up to 18 agents · rooms [2, 3] · 4 non-holdout days · units 44a, 44b.

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
Run 2026-10-04 (`analysis/explore.py`; data `data/processed/H41-readout-light-cone/G44/`). 2883 novel items, 660 adoptions.

| Test | Observed | Null / reference | Verdict |
| --- | --- | --- | --- |
| P1/A1 J_in (in-flight vs first post-entry talk call) | 0.68 [0.37, 1.73]; h(in-flight) 0.0211 (n 805), h(o=1) 0.0147 (n 19733) | field synthetic J_in 0.4–0.6 | fail |
| A6 (post hoc) delay-matched J_mh | 1.45 [0.83, 5.82]; lenient cone 1.09; by class U/D/N/W: 0.27 / 1.65 / 1.96 / ∞ | field synthetic 0.8–1.2 | fail |
| P2 acausal share A (best) / A_rob | 0.033 [0.012, 0.053] / 0.029; within-room A_rob 0.028 | bound 0.05 | pass |
| P3 early A vs time-shuffled null (A3: not in verdict) | 0.041 vs 0.402 | null | below |
| P4 static V = P(n < h), parts h=1&n=0 / 2≤h<∞ / h=∞ | 0.058 = 0.026 / 0.000 / 0.032; cross-room share 0.014 |  |  |
| P5 cycles per hop (receiving / talk calls) | 9 / 2.0 (n 622); v = 0.111 hops per call |  |  |
| P6 cadence b, volume c | b 1.52 [-0.04, 2.20], c 0.07 [0.01, 0.67] (n 584) | R4: b≈0, c<0 |  |
| P7 identified channels (robust acausal) | 0.26 of 19 | in-cone controls 0.85 | non-specific |

Verdict by the pre-registered rule A4 (J_in): **failed**. Post-hoc verdict with the delay-matched J_mh (A6): **failed**.

## Scorecard (period-specific axes)
- C (adequacy): J_in does not beat the field/room null (in-flight hazard).
- D (unfitted): acausal share 0.033; cycles per hop 9.

## Notes
- Data: `data/processed/H41-readout-light-cone/G44/`.
