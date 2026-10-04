# H01 × G36, round 2: effective superagents (Kolchinsky–Wolpert) on a substrate of agents

**Verdict:** mixed
**Role:** exploratory
**Period:** round 2 units 36b · regime III · 4 non-holdout days · 12 writers · 606 strict write events

## Why this period
It has a work ledger (strict git/deploy write events on shared projects), so candidate units (crews, synchrony and co-allocation communities, reply communities, with rooms and labs as baselines) and their viability (artifact advancement) can be measured. See the card's "Round 2 formal setup".

## Prediction
*Written 2026-10-04 on the main card ("Round 2 predictions" and Amendment A1), before any real-data run of R4–R8; no period-specific variant.* R4: crews are individuality maxima (composition excess > 0, first among coarse-grainings, local maxima). R5: positive KW stored and observed semantic information for crews, above the members'. R6: one-member scrambles are cheap, crews persist overnight (ΔC ≥ 0.2), coordination excess > 0. R7: departures cost no more than the departed share. R8: others respond to a member's failed write. Per-unit verdict rule in `analysis/r2_period_folders.py`.

## Result
Data: `data/processed/H01-emergent-superagents-exist/round2/G36/results.json`; pipeline `analysis/r2_run.py`; figures `figures/r2_summary_obs.pdf`, `figures/r2_kw.pdf`.

### Unit 36b
- **Candidate units:** 8 crews (sizes [2, 2, 3, 3, 4, 5, 8, 8]), 4 synchrony and 2 co-allocation communities, 2 reply communities, 2 rooms, 3 labs.

| coarse-graining | R4 median z (vs random groups) | local maxima | iota_alloc z | shift z | R4d ΔC overnight (leave-out) |
| --- | --- | --- | --- | --- | --- |
| crews (joint work on one artifact) | +0.35 (n 8) | 0.12 | -0.10 | +0.56 | +0.20 |
| behavior-state synchrony | -0.29 (n 4) | 0.00 | -0.41 | -0.72 | +0.44 |
| co-allocation (co-adoption) | +0.31 (n 2) | 0.00 | -0.45 | +0.08 | +0.21 |
| reply communities | +1.11 (n 2) | 0.00 | -0.49 | +0.58 | +0.19 |
| rooms (baseline) | +1.38 (n 2) | 0.50 | +0.66 | +0.58 | +0.15 |
| labs (baseline) | +0.02 (n 3) | 0.00 | -0.02 | +0.79 | +0.34 |
| single agents (substrate) | – | – | – | – | +0.74 |

- **R5 (KW, crews, τ = 2 h):** ΔV_st +0.0057 [+0.0017, +0.0133], ΔV_obs -0.0076, I(X₀;Y₀) 0.027 bits, Pinsker envelope ±0.097, η 1.00, members' ΔV_st +0.0001; CK error 0.178, scrambled mass on thin cells 0.01. Day-level landscape: – (n 24).
- **R6a (NE41 forced consolidations, n 1528):** own writes +0.24 (z +2.4), other members +0.06 (z +1.2), relative to the 5-min base, rotation null.
- **R8a:** others' write attempts within 30 min after an unconfirmed vs a confirmed push: ratio 1.05 (90 unconfirmed, 539 confirmed push events).
- **Per-unit verdict components:** R4 fail (crews' Stouffer Z +1.03, first vs rooms/labs/reply: False); R5a pass; R6b fail (ΔC +0.20); R4d fail.

### Goal change after this period (NE34, relevance scramble)
- 36b->37 (new): 8 crews, V_adv on R_G 0.81 → 0.24 (Δ -0.58 ± 0.06); R_G still written in the next goal's first 2 days for 100% of crews.

## Scorecard (period-specific axes)
- **C** 0–1: no candidate beats its activity-matched random-group null on individuality; allocation continuity beats its permutation null. **E** 0: no unit-level natural scramble inside the period except where noted. **F**: see the card (timing individuality has ≤ 7% power at this sampling).

## Notes
- 2026-10-04: round 2 per the card. Rooms and labs are baseline partitions only; coordination-based candidates (synchrony, co-allocation, reply, crews) were added at Vivian's request before the real-data run (A1.3). A dedicated coordination-first search is left to H58.
