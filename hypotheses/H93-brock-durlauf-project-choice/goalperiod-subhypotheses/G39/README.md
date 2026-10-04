# H93 × G39: Build your own interactive world (2026-04-27 → 05-01)

**Verdict:** supported
**Role:** replication
**Period:** regime III · mode I · 15 agents · #best / #rest (reshuffled; identical kickoff text) · 5 days. One unit.

## Why this period
Own-artifact week: every agent builds its own world (H78: 0 recruitments, all arrivals are births or returns). Habit should carry everything.

## Prediction
*Written 2026-10-04, before running on this period.* **What I had seen:** the card's list; this period's structural counts from the scheme (`counts.json`: choice events, options, named options per channel) and, where simulated, the synthetic power of M4 on this period's skeleton. No real βJ, P_multi or m.

- βĴ(M4) ≤ 0 or CI includes 0 (0.75); b_own > 0 with CI > 0.
- m (work) ≤ 0.3; P_multi < 0.5.
- Against: βĴ(M4) > 0 with CI > 0.

## Result
*Run 2026-10-04 (non-holdout days only). Data: `data/processed/H93-brock-durlauf-project-choice/G39/`; results `.../results/G39.json`.*

| Channel | events (testable units) | βĴ M0 (naive) | βĴ M2 | **βĴ M4 (validated)** | kickoff-free | cross-lab | read share | m | max P_multi | γ_c (ratio) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| work | 66 (39) | not identified | not identified | **not identified** | not identified | not identified | not identified | 0.10 | 0.00 | n/a |
| attention | 118 (39) | -14.07 [-20.61, -7.52] | -2.92 [-10.86, +5.03] | **-7.19 [-15.60, +1.22]** | not identified | -11.06 [-20.60, -1.53] | -4.73 [-13.33, +3.87] | 0.12 | 0.00 | 7.5 (-0.96) |

βĴ in nats per unit share (95% Wald CI; DL pool over testable units where the period has several). γ_c: smallest coupling at which the fitted fields of the largest unit support two stable equilibria; ratio = βĴ/γ_c. Null: the M4 false-positive rate is ≤ 0.10 under static fitness spread but 0.12–1.00 under fast repo bursts (card A2), so a positive βĴ is a share coefficient, not proof of J.

Work βĴ is not identified (no choice of an occupied repo: every arrival is a birth or a return). Attention βĴ(M4) −7.19 [−15.60, 1.22] (≤ 0 as predicted), habit 4.2, m 0.10–0.12, P_multi = 0.

## Scorecard (period-specific axes)
- G: 1 (own worlds, H11 ownership 1.00).

## Notes
- 2026-10-04: folder created by the round-1 agent. Predictions use the M4 estimator (card amendment A1, written before any real fit).
