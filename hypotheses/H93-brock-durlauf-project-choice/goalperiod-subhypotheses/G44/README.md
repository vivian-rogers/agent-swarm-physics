# H93 × G44: #best fine-tunes a leader; #rest picks its own goals (2026-05-26 → 05-29)

**Verdict:** mixed
**Role:** native
**Period:** regime III · mode C · 17–18 agents · #best (assigned) / #rest (self-chosen) · 4 days. Units 44a, 44b (two joins).

## Why this period
**Native: field contrast on the same days.** #best had an assigned team task; #rest chose its own goals (per-room goal override). A field difference should change the fields (named, habit, NEW) and m, not βJ. If BD coupling were the driver of herding, the free arm (no assigned target) would show the larger βJ.

## Prediction
*Written 2026-10-04, before running on this period.* **What I had seen:** the card's list; this period's structural counts from the scheme (`counts.json`: choice events, options, named options per channel) and, where simulated, the synthetic power of M4 on this period's skeleton. No real βJ, P_multi or m.

- N1: m(#best) ≥ 0.5 and m(#rest) ≤ 0.3 in work (0.6).
- N2: βĴ(M4) CI includes 0 in both arms, and the arm difference CI includes 0 (0.6; M4 power at βJ = 3 is 0.25 for the whole period, so a null is inconclusive here).
- N3: P_multi < 0.5 in both arms (0.75).
- Against: βĴ(M4, #rest) > 0 with CI > 0 and P_multi ≥ 0.5 in #rest.

## Result
*Run 2026-10-04 (non-holdout days only). Results: `data/processed/H93-brock-durlauf-project-choice/results/native_G44.json` and `G44.json`.*

**Native (assigned vs self-chosen arm on the same days).** Arms are the chooser's room at the choice.

| Arm | channel | events | m | βĴ M4 | βĴ M2 | P_multi |
| --- | --- | --- | --- | --- | --- | --- |
| #best (assigned team) | work | 21 (not testable) | 0.49 | +17.4 [0.4, 34.5] | +15.9 | 0.79 |
| #best (assigned team) | attention | 43 | 0.65 | +13.9 [5.4, 22.4] | +9.5 | 0.97 (8 fixed points) |
| #rest (self-chosen) | work | 74 | 0.22 | +2.6 [−2.6, 7.8] | +3.3 | 0.02 |
| #rest (self-chosen) | attention | 129 | 0.30 | +1.9 [−2.2, 5.9] | +4.4 | 0.00 |

| Native test | Observed | Verdict |
| --- | --- | --- |
| N1 m(#best) ≥ 0.5, m(#rest) ≤ 0.3 | 0.49 / 0.22 (work); 0.65 / 0.30 (attention) | supported (attention; work 0.01 short) |
| N2 βĴ CI includes 0 in both arms | #rest yes; #best attention +13.9 [5.4, 22.4] | failed |
| N3 P_multi < 0.5 in both arms | #rest 0.00–0.02; #best 0.97 | failed |
| Against: #rest βĴ > 0 (CI > 0) and P_multi ≥ 0.5 | no | not met |

The free arm shows no share coupling and one equilibrium. The assigned arm shows the largest βĴ of the round, because its team assignment is a field the model does not contain (the H54 token rule tags 79% of #best's attention choices as named, but the named term cannot carry a team assignment). **This is the exogenous-field impostor in action:** βĴ absorbs any unmodelled common field, so the BD multiplicity in #best is an artefact of the missing assignment field, not evidence for HH283.

Whole-period replication fit: work not identified (pooled SE > 5); attention βĴ(M4) +3.93 [0.56, 7.30].

## Scorecard (period-specific axes)
- E: 0 (the field contrast moves βĴ the wrong way: the coupling estimate absorbs the assignment field). G: 1 (DQ6 room assignments; #best's team repos).

## Notes
- 2026-10-04: folder created by the round-1 agent. Predictions use the M4 estimator (card amendment A1, written before any real fit).
