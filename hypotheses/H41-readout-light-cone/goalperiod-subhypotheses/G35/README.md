# H41 × G35: Test your game to make it as fun and functional as you can! (2026-03-16 → 2026-03-20)

**Verdict:** failed
**Verdict (1b):** failed, post hoc failed (unchanged: J_mh lower CI 1.005 on the deterministic draw but > 1 in 0/20 other seeds; borderline)
**Role:** replication (exploratory)
**Period:** regime II · up to 12 agents · rooms [2, 3] · 5 non-holdout days · units 35.

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
Run 2026-10-04 (`analysis/explore.py`; data `data/processed/H41-readout-light-cone/G35/`). 3068 novel items, 1907 adoptions.

| Test | Observed | Null / reference | Verdict |
| --- | --- | --- | --- |
| P1/A1 J_in (in-flight vs first post-entry talk call) | 1.60 [0.80, 3.16]; h(in-flight) 0.0172 (n 523), h(o=1) 0.0290 (n 18404) | field synthetic J_in 0.4–0.6 | fail |
| A6 (post hoc) delay-matched J_mh | 2.55 [0.99, 6.52]; lenient cone 3.63; by class U/D/N/W: ∞ / 0.06 / 2.83 / ∞ | field synthetic 0.8–1.2 | fail |
| P2 acausal share A (best) / A_rob | 0.202 [0.102, 0.277] / 0.199; within-room A_rob 0.003 | bound 0.05 | fail |
| P3 early A vs time-shuffled null (A3: not in verdict) | 0.041 vs 0.404 | null | below |
| P4 static V = P(n < h), parts h=1&n=0 / 2≤h<∞ / h=∞ | 0.115 = 0.005 / 0.001 / 0.110; cross-room share 0.253 |  |  |
| P5 cycles per hop (receiving / talk calls) | 53 / 3.0 (n 1631); v = 0.019 hops per call |  |  |
| P6 cadence b, volume c | b 1.39 [0.64, 2.47], c 0.30 [-0.30, 0.78] (n 1573) | R4: b≈0, c<0 |  |
| P7 identified channels (robust acausal) | 0.60 of 380 | in-cone controls 0.98 | non-specific |

Verdict by the pre-registered rule A4 (J_in): **failed**. Post-hoc verdict with the delay-matched J_mh (A6): **failed**.

## Scorecard (period-specific axes)
- C (adequacy): J_in does not beat the field/room null (in-flight hazard).
- D (unfitted): acausal share 0.202; cycles per hop 53.


## Round 2 (2026-10-05)
*Role unchanged. Predictions, nulls and kill rules are in the card's "Round 2" section (written 03:50 UTC before any round-2 statistic). Verdict lines above are round-1/1b and are not changed by round 2.*
- **R2 (ordered reads; predictions in the card, 2026-10-05 03:50 UTC):** 376 cross-room robustly acausal adoptions, 1,256 same-moment non-adopters. Ordered-read share 0.05 vs 0.16 for non-adopters. OR_ord 0.34 [0.17, 0.48], OR_post 0.19 [0.07, 0.31], **Λ 1.84 [1.20, 3.05]**: the only period with Λ's CI above 1, but both odds ratios are below 1 (adopters read the source's repos less than non-adopters).
- **R3-H (not scored, synthetic size 3/8):** M₂ 42 vs entry-conditioned null 33 (p 0.004); 73 adoptions at H = 2.
- **R4:** names J_mh 2.8 [1.3, 8.2]; numbers have 1 in-flight adoption (not estimable).

## Notes
- Data: `data/processed/H41-readout-light-cone/G35/`.
