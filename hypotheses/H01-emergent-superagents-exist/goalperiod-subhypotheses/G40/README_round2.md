# H01 × G40, round 2: effective superagents (Kolchinsky–Wolpert) on a substrate of agents

**Verdict:** mixed
**Role:** exploratory
**Period:** round 2 units 40 · regime III · 5 non-holdout days · 14 writers · 3619 strict write events

## Why this period
It has a work ledger (strict git/deploy write events on shared projects), so candidate units (crews, synchrony and co-allocation communities, reply communities, with rooms and labs as baselines) and their viability (artifact advancement) can be measured. See the card's "Round 2 formal setup".

## Prediction
*Written 2026-10-04 on the main card ("Round 2 predictions" and Amendment A1), before any real-data run of R4–R8; no period-specific variant.* R4: crews are individuality maxima (composition excess > 0, first among coarse-grainings, local maxima). R5: positive KW stored and observed semantic information for crews, above the members'. R6: one-member scrambles are cheap, crews persist overnight (ΔC ≥ 0.2), coordination excess > 0. R7: departures cost no more than the departed share. R8: others respond to a member's failed write. Per-unit verdict rule in `analysis/r2_period_folders.py`.

## Result
Data: `data/processed/H01-emergent-superagents-exist/round2/G40/results.json`; pipeline `analysis/r2_run.py`; figures `figures/r2_summary_obs.pdf`, `figures/r2_kw.pdf`.

### Unit 40
- **Candidate units:** 9 crews (sizes [2, 3, 3, 4, 4, 4, 4, 5, 13]), 4 synchrony and 2 co-allocation communities, 2 reply communities, 0 rooms, 3 labs.

| coarse-graining | R4 median z (vs random groups) | local maxima | iota_alloc z | shift z | R4d ΔC overnight (leave-out) |
| --- | --- | --- | --- | --- | --- |
| crews (joint work on one artifact) | -0.55 (n 8) | 0.00 | -0.42 | -1.10 | +0.37 |
| behavior-state synchrony | +0.44 (n 4) | 0.00 | -0.76 | +0.35 | +0.34 |
| co-allocation (co-adoption) | -0.25 (n 2) | 0.00 | +0.03 | -1.42 | +0.33 |
| reply communities | -0.34 (n 2) | 0.50 | -0.52 | -1.02 | +0.30 |
| rooms (baseline) | – (n 0) | – | – | – | – |
| labs (baseline) | -0.36 (n 3) | 0.00 | -0.66 | +0.04 | +0.20 |
| single agents (substrate) | – | – | – | – | +0.60 |

- **R5 (KW, crews, τ = 2 h):** ΔV_st +0.0034 [+0.0012, +0.0071], ΔV_obs -0.0079, I(X₀;Y₀) 0.022 bits, Pinsker envelope ±0.088, η 0.43, members' ΔV_st +0.0016; CK error 0.080, scrambled mass on thin cells 0.01. Day-level landscape: +0.0058 (n 36).
- **R6a (NE41 forced consolidations, n 1847):** own writes -0.14 (z -2.4), other members +0.02 (z +1.0), relative to the 5-min base, rotation null.
- **R8a:** others' write attempts within 30 min after an unconfirmed vs a confirmed push: ratio 1.26 (192 unconfirmed, 1455 confirmed push events).
- **R7a:** 6 departure rows (overlapping crews counted separately); crew write rate relative change +1.88 vs departed share 0.24; no crew died.
- **Per-unit verdict components:** R4 fail (crews' Stouffer Z -1.61, first vs rooms/labs/reply: False); R5a fail; R6b pass (ΔC +0.37); R4d pass.

### Goal change after this period (NE34, relevance scramble)
- 40->41 (new): 9 crews, V_adv on R_G 0.91 → 0.22 (Δ -0.69 ± 0.10); R_G still written in the next goal's first 2 days for 100% of crews.

## Scorecard (period-specific axes)
- **C** 0–1: no candidate beats its activity-matched random-group null on individuality; allocation continuity beats its permutation null. **E** 0: no unit-level natural scramble inside the period except where noted. **F**: see the card (timing individuality has ≤ 7% power at this sampling).

## Notes
- 2026-10-04: round 2 per the card. Rooms and labs are baseline partitions only; coordination-based candidates (synchrony, co-allocation, reply, crews) were added at Vivian's request before the real-data run (A1.3). A dedicated coordination-first search is left to H58.
