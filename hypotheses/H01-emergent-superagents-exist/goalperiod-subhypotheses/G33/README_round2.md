# H01 × G33, round 2: effective superagents (Kolchinsky–Wolpert) on a substrate of agents

**Verdict:** failed
**Role:** exploratory
**Period:** round 2 units 33 · regime II · 3 non-holdout days · 11 writers · 651 strict write events

## Why this period
It has a work ledger (strict git/deploy write events on shared projects), so candidate units (crews, synchrony and co-allocation communities, reply communities, with rooms and labs as baselines) and their viability (artifact advancement) can be measured. See the card's "Round 2 formal setup".

## Prediction
*Written 2026-10-04 on the main card ("Round 2 predictions" and Amendment A1), before any real-data run of R4–R8; no period-specific variant.* R4: crews are individuality maxima (composition excess > 0, first among coarse-grainings, local maxima). R5: positive KW stored and observed semantic information for crews, above the members'. R6: one-member scrambles are cheap, crews persist overnight (ΔC ≥ 0.2), coordination excess > 0. R7: departures cost no more than the departed share. R8: others respond to a member's failed write. Per-unit verdict rule in `analysis/r2_period_folders.py`.

## Result
Data: `data/processed/H01-emergent-superagents-exist/round2/G33/results.json`; pipeline `analysis/r2_run.py`; figures `figures/r2_summary_obs.pdf`, `figures/r2_kw.pdf`.

### Unit 33
- **Candidate units:** 2 crews (sizes [9, 11]), 3 synchrony and 1 co-allocation communities, 2 reply communities, 0 rooms, 3 labs.

| coarse-graining | R4 median z (vs random groups) | local maxima | iota_alloc z | shift z | R4d ΔC overnight (leave-out) |
| --- | --- | --- | --- | --- | --- |
| crews (joint work on one artifact) | – (n 0) | – | +1.29 | – | -0.01 |
| behavior-state synchrony | +2.11 (n 1) | 1.00 | +1.98 | -0.89 | +0.00 |
| co-allocation (co-adoption) | – (n 0) | – | – | – | -0.00 |
| reply communities | – (n 0) | – | -0.80 | – | +0.04 |
| rooms (baseline) | – (n 0) | – | – | – | – |
| labs (baseline) | -0.08 (n 2) | 0.00 | -0.06 | +1.66 | +0.00 |
| single agents (substrate) | – | – | – | – | +0.00 |

- **R5 (KW, crews, τ = 2 h):** ΔV_st +0.0000 [+0.0000, +0.0000], ΔV_obs +0.0008, I(X₀;Y₀) 0.000 bits, Pinsker envelope ±0.000, η –, members' ΔV_st -0.0017; CK error 0.049, scrambled mass on thin cells 0.17. Day-level landscape: – (n 4).
- **R8a:** others' write attempts within 30 min after an unconfirmed vs a confirmed push: ratio 1.02 (155 unconfirmed, 372 confirmed push events).
- **Per-unit verdict components:** R4 fail (crews' Stouffer Z –, first vs rooms/labs/reply: False); R5a fail; R6b fail (ΔC -0.01); R4d fail.

## Scorecard (period-specific axes)
- **C** 0–1: no candidate beats its activity-matched random-group null on individuality; allocation continuity beats its permutation null. **E** 0: no unit-level natural scramble inside the period except where noted. **F**: see the card (timing individuality has ≤ 7% power at this sampling).

## Notes
- 2026-10-04: round 2 per the card. Rooms and labs are baseline partitions only; coordination-based candidates (synchrony, co-allocation, reply, crews) were added at Vivian's request before the real-data run (A1.3). A dedicated coordination-first search is left to H58.
