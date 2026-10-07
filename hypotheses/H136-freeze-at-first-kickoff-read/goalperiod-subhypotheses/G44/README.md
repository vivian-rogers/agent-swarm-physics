# H136 × G44: kickoff read-out and freeze (kickoff day 2026-05-26)

**Verdict:** n/a (untestable)
**Role:** exploratory
**Period:** regime III · kickoff unit(s): G44best (4 readers), G44rest (12 readers) · layer: replication + native N1.

## Why this period
A card candidate kickoff (Design, replication list) and the native named-room contrast (N1).

## Prediction
*Written 2026-10-07 (card), before running on this period.*
N1: #best meets P2 and P3 (K small, ρ(K, D_r) ∋ 0); #rest has < 1/3 of agents frozen on a named target within 2 active h. Precondition first: each room needs ≥ 5 delayed active readers for O1/O3.

## Result
Structural precondition (`scheme/structure.py`; counted before any freeze time):

| Unit | Readers | Delayed active readers (need ≥ 5) | Read within 2 active min | Median wall read delay (s) [95% CI] | Read at first call of day | Previous day reserved |
| --- | --- | --- | --- | --- | --- | --- |
| G44best | 4 | 0 | 1.00 [0.51, 1.00] | 54 [44, 140] | 4/4 | yes |
| G44rest | 12 | 0 | 1.00 [0.76, 1.00] | 41 [40, 45] | 12/12 | yes |

The kickoff is posted about 1 min before the day window opens, so each agent reads it at boot. The kill test (O1, O3) is untestable here. The outcome analysis stopped at the precondition; P2, P4, P5 and the native predictions were not computed.

Synthetic on this skeleton (G44best, 500 runs per world): O1 power under W1 is 0.00 on the card's sample and 0.51 on all readers (size under W2 0.01). O3 power under W2 is 0.00. The card's pass rule is not met.

## Scorecard (period-specific axes)
F (identifiability): 0 here; the read and clock alignments coincide at this read-delay spread.

## Notes
- 2026-10-07: round 1; data in `data/processed/H136-freeze-at-first-kickoff-read/structure/`.
- The previous calendar day is reserved, so the active-before flag cannot be set (counted false). Without that condition the delayed-reader count is still below 5.
