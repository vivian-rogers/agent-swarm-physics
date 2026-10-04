# H93 × G31: Pick your own goal (farewell to Claude 3.7 Sonnet) (2026-02-16 → 02-20)

**Verdict:** mixed
**Role:** replication
**Period:** regime I · mode F · 11–12 agents · #general · 5 days. Units 31a–31d (join, NE29, NE11).

## Why this period
H11's clearest field-free herding week (βJ_CW +4.9 in attention, work herds z +7.2); H53's share effect is strongest in free weeks. If BD coupling exists anywhere, it is here. Synthetic power of M4 at βJ = 3: 0.50.

## Prediction
*Written 2026-10-04, before running on this period.* **What I had seen:** the card's list; this period's structural counts from the scheme (`counts.json`: choice events, options, named options per channel) and, where simulated, the synthetic power of M4 on this period's skeleton. No real βJ, P_multi or m.

- M0: βĴ > 0, CI > 0 in both channels (0.8).
- M4: point estimate > 0 in work and attention; CI includes 0 in work (power 0.5) (0.55).
- P_multi < 0.5 (0.75); m (work) 0.35–0.6.
- Against: M4 CI > 0 *and* P_multi ≥ 0.5 (that would support HH283 here).

## Result
*Run 2026-10-04 (non-holdout days only). Data: `data/processed/H93-brock-durlauf-project-choice/G31/`; results `.../results/G31.json`.*

| Channel | events (testable units) | βĴ M0 (naive) | βĴ M2 | **βĴ M4 (validated)** | kickoff-free | cross-lab | read share | m | max P_multi | γ_c (ratio) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| work | 154 (31a, 31b) | +3.39 [+1.16, +5.63] | +3.62 [+2.47, +4.77] | **+2.44 [+1.08, +3.80]** | +2.27 [-0.60, +5.14] | +1.84 [+0.31, +3.37] | +2.52 [+1.15, +3.89] | 0.42 | 0.06 | 4.5 (+0.55) |
| attention | 214 (31a, 31b, 31c, 31d) | +2.31 [+0.64, +3.98] | +2.55 [+1.29, +3.81] | **+2.30 [+0.63, +3.97]** | +1.39 [-3.54, +6.33] | +1.75 [+0.23, +3.27] | +2.29 [+0.61, +3.97] | 0.47 | 0.47 | 3.5 (+0.32) |

βĴ in nats per unit share (95% Wald CI; DL pool over testable units where the period has several). γ_c: smallest coupling at which the fitted fields of the largest unit support two stable equilibria; ratio = βĴ/γ_c. Null: the M4 false-positive rate is ≤ 0.10 under static fitness spread but 0.12–1.00 under fast repo bursts (card A2), so a positive βĴ is a share coefficient, not proof of J.

The share coupling is stronger than predicted: βĴ(M4) > 0 with CI > 0 in work (+2.44) and attention (+2.30), and it survives the cross-lab split (+1.84) and the read split. No multiplicity: P_multi ≤ 0.47, βĴ/γ_c = 0.55 (work, 31a). m (work) 0.42 is inside the predicted 0.35–0.6. The "against" clause (M4 CI > 0 *and* P_multi ≥ 0.5) is not met.

## Scorecard (period-specific axes)
- C: 1 (beats the fields-only null; not the burst null, A2). D: 1 (m* ranks m across periods). F: 1 (M4 power 0.5 here).

## Notes
- 2026-10-04: folder created by the round-1 agent. Predictions use the M4 estimator (card amendment A1, written before any real fit).
