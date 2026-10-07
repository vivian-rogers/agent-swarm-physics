# H135 × G44: Finetune your leader! (2026-05-26 → 05-29)

**Verdict:** pending
**Role:** exploratory (replication + native N2)
**Period:** regime III · mode C · 17–18 agents · #best (named leader) / #rest (free) · 4 days. Units: `period_units` (44a, 44b).

## Why this period
Native N2: #best works to an assigned target (H129: hop graph a tree; H94: λ_own 10.2) and #rest chooses freely (λ_own 4.1), on the same days. An assigned field should give a one-way flux in #best.

## Prediction
*Written 2026-10-07, before running H135 on this period.* **What I had seen:** the card; H94's and H129's latest rounds; this period's structural counts below (hops, co-alive projects, co-alive hops, pairs with ≥ 4 hops). No pair flux, rate ratio, slope or ψ had been computed.
- Card predictions per testable unit-channel: P1 (O1 slope in [0.5, 2], r > 0, p < 0.05), P1b (≥ 1/2 of pairs with ≥ 3 hops each way within ×1.5), P2 (m_π inside the W0 band), P3 (m_2^co inside the W0 band), P4 (ψ CI ∋ 1, ρ CI ∋ 0, LR p ≥ 0.05).
- Structural precondition (card; counted before any outcome): ≥ 60 hops among co-alive pairs and ≥ 8 co-alive pairs with n_ab + n_ba ≥ 4.
- **Declared before any outcome:** no unit-channel of this period passes the precondition under either co-alive rule. Every H135 statistic here is untestable; the period is descriptive (counts only).
- Native N2 (credence 0.35): #best m_π > 0 beyond its W0 band; #rest inside its band. **Untestable**: no 44 unit-channel passes the precondition under either rule, so a room split has fewer co-alive hops still. Declared before any outcome.

**Structural counts** (non-reserved days; `scheme/build.py`). Co-alive = present within the unit's first and last active hour (primary) or for ≥ 80% of its active seconds (variant).

| Unit | Channel | Hops | Projects | Co-alive projects | Co-alive hops | Pairs ≥ 4 | Testable | Co-alive hops (80%) | Pairs ≥ 4 (80%) | Testable (80%) | π model |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 44a | work | 28 | 27 | 8 | 0 | 0 | no | 3 | 0 | no | M3 |
| 44b | work | 29 | 23 | 1 | 0 | 0 | no | 1 | 0 | no | M3 |
| 44a | attention | 90 | 36 | 9 | 19 | 2 | no | 31 | 3 | no | M3 |
| 44b | attention | 61 | 29 | 8 | 10 | 1 | no | 10 | 1 | no | M3 |

## Result
Not run.

## Notes
- 2026-10-07: folder created by the round-1 agent. Data: `data/processed/H135-detailed-balance-potts-walker/G44/`.
