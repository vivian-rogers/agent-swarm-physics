# H135 × G42: Run your own Youtube channel! (2026-05-18 → 05-22)

**Verdict:** pending
**Role:** exploratory (replication)
**Period:** regime III · mode I · 15–16 agents · #best/#rest · 5 days. Units: `period_units` (42a, 42b).

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
| 42a | work | 2 | 10 | 6 | 0 | 0 | no | 0 | 0 | no | M3 |
| 42b | work | 10 | 10 | 3 | 0 | 0 | no | 3 | 0 | no | M3 |
| 42a | attention | 22 | 15 | 11 | 2 | 0 | no | 5 | 0 | no | M3 |
| 42b | attention | 26 | 15 | 8 | 5 | 0 | no | 16 | 1 | no | M3 |

## Result
Not run.

## Notes
- 2026-10-07: folder created by the round-1 agent. Data: `data/processed/H135-detailed-balance-potts-walker/G42/`.
