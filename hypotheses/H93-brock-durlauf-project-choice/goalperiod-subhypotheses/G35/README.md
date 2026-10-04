# H93 × G35: Test your game (forked per room) (2026-03-16 → 03-20)

**Verdict:** supported
**Role:** replication
**Period:** regime II · mode C · 12 agents · #best / #rest · 5 days. One unit.

## Why this period
Each room evolves its own fork of the #34 RPG: the allocation is set by an operator assignment (a field). Three work repos only.

## Prediction
*Written 2026-10-04, before running on this period.* **What I had seen:** the card's list; this period's structural counts from the scheme (`counts.json`: choice events, options, named options per channel) and, where simulated, the synthetic power of M4 on this period's skeleton. No real βJ, P_multi or m.

- Work: the choice set has ≤ 3 options; βĴ(M4) CI includes 0; habit carries the choices (b_own > 0).
- m (work) ≥ 0.5 (each room on its fork; the larger room sets the top share).
- P_multi < 0.5.
- Against: βĴ(M4) > 0 with CI > 0.

## Result
*Run 2026-10-04 (non-holdout days only). Data: `data/processed/H93-brock-durlauf-project-choice/G35/`; results `.../results/G35.json`.*

| Channel | events (testable units) | βĴ M0 (naive) | βĴ M2 | **βĴ M4 (validated)** | kickoff-free | cross-lab | read share | m | max P_multi | γ_c (ratio) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| work | 115 (35) | +1.63 [+0.93, +2.33] | +4.58 [+2.32, +6.84] | **+1.55 [-1.38, +4.47]** | n/a | +1.57 [-1.37, +4.51] | +7.42 [+0.37, +14.47] | 0.66 | 0.00 | 9.5 (+0.16) |
| attention | 61 (35) | +1.95 [+0.18, +3.71] | +1.73 [-1.28, +4.74] | **-1.86 [-5.78, +2.05]** | n/a | -1.29 [-7.87, +5.30] | not identified | 0.71 | 0.00 | 9.0 (-0.21) |

βĴ in nats per unit share (95% Wald CI; DL pool over testable units where the period has several). γ_c: smallest coupling at which the fitted fields of the largest unit support two stable equilibria; ratio = βĴ/γ_c. Null: the M4 false-positive rate is ≤ 0.10 under static fitness spread but 0.12–1.00 under fast repo bursts (card A2), so a positive βĴ is a share coefficient, not proof of J.

βĴ(M4) CI includes 0 in both channels; habit carries the choices (b_own 4.8 work); m = 0.66; P_multi = 0. The fork-per-room assignment is a field.

## Scorecard (period-specific axes)
- G: 1 (room forks match DQ6 room assignments).

## Notes
- 2026-10-04: folder created by the round-1 agent. Predictions use the M4 estimator (card amendment A1, written before any real fit).
