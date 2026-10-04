# H47 × G41: Perform novel research!

**Verdict:** supported
**Role:** native
**Period:** regime III · mode I · up to 15 agents · rooms [2, 3] · 5 active days (non-holdout). Units (shared `period_units`): 41 (goal_start).

## Why this period
Both rooms got the **same instruction** (perform novel research); #rest converged on multi-agent coordination and #best on AI-judge bias by themselves (goal-periods.md). A room-specific instruction drive is absent by design, so a sharp room boundary here must come from the channel (coupling, or drives the rooms generate themselves), not from the operator. It is also the A in NE42's A-B-A (it follows the merged #40).

## Prediction
*Written 2026-10-04 ~06:10 UTC, before running H47 on this period.*
- **P5a (primary):** C_B(41) ≤ 0.3 with room-relabel p < 0.01 (w30).
- **P5b:** the boundary is as sharp as in the instruction-driven G38/G44: |C_B(41) − median(C_B(38), C_B(44))| ≤ 0.15.
- **P5c (symmetry breaking):** the between-room centroid separation (F statistic vs a within-day room-relabel null) rises over the week (Spearman over days > 0), starting low on day 0 after the merged week.
- Replication items (P1, P2) also reported; leadership at the #41 kickoff (cohorts = new rooms): |L| not significant.
- **Against:** C_B(41) ≥ 0.6 (no boundary without instructions), or a boundary much weaker than in G38/G44 (then the room boundary is mostly the operator's drive).

## Result
| Native prediction | Observed | Null | Verdict |
| --- | --- | --- | --- |
| P5a (primary): C_B(41) ≤ 0.3, room-relabel p < 0.01 | C_B 0.17, p 0.003 (day level 0.13) | permutation median 1.03 | **met** |
| P5b: |C_B(41) − median(C_B(38), C_B(44))| ≤ 0.15 | 0.17 vs 0.02: difference 0.16 | – | not met (just) |
| P5c: separation rises over the week, low on day 0 | day-0 F 7.4 (z 12.6); Spearman over days 0.20 | F ≈ 1 under the null | not met: rooms already separated on the kickoff day |
| Replication P2 | G 0.39 (p 0.003) | – | not met (correlation concentrated in talking pairs) |
| Leadership at #41 (cohorts = new rooms) | L 0.04, p 0.629; both rooms at y ≈ 1 from the first 15 min | – | met (no lead) |

**Reading.** With the same instruction in both rooms, content still co-moves inside rooms and not across them (C_B 0.17, the third-sharpest boundary). So a sharp boundary does not need a room-specific operator drive. But the rooms had split into different topics from the first day (the separation is as large as in G38/G44), and the post hoc cross-period pattern says sharp boundaries go with separated topics. This week cannot say whether the topic split is coupling (each room's conversation picks its topic) or a fast room-level drive (who is in the room). It is the A2 phase of NE42.

Figure: `figures/G41_h47.pdf` (per-unit ρ_w/ρ_c, between-room separation per day, kickoff response curves). Data: `data/processed/H47-room-coherence-length/results/` (`coherence.json`, `separation.json`, `leadership.json`).

## Scorecard (period-specific axes)
- **C:** beats the room-relabel null (p 0.003).
- **E:** A2 of NE42 (the boundary returns after the merge; see NE42).
- **G:** identical-instruction ground truth (one kickoff, in the merged room); topic divergence matches the goal-periods notes (#rest coordination, #best judge bias).

## Notes
- 2026-10-04 ~06:10 UTC: folder and prediction written before the real-data run.
- 2026-10-04: results filled from `analysis/explore.py` (round 1, exploratory, non-holdout only).
