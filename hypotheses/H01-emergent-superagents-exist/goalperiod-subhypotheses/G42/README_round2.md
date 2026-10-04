# H01 × G42, round 2: effective superagents (Kolchinsky–Wolpert) on a substrate of agents

**Verdict:** failed
**Role:** exploratory
**Period:** round 2 units 42 · regime III · 5 non-holdout days · 15 writers · 1451 strict write events

## Why this period
It has a work ledger (strict git/deploy write events on shared projects), so candidate units (crews, synchrony and co-allocation communities, reply communities, with rooms and labs as baselines) and their viability (artifact advancement) can be measured. See the card's "Round 2 formal setup".

## Prediction
*Written 2026-10-04 on the main card ("Round 2 predictions" and Amendment A1), before any real-data run of R4–R8; no period-specific variant.* R4: crews are individuality maxima (composition excess > 0, first among coarse-grainings, local maxima). R5: positive KW stored and observed semantic information for crews, above the members'. R6: one-member scrambles are cheap, crews persist overnight (ΔC ≥ 0.2), coordination excess > 0. R7: departures cost no more than the departed share. R8: others respond to a member's failed write. Per-unit verdict rule in `analysis/r2_period_folders.py`.

## Result
Data: `data/processed/H01-emergent-superagents-exist/round2/G42/results.json`; pipeline `analysis/r2_run.py`; figures `figures/r2_summary_obs.pdf`, `figures/r2_kw.pdf`.

### Unit 42
- **Candidate units:** 6 crews (sizes [2, 2, 2, 2, 2, 8]), 4 synchrony and 2 co-allocation communities, 2 reply communities, 2 rooms, 3 labs.

| coarse-graining | R4 median z (vs random groups) | local maxima | iota_alloc z | shift z | R4d ΔC overnight (leave-out) |
| --- | --- | --- | --- | --- | --- |
| crews (joint work on one artifact) | +0.28 (n 6) | 0.00 | -0.65 | +0.49 | +0.65 |
| behavior-state synchrony | +0.83 (n 4) | 0.00 | -0.50 | +0.44 | +0.63 |
| co-allocation (co-adoption) | -0.20 (n 2) | 0.00 | -0.12 | -1.04 | +0.55 |
| reply communities | -0.17 (n 2) | 0.00 | -0.02 | -20.66 | +0.48 |
| rooms (baseline) | -0.17 (n 2) | 0.00 | -0.02 | -0.85 | +0.48 |
| labs (baseline) | -0.29 (n 2) | 0.00 | +0.72 | -0.66 | +0.61 |
| single agents (substrate) | – | – | – | – | +0.82 |

- **R5 (KW, crews, τ = 2 h):** ΔV_st +0.0013 [-0.0014, +0.0046], ΔV_obs -0.0072, I(X₀;Y₀) 0.016 bits, Pinsker envelope ±0.075, η 1.00, members' ΔV_st -0.0004; CK error 0.048, scrambled mass on thin cells 0.00. Day-level landscape: – (n 24).
- **R6a (NE41 forced consolidations, n 671):** own writes +0.14 (z +1.4), other members -0.01 (z -0.1), relative to the 5-min base, rotation null.
- **R8a:** others' write attempts within 30 min after an unconfirmed vs a confirmed push: ratio 1.17 (39 unconfirmed, 589 confirmed push events).
- **R7a:** 1 departure rows (overlapping crews counted separately); crew write rate relative change -0.55 vs departed share 0.64; no crew died.
- **Per-unit verdict components:** R4 fail (crews' Stouffer Z +1.07, first vs rooms/labs/reply: True); R5a fail; R6b pass (ΔC +0.65); R4d fail.

## Scorecard (period-specific axes)
- **C** 0–1: no candidate beats its activity-matched random-group null on individuality; allocation continuity beats its permutation null. **E** 0: no unit-level natural scramble inside the period except where noted. **F**: see the card (timing individuality has ≤ 7% power at this sampling).

## Notes
- 2026-10-04: round 2 per the card. Rooms and labs are baseline partitions only; coordination-based candidates (synchrony, co-allocation, reply, crews) were added at Vivian's request before the real-data run (A1.3). A dedicated coordination-first search is left to H58.
