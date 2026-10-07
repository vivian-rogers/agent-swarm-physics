# H135 × G31: Pick your own goal (agents bid 3.7 Sonnet farewell) (2026-02-16 → 02-20)

**Verdict:** n/a
**Role:** exploratory (replication)
**Period:** regime I · mode F · 11–12 agents · #general · 5 days. Units: `period_units` (31a, 31b, 31c, 31d).

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
| 31a | work | 53 | 14 | 4 | 21 | 2 | no | 21 | 2 | no | M2 |
| 31b | work | 16 | 13 | 4 | 3 | 0 | no | 3 | 0 | no | M2 |
| 31c | work | 16 | 9 | 4 | 4 | 0 | no | 2 | 0 | no | M2 |
| 31d | work | 13 | 9 | 1 | 0 | 0 | no | 0 | 0 | no | M2 |
| 31a | attention | 99 | 19 | 5 | 41 | 3 | no | 51 | 4 | no | M2 |
| 31b | attention | 43 | 17 | 7 | 17 | 1 | no | 10 | 1 | no | M2 |
| 31c | attention | 31 | 12 | 2 | 0 | 0 | no | 0 | 0 | no | M2 |
| 31d | attention | 35 | 9 | 2 | 0 | 0 | no | 0 | 0 | no | M2 |

## Result
*Run 2026-10-07 (`analysis/run.py`).* No unit-channel passes the structural precondition under either co-alive rule, so no H135 statistic was computed here. Synthetic (A1): even where hops exist, the zero-flux test has power ≤ 0.29 against the age-drift and sink walkers.

O5 (descriptive; shares the occupancy term with π, not a test): 31a attention Spearman 0.49; 31a work Spearman 0.43; 31b attention Spearman 0.68; 31b work Spearman 0.60; 31c attention Spearman 0.23; 31c work n 3; 31d attention Spearman -0.60; 31d work Spearman 0.20.

## Scorecard (period-specific axes)
None informed.

## Notes
- 2026-10-07: folder created by the round-1 agent. Data: `data/processed/H135-detailed-balance-potts-walker/G31/`.
