# H93 × G42: Run your own YouTube channel (2026-05-18 → 05-22)

**Verdict:** mixed
**Role:** replication
**Period:** regime III · mode I · 15–16 agents · #best / #rest (identical kickoff text) · 5 days. Units 42a, 42b (join).

## Why this period
Own-artifact week (individual channels). A same-mode partner of #39 and #41: if #41 herds and #42 does not with similar fields, that is the HH283 signature.

## Prediction
*Written 2026-10-04, before running on this period.* **What I had seen:** the card's list; this period's structural counts from the scheme (`counts.json`: choice events, options, named options per channel) and, where simulated, the synthetic power of M4 on this period's skeleton. No real βJ, P_multi or m.

- βĴ(M4) CI includes 0 (0.7); m (work) ≤ 0.35; P_multi < 0.5.
- Against: βĴ(M4) > 0 with CI > 0.

## Result
*Run 2026-10-04 (non-holdout days only). Data: `data/processed/H93-brock-durlauf-project-choice/G42/`; results `.../results/G42.json`.*

| Channel | events (testable units) | βĴ M0 (naive) | βĴ M2 | **βĴ M4 (validated)** | kickoff-free | cross-lab | read share | m | max P_multi | γ_c (ratio) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| work | 87 (42a, 42b) | +1.35 [-5.29, +7.99] | -3.73 [-7.51, +0.04] | **-5.89 [-11.64, -0.13]** | not identified | -6.70 [-12.57, -0.84] | -4.88 [-10.97, +1.21] | 0.29 | 0.00 | 9.5 (-0.56) |
| attention | 92 (42a, 42b) | +3.48 [+0.42, +6.54] | +4.60 [-0.86, +10.06] | **+1.10 [-4.62, +6.81]** | not identified | +1.16 [-7.55, +9.87] | +1.37 [-4.27, +7.01] | 0.26 | 0.28 | 8.0 (-0.13) |

βĴ in nats per unit share (95% Wald CI; DL pool over testable units where the period has several). γ_c: smallest coupling at which the fitted fields of the largest unit support two stable equilibria; ratio = βĴ/γ_c. Null: the M4 false-positive rate is ≤ 0.10 under static fitness spread but 0.12–1.00 under fast repo bursts (card A2), so a positive βĴ is a share coefficient, not proof of J.

Attention βĴ(M4) CI includes 0 as predicted. Work βĴ(M4) is *negative*: −5.89 [−11.64, −0.13] (agents avoid repos others work on). m 0.26–0.29 and P_multi ≤ 0.28 as predicted.

## Scorecard (period-specific axes)
- C: 1.

## Notes
- 2026-10-04: folder created by the round-1 agent. Predictions use the M4 estimator (card amendment A1, written before any real fit).
