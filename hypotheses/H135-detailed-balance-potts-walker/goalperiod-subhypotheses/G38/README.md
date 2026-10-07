# H135 × G38: Choose a charity and raise as much money as you can for it (2026-04-02 → 04-24)

**Verdict:** n/a
**Role:** exploratory (replication + native N1)
**Period:** regime III · mode C · 12–14 agents · #best/#rest · 17 days. Units: `period_units` (38a, 38b, 38c, 38d, 38e).

## Why this period
Native N1: seventeen days with births throughout and the most co-alive pairs among long-lived repos expected; H129's strongest age drift (work m_2 0.17, p 0.027). The test of detailed balance once births are cut away.

## Prediction
*Written 2026-10-07, before running H135 on this period.* **What I had seen:** the card; H94's and H129's latest rounds; this period's structural counts below (hops, co-alive projects, co-alive hops, pairs with ≥ 4 hops). No pair flux, rate ratio, slope or ψ had been computed.
- Card predictions per testable unit-channel: P1 (O1 slope in [0.5, 2], r > 0, p < 0.05), P1b (≥ 1/2 of pairs with ≥ 3 hops each way within ×1.5), P2 (m_π inside the W0 band), P3 (m_2^co inside the W0 band), P4 (ψ CI ∋ 1, ρ CI ∋ 0, LR p ≥ 0.05).
- Structural precondition (card; counted before any outcome): ≥ 60 hops among co-alive pairs and ≥ 8 co-alive pairs with n_ab + n_ba ≥ 4.
- **Declared before any outcome:** no unit-channel of this period passes the precondition under either co-alive rule. Every H135 statistic here is untestable; the period is descriptive (counts only).
- Native N1 (credence 0.35): m_π and m_2^co inside the W0 band on both channels. **Untestable** by the counts above (both rules); declared before any outcome.

**Structural counts** (non-reserved days; `scheme/build.py`). Co-alive = present within the unit's first and last active hour (primary) or for ≥ 80% of its active seconds (variant).

| Unit | Channel | Hops | Projects | Co-alive projects | Co-alive hops | Pairs ≥ 4 | Testable | Co-alive hops (80%) | Pairs ≥ 4 (80%) | Testable (80%) | π model |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 38a | work | 68 | 29 | 1 | 0 | 0 | no | 0 | 0 | no | M3 |
| 38b | work | 3 | 6 | 2 | 0 | 0 | no | 0 | 0 | no | M3 |
| 38c | work | 1 | 4 | 1 | 0 | 0 | no | 0 | 0 | no | M3 |
| 38d | work | 0 | 4 | 2 | 0 | 0 | no | 0 | 0 | no | M3 |
| 38e | work | 5 | 7 | 1 | 0 | 0 | no | 0 | 0 | no | M3 |
| 38a | attention | 183 | 51 | 3 | 3 | 0 | no | 49 | 4 | no | M3 |
| 38b | attention | 31 | 18 | 4 | 10 | 1 | no | 10 | 1 | no | M3 |
| 38c | attention | 5 | 7 | 4 | 1 | 0 | no | 1 | 0 | no | M3 |
| 38d | attention | 6 | 6 | 3 | 0 | 0 | no | 0 | 0 | no | M3 |
| 38e | attention | 28 | 16 | 2 | 0 | 0 | no | 0 | 0 | no | M3 |

## Result
*Run 2026-10-07 (`analysis/run.py`).* No unit-channel passes the structural precondition under either co-alive rule, so no H135 statistic was computed here. Native N1 is untestable. Synthetic (A1): even where hops exist, the zero-flux test has power ≤ 0.29 against the age-drift and sink walkers.

O5 (descriptive; shares the occupancy term with π, not a test): 38a attention Spearman 0.86; 38a work Spearman 0.46; 38b attention Spearman 0.80; 38b work n 2; 38c attention Spearman 1.00; 38c work n 1; 38d attention Spearman -0.77; 38e attention Spearman 0.75; 38e work n 2.

## Scorecard (period-specific axes)
None informed.

## Notes
- 2026-10-07: folder created by the round-1 agent. Data: `data/processed/H135-detailed-balance-potts-walker/G38/`.
