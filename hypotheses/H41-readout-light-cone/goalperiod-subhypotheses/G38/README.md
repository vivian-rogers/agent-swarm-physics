# H41 × G38: Choose a charity and raise as much money as you can for it (2026-04-02 → 2026-04-24)

**Verdict:** mixed
**Verdict (1b):** mixed (unchanged; no stale room lookups on non-holdout days; rebuilt tables identical)
**Role:** native (exploratory)
**Period:** regime III · up to 14 agents · rooms [2, 3] · 17 non-holdout days · units 38a, 38b, 38c, 38d, 38e.

## Why this period
**Native test: the two-room cage.** #38 is the largest two-room period (#best / #rest, 17 non-holdout days, regime III). The room split is a known cut of the read-out graph: an item can cross only through a room-mover, a human posting in both rooms, or an unlogged channel (shared repos and sites, the web, memory, history search). Cross-room adoptions are therefore a direct probe of unlogged channels (HH157's artifact leak). The replication numbers are reported as well.

## Prediction
*Written 2026-10-04 ~06:00 UTC (card, "Native tests"), before any real-data run.* Cross-room adoption = the adopter was in the other room than the source at t0.
- **G38-a:** ≥ 80% of cross-room adoptions are outside the logged cone at use.
- **G38-b:** the cross-room adoption hazard per at-risk talk call within 2 h is ≤ 1/5 of the within-room hazard.
- **G38-c:** among robustly acausal cross-room adoptions, shared artifact + web explain ≥ 30%, more than among within-room acausal adoptions.
- **G38-d:** median wall time to cross-room adoption ≥ 3× the within-room median.
- **Verdict:** supported if a, b and c hold; failed if a or b fails; mixed otherwise. Prior 0.4.
- Replication predictions (templated) also apply; see the card.

**Replication layer (templated):**
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
**Native test (G38 cage), verdict: mixed** (checks {'a': True, 'b': True, 'c': False}).

| Test | Observed | Prediction | Verdict |
| --- | --- | --- | --- |
| a: cross-room adoptions outside the logged cone | 1.00 (lenient 1.00); 54 of 2904 adoptions are cross-room | ≥ 0.80 | pass |
| b: cross / within hazard per talk call (2 h) | 0.001 [0.000, 0.002]; h_out 0.0000, h_in 0.0269 | ≤ 0.20 | pass |
| c: artifact + web among robust acausal, cross vs within | 0.19 (n 54) vs 0.31 (n 13) | ≥ 0.30 and > within | fail |
| d: median delay cross / within | 4272.3 / 5.1 min (ratio 830.5) | ≥ 3 | pass |

Channel mix of robust cross-room violations: {'private': 0.16666666666666666, 'web': 0.1111111111111111, 'templated': 0.018518518518518517, 'unexplained': 0.3333333333333333, 'room_move': 0.018518518518518517, 'search': 0.2777777777777778, 'human_logged': 0.018518518518518517, 'artifact': 0.05555555555555555}. In-cone cross-room adoptions by cone hop count: [].

**Replication layer:**

Run 2026-10-04 (`analysis/explore.py`; data `data/processed/H41-readout-light-cone/G38/`). 7841 novel items, 2904 adoptions.

| Test | Observed | Null / reference | Verdict |
| --- | --- | --- | --- |
| P1/A1 J_in (in-flight vs first post-entry talk call) | 1.03 [0.67, 1.81]; h(in-flight) 0.0509 (n 688), h(o=1) 0.0531 (n 31561) | field synthetic J_in 0.4–0.6 | fail |
| A6 (post hoc) delay-matched J_mh | 2.59 [1.72, 4.51]; lenient cone 5.04; by class U/D/N/W: – / 2.43 / 2.98 / 1.57 | field synthetic 0.8–1.2 | pass |
| P2 acausal share A (best) / A_rob | 0.032 [0.024, 0.040] / 0.023; within-room A_rob 0.005 | bound 0.05 | pass |
| P3 early A vs time-shuffled null (A3: not in verdict) | 0.019 vs 0.388 | null | below |
| P4 static V = P(n < h), parts h=1&n=0 / 2≤h<∞ / h=∞ | 0.042 = 0.012 / 0.000 / 0.030; cross-room share 0.019 |  |  |
| P5 cycles per hop (receiving / talk calls) | 12 / 1.0 (n 2815); v = 0.083 hops per call |  |  |
| P6 cadence b, volume c | b 0.91 [0.36, 1.58], c -0.27 [-0.59, 0.09] (n 2740) | R4: b≈0, c<0 |  |
| P7 identified channels (robust acausal) | 0.66 of 67 | in-cone controls 0.75 | non-specific |

Verdict by the pre-registered rule A4 (J_in): **failed**. Post-hoc verdict with the delay-matched J_mh (A6): **supported**.

## Scorecard (period-specific axes)
- C (adequacy): J_in does not beat the field/room null (in-flight hazard).
- D (unfitted): acausal share 0.032; cycles per hop 12.
- E/G: the room cut is known structure; cross-room spread outside the logged cone tests the cage (G).


## Round 2 (2026-10-05)
*Role unchanged. Predictions, nulls and kill rules are in the card's "Round 2" section (written 03:50 UTC before any round-2 statistic). Verdict lines above are round-1/1b and are not changed by round 2.*
- **Native, R2 (the cage's leaks):** 54 cross-room robustly acausal adoptions, 242 controls. Ordered-read share 0.06 vs 0.04. OR_ord 2.3 [0, 12], OR_post 9.2 [2.1, ∞], Λ 0.25 [0, 1.31]. In the cage, reading the other room's fresh artifacts does not precede leaks; the few leaks are not traced by artifact reads either (round 1's G38-c also failed).
- **R4:** numbers gate here: J_mh,D 2.45 [1.36, 5.79] (20 in-flight adoptions), J_mh,D without a shared artifact touch 3.4 [1.7, 16.8]. A shared specific artifact touch is enriched among in-flight number adoptions (0.50 vs 0.24 post-t0), but ψ_D is 1.7 [0.4, 9.8]. Names J_mh 3.0 [1.9, 6.9].
- R3-Q: R_m 0.009, R_e 0.009 (critical 0.033): no quantization from the message.

## Notes
- Data: `data/processed/H41-readout-light-cone/G38/`.
