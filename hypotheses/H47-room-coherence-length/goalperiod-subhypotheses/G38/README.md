# H47 × G38: Choose a charity and raise as much money as you can for it

**Verdict:** supported
**Role:** native
**Period:** regime III · mode C · up to 14 agents · rooms [2, 3] · 17 active days (non-holdout). Units (shared `period_units`): 38a (goal_start); 38b (ne:NE17); 38c (roster_join:Claude Opus 4.7); 38d (ne:NE18); 38e (roster_join:Kimi K2.6).

## Why this period
The rooms got **different instructions** for the charity goal (the drive-confounded contrast to G41). Five units (NE17 outreach approval, two joins, NE18). If room coherence is an instruction drive, the room-specific kickoff directions should carry the within-room co-fluctuation, and the boundary should be sharper than in G41.

## Prediction
*Written 2026-10-04 ~06:10 UTC, before running H47 on this period.*
- **P6a (primary):** instruction-direction share ≤ 0.15: projecting out the unit's goal, kickoff and per-room kickoff directions (L0 → L1) lowers Δ_B by at most 15% (pooled w30).
- **P6b:** day-0 between-room separation larger than G41's day 0.
- Replication items (P1, P2) also reported; leadership at the #38 kickoff: |L| not significant.
- **Against:** a large instruction share (> 0.3): the boundary is carried by the operator's room-specific instructions.

## Result
| Native prediction | Observed | Null | Verdict |
| --- | --- | --- | --- |
| P6a (primary): instruction-direction share ≤ 0.15 | all static directions: -0.02; room-kickoff difference only: 0.001 | – | **met** |
| P6b: day-0 separation > G41's day 0 (7.4) | 9.0 (z 12.4) | F ≈ 1 under the null | met |
| Replication P1 | C_B 0.07 [0.01, 0.19], p 0.003 | – | met |
| Replication P2 | G 0.40 (p 0.003) | – | not met |
| Leadership at the #38 kickoff | L 0.76, p 0.044 | – | not met (L significant) |

**Reading.** The room-specific charity instructions (room kickoff cosine 0.86) give one of the two sharpest boundaries (C_B 0.07), but the instruction *direction* itself carries ~0.1% of the room excess: the static field is removed by the agent means, and the time-varying room co-fluctuation lies elsewhere. **The #38 lead index is the one significant L of eight (p 0.044, expected about 0.4 false positives in 8 tests),** and it is not a lead in time: both response curves are flat from the first 15 minutes. #best's kickoff-day content already matches its next two days, while #rest's day-0 content stays near its pre-day position (first-statement shift 0.10). That reads as a room-specific instruction arc (a room drive), not one room leading another.

Figure: `figures/G38_h47.pdf` (per-unit ρ_w/ρ_c, between-room separation per day, kickoff response curves). Data: `data/processed/H47-room-coherence-length/results/` (`coherence.json`, `separation.json`, `leadership.json`).

## Scorecard (period-specific axes)
- **C:** beats the room-relabel null (p 0.003).
- **G:** room-specific kickoffs (goal_fields kickoff_room cosine 0.86); DQ6 assigned rooms give the same C_B.
- **H:** the static instruction direction (R-drive in its simplest form) does not carry the room excess; time-varying room drives are not excluded.

## Notes
- 2026-10-04 ~06:10 UTC: folder and prediction written before the real-data run.
- 2026-10-04: results filled from `analysis/explore.py` (round 1, exploratory, non-holdout only).
