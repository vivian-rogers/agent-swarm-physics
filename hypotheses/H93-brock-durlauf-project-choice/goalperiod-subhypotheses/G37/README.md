# H93 × G37: Pick your own goal (free week, two rooms) (2026-03-30 → 04-01)

**Verdict:** mixed
**Role:** native
**Period:** regime III · mode F · 12 agents · #best / #rest (identical kickoff text) · 3 days. One unit.

## Why this period
**Native: rooms as same-field replicas.** Both rooms received identical kickoff text in a free week. In BD with a unique equilibrium, two rooms under one field land in the same state up to finite-N noise; with multiple equilibria they can split (one herded, one dispersed). The test fits M4 on the whole period (one field), simulates the fitted model on the real event skeleton (200 runs), and compares the observed room difference Δm of the order parameter with the simulated distribution. Per-room BD fixed points are counted at the room fits and at the pooled fit.

## Prediction
*Written 2026-10-04, before running on this period.* **What I had seen:** the card's list; this period's structural counts from the scheme (`counts.json`: choice events, options, named options per channel) and, where simulated, the synthetic power of M4 on this period's skeleton. No real βJ, P_multi or m.

- N1: the observed Δm lies inside the central 95% of the simulated Δm (two-sided p > 0.05) in the channel with more events (attention) (0.65).
- N2: P_multi < 0.5 in both rooms at the pooled fit (0.75).
- Against (supports HH283): p ≤ 0.05 with one room herded (m ≥ 0.5) and the other dispersed (m ≤ 0.3), and P_multi ≥ 0.5.

## Result
*Run 2026-10-04 (non-holdout days only). Results: `data/processed/H93-brock-durlauf-project-choice/results/native_G37.json` and `G37.json`.*

**Native (rooms as same-field replicas).** Attention, 110 events: #best m = 0.63, #rest m = 0.40, Δm = +0.22; the M4 model fitted on the whole period and simulated on the real event skeleton (200 runs) gives Δm 95% range [−0.05, +0.39], two-sided p = 0.50. The two rooms are consistent with one equilibrium under one field (**N1 supported**). Work: only #rest has ≥ 2 co-hosts per arrival, so Δm is not defined.

BD fixed points: at the pooled fit, P_multi = 0.25 (#best) and 0.25 (#rest) in attention, 0.47 in #rest work (**N2 supported**, by a margin of 0.03 in work). At the rooms' own fits, #rest work (37 events) has βĴ +7.11 [4.33, 9.89] and P_multi 0.88 (7 stable fixed points, all herded at m* ≈ 0.90–0.96), and #best attention (13 events) 0.61. The room fits sit near or above the boundary; the pooled fit sits below it (βĴ/γ_c 0.82 work, 0.77 attention).

| Native test | Observed | Verdict |
| --- | --- | --- |
| N1 Δm inside the simulated 95% (attention) | +0.22 in [−0.05, +0.39], p = 0.50 | supported |
| N2 P_multi < 0.5 in both rooms at the pooled fit | 0.25, 0.25 (attention); 0.47 (#rest work) | supported |
| Against: one room herded, one dispersed, P_multi ≥ 0.5 | #best 0.63, #rest 0.40 (neither ≤ 0.3) | not met |
| (context) room fits | #rest work P_multi 0.88 (37 events) | the room fit alone would claim multiplicity |

## Scorecard (period-specific axes)
- C: 1 (rooms inside the one-equilibrium band). E: 1 (a same-field replica pair; no split). H: 1 (fields-plus-share reproduces both rooms).

## Notes
- 2026-10-04: folder created by the round-1 agent. Predictions use the M4 estimator (card amendment A1, written before any real fit).
