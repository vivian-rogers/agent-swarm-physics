# H136 × G41: kickoff read-out and freeze (kickoff day 2026-05-11)

**Verdict:** n/a (untestable: structural precondition not met; no freeze time computed)
**Role:** exploratory
**Period:** regime III · kickoff unit(s): G41 (14 readers) · layer: replication.

## Why this period
A card candidate kickoff (Design, replication list).

## Prediction
*Written 2026-10-07 (card), before running on this period.*
Replication (card, written 2026-10-07): if the unit has ≥ 5 delayed active readers, P1 (b CI ∋ 1, excludes 0), P2 (K ≤ 2 for ≥ 1/2 of frozen agents), P3 (ρ(K, D_r) CI ∋ 0). Otherwise the kill is untestable here.

## Result
Structural precondition (`scheme/structure.py`; counted before any freeze time):

| Unit | Readers | Delayed active readers (need ≥ 5) | Read within 2 active min | Median wall read delay (s) [95% CI] | Read at first call of day | Previous day reserved |
| --- | --- | --- | --- | --- | --- | --- |
| G41 | 14 | 0 | 1.00 [0.78, 1.00] | 44 [35, 57] | 14/14 | no |

The kickoff is posted about 1 min before the day window opens, so each agent reads it at boot. The kill test (O1, O3) is untestable here. The outcome analysis stopped at the precondition; P2, P4, P5 and the native predictions were not computed.

## Scorecard (period-specific axes)
F (identifiability): 0 here; the read and clock alignments coincide at this read-delay spread.

## Notes
- 2026-10-07: round 1; data in `data/processed/H136-freeze-at-first-kickoff-read/structure/`.
