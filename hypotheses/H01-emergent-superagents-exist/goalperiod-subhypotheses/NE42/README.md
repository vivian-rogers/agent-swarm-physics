# H01 × NE42: Merge and split back at a fixed roster: does #best/#rest identity survive the merge? (#39 → #40 → #41)

**Verdict:** supported (native, round 1b)
**Verdict (1b):** supported (both models; goal-confounded)
**Role:** native
**Period:** regime III · #39 (two rooms, #best / #rest; 04-27 → 05-01), #40 (merged into #universe-coordination on 05-04, GPT-5 left alone in #rest; 05-04 → 05-08), #41 (split back to the same partition on 05-11; 05-11 → 05-15). N = 15. Goal-confounded: #40 is a shared-objective week.

## Why this period
DQ9's leverage for H01: an **A-B-A** at a fixed roster. Round 1 used the 05-04 step only as a pair DiD of residual alignment (P7: +0.18, permutation p 0.004). The native question is whether the old room partition stays an ordered unit when the channel between its halves is opened: if room order is carried by the channel (D3.2, coupling), the #39 partition should lose its order in #40 and regain it in #41; if it is carried by who the agents are or what they each work on (a fixed agent field), it should persist through #40.

## Design (round 1b native test)
- **Labels:** each agent's modal #39 room (best / rest); GPT-5 excluded (alone in #rest in #40). The same labels are applied in #39, #40 and #41.
- **Statistic 1 (D3.1.a):** P1's room-order ΔH per day (semantic entropy of the label groups vs 1,000 size-keeping permutations of the labels; k = 40 meaning clusters, 8 statements per agent-day, 20 rarefaction draws), median per period.
- **Statistic 2 (D3.2):** within-label minus cross-label mean residual cosine of rarefied agent-day vectors (P6's room criterion with the old labels; first-day agent field).
- Instruments: round-1b primary (shared goal vectors, restatements removed), bge-small and gte-modernbert.

## Prediction
*Written 2026-10-04 07:45 UTC, before running either statistic with the old labels on #40 or #41. Not blind: I have seen round 1's P1 per-unit values (#39 −0.037, #41 −0.190, #40 no P1 days) and P7 DiD, and H47's NE42 result (content coherence across the old boundary 0.57× → 1.37× → 0.17× of within, DiD 1.00, p 0.001).*
- **N2a:** median ΔH with the #39 labels is closer to 0 (larger) in #40 than in both #39 and #41 [0.65].
- **N2b:** within − cross residual cosine with the #39 labels is smaller in #40 than in both #39 and #41 [0.6].
- **Reading:** both → room order follows the channel (it dissolves when the channel opens and returns when it closes); neither → the partition is carried by agent-level fields. #40's shared objective works in the same direction as the coupling reading (a common task also removes the partition's order), so a pass is coupling-or-task, not coupling alone.

## Result
<!-- R1B -->
| instrument | period | P1 ΔH median, #39 labels (days < 0) | within − cross, #39 labels | agent-label perm p |
| --- | --- | --- | --- | --- |
| bge_restate | #39 | -0.036 (100%) | +0.113 | 0.0135 |
| bge_restate | #40 | +0.010 (40%) | -0.033 | 0.7226 |
| bge_restate | #41 | -0.205 (100%) | +0.221 | 0.0005 |
| gte_restate | #39 | -0.078 (100%) | +0.079 | 0.0255 |
| gte_restate | #40 | -0.019 (100%) | -0.053 | 0.8031 |
| gte_restate | #41 | -0.266 (100%) | +0.250 | 0.0005 |

**N2a passed** in both models (the old partition's order vanishes in #40 and returns in #41); **N2b passed** in both models (within − cross falls from +0.11/+0.08 to −0.03/−0.05 and returns to +0.22/+0.25). Room order follows the channel, as H47 found for coherence; #40's shared objective is a confound in the same direction.

Data: `data/processed/H01-emergent-superagents-exist/r1b/native.json`.
<!-- /R1B -->

## Notes
- 2026-10-04: folder created for the round-1b native layer (DQ9 cross-index: H01 → NE42). Round 1's P7 result stays in [`G40/`](../G40/README.md).
