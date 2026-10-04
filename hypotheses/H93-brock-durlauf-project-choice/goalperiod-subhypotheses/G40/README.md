# H93 × G40: Connect your worlds into a 3D universe (NE42 merge) (2026-05-04 → 05-08)

**Verdict:** mixed
**Role:** replication
**Period:** regime III · mode C · 15 agents · one merged room (#universe-coordination) · 5 days. One unit.

## Why this period
One kickoff-named hub plus each agent's own world, in one room (H11: work spread by fields; H78: all recruitments into the named hub). A field-made allocation with two kinds of attractor.

## Prediction
*Written 2026-10-04, before running on this period.* **What I had seen:** the card's list; this period's structural counts from the scheme (`counts.json`: choice events, options, named options per channel) and, where simulated, the synthetic power of M4 on this period's skeleton. No real βJ, P_multi or m.

- βĴ(M4) CI includes 0; the hub's pull appears as b_named and b_cum (0.6).
- m (work) ≥ 0.4 (hub share).
- P_multi < 0.5.
- Against: βĴ(M4) > 0 with CI > 0 and P_multi ≥ 0.5.

## Result
*Run 2026-10-04 (non-holdout days only). Data: `data/processed/H93-brock-durlauf-project-choice/G40/`; results `.../results/G40.json`.*

| Channel | events (testable units) | βĴ M0 (naive) | βĴ M2 | **βĴ M4 (validated)** | kickoff-free | cross-lab | read share | m | max P_multi | γ_c (ratio) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| work | 60 (40) | +7.12 [+5.42, +8.82] | +5.12 [+2.72, +7.53] | **+3.63 [-0.51, +7.77]** | not identified | +5.10 [-0.10, +10.30] | +5.57 [-0.00, +11.15] | 0.71 | 0.04 | 9.5 (+0.38) |
| attention | 100 (40) | +3.08 [+2.12, +4.05] | +3.42 [+1.15, +5.70] | **+3.14 [+0.76, +5.52]** | not identified | +3.53 [-2.04, +9.11] | +4.24 [+1.27, +7.20] | 0.72 | 0.00 | 10.0 (+0.31) |

βĴ in nats per unit share (95% Wald CI; DL pool over testable units where the period has several). γ_c: smallest coupling at which the fitted fields of the largest unit support two stable equilibria; ratio = βĴ/γ_c. Null: the M4 false-positive rate is ≤ 0.10 under static fitness spread but 0.12–1.00 under fast repo bursts (card A2), so a positive βĴ is a share coefficient, not proof of J.

Work βĴ(M4) +3.63 [−0.51, 7.77] (CI includes 0, as predicted); attention +3.14 [0.76, 5.52] (CI > 0, against). m = 0.71 (hub), P_multi ≤ 0.04, βĴ/γ_c 0.38. The hub's pull sits mostly in habit (4.2) and the named term (1.7).

## Scorecard (period-specific axes)
- C: 1.

## Notes
- 2026-10-04: folder created by the round-1 agent. Predictions use the M4 estimator (card amendment A1, written before any real fit).
