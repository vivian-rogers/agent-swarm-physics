# H135 × G30: Adopt a park and get it cleaned! (2026-02-09 → 02-13)

**Verdict:** n/a
**Role:** exploratory (replication)
**Period:** regime I · mode C · 11 agents · #general · 5 days. Units: `period_units` (30a, 30b).

## Why this period
Replication period in H94's and H129's sets (non-reserved).

## Prediction
*Written 2026-10-07, before running H135 on this period.* **What I had seen:** the card; H94's and H129's latest rounds; this period's structural counts below (hops, co-alive projects, co-alive hops, pairs with ≥ 4 hops). No pair flux, rate ratio, slope or ψ had been computed.
- Card predictions per testable unit-channel: P1 (O1 slope in [0.5, 2], r > 0, p < 0.05), P1b (≥ 1/2 of pairs with ≥ 3 hops each way within ×1.5), P2 (m_π inside the W0 band), P3 (m_2^co inside the W0 band), P4 (ψ CI ∋ 1, ρ CI ∋ 0, LR p ≥ 0.05).
- Structural precondition (card; counted before any outcome): ≥ 60 hops among co-alive pairs and ≥ 8 co-alive pairs with n_ab + n_ba ≥ 4.
- **Declared before any outcome:** no unit-channel of this period passes the precondition under either co-alive rule. Every H135 statistic here is untestable; the period is descriptive (counts only).

**Structural counts** (non-reserved days; `scheme/build.py`). Co-alive = present within the unit's first and last active hour (primary) or for ≥ 80% of its active seconds (variant).

| Unit | Channel | Hops | Projects | Co-alive projects | Co-alive hops | Pairs ≥ 4 | Testable | Co-alive hops (80%) | Pairs ≥ 4 (80%) | Testable (80%) | π model |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 30a | work | 6 | 2 | 2 | 6 | 1 | no | 0 | 0 | no | M2 |
| 30b | work | 26 | 2 | 2 | 26 | 1 | no | 26 | 1 | no | M2 |
| 30a | attention | 19 | 3 | 2 | 18 | 1 | no | 18 | 1 | no | M2 |
| 30b | attention | 127 | 6 | 2 | 73 | 1 | no | 73 | 1 | no | M2 |

## Result
*Run 2026-10-07 (`analysis/run.py`).* No unit-channel passes the structural precondition under either co-alive rule, so no H135 statistic was computed here. Synthetic (A1): even where hops exist, the zero-flux test has power ≤ 0.29 against the age-drift and sink walkers.

O5 (descriptive; shares the occupancy term with π, not a test): 30a attention n 3; 30a work n 2; 30b attention Spearman 0.49; 30b work n 2.

## Scorecard (period-specific axes)
None informed.

## Notes
- 2026-10-07: folder created by the round-1 agent. Data: `data/processed/H135-detailed-balance-potts-walker/G30/`.
