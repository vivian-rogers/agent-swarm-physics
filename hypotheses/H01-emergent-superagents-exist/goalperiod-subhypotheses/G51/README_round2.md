# H01 × G51, round 2: effective superagents (Kolchinsky–Wolpert) on a substrate of agents

**Verdict:** mixed
**Role:** exploratory
**Period:** round 2 units 51a, 51b, 51c, 51d, 51e · regime III · 45 non-holdout days · 27 writers · 40489 strict write events

## Why this period
It has a work ledger (strict git/deploy write events on shared projects), so candidate units (crews, synchrony and co-allocation communities, reply communities, with rooms and labs as baselines) and their viability (artifact advancement) can be measured. See the card's "Round 2 formal setup".

## Prediction
*Written 2026-10-04 on the main card ("Round 2 predictions" and Amendment A1), before any real-data run of R4–R8; no period-specific variant.* R4: crews are individuality maxima (composition excess > 0, first among coarse-grainings, local maxima). R5: positive KW stored and observed semantic information for crews, above the members'. R6: one-member scrambles are cheap, crews persist overnight (ΔC ≥ 0.2), coordination excess > 0. R7: departures cost no more than the departed share. R8: others respond to a member's failed write. Per-unit verdict rule in `analysis/r2_period_folders.py`.

## Result
Data: `data/processed/H01-emergent-superagents-exist/round2/G51/results.json`; pipeline `analysis/r2_run.py`; figures `figures/r2_summary_obs.pdf`, `figures/r2_kw.pdf`.

### Unit 51a
- **Candidate units:** 14 crews (sizes [2, 3, 3, 3, 3, 3, 3, 4, 4, 5, 5, 6] …), 5 synchrony and 2 co-allocation communities, 4 reply communities, 0 rooms, 4 labs.

| coarse-graining | R4 median z (vs random groups) | local maxima | iota_alloc z | shift z | R4d ΔC overnight (leave-out) |
| --- | --- | --- | --- | --- | --- |
| crews (joint work on one artifact) | -0.11 (n 14) | 0.07 | -0.04 | -1.34 | +0.43 |
| behavior-state synchrony | -0.08 (n 5) | 0.00 | -0.76 | -1.19 | +0.53 |
| co-allocation (co-adoption) | -0.34 (n 2) | 0.00 | +0.03 | -0.86 | +0.35 |
| reply communities | -0.10 (n 3) | 0.00 | +0.17 | -0.90 | +0.33 |
| rooms (baseline) | – (n 0) | – | – | – | – |
| labs (baseline) | -0.31 (n 3) | 0.00 | -0.03 | -1.10 | +0.47 |
| single agents (substrate) | – | – | – | – | +0.73 |

- **R5 (KW, crews, τ = 2 h):** ΔV_st -0.0528 [-0.0845, -0.0217], ΔV_obs -0.0052, I(X₀;Y₀) 0.682 bits, Pinsker envelope ±0.486, η –, members' ΔV_st -0.0065; CK error 0.066, scrambled mass on thin cells 0.20. Day-level landscape: – (n 28).
- **R6a (NE41 forced consolidations, n 2311):** own writes -0.43 (z -8.2), other members +0.09 (z +3.8), relative to the 5-min base, rotation null.
- **R8a:** others' write attempts within 30 min after an unconfirmed vs a confirmed push: ratio 1.08 (333 unconfirmed, 2264 confirmed push events).
- **Per-unit verdict components:** R4 fail (crews' Stouffer Z +0.01, first vs rooms/labs/reply: False); R5a fail; R6b pass (ΔC +0.43); R4d fail.
### Unit 51b
- **Candidate units:** 31 crews (sizes [2, 2, 2, 2, 2, 2, 3, 3, 3, 3, 4, 4] …), 4 synchrony and 3 co-allocation communities, 3 reply communities, 0 rooms, 5 labs.

| coarse-graining | R4 median z (vs random groups) | local maxima | iota_alloc z | shift z | R4d ΔC overnight (leave-out) |
| --- | --- | --- | --- | --- | --- |
| crews (joint work on one artifact) | -0.42 (n 31) | 0.00 | -0.55 | -0.72 | +0.64 |
| behavior-state synchrony | -0.57 (n 4) | 0.00 | -0.33 | -0.56 | +0.59 |
| co-allocation (co-adoption) | -0.25 (n 3) | 0.00 | -0.51 | -0.81 | +0.57 |
| reply communities | -0.22 (n 3) | 0.33 | -0.55 | -0.61 | +0.48 |
| rooms (baseline) | – (n 0) | – | – | – | – |
| labs (baseline) | -0.54 (n 5) | 0.00 | -0.22 | -0.28 | +0.66 |
| single agents (substrate) | – | – | – | – | +0.82 |

- **R5 (KW, crews, τ = 2 h):** ΔV_st -0.0098 [-0.0130, -0.0064], ΔV_obs -0.0048, I(X₀;Y₀) 0.077 bits, Pinsker envelope ±0.163, η –, members' ΔV_st -0.0016; CK error 0.078, scrambled mass on thin cells 0.02. Day-level landscape: +0.0019 (n 558).
- **R6a (NE41 forced consolidations, n 25253):** own writes -0.27 (z -16.5), other members +0.04 (z +4.4), relative to the 5-min base, rotation null.
- **R8a:** others' write attempts within 30 min after an unconfirmed vs a confirmed push: ratio 0.97 (2947 unconfirmed, 33243 confirmed push events).
- **R7a:** 1 departure rows (overlapping crews counted separately); crew write rate relative change +0.02 vs departed share 0.21; no crew died.
- **R7b:** 31 crews alive ≥ 6 active days, median Jaccard(first third, last third members) 1.00 (no turnover).
- **Per-unit verdict components:** R4 fail (crews' Stouffer Z +0.10, first vs rooms/labs/reply: False); R5a fail; R6b pass (ΔC +0.64); R4d fail.
### Unit 51c
- **Candidate units:** 25 crews (sizes [2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2] …), 3 synchrony and 3 co-allocation communities, 3 reply communities, 0 rooms, 5 labs.

| coarse-graining | R4 median z (vs random groups) | local maxima | iota_alloc z | shift z | R4d ΔC overnight (leave-out) |
| --- | --- | --- | --- | --- | --- |
| crews (joint work on one artifact) | -0.35 (n 25) | 0.00 | -0.54 | -0.17 | +0.60 |
| behavior-state synchrony | -0.27 (n 3) | 0.00 | -0.53 | -0.22 | +0.51 |
| co-allocation (co-adoption) | -0.38 (n 3) | 0.00 | -0.17 | -0.39 | +0.56 |
| reply communities | -0.45 (n 3) | 0.33 | +0.01 | -0.41 | +0.50 |
| rooms (baseline) | – (n 0) | – | – | – | – |
| labs (baseline) | -0.45 (n 5) | 0.00 | -0.42 | +0.64 | +0.64 |
| single agents (substrate) | – | – | – | – | +0.81 |

- **R5 (KW, crews, τ = 2 h):** ΔV_st -0.0000 [-0.0004, +0.0001], ΔV_obs -0.0006, I(X₀;Y₀) 0.000 bits, Pinsker envelope ±0.005, η –, members' ΔV_st -0.0001; CK error 0.092, scrambled mass on thin cells 0.00. Day-level landscape: +0.0005 (n 325).
- **R6a (NE41 forced consolidations, n 11229):** own writes +0.19 (z +4.7), other members -0.01 (z -0.7), relative to the 5-min base, rotation null.
- **R8a:** others' write attempts within 30 min after an unconfirmed vs a confirmed push: ratio 1.12 (1483 unconfirmed, 11722 confirmed push events).
- **R7a:** 6 departure rows (overlapping crews counted separately); crew write rate relative change +0.91 vs departed share 0.43; no crew died.
- **R7b:** 25 crews alive ≥ 6 active days, median Jaccard(first third, last third members) 1.00 (no turnover).
- **Per-unit verdict components:** R4 fail (crews' Stouffer Z -1.19, first vs rooms/labs/reply: True); R5a fail; R6b pass (ΔC +0.60); R4d fail.
### Unit 51d
- **Candidate units:** 17 crews (sizes [2, 2, 2, 2, 2, 2, 3, 3, 3, 3, 4, 4] …), 4 synchrony and 4 co-allocation communities, 4 reply communities, 0 rooms, 6 labs.

| coarse-graining | R4 median z (vs random groups) | local maxima | iota_alloc z | shift z | R4d ΔC overnight (leave-out) |
| --- | --- | --- | --- | --- | --- |
| crews (joint work on one artifact) | -0.29 (n 17) | 0.00 | -0.50 | -0.44 | +0.69 |
| behavior-state synchrony | -0.60 (n 4) | 0.00 | +0.36 | +0.17 | +0.56 |
| co-allocation (co-adoption) | -0.24 (n 4) | 0.00 | -0.50 | +0.57 | +0.55 |
| reply communities | -0.60 (n 4) | 0.00 | -0.13 | -0.38 | +0.60 |
| rooms (baseline) | – (n 0) | – | – | – | – |
| labs (baseline) | -0.58 (n 6) | 0.00 | -0.47 | -0.14 | +0.65 |
| single agents (substrate) | – | – | – | – | +0.83 |

- **R5 (KW, crews, τ = 2 h):** ΔV_st +0.0000 [-0.0004, +0.0004], ΔV_obs -0.0006, I(X₀;Y₀) 0.002 bits, Pinsker envelope ±0.025, η 1.00, members' ΔV_st -0.0001; CK error 0.109, scrambled mass on thin cells 0.00. Day-level landscape: +0.0014 (n 102).
- **R6a (NE41 forced consolidations, n 3324):** own writes +0.13 (z +2.8), other members +0.05 (z +1.4), relative to the 5-min base, rotation null.
- **R8a:** others' write attempts within 30 min after an unconfirmed vs a confirmed push: ratio 0.99 (1170 unconfirmed, 3626 confirmed push events).
- **R7a:** 2 departure rows (overlapping crews counted separately); crew write rate relative change -0.50 vs departed share 0.25; no crew died.
- **R7b:** 17 crews alive ≥ 6 active days, median Jaccard(first third, last third members) 1.00 (no turnover).
- **Per-unit verdict components:** R4 fail (crews' Stouffer Z -0.45, first vs rooms/labs/reply: True); R5a fail; R6b pass (ΔC +0.69); R4d fail.
### Unit 51e
- **Candidate units:** 13 crews (sizes [2, 2, 2, 2, 2, 2, 2, 3, 3, 4, 4, 6] …), 5 synchrony and 3 co-allocation communities, 4 reply communities, 0 rooms, 6 labs.

| coarse-graining | R4 median z (vs random groups) | local maxima | iota_alloc z | shift z | R4d ΔC overnight (leave-out) |
| --- | --- | --- | --- | --- | --- |
| crews (joint work on one artifact) | +0.75 (n 13) | 0.23 | -0.11 | -0.06 | +0.61 |
| behavior-state synchrony | -0.37 (n 5) | 0.00 | -0.05 | -0.91 | +0.61 |
| co-allocation (co-adoption) | -0.12 (n 3) | 0.00 | -0.50 | -1.12 | +0.46 |
| reply communities | -0.19 (n 3) | 0.00 | -0.28 | -0.27 | +0.54 |
| rooms (baseline) | – (n 0) | – | – | – | – |
| labs (baseline) | -0.47 (n 6) | 0.00 | -0.37 | -0.36 | +0.79 |
| single agents (substrate) | – | – | – | – | +0.90 |

- **R5 (KW, crews, τ = 2 h):** ΔV_st +0.0009 [+0.0000, +0.0021], ΔV_obs -0.0008, I(X₀;Y₀) 0.006 bits, Pinsker envelope ±0.045, η 1.00, members' ΔV_st -0.0002; CK error 0.129, scrambled mass on thin cells 0.00. Day-level landscape: – (n 13).
- **R6a (NE41 forced consolidations, n 277):** own writes -0.58 (z -3.1), other members -0.05 (z -0.4), relative to the 5-min base, rotation null.
- **R8a:** others' write attempts within 30 min after an unconfirmed vs a confirmed push: ratio 1.04 (97 unconfirmed, 938 confirmed push events).
- **Per-unit verdict components:** R4 pass (crews' Stouffer Z +2.97, first vs rooms/labs/reply: True); R5a fail; R6b pass (ΔC +0.61); R4d fail.

### #focus channel cut (08-05)
- Crews of 51b split across #general/#focus (7) vs kept together (24): change in V_adv on R_G from the last two 51b days to 08-05/06: +0.05 vs +0.03 (DiD +0.02). No channel-cut cost.

## Scorecard (period-specific axes)
- **C** 0–1: no candidate beats its activity-matched random-group null on individuality; allocation continuity beats its permutation null. **E** 0: no unit-level natural scramble inside the period except where noted. **F**: see the card (timing individuality has ≤ 7% power at this sampling).

## Notes
- 2026-10-04: round 2 per the card. Rooms and labs are baseline partitions only; coordination-based candidates (synchrony, co-allocation, reply, crews) were added at Vivian's request before the real-data run (A1.3). A dedicated coordination-first search is left to H58.
