# H36 × NE40: History-search answerer swap (dated 2026-04-20 by H56; shipped with NE18; inside #38)

**Verdict:** supported (native, round 1b)
**Verdict (1b):** supported (silent as predicted; not detected)
**Role:** native
**Period:** regime III · #38 (17 days, two rooms) · day 0 = 2026-04-20 (also NE18, the documented history-search rework, and the start of H01's unit 38c). Gemini-style answer bullets on 55/61 days up to 04-17, 0/68 from 04-20 (H56 stylometry).

## Why this period
NE40 is a change of the agents' memory oracle that nobody announced. H56 found it from plain log features (answer stylometry), not from entropy production. HH268 asks whether H36's detector, which reads what agents say and when they act, can find it blind. Round 1 scored the same day as NE18 (Z_phys 0.73, no alarm).

## Design (round 1b native test)
Daily scores from the round-1b replication (fixed activity bins and outages, both models): Z_phys, Z_act, Z_cont, R1, C3; hit = ≥ threshold on day −1, 0 or +1. Blind dating: the rank of 04-20 among #38's non-holdout active days, excluding the kickoff window (04-02..04-03) and ±1 day around NE36 (04-02) and NE17 (04-14).

## Prediction
*Written 2026-10-04 07:50 UTC, before any round-1b score was computed (round 1's NE18 row, Z_phys 0.73, was seen).*
- **N3a:** no pre-registered alarm (Z_phys < 2 on −1..+1) [0.8].
- **N3b:** R1 < 2 on −1..+1 [0.65]; C3 does not fire [0.7].
- **N3c:** 04-20 is not the top day of #38 by any score (blind dating fails) [0.8].

## Result
<!-- R1B -->
**NE40** (day 0 2026-04-20, #38; same day: NE18,NE40; 8 candidate days for blind dating), bge:

| Score | day −1 | day 0 | day +1 | hit (≥ 2) | top day in window | percentile vs candidates |
| --- | --- | --- | --- | --- | --- | --- |
| Z_phys | -0.33 | 0.36 | -0.80 | no | no | 0.62 |
| Z_act | -0.46 | 1.32 | -0.11 | no | no | 0.88 |
| Z_act_trim | -0.73 | -0.66 | -0.77 | no | no | 0.25 |
| Z_cont | -0.16 | -0.67 | -1.76 | no | no | 0.25 |
| R1 | -0.54 | -0.70 | -0.37 | no | no | 0.50 |
| C3 | -0.16 | -0.67 | -1.37 | no | no | 0.25 |

**NE40** (day 0 2026-04-20, #38; same day: NE18,NE40; 8 candidate days for blind dating), gte:

| Score | day −1 | day 0 | day +1 | hit (≥ 2) | top day in window | percentile vs candidates |
| --- | --- | --- | --- | --- | --- | --- |
| Z_phys | -0.49 | 0.11 | -1.04 | no | no | 0.50 |
| Z_act | -0.46 | 1.32 | -0.11 | no | no | 0.88 |
| Z_act_trim | -0.73 | -0.66 | -0.77 | no | no | 0.25 |
| Z_cont | -0.51 | -1.24 | -2.08 | no | no | 0.00 |
| R1 | -0.59 | -0.44 | -0.01 | no | yes | 1.00 |
| C3 | -0.51 | -1.24 | -1.01 | no | no | 0.00 |
<!-- /R1B -->

## Round 2 (2026-10-05)
<!-- R2 -->
Scaffold detector R5 (card: Round 2; prediction P5.3 for NE14b: not separately predicted).

| Channel | z on day 0 |
| --- | --- |
| z_R5 (alarm ≥ 4) | 2.82 |
| tool mix | -0.50 |
| bash grammar | -0.95 |
| context-boundary rate (abs) | 2.82 |
| schema diff S (H74, shared) | 0 |
| H74 mix M | 0.79 |

Data: `data/processed/H36-reorganization-alarm/r2/scaffold_days.parquet`.
<!-- /R2 -->
