# H93 × G30: Adopt a park and get it cleaned (2026-02-09 → 02-13)

**Verdict:** supported
**Role:** replication
**Period:** regime I · mode C · 11 agents · #general · 5 days. Units 30a (day 1), 30b (NE10, first nudges).

## Why this period
One shared park repo carries almost all work (2 work repos), so the work channel has almost no choice; attention has 7 projects. A near-trivial field-made allocation: the null case for BD.

## Prediction
*Written 2026-10-04, before running on this period.* **What I had seen:** the card's list; this period's structural counts from the scheme (`counts.json`: choice events, options, named options per channel) and, where simulated, the synthetic power of M4 on this period's skeleton. No real βJ, P_multi or m.

- Work: < 10 choices of an existing option per unit, so descriptive; m ≥ 0.8 (one repo).
- Attention: βĴ(M4) CI includes 0 (field-made concentration on the park project); P_multi < 0.5.
- Against: βĴ(M4) > 0 with CI > 0 in attention.

## Result
*Run 2026-10-04 (non-holdout days only). Data: `data/processed/H93-brock-durlauf-project-choice/G30/`; results `.../results/G30.json`.*

| Channel | events (testable units) | βĴ M0 (naive) | βĴ M2 | **βĴ M4 (validated)** | kickoff-free | cross-lab | read share | m | max P_multi | γ_c (ratio) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| work | 91 (30b) | +0.85 [+0.00, +1.70] | +0.57 [-0.35, +1.48] | **-1.31 [-2.92, +0.30]** | n/a | -1.48 [-3.19, +0.22] | -1.31 [-2.92, +0.30] | 0.77 | 0.00 | 5.0 (-0.26) |
| attention | 175 (30b) | +4.09 [+3.01, +5.16] | +1.72 [+0.59, +2.84] | **+0.33 [-0.91, +1.58]** | not identified | -0.13 [-1.66, +1.39] | +0.33 [-0.91, +1.58] | 0.73 | 0.00 | 4.5 (+0.07) |

βĴ in nats per unit share (95% Wald CI; DL pool over testable units where the period has several). γ_c: smallest coupling at which the fitted fields of the largest unit support two stable equilibria; ratio = βĴ/γ_c. Null: the M4 false-positive rate is ≤ 0.10 under static fitness spread but 0.12–1.00 under fast repo bursts (card A2), so a positive βĴ is a share coefficient, not proof of J.

Attention: βĴ(M4) CI includes 0 and P_multi = 0, as predicted. Work was testable in unit 30b after all (91 events but only 2 repos): βĴ(M4) −1.31 [−2.92, 0.30]; m = 0.77, just under the predicted ≥ 0.8. A field-made, one-repo allocation.

## Scorecard (period-specific axes)
- C: 1 (M4 beats M0's apparent coupling: +4.1 → +0.3 in attention). G: 1 (one park repo, as the goal says).

## Notes
- 2026-10-04: folder created by the round-1 agent. Predictions use the M4 estimator (card amendment A1, written before any real fit).
