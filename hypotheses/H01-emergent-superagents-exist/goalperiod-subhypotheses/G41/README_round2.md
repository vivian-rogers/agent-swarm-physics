# H01 × G41, round 2: effective superagents (Kolchinsky–Wolpert) on a substrate of agents

**Verdict:** failed
**Role:** exploratory
**Period:** round 2 units 41 · regime III · 5 non-holdout days · 14 writers · 3037 strict write events

## Why this period
It has a work ledger (strict git/deploy write events on shared projects), so candidate units (crews, synchrony and co-allocation communities, reply communities, with rooms and labs as baselines) and their viability (artifact advancement) can be measured. See the card's "Round 2 formal setup".

## Prediction
*Written 2026-10-04 on the main card ("Round 2 predictions" and Amendment A1), before any real-data run of R4–R8; no period-specific variant.* R4: crews are individuality maxima (composition excess > 0, first among coarse-grainings, local maxima). R5: positive KW stored and observed semantic information for crews, above the members'. R6: one-member scrambles are cheap, crews persist overnight (ΔC ≥ 0.2), coordination excess > 0. R7: departures cost no more than the departed share. R8: others respond to a member's failed write. Per-unit verdict rule in `analysis/r2_period_folders.py`.

## Result
Data: `data/processed/H01-emergent-superagents-exist/round2/G41/results.json`; pipeline `analysis/r2_run.py`; figures `figures/r2_summary_obs.pdf`, `figures/r2_kw.pdf`.

### Unit 41
- **Candidate units:** 16 crews (sizes [2, 2, 3, 3, 3, 3, 4, 4, 5, 5, 5, 6] …), 3 synchrony and 2 co-allocation communities, 2 reply communities, 2 rooms, 3 labs.

| coarse-graining | R4 median z (vs random groups) | local maxima | iota_alloc z | shift z | R4d ΔC overnight (leave-out) |
| --- | --- | --- | --- | --- | --- |
| crews (joint work on one artifact) | -0.60 (n 15) | 0.00 | -0.38 | -0.43 | +0.41 |
| behavior-state synchrony | -0.55 (n 3) | 0.00 | -0.71 | -0.82 | +0.44 |
| co-allocation (co-adoption) | -0.85 (n 1) | 0.00 | -0.21 | -1.16 | +0.38 |
| reply communities | -0.85 (n 1) | 0.00 | -0.21 | -1.11 | +0.38 |
| rooms (baseline) | -0.85 (n 1) | 0.00 | -0.21 | -0.94 | +0.38 |
| labs (baseline) | -0.04 (n 3) | 0.00 | -0.18 | -0.64 | +0.45 |
| single agents (substrate) | – | – | – | – | +0.54 |

- **R5 (KW, crews, τ = 2 h):** ΔV_st -0.0000 [-0.0012, +0.0008], ΔV_obs -0.0010, I(X₀;Y₀) 0.000 bits, Pinsker envelope ±0.002, η –, members' ΔV_st +0.0022; CK error 0.154, scrambled mass on thin cells 0.00. Day-level landscape: +0.0107 (n 64).
- **R6a (NE41 forced consolidations, n 2876):** own writes +0.02 (z +0.4), other members +0.04 (z +1.7), relative to the 5-min base, rotation null.
- **R8a:** others' write attempts within 30 min after an unconfirmed vs a confirmed push: ratio 1.00 (587 unconfirmed, 2215 confirmed push events).
- **Per-unit verdict components:** R4 fail (crews' Stouffer Z -0.87, first vs rooms/labs/reply: False); R5a fail; R6b pass (ΔC +0.41); R4d fail.

### Goal change after this period (NE34, relevance scramble)
- 41->42 (new): 16 crews, V_adv on R_G 0.83 → 0.31 (Δ -0.52 ± 0.04); R_G still written in the next goal's first 2 days for 88% of crews.

## Scorecard (period-specific axes)
- **C** 0–1: no candidate beats its activity-matched random-group null on individuality; allocation continuity beats its permutation null. **E** 0: no unit-level natural scramble inside the period except where noted. **F**: see the card (timing individuality has ≤ 7% power at this sampling).

## Notes
- 2026-10-04: round 2 per the card. Rooms and labs are baseline partitions only; coordination-based candidates (synchrony, co-allocation, reply, crews) were added at Vivian's request before the real-data run (A1.3). A dedicated coordination-first search is left to H58.
