# H89 × NE32: Isolated newcomers merge into the village (#51, 2026-07-09 / 07-10)

**Verdict:** supported
**Role:** native
**Period:** inside G51 · regime III · non-holdout days only.

## Why this test
NE32: GPT-5.6 Sol, Terra and Luna join on 07-09 in separate isolated rooms, which close on 07-10. Isolation switches the newcomers' in-cone parentage from veterans off, then on. Exception (c): the transitions across the join and the merge are the object.

## Prediction
*Written 2026-10-04 20:35 UTC, before any native statistic.*
- **N2-a:** at the newcomers' entry transition (07-08 → 07-09, or their first active day if a newcomer has < 6 eligible messages on 07-09), the roster-migration share of style exceeds that of content.
- **N2-b (enculturation at the merge):** the newcomers' content change from their first active day to the next points toward the veterans' centroid on the first day (cross-fitted cosine > 0), and more so than their style change does.
- Prior 0.45. **Verdict:** supported = N2-a and N2-b; failed = neither; mixed otherwise.
- *Counts against:* content migration share ≥ style's at entry; newcomer content cosine ≤ 0 or ≤ the style cosine.

## Result
**supported.** Only GPT-5.6 Terra (agent 37) passes the activity threshold on 07-09; Luna (36) and Sol (35) first pass it on 2026-07-14 and 2026-07-17, so their first active days replace 07-09 (pre-registered fallback). Only Terra's next day is the merge day.

| Prediction | Observed | Reference | Verdict |
| --- | --- | --- | --- |
| N2-a newcomer entry share: style > content | energy-pooled over the three entries: style +0.083, content bge +0.023, gte +0.037, conventions +0.039 (agent 35 into 2026-07-17: style +nan (ρ -0.17), content +0.016; agent 36 into 2026-07-14: style +0.138 (ρ 0.83), content +0.026; agent 37 into 2026-07-09: style +0.078 (ρ 0.71), content +0.023) | 0 | pass |
| N2-b newcomers move toward the veterans: content cos > 0 and > style cos | cross-fitted cosine: content bge +0.26, gte -0.03; style -0.48 | 0 | pass |

Mechanism (descriptive): newcomer social weight λ on its first two active days: 35@2026-07-17 –, 35@2026-07-21 –, 36@2026-07-14 –, 36@2026-07-16 –, 37@2026-07-09 –, 37@2026-07-10 0.26.

## Scorecard (period-specific axes)
E (interventional): isolation then merge switches the newcomers' in-cone parentage; only one newcomer is active across the merge. G: roster and room dates from `roster` and the NE catalog.

## Notes
