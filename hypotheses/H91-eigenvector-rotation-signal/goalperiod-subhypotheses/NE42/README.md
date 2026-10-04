# H91 × NE42: the #best/#rest merge (2026-05-04) and split back (2026-05-11), an A-B-A room step

**Verdict:** mixed
**Role:** native (exploratory)
**Period:** regime III · #39 (two rooms) → #40 (one merged room, 15 agents) → #41 (two rooms, same partition). Both steps coincide with goal kickoffs (goal-confounded, H36).

## Why this period
The only non-holdout A-B-A room step: the same agents lose and regain their room partition within a week. Talk modes separate rooms in two-room units (H12 1b), and talk co-activation vanished in the merged week (H25 native). A change in who can read whom should rotate the talk eigenvectors; a goal step alone should not.

## Prediction
*Written 2026-10-04 ~20:12 UTC, before running on this period. Credences in brackets.*
- **N1a.** Talk rotation excess z_rot ≥ 2 on the 05-04 pair (#39 last day → #40 day 0) [0.5] and on the 05-11 pair (#40 last day → #41 day 0) [0.5].
- **N1b.** Content A_C ≥ 2 on at least one of the two pairs [0.5].
- **N1c.** Mean talk A_rot over the two NE42 pairs exceeds the median talk A_rot over goal-only kickoffs (no room or roster event) [0.55].
- **Counts against:** talk z_rot < 2 on both pairs and N1c fails: a regrouping of the reading network does not rotate the equal-time talk modes beyond finite-T noise.
- **Verdict rule:** *supported* if N1a holds on both pairs; *failed* if it holds on neither and N1b fails; *mixed* otherwise.

## Result
*Run 2026-10-04 ~20:30 UTC.* Rotation excess z_boot (k = 2) against the same-day block bootstrap (R = 199); A = trailing alarm (B = 10).

| Prediction | Observed | Reference | Verdict |
| --- | --- | --- | --- |
| N1a talk z ≥ 2, merge 05-04 | z 1.97, p_boot 0.005 (N 9, 236 kept minutes); split null z 1.15 | talk size 0.13 at N 8, L 240 | fail by threshold (p < 0.01) |
| N1a talk z ≥ 2, split 05-11 | z 1.47, p_boot 0.025 (N 11, 213 min) | as above | fail |
| N1b content A_C ≥ 2 on one pair | merge: z 2.09 / 1.72 (bge / gte; p 0.005 / 0.01), A_C 2.42; split: z 1.08 / 0.51, A_C −1.60 | alarm at 2 | pass |
| N1c NE42 mean talk A > goal-only median | 0.96 vs −0.02 (20 goal-only kickoffs); NE42 exceeds 85% of them | – | pass |

Both steps are also goal kickoffs (#40, #41), where R1 fires (3.5 and 9.7). The merge is the only event in the non-holdout record where talk and content both rotate beyond the bootstrap at p ≤ 0.01. The split back to the same partition rotates less, which fits H25's finding that the merged week had no talk co-activation: on 05-11 the comparison day (#40's last day) has little talk structure to rotate away from.

Data: `data/processed/H91-eigenvector-rotation-signal/native/results.json`, `days_scored.parquet`.

## Scorecard (period-specific axes)
- E (interventional): 1. The A-B-A step moves the eigenvectors in the predicted direction on the A → B side; the B → A side is weaker.
- G (ground truth): 1. 13 and 14 agents change modal room on the two days; only the merge clears p < 0.01.
