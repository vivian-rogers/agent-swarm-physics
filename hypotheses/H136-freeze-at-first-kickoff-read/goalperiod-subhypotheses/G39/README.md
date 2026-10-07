# H136 × G39: kickoff read-out and freeze (kickoff day 2026-04-27)

**Verdict:** n/a (untestable)
**Role:** exploratory
**Period:** regime III · kickoff unit(s): G39 (14 readers) · layer: replication.

## Why this period
A card candidate kickoff (Design, replication list).

## Prediction
*Written 2026-10-07 (card), before running on this period.*
Replication (card, written 2026-10-07): if the unit has ≥ 5 delayed active readers, P1 (b CI ∋ 1, excludes 0), P2 (K ≤ 2 for ≥ 1/2 of frozen agents), P3 (ρ(K, D_r) CI ∋ 0). Otherwise the kill is untestable here.

## Result
Structural precondition (`scheme/structure.py`; counted before any freeze time):

| Unit | Readers | Delayed active readers (need ≥ 5) | Read within 2 active min | Median wall read delay (s) [95% CI] | Read at first call of day | Previous day reserved |
| --- | --- | --- | --- | --- | --- | --- |
| G39 | 14 | 2 | 0.79 [0.52, 0.92] | 38 [33, 51] | 13/14 | no |

The kickoff is posted about 1 min before the day window opens, so each agent reads it at boot. The kill test (O1, O3) is untestable here. The outcome analysis stopped at the precondition; P2, P4, P5 and the native predictions were not computed.

Synthetic on this skeleton (G39, 500 runs per world): O1 power under W1 is 0.00 on the card's sample and 0.96 on all readers (size under W2 0.05). O3 power under W2 is 0.07. The card's pass rule is not met.

## Scorecard (period-specific axes)
F (identifiability): 0 here; the read and clock alignments coincide at this read-delay spread.

## Notes
- 2026-10-07: round 1; data in `data/processed/H136-freeze-at-first-kickoff-read/structure/`.
