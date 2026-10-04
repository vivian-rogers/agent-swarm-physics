# H01 × G31, round 2: effective superagents (Kolchinsky–Wolpert) on a substrate of agents

**Verdict:** failed
**Role:** exploratory
**Period:** round 2 units 31 · regime I · 5 non-holdout days · 12 writers · 1090 strict write events

## Why this period
It has a work ledger (strict git/deploy write events on shared projects), so candidate units (crews, synchrony and co-allocation communities, reply communities, with rooms and labs as baselines) and their viability (artifact advancement) can be measured. See the card's "Round 2 formal setup".

## Prediction
*Written 2026-10-04 on the main card ("Round 2 predictions" and Amendment A1), before any real-data run of R4–R8; no period-specific variant.* R4: crews are individuality maxima (composition excess > 0, first among coarse-grainings, local maxima). R5: positive KW stored and observed semantic information for crews, above the members'. R6: one-member scrambles are cheap, crews persist overnight (ΔC ≥ 0.2), coordination excess > 0. R7: departures cost no more than the departed share. R8: others respond to a member's failed write. Per-unit verdict rule in `analysis/r2_period_folders.py`.

## Result
Data: `data/processed/H01-emergent-superagents-exist/round2/G31/results.json`; pipeline `analysis/r2_run.py`; figures `figures/r2_summary_obs.pdf`, `figures/r2_kw.pdf`.

### Unit 31
- **Candidate units:** 20 crews (sizes [2, 3, 3, 3, 3, 3, 3, 4, 4, 5, 5, 5] …), 3 synchrony and 2 co-allocation communities, 2 reply communities, 0 rooms, 3 labs.

| coarse-graining | R4 median z (vs random groups) | local maxima | iota_alloc z | shift z | R4d ΔC overnight (leave-out) |
| --- | --- | --- | --- | --- | --- |
| crews (joint work on one artifact) | -0.51 (n 19) | 0.05 | -0.47 | -0.11 | +0.12 |
| behavior-state synchrony | +0.48 (n 3) | 0.00 | -0.38 | +1.05 | +0.23 |
| co-allocation (co-adoption) | +0.36 (n 2) | 0.50 | -0.47 | +0.82 | +0.05 |
| reply communities | -0.60 (n 2) | 0.00 | -0.63 | -0.61 | +0.11 |
| rooms (baseline) | – (n 0) | – | – | – | – |
| labs (baseline) | +0.04 (n 3) | 0.00 | -0.43 | -0.24 | +0.09 |
| single agents (substrate) | – | – | – | – | +0.47 |

- **R5 (KW, crews, τ = 2 h):** ΔV_st +0.0001 [-0.0010, +0.0012], ΔV_obs -0.0017, I(X₀;Y₀) 0.013 bits, Pinsker envelope ±0.067, η 0.01, members' ΔV_st +0.0000; CK error 0.066, scrambled mass on thin cells 0.01. Day-level landscape: -0.0034 (n 80).
- **R8a:** others' write attempts within 30 min after an unconfirmed vs a confirmed push: ratio 1.05 (918 unconfirmed, 2550 confirmed push events).
- **Per-unit verdict components:** R4 fail (crews' Stouffer Z -0.94, first vs rooms/labs/reply: False); R5a fail; R6b fail (ΔC +0.12); R4d fail.

## Scorecard (period-specific axes)
- **C** 0–1: no candidate beats its activity-matched random-group null on individuality; allocation continuity beats its permutation null. **E** 0: no unit-level natural scramble inside the period except where noted. **F**: see the card (timing individuality has ≤ 7% power at this sampling).

## Notes
- 2026-10-04: round 2 per the card. Rooms and labs are baseline partitions only; coordination-based candidates (synchrony, co-allocation, reply, crews) were added at Vivian's request before the real-data run (A1.3). A dedicated coordination-first search is left to H58.
