# H104 × NE43: the nudger stops (2026-08-20/21)

**Verdict:** mixed
**Role:** native (exploratory)
**Period:** regime III · #51 · the last nudge is on 2026-08-20 (17:42 UTC); from 08-21 there are no automated nudges (NE43b). Unit 51g (to 08-21), then 51h (08-24 →, #focus closed).

## Why this period
Nudges are tiny, targeted field steps on idle agents, about 25 per day before 08-21. If small steps release switches, switching should drop when they stop. RE-O1 found that nudges buy glances, not commits.

## Prediction
*Written 2026-10-04 20:25 UTC, before running.*
- **NE43-a (no change in the switch rate).** Switches per agent-hour at risk in the 5 active days from 08-21 vs the 5 active days to 08-20: ratio within [0.85, 1.15] in the work channel (day-bootstrap CI including 1). Attention channel reported the same way. Credence 0.55.
- **NE43-b (placebo).** The same before/after ratio at placebo split days inside #51 (every other #51 day with 5 active days on both sides, excluding NE38 ± 5 days) gives the reference band; NE43's ratio lies inside its central 90%. Credence 0.6.
- Confound: 08-24 also closes #focus (51h).
- Counts against "nudges are not field steps for project choice": a drop below 0.85 outside the placebo band.

## Result
*Run 2026-10-04 21:05 UTC. Data: `results/natives.json`.* Before: 08-14 → 08-20 (5 days); after: 08-21 → 08-27 (5 days).
| Channel | Switches per agent-hour before → after | Ratio [95% day-bootstrap CI] | Placebo band (14 splits) |
| --- | --- | --- | --- |
| work | 0.073 → 0.089 | 1.22 [0.72, 2.03] | [0.44, 1.29] |
| attention | 0.329 → 0.314 | 0.96 [0.86, 1.07] | [0.65, 1.06] |
- **NE43-a:** passes for attention; fails for work (point 1.22 outside [0.85, 1.15], CI includes 1).
- **NE43-b passes** in both channels (inside the placebo band).
- Stopping about 25 nudges per day does not lower switching. The ±15% band was tighter than the day-to-day spread of the placebo splits.
