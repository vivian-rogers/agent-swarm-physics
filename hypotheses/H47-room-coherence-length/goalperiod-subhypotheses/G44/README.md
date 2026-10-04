# H47 × G44: Finetune your leader!

**Verdict:** supported
**Role:** native
**Period:** regime III · mode C · up to 18 agents · rooms [2, 3] · 4 active days (non-holdout). Units (shared `period_units`): 44a (goal_start); 44b (roster_join:Claude Opus 4.8; roster_join:[Temporary] Fine-tuned Leader).

## Why this period
Room-specific instructions again: #best fine-tunes a leader, #rest picks its own goals (goal-periods.md). Two units (44a, 44b: the Opus 4.8 and fine-tuned-leader joins). The day before the kickoff (05-25, #43) is held out, so the leadership pre-baseline uses 05-22.

## Prediction
*Written 2026-10-04 ~06:10 UTC, before running H47 on this period.*
- **P6a (primary):** instruction-direction share ≤ 0.15 (pooled w30).
- **P6b:** day-0 between-room separation larger than G41's day 0.
- Replication items (P1, P2) also reported; leadership at the #44 kickoff (pre-baseline 05-22): |L| not significant.
- **Against:** a large instruction share (> 0.3).

## Result
| Native prediction | Observed | Null | Verdict |
| --- | --- | --- | --- |
| P6a (primary): instruction-direction share ≤ 0.15 | all static directions: -0.01; room-kickoff difference only: 0.001 | – | **met** |
| P6b: day-0 separation > G41's day 0 (7.4) | 5.9 (z 11.9) | F ≈ 1 under the null | not met |
| Replication P1 | C_B -0.04 [-0.39, 0.13], p 0.003 | – | met |
| Replication P2 | G 0.19 (p 0.003) | – | not met |
| Leadership at the #44 kickoff | L 0.07, p 0.443 | – | met (no lead) |

**Reading.** Room-specific instructions (room kickoff cosine 0.81; #best fine-tunes a leader, #rest picks its own goals) and the sharpest boundary of all (C_B −0.04: no cross-room correlation). The instruction direction carries ~0.1% of the room excess. The leadership pre-baseline is 05-22 (05-25 is held out).

Figure: `figures/G44_h47.pdf` (per-unit ρ_w/ρ_c, between-room separation per day, kickoff response curves). Data: `data/processed/H47-room-coherence-length/results/` (`coherence.json`, `separation.json`, `leadership.json`).

## Scorecard (period-specific axes)
- **C:** beats the room-relabel null (p 0.003).
- **G:** room-specific kickoffs (goal_fields kickoff_room cosine 0.81); DQ6 assigned rooms give the same C_B.
- **H:** the static instruction direction (R-drive in its simplest form) does not carry the room excess; time-varying room drives are not excluded.

## Notes
- 2026-10-04 ~06:10 UTC: folder and prediction written before the real-data run.
- 2026-10-04: results filled from `analysis/explore.py` (round 1, exploratory, non-holdout only).
