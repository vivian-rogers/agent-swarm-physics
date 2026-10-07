# H141 × NE38: one agent's role is reassigned (inside #51, 2026-07-29)

**Verdict:** descriptive
**Role:** exploratory (native N3; descriptive, one agent)
**Period:** inside #51 (regime III, private roles). On 2026-07-29 a human reassigns Claude Opus 5's role from word puzzles to mathematics (`agent_goals` start date; `natural-experiments.md`). Comparison days: 2026-07-24 → 07-28 before; 07-29 → 08-12 after (non-reserved).

## Why this natural experiment
The text field changes direction for one agent at a dated time while the room, scaffold and other agents stay fixed. If the easy plane is set by the goal text, that agent's slow direction should rotate with its role. H54 found the agent moved onto its new goal within a day (DiD +0.61 [0.56, 0.66]); H97 found the reassignment erased its position about 6× more than its ordinary days.

## Prediction
*Written 2026-10-07 ~11:40 UTC, before running. Seen: H54's and H97's NE38 numbers; no projection on either goal axis.*
- **N3:** after 07-29, the day-scale persistence along the new goal axis exceeds that along the old one; before 07-29 the reverse. Credence 0.3.
- Counts against: the order does not change. One agent and few days: descriptive; no verdict beyond "consistent / not consistent".

## Result
*Round 1, 2026-10-07. A1 variogram persistence P(1) = 1 − G(1)/G(≥ 2) along each 1-d goal axis, arm-specific (before: 07-24, 07-27, 07-28, 07-29 before 16:51 UTC, 352 statements, 3 lag-1 pairs; after: 07-29 16:51 → 08-12, 214 statements, 10 lag-1 pairs). Data: `results/ne38.json`.*

| Variant | P(1) along new (math) and old (game-dev) goal axis | after: new > old | before: old > new |
| --- | --- | --- | --- |
| bge style_resid_period | before: new 0.82, old -5.25; after: new 0.85, old 0.54 | yes | no |
| gte style_resid_period | before: new nan, old -0.86; after: new 1.19, old 0.76 (before, new axis: undefined) | yes | — |
| bge white32 | before: new 0.81, old 0.10; after: new 1.20, old 0.32 | yes | no |

**N3 not consistent.** After the reassignment the new axis is more persistent than the old one, as predicted. Before it, the new (math) axis was already the more persistent one, so the order does not flip. Values outside [0, 1] show the noise of one agent with 3–10 day pairs. The registered O3 estimator gives the same orders (before: new 0.95 vs old −0.75, bge).

## Scorecard (period-specific axes)
E: 0 (the predicted rotation of the slow direction is not seen; one agent, descriptive).

## Notes
- The agent joined #51 shortly before; H73 round 2 lists 3 eligible days before 07-29 for it. The before arm is short.
