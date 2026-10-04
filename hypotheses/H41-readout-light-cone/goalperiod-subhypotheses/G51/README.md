# H41 × G51: Each agent: Maximize your assigned goal! (2026-07-06 → 2026-09-04)

**Verdict:** mixed
**Role:** native (exploratory)
**Period:** regime III · up to 32 agents · rooms [0, 15] · 45 non-holdout days · units 51a, 51b, 51c, 51d, 51e, 51f, 51g, 51h, 51i, 51j, 51k, 51l.

## Why this period
**Native test: isolation and hopping rooms.** #51 (21–29 agents, regime III) has agents alone in onboarding rooms (NE32's Sol/Terra/Luna rooms on 07-09, Grok 4.5's on 07-10) and frequent hops between #general and #focus from 08-05. An agent alone in a room has no logged input from other agents, so every #general-novel item it uses there is outside the logged cone: a ground-truth "no logged channel" condition. #51 also has the widest cadence spread for the cadence-vs-volume test. The replication numbers are reported as well.

## Prediction
*Written 2026-10-04 ~06:00 UTC (card, "Native tests"), before any real-data run.*
- **G51-a:** every adoption of a #general-novel item by an agent alone in a room is acausal (by construction), and ≥ 50% of them have an identified channel.
- **G51-b:** #general ↔ #focus cross-room adoptions are mostly inside the logged cone (≥ 70%): hoppers bridge on minute scales.
- **G51-c:** cadence regression b ∈ [0.5, 1.5] with CI excluding 0, and c > −0.2.
- **Verdict:** supported if b and c hold and a's channel share ≥ 50% (or a has < 5 events); failed if c fails with b ≈ 0; mixed otherwise. Prior 0.35.

**Replication layer (templated):**
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
**Native test (G51 isolation and hopping rooms), verdict: mixed** (checks {'a_iso_channels': True, 'b_focus': True, 'c_cadence_b': False, 'c_cadence_c': True}).

| Test | Observed | Prediction | Verdict |
| --- | --- | --- | --- |
| a: adoptions of #general-novel items by agents alone in a room | 1 adoptions (rooms [15]); acausal 1.00; identified channel 1.00; mix {'artifact': 1} | all acausal; ≥ 0.5 identified | pass |
| b: #general ↔ #focus cross-room adoptions inside the cone | 0.97 (lenient 0.97; n 1720); by hop count [[1, 1588], [2, 70], [3, 11]] | ≥ 0.70 | pass |
| c: cadence b, volume c | b 0.04 [-0.44, 0.59], c 0.65 [0.17, 1.19] (n 7665) | b ∈ [0.5, 1.5], CI > 0; c > −0.2 | fail |

**Replication layer:**

Run 2026-10-04 (`analysis/explore.py`; data `data/processed/H41-readout-light-cone/G51/`). 51929 novel items, 16521 adoptions.

| Test | Observed | Null / reference | Verdict |
| --- | --- | --- | --- |
| P1/A1 J_in (in-flight vs first post-entry talk call) | 40.70 [12.25, 109.98]; h(in-flight) 0.0003 (n 158639), h(o=1) 0.0135 (n 224975) | field synthetic J_in 0.4–0.6 | pass |
| A6 (post hoc) delay-matched J_mh | 15.80 [7.44, 31.06]; lenient cone 18.35; by class U/D/N/W: ∞ / 11.34 / 18.66 / 12.85 | field synthetic 0.8–1.2 | pass |
| P2 acausal share A (best) / A_rob | 0.028 [0.014, 0.047] / 0.027; within-room A_rob 0.005 | bound 0.05 | pass |
| P3 early A vs time-shuffled null (A3: not in verdict) | 0.017 vs 0.410 | null | below |
| P4 static V = P(n < h), parts h=1&n=0 / 2≤h<∞ / h=∞ | 0.054 = 0.003 / 0.001 / 0.050; cross-room share 0.507 |  |  |
| P5 cycles per hop (receiving / talk calls) | 27 / 3.0 (n 15426); v = 0.037 hops per call |  |  |
| P6 cadence b, volume c | b 0.04 [-0.44, 0.59], c 0.65 [0.17, 1.19] (n 7665) | R4: b≈0, c<0 |  |
| P7 identified channels (robust acausal) | 0.84 of 438 | in-cone controls 0.84 | non-specific |

Verdict by the pre-registered rule A4 (J_in): **supported**. Post-hoc verdict with the delay-matched J_mh (A6): **supported**.

## Scorecard (period-specific axes)
- C (adequacy): J_in beats the field/room null (in-flight hazard).
- D (unfitted): acausal share 0.028; cycles per hop 27.
- G: isolated agents are a no-logged-input ground truth.

## Notes
- Data: `data/processed/H41-readout-light-cone/G51/`.
