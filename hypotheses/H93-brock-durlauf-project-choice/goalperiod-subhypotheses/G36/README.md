# H93 × G36: Interact with other AI agents outside the Village (2026-03-23 → 03-27)

**Verdict:** mixed
**Role:** replication
**Period:** regime II → III · mode C · 12 agents · #best / #rest · 5 days. Units 36a, 36b (NE14, NE41), 36c (NE16).

## Why this period
Two rooms with identical kickoff text; 16 work repos and 42 attention projects: an outward-facing week with many small projects.

## Prediction
*Written 2026-10-04, before running on this period.* **What I had seen:** the card's list; this period's structural counts from the scheme (`counts.json`: choice events, options, named options per channel) and, where simulated, the synthetic power of M4 on this period's skeleton. No real βJ, P_multi or m.

- βĴ(M4) CI includes 0 in both channels (0.65); m (work) 0.3–0.5.
- P_multi < 0.5.
- Against: M4 CI > 0.

## Result
*Run 2026-10-04 (non-holdout days only). Data: `data/processed/H93-brock-durlauf-project-choice/G36/`; results `.../results/G36.json`.*

| Channel | events (testable units) | βĴ M0 (naive) | βĴ M2 | **βĴ M4 (validated)** | kickoff-free | cross-lab | read share | m | max P_multi | γ_c (ratio) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| work | 106 (36b, 36c) | +2.99 [+1.90, +4.08] | +1.74 [+0.50, +2.97] | **+1.89 [+0.36, +3.42]** | +1.91 [+0.37, +3.45] | +2.14 [+0.27, +4.01] | +1.96 [+0.43, +3.50] | 0.54 | 0.04 | 5.0 (+0.39) |
| attention | 207 (36a, 36b, 36c) | +7.07 [+5.79, +8.35] | +4.25 [+2.42, +6.08] | **+1.54 [-2.61, +5.69]** | +1.43 [-2.66, +5.52] | +1.85 [-2.58, +6.28] | +1.75 [-2.51, +6.01] | 0.43 | 0.23 | 4.5 (+0.86) |

βĴ in nats per unit share (95% Wald CI; DL pool over testable units where the period has several). γ_c: smallest coupling at which the fitted fields of the largest unit support two stable equilibria; ratio = βĴ/γ_c. Null: the M4 false-positive rate is ≤ 0.10 under static fitness spread but 0.12–1.00 under fast repo bursts (card A2), so a positive βĴ is a share coefficient, not proof of J.

Work βĴ(M4) +1.89 [0.36, 3.42] (predicted CI includes 0); attention +1.54 [−2.61, 5.69] as predicted. m (work) 0.54, just above the predicted 0.3–0.5. P_multi ≤ 0.23.

## Scorecard (period-specific axes)
- C: 1.

## Notes
- 2026-10-04: folder created by the round-1 agent. Predictions use the M4 estimator (card amendment A1, written before any real fit).
