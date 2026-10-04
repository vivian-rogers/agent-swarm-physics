# H62 × NE42: rooms merged then split at a fixed roster (#39 → #40 → #41; 2026-05-04 / 2026-05-11)

**Verdict:** mixed
**Role:** native
**Period:** #39 (two rooms), #40 (merged, regime III, mode C), #41 (split back); 15 agents; non-holdout days. Exception (c) of CLAUDE.md: the transition is the object; each week is fitted separately and the weeks are compared.

## Why this period
The only A-B-A change of room size at a fixed roster: an intervention on room-only exposure that leaves reply ties free to form (axis E).

## Prediction
*Written 2026-10-04 19:33 UTC, before any native statistic.* NE42: #best and #rest merged into one room on 2026-05-04 (#40) and split back on 05-11 (#41) at a fixed roster. The merge raises agents posting per room-day (7 → 14 → 7 in H62's count) and leaves the reply ties to form as before.
- **N42-a (room channel dilutes):** T_room(#40) < T_room(#39) and T_room(#40) < T_room(#41).
- **N42-b (reply channel does not):** T_rep(#40) within ±30% of the mean of T_rep(#39) and T_rep(#41).
- **N42-c (merged week, cross-group pairs):** among pairs split by the #39 partition, reply-channel exposures transmit at ≥ 2× the room-only rate (T_rep,cross / T_room,cross ≥ 2).
- Credence 0.4 (the goal changes with the merge, which also changes topics). Verdict: supported = N42-a and N42-b pass; failed = both fail; mixed = otherwise.

## Result
*Run 2026-10-04 after the prediction above.*

| Prediction | Observed | Verdict |
| --- | --- | --- |
| N42-a T_room(#40) below #39 and #41 | T_room #39 0.004, #40 0.011, #41 0.011 | fail |
| N42-b T_rep(#40) within ±30% of the #39/#41 mean | T_rep #39 0.016, #40 0.037, #41 0.045 (mean of #39/#41 0.030) | pass |
| N42-c #40 cross-group pairs: T_rep / T_room ≥ 2 | 3.69 [3.11, 4.43]; T_rep 0.049 (8841 events), T_room 0.013 (17400) | pass |

T_rep / T_room by week: #39 4.08, #40 3.49, #41 3.90. **Native verdict: mixed.**
