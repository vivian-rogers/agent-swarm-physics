# H135 × G36: Interact with other AI agents outside the Village! (2026-03-23 → 03-27)

**Verdict:** pending
**Role:** exploratory (replication)
**Period:** regime II→III · mode C · 12 agents · #best/#rest · 5 days. Units: `period_units` (36a, 36b, 36c).

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
| 36a | work | 8 | 8 | 2 | 4 | 1 | no | 4 | 1 | no | M3 |
| 36b | work | 12 | 5 | 2 | 6 | 1 | no | 6 | 1 | no | M3 |
| 36c | work | 25 | 11 | 2 | 1 | 0 | no | 1 | 0 | no | M3 |
| 36a | attention | 41 | 17 | 3 | 19 | 2 | no | 19 | 2 | no | M3 |
| 36b | attention | 62 | 25 | 4 | 21 | 1 | no | 21 | 1 | no | M3 |
| 36c | attention | 89 | 18 | 3 | 4 | 1 | no | 24 | 2 | no | M3 |

## Result
Not run.

## Notes
- 2026-10-07: folder created by the round-1 agent. Data: `data/processed/H135-detailed-balance-potts-walker/G36/`.
