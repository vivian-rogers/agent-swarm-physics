# H93 × G51: Each agent: maximize your assigned goal (private roles) (2026-07-06 → 09-04 (non-holdout units 51a–51l))

**Verdict:** mixed
**Role:** native (also replication)
**Period:** regime III · mode I/K · 21–32 agents · #general (+ #focus in 51g) · 45 non-holdout days. Units 51a–51l (joins, NE32, NE38, room changes, NE33); 51m is held out.

## Why this period
**Native: twelve same-goal units as replicas, plus the replication fit.** The private-role era has the same goal type for 9 weeks. HH283's multiple equilibria would show as some units herded and others dispersed under the same fields. Each testable unit gets an M4 fit and P_multi; the period is simulated from the pooled fit, and each unit's observed m is compared with its simulated 95% band. M4 power at βJ = 3: 1.00 (15 runs), so a null βJ here is powered.

## Prediction
*Written 2026-10-04, before running on this period.* **What I had seen:** the card's list; this period's structural counts from the scheme (`counts.json`: choice events, options, named options per channel) and, where simulated, the synthetic power of M4 on this period's skeleton. No real βJ, P_multi or m.

- N1: P_multi < 0.5 in every testable unit (0.8).
- N2: ≤ 1 of the banded units has its observed m outside its simulated 95% band (0.6).
- N3: pooled βĴ(M4) CI includes 0 or βĴ < 2 (0.6).
- N4: m ≤ 0.35 in every unit (own roles) (0.7).
- Against (supports HH283): ≥ 2 units outside their bands, with herded (m ≥ 0.5) and dispersed (m ≤ 0.3) units under similar fields, and P_multi ≥ 0.5.

## Result
*Run 2026-10-04 (non-holdout days only). Results: `data/processed/H93-brock-durlauf-project-choice/results/native_G51.json` and `G51.json`.*

**Native (twelve same-goal units) and replication.**

| Channel | events (testable units) | βĴ M0 (naive) | βĴ M2 | **βĴ M4 (validated)** | kickoff-free | cross-lab | read share | m | max P_multi | γ_c (ratio) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| work | 1477 (51a, 51b, 51c, 51d, 51e, 51f, 51g, 51h, 51i, 51j) | -15.71 [-22.96, -8.46] | -9.75 [-16.44, -3.06] | **-11.66 [-18.96, -4.36]** | -11.92 [-19.54, -4.31] | -10.44 [-17.51, -3.38] | -14.06 [-19.91, -8.20] | 0.11 | 0.28 | 8.5 (-1.26) |
| attention | 4089 (51a, 51b, 51c, 51d, 51e, 51f, 51g, 51h, 51i, 51j, 51k, 51l) | +6.58 [+4.20, +8.96] | +1.61 [-1.10, +4.32] | **+0.84 [-1.90, +3.57]** | +1.03 [-1.71, +3.78] | +1.89 [-1.00, +4.77] | +0.86 [-1.87, +3.59] | 0.13 | 0.83 | 8.5 (+0.30) |

**Work: agents avoid repos that others currently work on.** Pooled βĴ(M4) −11.7 [−19.0, −4.4] over 10 units (τ² = 117: heterogeneous; units 51b and 51h are positive), with habit b_own 4.8 (×120 odds of returning to one's own repo). The avoidance survives the kickoff-free placebo (−11.9), the cross-lab split (−10.4) and the read split (−14.1 on read options). This is an antiferromagnetic Potts coupling: division of labour among private roles.
**Attention: no pooled coupling** (+0.84 [−1.90, 3.57]; units range −8.7 to +9.4).

| Native test | Observed | Verdict |
| --- | --- | --- |
| N1 P_multi < 0.5 in every testable unit | 20/22 unit-channels; 51j attention 0.50, 51l attention 0.83 (8 fixed points; βĴ +9.4 on 105 events, one day) | failed (by the letter) |
| N2 ≤ 1 unit outside its simulated 95% band | work 4/12 outside (all *below*: more dispersed than simulated); attention 12/12 outside (all *above*) | failed: a one-sided misfit of the pooled simulation, not bimodality |
| N3 pooled βĴ CI includes 0 or βĴ < 2 | work −11.7 (< 2); attention +0.84 [−1.90, 3.57] | supported |
| N4 m ≤ 0.35 in every unit | work 0.05–0.15; attention 0.11–0.21 | supported |
| Against: herded (m ≥ 0.5) and dispersed units under similar fields | no unit has m > 0.21 | not met |

No same-goal unit lands in a herded state, so the replica design finds no second equilibrium. The two attention units with P_multi ≥ 0.5 are one- and two-day units whose βĴ is inflated by the same burst confound as elsewhere (A2); their observed m (0.17–0.19) sits in the dispersed state.

## Scorecard (period-specific axes)
- C: 1 (fields + AF share coupling; pooled simulation misfits attention levels). D: 1 (no herded unit in 12, as the unique-equilibrium reading predicts). F: 2 (M4 power 1.00 at βJ = 3; false positives 0.00). I: 1 (12 same-goal units agree on m ≤ 0.21).

## Notes
- 2026-10-04: folder created by the round-1 agent. Predictions use the M4 estimator (card amendment A1, written before any real fit).
