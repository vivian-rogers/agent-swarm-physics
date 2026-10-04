# H115 × G35: Test your game to make it as fun and functional as you can! (2026-03-16 → 03-20)

**Verdict:** failed
**Role:** replication (exploratory)
**Period:** regime II · mode C · 13 agents · rooms #best / #rest (from 03-16) · 5 days. Daily lead designers per room on 03-16, 03-17, 03-18 (DQ6 `leader`, 6 room-days).

## Why this period
Rotating designated leaders inside fixed rooms: a within-room, within-day role with ground truth, in the computer-use scaffold where the per-call clock holds (H40).

## Prediction
*Written 2026-10-04 22:05 UTC, before running on this period.* R1: in each of the 6 leader room-days, the lead designer's normalized sink rank among that room's agents is u_L ≥ 0.5 (source half) in ≥ 2/3 of the room-days (4 of 6). [0.5] Against: u_L < 0.5 in ≥ 4 of 6.

## Result
*Run 2026-10-04 22:19–22:22 UTC* (`data/processed/H115-debate-judge-role-recovery/G35/replication.json`). Additive fit, λ = 4; #best has 3 agents, #rest 9.

| Room-day | lead | rank / n | u_L | in-flight u_L | skeleton-null mean u_L |
| --- | --- | --- | --- | --- | --- |
| 03-16 #best | 23 | 1 / 3 | 0.00 | 0.00 | 0.49 |
| 03-16 #rest | 18 | 6 / 9 | 0.63 | 0.50 | 0.52 |
| 03-17 #best | 20 | 2 / 3 | 0.50 | 0.50 | 0.49 |
| 03-17 #rest | 19 | n/a: the Claude Code agent is never a recipient in the ledger | | | |
| 03-18 #best | 22 | 3 / 3 | 1.00 | 1.00 | 0.54 |
| 03-18 #rest | 6 | 3 / 9 | 0.25 | 0.63 | 0.38 |

- **R1 not met:** source half in 3 of 5 eligible room-days (needed 4); mean u_L 0.48 equals the skeleton-null mean 0.48. Daily lead designers carry no talk-coupling role signal at this resolution.

## Scorecard (period-specific axes)
G (DQ6 lead designers), E (daily rotation), I.

## Notes
