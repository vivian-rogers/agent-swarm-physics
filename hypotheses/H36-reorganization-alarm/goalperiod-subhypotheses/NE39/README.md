# H36 × NE39: Blind detection of the undocumented public-chat closure (≈ 2025-07-01, inside #6)

**Verdict:** failed (native, round 1b)
**Verdict (1b):** failed (content silent; activity alarm on +1, NE02 window)
**Role:** native
**Period:** regime I · #6 (merch store competition, 2025-06-26 → 07-15) · N = 4 · one room. Day 0 = 2025-07-01, the first active day after human messages per day fell from ~100 (16–24 speakers) to ≤ 4 (1 speaker) (DQ9; NE39 in the catalog). NE02 (screenshot redaction, ~0.6% of turns) is on 07-03, two active days later.

## Why this period
DQ9's leverage for H36: **blind detection of an undocumented step** (a cut of the human input channel at a fixed roster inside one goal). The alarm was never told about NE39 (it is not in `kicks`), so this is the cleanest test of whether the swarm statistics see a structural change nobody announced.

## Design (round 1b native test)
- Daily scores from the round-1b replication (fixed activity bins and outages, both embedding models): the pre-registered Z_phys, its channel members Z_act and Z_cont, the rival R1 (content centroid shift) and the post hoc operator rule C3 (R1 ≥ 3 or Z_cont ≥ 2).
- **Hit:** score ≥ threshold on day −1, 0 or +1.
- **Blind dating:** within #6's active days, excluding the kickoff window (06-26..06-29) and NE02's day 0, the rank of day 0 (and of the best day in −1..+1) by each score; chance of a top-1 in −1..+1 is about 3/9.

## Prediction
*Written 2026-10-04 07:50 UTC, before any round-1b score was computed (round-1 scores for #6 days were in the G06 table; I did not look at 06-30..07-02 specifically, but they were visible in the round-1 outputs).*
- **N1a:** no pre-registered alarm (Z_phys < 2 on −1..+1) [0.75]; Z_act |z| < 2 on day 0 [0.7].
- **N1b:** R1 ≥ 2 on −1..+1 [0.45] (agents stop answering viewers, so the topic mix shifts); C3 fires [0.4].
- **N1c:** blind dating by R1 puts the top day in −1..+1 [0.35].
- **Reading:** a hit by R1/C3 with no physics alarm → a first-moment content detector can see an input-channel cut that fluctuation statistics cannot.

## Result
<!-- R1B -->
**NE39** (day 0 2025-07-01, #6; same day: NE39; 7 candidate days for blind dating), bge:

| Score | day −1 | day 0 | day +1 | hit (≥ 2) | top day in window | percentile vs candidates |
| --- | --- | --- | --- | --- | --- | --- |
| Z_phys | -0.80 | -0.24 | 3.27 | yes | no | 0.86 |
| Z_act | -0.48 | 0.24 | 7.21 | yes | no | 0.86 |
| Z_act_trim | -0.19 | 0.50 | 8.22 | yes | no | 0.86 |
| Z_cont | -1.18 | -1.03 | -0.94 | no | no | 0.00 |
| R1 | 0.32 | -0.43 | -0.32 | no | no | 0.57 |
| C3 | -0.68 | -1.03 | -0.94 | no | no | 0.00 |

**NE39** (day 0 2025-07-01, #6; same day: NE39; 7 candidate days for blind dating), gte:

| Score | day −1 | day 0 | day +1 | hit (≥ 2) | top day in window | percentile vs candidates |
| --- | --- | --- | --- | --- | --- | --- |
| Z_phys | -0.68 | -0.08 | 3.35 | yes | no | 0.86 |
| Z_act | -0.48 | 0.24 | 7.21 | yes | no | 0.86 |
| Z_act_trim | -0.19 | 0.50 | 8.22 | yes | no | 0.86 |
| Z_cont | -0.85 | -0.61 | -0.77 | no | no | 0.29 |
| R1 | 0.12 | -0.83 | -0.55 | no | no | 0.57 |
| C3 | -0.85 | -0.61 | -0.77 | no | no | 0.14 |
<!-- /R1B -->
