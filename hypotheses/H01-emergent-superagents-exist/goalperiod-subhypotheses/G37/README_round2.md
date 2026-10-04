# H01 × G37, round 2: effective superagents (Kolchinsky–Wolpert) on a substrate of agents

**Verdict:** failed
**Role:** exploratory
**Period:** round 2 units 37 · regime III · 3 non-holdout days · 12 writers · 237 strict write events

## Why this period
It has a work ledger (strict git/deploy write events on shared projects), so candidate units (crews, synchrony and co-allocation communities, reply communities, with rooms and labs as baselines) and their viability (artifact advancement) can be measured. See the card's "Round 2 formal setup".

## Prediction
*Written 2026-10-04 on the main card ("Round 2 predictions" and Amendment A1), before any real-data run of R4–R8; no period-specific variant.* R4: crews are individuality maxima (composition excess > 0, first among coarse-grainings, local maxima). R5: positive KW stored and observed semantic information for crews, above the members'. R6: one-member scrambles are cheap, crews persist overnight (ΔC ≥ 0.2), coordination excess > 0. R7: departures cost no more than the departed share. R8: others respond to a member's failed write. Per-unit verdict rule in `analysis/r2_period_folders.py`.

## Result
Data: `data/processed/H01-emergent-superagents-exist/round2/G37/results.json`; pipeline `analysis/r2_run.py`; figures `figures/r2_summary_obs.pdf`, `figures/r2_kw.pdf`.

### Unit 37
- **Candidate units:** 4 crews (sizes [2, 3, 4, 4]), 4 synchrony and 2 co-allocation communities, 2 reply communities, 2 rooms, 3 labs.

| coarse-graining | R4 median z (vs random groups) | local maxima | iota_alloc z | shift z | R4d ΔC overnight (leave-out) |
| --- | --- | --- | --- | --- | --- |
| crews (joint work on one artifact) | -0.74 (n 4) | 0.00 | +0.93 | -1.00 | +0.26 |
| behavior-state synchrony | -0.67 (n 3) | 0.00 | -0.07 | -0.95 | +0.45 |
| co-allocation (co-adoption) | -0.23 (n 2) | 0.00 | -0.50 | -0.83 | +0.18 |
| reply communities | -0.06 (n 2) | 0.00 | -0.38 | -0.34 | +0.25 |
| rooms (baseline) | -0.06 (n 2) | 0.00 | -0.38 | -0.30 | +0.25 |
| labs (baseline) | +0.74 (n 3) | 0.33 | +0.92 | -0.20 | +0.23 |
| single agents (substrate) | – | – | – | – | +0.49 |

- **R5 (KW, crews, τ = 2 h):** ΔV_st -0.0418 [-0.0654, -0.0178], ΔV_obs -0.0142, I(X₀;Y₀) 0.365 bits, Pinsker envelope ±0.356, η –, members' ΔV_st -0.0144; CK error 0.085, scrambled mass on thin cells 0.16. Day-level landscape: – (n 8).
- **R6a (NE41 forced consolidations, n 242):** own writes +0.59 (z +1.1), other members -0.23 (z -0.7), relative to the 5-min base, rotation null.
- **R8a:** others' write attempts within 30 min after an unconfirmed vs a confirmed push: ratio 0.94 (32 unconfirmed, 69 confirmed push events).
- **Per-unit verdict components:** R4 fail (crews' Stouffer Z -0.94, first vs rooms/labs/reply: False); R5a fail; R6b pass (ΔC +0.26); R4d fail.

### Goal change after this period (NE34, relevance scramble)
- 37->38 (new): 4 crews, V_adv on R_G 0.20 → 0.64 (Δ +0.44 ± 0.14); R_G still written in the next goal's first 2 days for 100% of crews.

## Scorecard (period-specific axes)
- **C** 0–1: no candidate beats its activity-matched random-group null on individuality; allocation continuity beats its permutation null. **E** 0: no unit-level natural scramble inside the period except where noted. **F**: see the card (timing individuality has ≤ 7% power at this sampling).

## Notes
- 2026-10-04: round 2 per the card. Rooms and labs are baseline partitions only; coordination-based candidates (synchrony, co-allocation, reply, crews) were added at Vivian's request before the real-data run (A1.3). A dedicated coordination-first search is left to H58.
