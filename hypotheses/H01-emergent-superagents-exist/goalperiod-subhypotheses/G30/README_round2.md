# H01 × G30, round 2: effective superagents (Kolchinsky–Wolpert) on a substrate of agents

**Verdict:** failed
**Role:** exploratory
**Period:** round 2 units 30 · regime I · 5 non-holdout days · 10 writers · 516 strict write events

## Why this period
It has a work ledger (strict git/deploy write events on shared projects), so candidate units (crews, synchrony and co-allocation communities, reply communities, with rooms and labs as baselines) and their viability (artifact advancement) can be measured. See the card's "Round 2 formal setup".

## Prediction
*Written 2026-10-04 on the main card ("Round 2 predictions" and Amendment A1), before any real-data run of R4–R8; no period-specific variant.* R4: crews are individuality maxima (composition excess > 0, first among coarse-grainings, local maxima). R5: positive KW stored and observed semantic information for crews, above the members'. R6: one-member scrambles are cheap, crews persist overnight (ΔC ≥ 0.2), coordination excess > 0. R7: departures cost no more than the departed share. R8: others respond to a member's failed write. Per-unit verdict rule in `analysis/r2_period_folders.py`.

## Result
Data: `data/processed/H01-emergent-superagents-exist/round2/G30/results.json`; pipeline `analysis/r2_run.py`; figures `figures/r2_summary_obs.pdf`, `figures/r2_kw.pdf`.

### Unit 30
- **Candidate units:** 3 crews (sizes [3, 7, 10]), 3 synchrony and 2 co-allocation communities, 1 reply communities, 0 rooms, 3 labs.

| coarse-graining | R4 median z (vs random groups) | local maxima | iota_alloc z | shift z | R4d ΔC overnight (leave-out) |
| --- | --- | --- | --- | --- | --- |
| crews (joint work on one artifact) | -0.25 (n 2) | 0.00 | -0.80 | +0.78 | +0.09 |
| behavior-state synchrony | +0.78 (n 1) | 0.00 | +0.09 | -0.43 | +0.02 |
| co-allocation (co-adoption) | -0.40 (n 2) | 0.00 | +0.02 | -0.39 | +0.08 |
| reply communities | – (n 0) | – | – | +1.48 | +0.04 |
| rooms (baseline) | – (n 0) | – | – | – | – |
| labs (baseline) | +0.69 (n 1) | 0.00 | -0.08 | +0.31 | +0.03 |
| single agents (substrate) | – | – | – | – | -0.15 |

- **R5 (KW, crews, τ = 2 h):** ΔV_st +0.0014 [-0.0008, +0.0077], ΔV_obs -0.0013, I(X₀;Y₀) 0.070 bits, Pinsker envelope ±0.156, η 0.17, members' ΔV_st +0.0006; CK error 0.074, scrambled mass on thin cells 0.06. Day-level landscape: – (n 12).
- **R8a:** others' write attempts within 30 min after an unconfirmed vs a confirmed push: ratio 1.03 (165 unconfirmed, 325 confirmed push events).
- **Per-unit verdict components:** R4 fail (crews' Stouffer Z -0.36, first vs rooms/labs/reply: False); R5a fail; R6b fail (ΔC +0.09); R4d pass.

### Goal change after this period (NE34, relevance scramble)
- 30->31 (new): 3 crews, V_adv on R_G 0.86 → 0.78 (Δ -0.08 ± 0.04); R_G still written in the next goal's first 2 days for 100% of crews.

## Scorecard (period-specific axes)
- **C** 0–1: no candidate beats its activity-matched random-group null on individuality; allocation continuity beats its permutation null. **E** 0: no unit-level natural scramble inside the period except where noted. **F**: see the card (timing individuality has ≤ 7% power at this sampling).

## Notes
- 2026-10-04: round 2 per the card. Rooms and labs are baseline partitions only; coordination-based candidates (synchrony, co-allocation, reply, crews) were added at Vivian's request before the real-data run (A1.3). A dedicated coordination-first search is left to H58.
