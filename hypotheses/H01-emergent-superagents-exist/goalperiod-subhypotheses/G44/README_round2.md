# H01 × G44, round 2: effective superagents (Kolchinsky–Wolpert) on a substrate of agents

**Verdict:** failed
**Role:** exploratory
**Period:** round 2 units 44 · regime III · 4 non-holdout days · 16 writers · 1594 strict write events

## Why this period
It has a work ledger (strict git/deploy write events on shared projects), so candidate units (crews, synchrony and co-allocation communities, reply communities, with rooms and labs as baselines) and their viability (artifact advancement) can be measured. See the card's "Round 2 formal setup".

## Prediction
*Written 2026-10-04 on the main card ("Round 2 predictions" and Amendment A1), before any real-data run of R4–R8; no period-specific variant.* R4: crews are individuality maxima (composition excess > 0, first among coarse-grainings, local maxima). R5: positive KW stored and observed semantic information for crews, above the members'. R6: one-member scrambles are cheap, crews persist overnight (ΔC ≥ 0.2), coordination excess > 0. R7: departures cost no more than the departed share. R8: others respond to a member's failed write. Per-unit verdict rule in `analysis/r2_period_folders.py`.

## Result
Data: `data/processed/H01-emergent-superagents-exist/round2/G44/results.json`; pipeline `analysis/r2_run.py`; figures `figures/r2_summary_obs.pdf`, `figures/r2_kw.pdf`.

### Unit 44
- **Candidate units:** 10 crews (sizes [2, 2, 2, 2, 2, 3, 4, 5, 6, 6]), 3 synchrony and 2 co-allocation communities, 2 reply communities, 2 rooms, 3 labs.

| coarse-graining | R4 median z (vs random groups) | local maxima | iota_alloc z | shift z | R4d ΔC overnight (leave-out) |
| --- | --- | --- | --- | --- | --- |
| crews (joint work on one artifact) | -0.29 (n 10) | 0.10 | -0.30 | -0.87 | +0.58 |
| behavior-state synchrony | -0.22 (n 3) | 0.00 | +0.00 | -0.84 | +0.49 |
| co-allocation (co-adoption) | -0.16 (n 2) | 0.00 | -0.21 | -1.67 | +0.50 |
| reply communities | -0.16 (n 2) | 0.00 | -0.13 | -0.84 | +0.45 |
| rooms (baseline) | -0.16 (n 2) | 0.00 | -0.13 | -0.72 | +0.45 |
| labs (baseline) | -0.06 (n 3) | 0.00 | +0.07 | -0.30 | +0.52 |
| single agents (substrate) | – | – | – | – | +0.81 |

- **R5 (KW, crews, τ = 2 h):** ΔV_st +0.0001 [-0.0014, +0.0018], ΔV_obs -0.0019, I(X₀;Y₀) 0.000 bits, Pinsker envelope ±0.010, η 1.00, members' ΔV_st -0.0000; CK error 0.136, scrambled mass on thin cells 0.00. Day-level landscape: -0.0070 (n 30).
- **R6a (NE41 forced consolidations, n 781):** own writes -0.37 (z -4.8), other members -0.19 (z -3.7), relative to the 5-min base, rotation null.
- **R8a:** others' write attempts within 30 min after an unconfirmed vs a confirmed push: ratio 0.99 (140 unconfirmed, 1204 confirmed push events).
- **Per-unit verdict components:** R4 fail (crews' Stouffer Z +0.79, first vs rooms/labs/reply: False); R5a fail; R6b pass (ΔC +0.58); R4d fail.

## Scorecard (period-specific axes)
- **C** 0–1: no candidate beats its activity-matched random-group null on individuality; allocation continuity beats its permutation null. **E** 0: no unit-level natural scramble inside the period except where noted. **F**: see the card (timing individuality has ≤ 7% power at this sampling).

## Notes
- 2026-10-04: round 2 per the card. Rooms and labs are baseline partitions only; coordination-based candidates (synchrony, co-allocation, reply, crews) were added at Vivian's request before the real-data run (A1.3). A dedicated coordination-first search is left to H58.
