# H01 × G38, round 2: effective superagents (Kolchinsky–Wolpert) on a substrate of agents

**Verdict:** mixed
**Role:** exploratory
**Period:** round 2 units 38a, 38b, 38c · regime III · 17 non-holdout days · 12 writers · 1732 strict write events

## Why this period
It has a work ledger (strict git/deploy write events on shared projects), so candidate units (crews, synchrony and co-allocation communities, reply communities, with rooms and labs as baselines) and their viability (artifact advancement) can be measured. See the card's "Round 2 formal setup".

## Prediction
*Written 2026-10-04 on the main card ("Round 2 predictions" and Amendment A1), before any real-data run of R4–R8; no period-specific variant.* R4: crews are individuality maxima (composition excess > 0, first among coarse-grainings, local maxima). R5: positive KW stored and observed semantic information for crews, above the members'. R6: one-member scrambles are cheap, crews persist overnight (ΔC ≥ 0.2), coordination excess > 0. R7: departures cost no more than the departed share. R8: others respond to a member's failed write. Per-unit verdict rule in `analysis/r2_period_folders.py`.

## Result
Data: `data/processed/H01-emergent-superagents-exist/round2/G38/results.json`; pipeline `analysis/r2_run.py`; figures `figures/r2_summary_obs.pdf`, `figures/r2_kw.pdf`.

### Unit 38a
- **Candidate units:** 9 crews (sizes [2, 3, 3, 3, 4, 4, 5, 5, 6]), 4 synchrony and 2 co-allocation communities, 2 reply communities, 2 rooms, 3 labs.

| coarse-graining | R4 median z (vs random groups) | local maxima | iota_alloc z | shift z | R4d ΔC overnight (leave-out) |
| --- | --- | --- | --- | --- | --- |
| crews (joint work on one artifact) | +0.53 (n 9) | 0.00 | +0.60 | +1.48 | +0.51 |
| behavior-state synchrony | -0.69 (n 4) | 0.00 | -0.15 | -0.46 | +0.40 |
| co-allocation (co-adoption) | +0.07 (n 2) | 0.00 | +0.56 | +1.25 | +0.47 |
| reply communities | -0.61 (n 2) | 0.00 | -0.68 | +0.22 | +0.41 |
| rooms (baseline) | -0.61 (n 2) | 0.00 | -0.68 | +0.34 | +0.41 |
| labs (baseline) | -0.39 (n 3) | 0.00 | -0.64 | +0.10 | +0.27 |
| single agents (substrate) | – | – | – | – | +0.43 |

- **R5 (KW, crews, τ = 2 h):** ΔV_st +0.0017 [-0.0017, +0.0052], ΔV_obs -0.0022, I(X₀;Y₀) 0.022 bits, Pinsker envelope ±0.088, η 0.98, members' ΔV_st -0.0026; CK error 0.086, scrambled mass on thin cells 0.01. Day-level landscape: -0.0098 (n 63).
- **R6a (NE41 forced consolidations, n 2796):** own writes +0.31 (z +5.2), other members +0.03 (z +1.1), relative to the 5-min base, rotation null.
- **R8a:** others' write attempts within 30 min after an unconfirmed vs a confirmed push: ratio 1.04 (422 unconfirmed, 1242 confirmed push events).
- **R7b:** 9 crews alive ≥ 6 active days, median Jaccard(first third, last third members) 1.00 (no turnover).
- **Per-unit verdict components:** R4 pass (crews' Stouffer Z +2.06, first vs rooms/labs/reply: True); R5a fail; R6b pass (ΔC +0.51); R4d pass.
### Unit 38b
- **Candidate units:** 3 crews (sizes [2, 5, 5]), 2 synchrony and 2 co-allocation communities, 2 reply communities, 2 rooms, 3 labs.

| coarse-graining | R4 median z (vs random groups) | local maxima | iota_alloc z | shift z | R4d ΔC overnight (leave-out) |
| --- | --- | --- | --- | --- | --- |
| crews (joint work on one artifact) | -1.08 (n 3) | 0.00 | -0.76 | -0.81 | +0.50 |
| behavior-state synchrony | -0.10 (n 2) | 0.00 | -0.26 | -0.45 | +0.40 |
| co-allocation (co-adoption) | -0.38 (n 2) | 0.00 | -0.76 | -0.37 | +0.45 |
| reply communities | -0.34 (n 2) | 0.00 | -0.78 | -0.57 | +0.48 |
| rooms (baseline) | -0.41 (n 2) | 0.00 | -0.74 | -0.45 | +0.45 |
| labs (baseline) | +0.35 (n 3) | 0.00 | +0.16 | -0.12 | +0.44 |
| single agents (substrate) | – | – | – | – | +0.42 |

- **R5 (KW, crews, τ = 2 h):** ΔV_st -0.0671 [-0.0875, -0.0034], ΔV_obs -0.0250, I(X₀;Y₀) 0.352 bits, Pinsker envelope ±0.349, η –, members' ΔV_st -0.0151; CK error 0.047, scrambled mass on thin cells 0.20. Day-level landscape: – (n 9).
- **R6a (NE41 forced consolidations, n 381):** own writes -0.61 (z -2.3), other members -0.20 (z -1.5), relative to the 5-min base, rotation null.
- **R8a:** others' write attempts within 30 min after an unconfirmed vs a confirmed push: ratio 1.15 (19 unconfirmed, 186 confirmed push events).
- **Per-unit verdict components:** R4 fail (crews' Stouffer Z -1.02, first vs rooms/labs/reply: False); R5a fail; R6b pass (ΔC +0.50); R4d fail.
### Unit 38c
- **Candidate units:** 2 crews (sizes [3, 5]), 3 synchrony and 2 co-allocation communities, 2 reply communities, 2 rooms, 3 labs.

| coarse-graining | R4 median z (vs random groups) | local maxima | iota_alloc z | shift z | R4d ΔC overnight (leave-out) |
| --- | --- | --- | --- | --- | --- |
| crews (joint work on one artifact) | -0.07 (n 2) | 0.00 | +2.47 | +1.34 | +0.47 |
| behavior-state synchrony | -0.94 (n 3) | 0.00 | -0.55 | -0.15 | +0.51 |
| co-allocation (co-adoption) | +0.03 (n 2) | 0.00 | +1.61 | +1.41 | +0.47 |
| reply communities | +0.10 (n 2) | 0.00 | +1.63 | +1.40 | +0.41 |
| rooms (baseline) | +0.12 (n 2) | 0.00 | +1.60 | +1.75 | +0.41 |
| labs (baseline) | -0.40 (n 2) | 0.00 | -0.17 | +0.20 | +0.51 |
| single agents (substrate) | – | – | – | – | +0.56 |

- **R5 (KW, crews, τ = 2 h):** ΔV_st +0.0088 [+0.0018, +0.0174], ΔV_obs -0.0001, I(X₀;Y₀) 0.094 bits, Pinsker envelope ±0.180, η 0.94, members' ΔV_st +0.0000; CK error 0.108, scrambled mass on thin cells 0.05. Day-level landscape: – (n 8).
- **R6a (NE41 forced consolidations, n 353):** own writes +0.09 (z +0.5), other members -0.08 (z -0.9), relative to the 5-min base, rotation null.
- **R8a:** others' write attempts within 30 min after an unconfirmed vs a confirmed push: ratio 1.23 (29 unconfirmed, 154 confirmed push events).
- **Per-unit verdict components:** R4 fail (crews' Stouffer Z -0.11, first vs rooms/labs/reply: False); R5a pass; R6b pass (ΔC +0.47); R4d fail.

### Goal change after this period (NE34, relevance scramble)
- 38c->39 (new): 2 crews, V_adv on R_G 0.64 → 0.28 (Δ -0.36 ± 0.08); R_G still written in the next goal's first 2 days for 100% of crews.

## Scorecard (period-specific axes)
- **C** 0–1: no candidate beats its activity-matched random-group null on individuality; allocation continuity beats its permutation null. **E** 0: no unit-level natural scramble inside the period except where noted. **F**: see the card (timing individuality has ≤ 7% power at this sampling).

## Notes
- 2026-10-04: round 2 per the card. Rooms and labs are baseline partitions only; coordination-based candidates (synchrony, co-allocation, reply, crews) were added at Vivian's request before the real-data run (A1.3). A dedicated coordination-first search is left to H58.
