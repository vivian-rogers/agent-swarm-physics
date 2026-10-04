# H126 × NE38: Opus 5's goal reassignment (2026-07-29 16:51 UTC, inside #51)

**Verdict:** supported
**Role:** exploratory (native)
**Period:** regime III · one agent (agent 40, Claude Opus 5) · 2026-07-24 → 2026-08-04, split at 2026-07-29 16:51 UTC.

## Why this period
A human changed one agent's goal (word puzzles → mathematics). The new goal is a field step on one spin with the rest of the swarm unchanged: the cleanest single-agent kickoff. H105 saw its occupancy along the new goal go 0.00 → 0.96.

## Prediction
*Written 2026-10-04 ~22:25 UTC, before running on this period.*
**Native N3:** along Opus 5's new-goal direction, M2 with segment-specific rates gives Δln k_on 90% CI above 0 and Δln k_off CI containing 0 (the field raises the on-rate only). Credence 0.2. Counts against: Δln k_off CI below 0 (the field holds the agent on goal). Note before data: an occupancy of 0.96 needs k_on/k_off ≈ 24, which is hard to reach by k_on alone on a per-call clock.

## Result
*Run 2026-10-04 (UTC), after Amendment A1 (N3 is low-power: 30% for a true k_on step).*

Opus 5: 432 statements before, 199 after; raw on-goal fraction 0.06 → 0.89. k_on 0.0014 → 0.0347 per call (Δln +3.18 [+1.09, +13.05]); k_off 0.0661 → 0.0004 (Δln -5.05 [-12.91, +0.19]); 90% parametric bootstrap. Emissions q₀ 0.044, q₁ 0.90. **N3 supported.**

## Scorecard (period-specific axes)
E: a one-agent field step (natural experiment).
