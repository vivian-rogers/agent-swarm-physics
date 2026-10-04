# H101 × NE42: room merge and split at a fixed roster (#39 → #40 → #41, 2026-04-27 → 05-15)

**Verdict:** mixed
**Role:** native (exploratory)
**Period:** goals #39 (two rooms), #40 (one merged room), #41 (two rooms again) · 15 agents · regime III · 5 days each.

## Why this period
An A-B-A change of the room structure at a fixed roster. Rooms route reading (Q1), so they should shape who co-uses what. Two rooms make two room-level fields; one room makes one shared field. The K-model removes only a uniform field, so the merge should move multi-information from room blocks (pairwise J within rooms) into the uniform field share φ.

## Prediction
*Written 2026-10-04 20:39 UTC, before running on these units.*
- **NE42-a (rooms are pairwise blocks).** In #39 and #41, mean J within rooms exceeds mean J across rooms (subset-averaged K-pairwise J, permutation over room labels within day, p < 0.05 in both). [0.6]
- **NE42-b (merge raises the shared-field share).** φ(#40) > φ(#39) and φ(#40) > φ(#41), each difference ≥ 0.05. [0.45]
- **NE42-c (sufficiency unchanged).** |ρ_F(#40) − mean ρ_F(#39, #41)| < 0.1. [0.5]
- *Against the reading:* J within ≤ J across in both two-room weeks (co-usage ignores rooms), or φ falls at the merge.

## Result
Data: `natives/ne42.json` (unit numbers from the replication run, n = 6 subsets).

| Unit | rooms | I_N | φ (field share) | ρ_F | r_HO | z | field-ref r_HO | J within − J across room [p] |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| #39 | 2 | 0.069 | 0.535 | 0.867 | 0.062 | 5.1 | 0.141 | +0.37 [p 0.0005] |
| #40 | 1 | 0.105 | 0.469 | 0.891 | 0.058 | 17.5 | 0.130 | – |
| #41 | 2 | 0.158 | 0.338 | 0.944 | 0.037 | 11.2 | 0.106 | +1.44 [p 0.0005] |

- **NE42-a supported.** In both two-room weeks, agents in the same room co-use more than agents across rooms (K-pairwise J averaged over subsets; room labels shuffled within day): rooms appear as pairwise blocks.
- **NE42-b failed.** The field share does not rise at the merge: φ goes 0.535 → 0.469 → 0.338. It falls over the three weeks instead.
- **NE42-c supported.** ρ_F(#40) = 0.891 vs the two-room mean 0.906 (difference 0.015 < 0.1).
- Reading: rooms shape *who* co-uses (pairwise blocks), not *how much* is shared by everyone. The remainder stays within the heterogeneous-field reference in all three weeks.

## Scorecard (period-specific axes)
E (an A-B-A intervention on the room structure), G (DQ6 room assignments).

## Notes
