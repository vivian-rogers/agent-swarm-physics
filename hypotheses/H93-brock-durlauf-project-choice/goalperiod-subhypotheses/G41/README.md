# H93 × G41: Perform novel research (NE42 split back) (2026-05-11 → 05-15)

**Verdict:** mixed
**Role:** replication
**Period:** regime III · mode I · 15 agents · #best / #rest · 5 days. One unit.

## Why this period
A mode-I week that herds anyway (H11 +4.3; ~11 #rest agents converged on one research topic). The case where a coupling could create order that the goal text does not. M4 power 0.70 at βJ = 3.

## Prediction
*Written 2026-10-04, before running on this period.* **What I had seen:** the card's list; this period's structural counts from the scheme (`counts.json`: choice events, options, named options per channel) and, where simulated, the synthetic power of M4 on this period's skeleton. No real βJ, P_multi or m.

- M0 > 0, CI > 0 (0.75).
- M4: point estimate > 0; CI includes 0 (0.5).
- P_multi < 0.5 (0.7); m (work) 0.35–0.6.
- Against: P_multi ≥ 0.5 with M4 CI > 0 (supports HH283).

## Result
*Run 2026-10-04 (non-holdout days only). Data: `data/processed/H93-brock-durlauf-project-choice/G41/`; results `.../results/G41.json`.*

| Channel | events (testable units) | βĴ M0 (naive) | βĴ M2 | **βĴ M4 (validated)** | kickoff-free | cross-lab | read share | m | max P_multi | γ_c (ratio) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| work | 108 (41) | +3.74 [+2.50, +4.99] | +3.38 [+1.81, +4.96] | **+3.94 [+2.20, +5.67]** | +5.89 [+2.25, +9.53] | +3.82 [+1.89, +5.75] | +5.54 [+3.56, +7.52] | 0.40 | 0.02 | 6.0 (+0.66) |
| attention | 161 (41) | +3.14 [+1.64, +4.64] | +3.70 [+1.90, +5.50] | **+4.52 [+2.54, +6.49]** | +9.27 [+5.28, +13.26] | +6.59 [+3.68, +9.50] | +5.51 [+3.36, +7.66] | 0.38 | 0.03 | 6.0 (+0.75) |

βĴ in nats per unit share (95% Wald CI; DL pool over testable units where the period has several). γ_c: smallest coupling at which the fitted fields of the largest unit support two stable equilibria; ratio = βĴ/γ_c. Null: the M4 false-positive rate is ≤ 0.10 under static fitness spread but 0.12–1.00 under fast repo bursts (card A2), so a positive βĴ is a share coefficient, not proof of J.

M0 > 0 and the M4 point estimate > 0 as predicted, but the CI excludes 0 in both channels (+3.94 work, +4.52 attention) and survives the kickoff-free placebo (+5.89) and the cross-lab split (+3.82). P_multi ≤ 0.03; βĴ/γ_c 0.66–0.75 (upper CI 0.95–1.08). The "against" clause (P_multi ≥ 0.5) is not met.

## Scorecard (period-specific axes)
- C: 1. F: 1 (power 0.70).

## Notes
- 2026-10-04: folder created by the round-1 agent. Predictions use the M4 estimator (card amendment A1, written before any real fit).
