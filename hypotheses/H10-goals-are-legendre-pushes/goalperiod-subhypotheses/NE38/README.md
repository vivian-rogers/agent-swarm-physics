# H10 × NE38: a human reassigns one agent's private goal inside #51 (Claude Opus 5, 2026-07-29 16:51 UTC)

**Verdict:** mixed (round 1b native; quench, control drifted)
**Role:** native (round 1b, 2026-10-04; transition exception c: one agent across its own field change)
**Period:** #51 head (regime III, one room, private per-agent goals). Claude Opus 5 joins 07-24 with the game-developer goal (shared with two incumbents); on 07-29 16:51 UTC a human reassigns it to the mathematician goal (DQ6 `role` rows; the first role is recovered from an operator message because `agent_goals` is a snapshot). Nothing else changes for the other agents.

## Why this period
The cleanest single-agent field change in the record (DQ9: "NE38 single-agent field change: Legendre response of one agent"). H10 asks whether the response to a goal is the exponential tilt of the unforced distribution, P_A(y) ∝ P_F(y) e^{λy}. With one agent and many 30-min windows on each side, the tilt can be checked directly on the window distribution, without needing cross-agent P1. Concurrent controls (agents whose goals did not change) remove any swarm-wide drift.

## Design (round 1b)
- **Segments.** F = Opus 5's windows on 07-24 → 07-28 (game-dev role; 07-29 excluded). A = 07-30 → 08-04 (days 2+ after the reassignment, before NE43's first step on 08-05).
- **Direction.** ĝ_math = Opus 5's assigned goal (shared `goal_fields`, kind `agent_goal`, gid 242), whitened, regime III, n = 32.
- **Statistics.** Window means x_t of y = ẑ·ĝ_math (≥ 2 statements per window). Push Δ = mean_A − mean_F; ε = Δ/√κ2^F (noise-corrected); ρ = ln(κ2^A/κ2^F) along ĝ_math and ρ⊥ along 50 transverse directions; **tilt check:** reweight F's empirical windows by e^{λ x}, λ chosen to match mean_A (impossible if mean_A ≥ max_F); the tilt's predicted A variance vs the observed.
- **Controls.** (i) All other #51 agents, same dates, along ĝ_math (swarm drift toward math content); (ii) the two incumbent game developers along their own unchanged goal (same dates).
- Both embedding models; restatement-deduped variant.

## Prediction
*Written 2026-10-04 07:20 UTC, before any H10 statistic on #51. Seen before: H54's NE38 result (DiD +0.61 [0.56, 0.66] toward the new goal, −0.29 away from the old one, at day resolution on centered alignment) and H54's G51 role-swap accuracy 0.95; counts per day for Opus 5 (84–155 chat statements a day before 07-29, 19–43 after).*
- **N2a (a non-perturbative push).** ε > 2 and mean_A above the 90th percentile of F's windows. Credence 0.65.
- **N2b (not a tilt).** The tilt matched to mean_A predicts a smaller A variance than observed (ρ_obs − ρ_tilt > ln 1.5), or mean_A is unreachable by reweighting (mean_A ≥ max_F). Credence 0.55.
- **N2c (controls flat).** The other agents' mean alignment with ĝ_math moves by < 0.25 Δ (credence 0.8); the incumbents' alignment with their own goal moves by < 1 of their F-SDs (credence 0.7).
- **Verdict rule (native):** **failed** for H10 (a quench, not a Legendre push) if N2a and N2b hold with N2c; **supported** if mean_A is reachable and the tilt's variance is within ln 1.5 of the observed while N2c holds; **mixed** otherwise.

## Result
*Run 2026-10-04 (after the prediction above). Data: `r1b/<config>/natives.json` (NE38). Script: `analysis/natives_r1b.py`.*
Opus 5: 42 windows in F (07-24 → 07-28), 46 in A (07-30 → 08-04).

| Prediction | bge-small | gte-modernbert | Verdict |
| --- | --- | --- | --- |
| N2a ε > 2 and mean_A > F's 90th percentile | Δ 0.450 [0.416, 0.483], ε 10.2 [8.7, 13.7]; mean_A 0.47 vs q90_F 0.09 | Δ 0.507, ε 20.3 (lower CI 10.7); mean_A 0.51 vs q90_F 0.07 | ✓ / ✓ |
| N2b not a tilt (unreachable, or variance beyond the tilt) | mean_A 0.47 > max_F 0.17: **no exponential reweighting of F reaches A** | mean_A 0.51 > max_F 0.14: unreachable | ✓ / ✓ |
| N2c controls flat: other agents < 0.25 Δ; incumbents < 1 F-SD | others +0.011 (0.02 Δ); incumbent GPT-5.5 −3.1 F-SDs along its own goal (Opus 4.7: too few windows) | others +0.045 (0.09 Δ); GPT-5.5 −1.04 F-SDs | ✗ / ✗ (incumbent only) |
| ρ along ĝ_math / transverse | +0.26 / −0.22 | n/a (A variance ≤ noise) / −0.79 | descriptive |

Restatement-deduped: bge mixed (same numbers), gte **failed** for H10 (the incumbent moved −0.90 SD, so N2c passes). **Reading.** One agent's goal change moves it 10–20 of its own pre-change SDs onto the new goal within a day, to alignments its pre-change content never visited (H54's DiD +0.61 at day level). No exponential tilt of the unforced distribution can produce that: the response is a quench into a new state. The rule says mixed only because the one measurable incumbent drifted away from its own unchanged goal over the same days (3.1 SDs in bge, 1.0 in gte), so the concurrent control is not flat.

## Notes
- 2026-10-04: native folder created in round 1b (DQ9 cross-index).
