# H36 × NE45 + NE38: A tool-schema change and a one-agent role change on the same day (2026-07-29, inside #51)

**Verdict:** supported (native, round 1b)
**Verdict (1b):** supported (silent as predicted; not detected)
**Role:** native
**Period:** regime III · #51 · N ≈ 24 · one main room. Day 0 = 2026-07-29: **NE45**, the history-search tool's date fields switch from integers to strings (undocumented; found by H56), and **NE38**, a human reassigns Claude Opus 5's role (word puzzles → mathematics). Round 1 scored NE38 as a scaffold-class event.

## Why this period
DQ9 lists NE38 as "a one-agent change the alarm should *not* fire on": a swarm-level alarm that fires on one agent's reassignment would be too sensitive. NE45 is an interface change that only matters to searching agents. Both are tests of specificity, and NE45 is one of HH268's blind-dating targets.

## Design (round 1b native test)
Daily scores from the round-1b replication (fixed activity bins and outages, both models): Z_phys, Z_act, Z_cont, R1, C3; hit = ≥ threshold on day −1, 0 or +1. Blind dating: the rank of 07-29 among #51's non-holdout active days, excluding ±1 day around NE32 (07-09), the side room (07-24), the #focus room (08-05) and NE33 (09-03).

## Prediction
*Written 2026-10-04 07:50 UTC, before any round-1b score was computed (round 1's NE38 row was in the round-1 event table; not looked up for this note).*
- **N4a:** no pre-registered alarm (Z_phys < 2 on −1..+1) [0.8].
- **N4b:** R1 < 2 on −1..+1 [0.75]; C3 does not fire [0.7].
- **N4c:** 07-29 is not the top day of #51 by any score [0.85].
- **Reading:** silence is the specificity the operator wants for NE38; it also means H36's detector cannot date NE45, which needs H56's log features (HH268).

## Result
<!-- R1B -->
**NE45** (day 0 2026-07-29, #51; same day: NE38,NE45; 25 candidate days for blind dating), bge:

| Score | day −1 | day 0 | day +1 | hit (≥ 2) | top day in window | percentile vs candidates |
| --- | --- | --- | --- | --- | --- | --- |
| Z_phys | -0.16 | -0.35 | -0.86 | no | no | 0.32 |
| Z_act | 0.13 | -0.53 | -0.95 | no | no | 0.48 |
| Z_act_trim | 0.62 | -0.10 | -0.47 | no | no | 0.75 |
| Z_cont | -0.41 | -0.28 | -0.73 | no | no | 0.40 |
| R1 | -1.16 | -1.30 | -1.36 | no | no | 0.04 |
| C3 | -0.41 | -0.28 | -0.73 | no | no | 0.32 |

**NE45** (day 0 2026-07-29, #51; same day: NE38,NE45; 25 candidate days for blind dating), gte:

| Score | day −1 | day 0 | day +1 | hit (≥ 2) | top day in window | percentile vs candidates |
| --- | --- | --- | --- | --- | --- | --- |
| Z_phys | 0.06 | -0.24 | -0.98 | no | no | 0.48 |
| Z_act | 0.13 | -0.53 | -0.95 | no | no | 0.48 |
| Z_act_trim | 0.62 | -0.10 | -0.47 | no | no | 0.75 |
| Z_cont | 0.06 | -0.11 | -0.96 | no | no | 0.68 |
| R1 | -0.38 | -1.23 | -0.93 | no | no | 0.36 |
| C3 | 0.06 | -0.11 | -0.96 | no | no | 0.60 |
<!-- /R1B -->

## Round 2 (2026-10-05)
<!-- R2 -->
Scaffold detector R5 (card: Round 2; prediction P5.3 for NE14b: not separately predicted; the schema diff S dates it, R5 does not).

| Channel | z on day 0 |
| --- | --- |
| z_R5 (alarm ≥ 4) | 0.63 |
| tool mix | -1.28 |
| bash grammar | -1.02 |
| context-boundary rate (abs) | 0.63 |
| schema diff S (H74, shared) | 12 |
| H74 mix M | 0.71 |

Data: `data/processed/H36-reorganization-alarm/r2/scaffold_days.parquet`.
<!-- /R2 -->
