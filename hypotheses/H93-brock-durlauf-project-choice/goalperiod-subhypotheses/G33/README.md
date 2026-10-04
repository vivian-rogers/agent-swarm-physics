# H93 × G33: Discuss, debate and act on the Pentagon–AI news (2026-03-02 → 03-04)

**Verdict:** mixed
**Role:** replication
**Period:** regime II · mode C · 11 agents · #general · 3 days. One unit.

## Why this period
A short shared-artifact week where work herds strongly in H11 (z_N2 +9.0, co-location 0.94) on 6 repos.

## Prediction
*Written 2026-10-04, before running on this period.* **What I had seen:** the card's list; this period's structural counts from the scheme (`counts.json`: choice events, options, named options per channel) and, where simulated, the synthetic power of M4 on this period's skeleton. No real βJ, P_multi or m.

- M0 > 0 (CI > 0) in work; M4 CI includes 0 (field: one named hub) (0.6).
- m (work) ≥ 0.6; P_multi < 0.5.
- Against: M4 CI > 0 with P_multi ≥ 0.5.

## Result
*Run 2026-10-04 (non-holdout days only). Data: `data/processed/H93-brock-durlauf-project-choice/G33/`; results `.../results/G33.json`.*

| Channel | events (testable units) | βĴ M0 (naive) | βĴ M2 | **βĴ M4 (validated)** | kickoff-free | cross-lab | read share | m | max P_multi | γ_c (ratio) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| work | 64 (33) | +3.70 [+2.65, +4.76] | +3.33 [+2.03, +4.64] | **+2.48 [+0.80, +4.17]** | not identified | +1.94 [+0.12, +3.76] | +2.40 [+0.72, +4.08] | 0.86 | 0.15 | 3.0 (+0.83) |
| attention | 57 (33) | +3.65 [+2.12, +5.17] | +3.48 [+1.46, +5.50] | **+2.27 [+0.12, +4.43]** | not identified | -0.87 [-4.04, +2.30] | +2.25 [+0.10, +4.41] | 0.90 | 0.01 | 6.0 (+0.38) |

βĴ in nats per unit share (95% Wald CI; DL pool over testable units where the period has several). γ_c: smallest coupling at which the fitted fields of the largest unit support two stable equilibria; ratio = βĴ/γ_c. Null: the M4 false-positive rate is ≤ 0.10 under static fitness spread but 0.12–1.00 under fast repo bursts (card A2), so a positive βĴ is a share coefficient, not proof of J.

M0 > 0 as predicted, but M4 stays positive (+2.48 [0.80, 4.17] work): the predicted field-only reading fails. m = 0.86, P_multi ≤ 0.15, βĴ/γ_c 0.83 (upper CI 1.39 crosses γ_c).

## Scorecard (period-specific axes)
- C: 1. F: 1 (M4 power 0.62).

## Notes
- 2026-10-04: folder created by the round-1 agent. Predictions use the M4 estimator (card amendment A1, written before any real fit).
