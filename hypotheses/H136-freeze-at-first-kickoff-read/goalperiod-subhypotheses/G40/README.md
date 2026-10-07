# H136 × G40: kickoff read-out and freeze (kickoff day 2026-05-04)

**Verdict:** n/a (untestable)
**Role:** exploratory
**Period:** regime III · kickoff unit(s): G40 (15 readers) · layer: replication + native N2.

## Why this period
A card candidate kickoff (Design, replication list) and the hub-link R-copy test (N2).

## Prediction
*Written 2026-10-07 (card), before running on this period.*
N2: the kickoff-read anchor beats the hub-link anchor (O4). Replication: P1–P3 if ≥ 5 delayed active readers.

## Result
Structural precondition (`scheme/structure.py`; counted before any freeze time):

| Unit | Readers | Delayed active readers (need ≥ 5) | Read within 2 active min | Median wall read delay (s) [95% CI] | Read at first call of day | Previous day reserved |
| --- | --- | --- | --- | --- | --- | --- |
| G40 | 15 | 0 | 1.00 [0.80, 1.00] | 71 [71, 73] | 15/15 | no |

The kickoff is posted about 1 min before the day window opens, so each agent reads it at boot. The kill test (O1, O3) is untestable here. The outcome analysis stopped at the precondition; P2, P4, P5 and the native predictions were not computed.

Synthetic on this skeleton (G40, 500 runs per world): O1 power under W1 is 0.00 on the card's sample and 0.58 on all readers (size under W2 0.00). O3 power under W2 is 0.05. The card's pass rule is not met.

## Scorecard (period-specific axes)
F (identifiability): 0 here; the read and clock alignments coincide at this read-delay spread.

## Notes
- 2026-10-07: round 1; data in `data/processed/H136-freeze-at-first-kickoff-read/structure/`.
