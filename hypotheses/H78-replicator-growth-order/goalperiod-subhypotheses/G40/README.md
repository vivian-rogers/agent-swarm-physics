# H78 × G40: Connect your worlds into a 3D universe (NE42 merge) (2026-05-04 → 05-08)

**Verdict:** mixed
**Role:** native
**Period:** regime III · one shared hub named by the kickoff, one merged room · 15 agents · 5 days. One unit.

## Why this period
One hub named by the kickoff in one merged room (H54: hub named; H53: an 8-agent hub wave with R = 0; H11: work spread by fields). This is the field-made growth regime the HH asks to condition away: the order estimator should see formation (p ≈ 0), not autocatalysis.

## Prediction
*Written 2026-10-04, before running on this period.* **What I had seen:** the card's list, plus this period's aggregate counts from the built tables (recruitments, births, switch-outs, expiries; listed below) used to calibrate the synthetic worlds. No σ*, fitness, order or step statistic had been computed on this period. Counts: 23 recruitments, 12 births, 14 switch-outs, 10 expiries.

- **N78-40a:** ≥ 50% of all arrivals go to kickoff-named repos (0.55).
- **N78-40b:** the order fitted on the named stratum alone is p̂ ≤ 0.5 (growth independent of n: formation), and below the formation-free p̂ of the same period (0.35).
- **N78-40c (A0):** the share of hosts on named repos rises after the kickoff, not drops (m_after > m_before; 0.6): the Mathis decoupling does not occur in a field-set week.
- Against: named-stratum p̂ ≥ 1.

## Result
*Run 2026-10-04 (non-holdout days only; host expiry E = 100).*

| Prediction | Observed | Verdict |
| --- | --- | --- |
| N78-40a ≥ 50% of arrivals to named repos | 48/48 recruitments into named repos; formation share of all arrivals 1.00 | supported |
| N78-40b named-stratum p̂ ≤ 0.5 | 1.62 [1.10, 2.13] (48) | failed |
| N78-40c named-host share rises after the kickoff | 0.86 → 0.99 at 4.5 active h, calibrated step (surrogate p = 0.025) | supported |

The field-made hub does not grow like a pure formation term (p ≈ 0): its recruitment rises with its host count, at a rate the fitness-spread null also produces (1.32–1.34 at this period's counts). The step time (4.5 active h) equals H48's content-settling time. No formation-free recruitment exists, so the primary p is undefined. Data: `data/processed/H78-replicator-growth-order/GG40/`, results `.../results/GG40.json`.

## Scorecard (period-specific axes)
- E: 0 (the field-made hub is not separable from copying by p). G: 1 (the kickoff-named hub takes every recruit).

## Notes
- 2026-10-04: folder created by the round-1 agent.
- 2026-10-04: amendment A1 (card) moved the primary host expiry from E = 300 to E = 100 before this period was run; the counts quoted under Prediction are at E = 300. A2 (post hoc) added the touch-based impostor class, the fitness-spread null worlds and the AR(1) surrogate null for the A0 step test.
