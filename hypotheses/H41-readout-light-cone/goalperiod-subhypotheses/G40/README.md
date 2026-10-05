# H41 × G40: Connect your worlds into a 3D universe! (2026-05-04 → 2026-05-08)

**Verdict:** failed
**Role:** replication (exploratory)
**Period:** regime III · up to 15 agents · rooms [4] · 5 non-holdout days · units 40.

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
Run 2026-10-04 (`analysis/explore.py`; data `data/processed/H41-readout-light-cone/G40/`). 6043 novel items, 1955 adoptions.

| Test | Observed | Null / reference | Verdict |
| --- | --- | --- | --- |
| P1/A1 J_in (in-flight vs first post-entry talk call) | 0.59 [0.34, 1.17]; h(in-flight) 0.0242 (n 1981), h(o=1) 0.0145 (n 64425) | field synthetic J_in 0.4–0.6 | fail |
| A6 (post hoc) delay-matched J_mh | 1.31 [0.83, 2.65]; lenient cone 1.06; by class U/D/N/W: – / 0.68 / 2.04 / ∞ | field synthetic 0.8–1.2 | fail |
| P2 acausal share A (best) / A_rob | 0.025 [0.013, 0.036] / 0.014; within-room A_rob 0.014 | bound 0.05 | pass |
| P3 early A vs time-shuffled null (A3: not in verdict) | 0.038 vs 0.400 | null | below |
| P4 static V = P(n < h), parts h=1&n=0 / 2≤h<∞ / h=∞ | 0.027 = 0.025 / 0.000 / 0.002; cross-room share 0.002 |  |  |
| P5 cycles per hop (receiving / talk calls) | 19 / 1.0 (n 1902); v = 0.053 hops per call |  |  |
| P6 cadence b, volume c | b 0.32 [-1.31, 2.37], c -0.17 [-1.12, 0.90] (n 1874) | R4: b≈0, c<0 |  |
| P7 identified channels (robust acausal) | 0.93 of 28 | in-cone controls 0.97 | non-specific |

Verdict by the pre-registered rule A4 (J_in): **failed**. Post-hoc verdict with the delay-matched J_mh (A6): **failed**.

## Scorecard (period-specific axes)
- C (adequacy): J_in does not beat the field/room null (in-flight hazard).
- D (unfitted): acausal share 0.025; cycles per hop 19.


## Round 2 (2026-10-05)
*Role unchanged. Predictions, nulls and kill rules are in the card's "Round 2" section (written 03:50 UTC before any round-2 statistic). Verdict lines above are round-1/1b and are not changed by round 2.*
- **R4 (numbers):** the one period where numbers are co-generated: J_mh,D 0.69 [0.32, 1.55] on 26 in-flight adoptions (start-time RD 0.78, not validated). None of the in-flight number adoptions has a shared specific artifact touch with the source in the 30 min before, so the measured common stimulus does not explain it. #40 is the merged week with one cross-world objective; a common dashboard or API remains the candidate (round-3 redirect R8). Names J_mh 2.1 [1.0, 4.6].
- R3-Q: R_m 0.049 is above the Rayleigh 5% value (0.040), one of 4/25 periods.

## Notes
- Data: `data/processed/H41-readout-light-cone/G40/`.
