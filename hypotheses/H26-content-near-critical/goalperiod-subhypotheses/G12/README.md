# H26 × G12: Debate tournament, content loop gain with and without the motion field (2025-09-01 → 09-05)

**Verdict:** mixed (native, round 1b)
**Verdict (1b):** supported (bge) / mixed (gte; N2b missed by 0.004)
**Role:** native
**Period:** regime I · mode K · N = 7 · one room (#general) · 10 debates on 09-01 → 09-04, each with a motion (a strong common content field) switched on at its start and off at its verdict; DQ6 `ground_truth_labels` gives the debate windows (team rows, 13–47 min each).

## Why this period
DQ9: "verdicts as field switch-offs at known times ... content loop gain with and without the motion field (H26)". H26's central ambiguity is drive versus coupling (R1 vs R3): an equal-time gain cannot tell a common field from feedback. In #12 the field is known and switches on and off ten times at known instants in one room at a fixed roster. If content co-movement is mostly the field, the gain should be high while a motion is on and fall when it is removed; coupling (agents answering each other) would keep it up after the motion direction is removed.

## Design (round 1b native test)
- **Slots:** 10-minute windows over the #12 active days (finer than w30 because debates last 13–47 min); a slot is **on** if it lies inside a debate's team window, else **off**.
- **States:** agent × slot mean of unit statement vectors (restatements removed), bge-small and gte-modernbert (H01's per-regime whitening, d = 32); split halves for the signal variance (≥ 2 statements).
- **Estimator:** H26's L2 whole-room gain g_room = 1 − 1/VR (one room, upper bound), deviations from the agent's #12 mean; contributions summed separately over on and off slots.
- **Motion removal:** for each debate, the mean direction of the other agents' on-slot deviations in that debate (leave-one-agent-out) is projected out of each agent's on-slot deviations → g_on,rm.
- **CIs:** bootstrap over debates (on) and over days (off), 400 draws.

## Prediction
*Written 2026-10-04 07:45 UTC, before computing any statistic on #12 (seen: DQ6 label counts, debate window lengths and per-debater statement counts).*
- **N2a:** g_on > g_off, both models [0.6].
- **N2b:** removing each debate's motion direction cuts the on-gain by at least half (g_on,rm ≤ 0.5 g_on), both models [0.5].
- **Reading:** N2a and N2b → content co-movement in a debate is mostly the motion field (R1, drives); N2a without N2b → co-fluctuation beyond the field while the room is engaged (coupling-like); neither → no field-dependence of the content gain.

## Result
<!-- R1B -->
| instrument | g_on [95% CI] | g_off [95% CI] | g_on after motion removal [95% CI] | N2a | N2b |
| --- | --- | --- | --- | --- | --- |
| bge_restate | 0.72 [0.68, 0.75] | 0.66 [0.63, 0.68] | 0.33 [-0.01, 0.48] | pass | pass |
| gte_restate | 0.73 [0.68, 0.76] | 0.67 [0.63, 0.70] | 0.37 [0.07, 0.51] | pass | fail |

L2 whole-room gains (one room, upper bounds), 10-min slots, restatements removed. The on/off CIs overlap; removing one leave-one-agent-out direction per debate halves the on-gain (gte misses the 0.5× bar by 0.004). About half of the content co-movement in a debate is the motion field.
<!-- /R1B -->

## Notes
- 2026-10-04: folder created for the round-1b native layer (DQ9 cross-index: H26 → #12). #12 is regime I and was outside round 1's unit set (regime III + #35).
