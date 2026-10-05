# H41 × G31: Pick your own goal (agents bid 3.7 Sonnet farewell) (2026-02-16 → 2026-02-20)

**Verdict:** mixed
**Role:** native (exploratory)
**Period:** regime I · up to 12 agents · rooms [0] · 5 non-holdout days · units 31a, 31b, 31c, 31d.

## Why this period
**Native test: the regime-I clock.** In regime I, chat-mode calls are *scheduled* (logged starts a median 55 s after the previous end; start-to-start ≈ 74 s), not chained, and H08 found that regime-I calls producing chat may be unlogged. Which clock makes adoption delays homogeneous across agents (wall seconds, all receiving calls, or chat-mode calls) tests whether the call cycle is the unit of propagation. #31 is a one-room regime-I week with 11–12 agents and dense chat. The replication numbers are reported as well.

## Prediction
*Written 2026-10-04 ~06:00 UTC (card, "Native tests"), before any real-data run.*
- **G31-a:** J_in > 1 (lower CI > 1), but smaller than the regime-III median J_in.
- **G31-b:** median cycles per hop ≤ 5 receiving calls and ≤ 2 chat-mode calls.
- **G31-c (clock test):** across adopters with ≥ 5 hop events, the between-agent SD of log median hop delay is smaller in receiving calls than in wall seconds.
- **Verdict:** supported if a and c hold; failed if c fails and J_in's CI includes 1; mixed otherwise. Prior 0.45.

**Replication layer (templated):**
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
**Native test (G31 regime-I clock), verdict: mixed** (checks {'a': False, 'b': False, 'c': True}).

| Test | Observed | Prediction | Verdict |
| --- | --- | --- | --- |
| a: J_in | 1.86 [1.24, 3.61] (in-flight at risk 1494); regime-III median 1.04 | > 1 and < regime-III median | fail |
| b: cycles per hop (receiving / chat-mode / talk calls) | 43 / 3.0 / 4.0 (n 1472) | ≤ 5 / ≤ 2 | fail |
| c: between-agent SD of log median hop delay (seconds / receiving calls / chat calls) | 0.67 / 0.59 / 0.53 (12 agents; calls − seconds [-0.28, 0.12]) | calls < seconds | pass |

**Replication layer:**

Run 2026-10-04 (`analysis/explore.py`; data `data/processed/H41-readout-light-cone/G31/`). 3722 novel items, 1493 adoptions.

| Test | Observed | Null / reference | Verdict |
| --- | --- | --- | --- |
| P1/A1 J_in (in-flight vs first post-entry talk call) | 1.86 [1.19, 3.94]; h(in-flight) 0.0060 (n 1494), h(o=1) 0.0118 (n 37694) | field synthetic J_in 0.4–0.6 | pass |
| A6 (post hoc) delay-matched J_mh | 2.95 [1.50, 6.53]; lenient cone 6.46; by class U/D/N/W: ∞ / 4.25 / 2.59 / ∞ | field synthetic 0.8–1.2 | pass |
| P2 acausal share A (best) / A_rob | 0.006 [0.003, 0.009] / 0.002; within-room A_rob 0.002 | bound 0.10 | pass |
| P3 early A vs time-shuffled null (A3: not in verdict) | 0.012 vs 0.398 | null | below |
| P4 static V = P(n < h), parts h=1&n=0 / 2≤h<∞ / h=∞ | 0.006 = 0.006 / 0.000 / 0.000; cross-room share 0.000 |  |  |
| P5 cycles per hop (receiving / talk calls) | 43 / 4.0 (n 1472); v = 0.023 hops per call |  |  |
| P6 cadence b, volume c | b 0.29 [-0.03, 1.14], c -0.29 [-0.52, -0.00] (n 1451) | R4: b≈0, c<0 |  |
| P7 identified channels (robust acausal) | 0.67 of 3 | in-cone controls 0.97 | non-specific |

Verdict by the pre-registered rule A4 (J_in): **supported**. Post-hoc verdict with the delay-matched J_mh (A6): **supported**.

## Scorecard (period-specific axes)
- C (adequacy): J_in beats the field/room null (in-flight hazard).
- D (unfitted): acausal share 0.006; cycles per hop 43.
- B: the call-unit (clock) assumption in regime I.


## Round 2 (2026-10-05)
*Role unchanged. Predictions, nulls and kill rules are in the card's "Round 2" section (written 03:50 UTC before any round-2 statistic). Verdict lines above are round-1/1b and are not changed by round 2.*
- **R3-H (descriptive, not scored):** 34 adoptions at H = 2 in one room; M₂ 23 vs entry-conditioned null 17 (p 0.04). R3-Q: R_m 0.026, R_e 0.057 (critical 0.045).
- **R4:** names J_mh 2.6 [1.3, 5.8]; start-time RD 1.6 [0.7, 4.2] (not validated; regime-I RDs are biased, H50 r2). Numbers: 1 in-flight adoption.

## Notes
- Data: `data/processed/H41-readout-light-cone/G31/`.
