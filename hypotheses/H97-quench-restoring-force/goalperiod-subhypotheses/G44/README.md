# H97 × G44: assigned named-target room vs free-choice room (#42 → #44)

**Verdict:** failed
**Role:** native
**Period:** regime III · mode C · 16 agents in two rooms (#best: assigned, specific kickoff of 1,810 characters; #rest: pick your own goal, 219 characters) · kickoff 2026-05-26. The previous period #43 is held out, so the pre-state is #42's last active day (05-22).

## Why this period
Both rooms cross the same boundary on the same day, with the same gap and platform. Only the field differs: a named target in #best, none in #rest (DQ6 room assignments). H75 found the named-target room settles ×5.7 faster at the same switch rate.

## Prediction
*Written 2026-10-04 ~20:41 UTC, before running on this unit.*
- **N2:** mean χ^mem(#best) > mean χ^mem(#rest) (one-sided room-label permutation reported). Credence 0.55.
- Descriptive: each agent's displacement along its own room kickoff minus the other room's kickoff.
- Counts against: χ^mem(#best) ≤ χ^mem(#rest).
- Power: #best has about 4 agents; a null result is not informative.

## Result
| Statistic | bge-small | gte-modernbert |
| --- | --- | --- |
| mean χ^mem #best − #rest (4 vs 12 agents) | +0.00 (perm p 0.49) | −0.16 (p 0.87) |
| displacement along own minus other room kickoff, #best | +0.31 | +0.31 |
| same, #rest | −0.10 | −0.13 |

**N2 failed** (no difference; underpowered with 4 agents in #best). The *direction* of the move is room-specific (the #best room moves toward its own kickoff, the #rest room does not), but how much each agent forgets its pre-state does not depend on the room's field. The pre-state is #42's last day (a week-plus gap through the held-out #43) for both rooms.

Data: `data/processed/H97-quench-restoring-force/natives/G44.json` (both models).

## Scorecard (period-specific axes)
- E: the room contrast is a same-day quasi-intervention; the memory statistic does not separate the rooms.
- G: room membership from DQ6.

## Notes
- The week-long gap through the held-out #43 is shared by both rooms; it lowers both memories, not their difference.
