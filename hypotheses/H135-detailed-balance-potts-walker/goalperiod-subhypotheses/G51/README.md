# H135 × G51: Each agent: Maximize your assigned goal! (2026-07-06 → 09-04 (non-reserved; tail reserved))

**Verdict:** pending
**Role:** exploratory (replication)
**Period:** regime III · mode P · 21–32 agents · #general (+#focus in 51g) · 45 days. Units: `period_units` (51a, 51b, 51c, 51d, 51e, 51f, 51g, 51h, 51i, 51j, 51k, 51l).

## Why this period
Own-role private goals, twelve non-reserved units (51a–51l), the most hops of any period. The units are fitted separately.

## Prediction
*Written 2026-10-07, before running H135 on this period.* **What I had seen:** the card; H94's and H129's latest rounds; this period's structural counts below (hops, co-alive projects, co-alive hops, pairs with ≥ 4 hops). No pair flux, rate ratio, slope or ψ had been computed.
- Card predictions per testable unit-channel: P1 (O1 slope in [0.5, 2], r > 0, p < 0.05), P1b (≥ 1/2 of pairs with ≥ 3 hops each way within ×1.5), P2 (m_π inside the W0 band), P3 (m_2^co inside the W0 band), P4 (ψ CI ∋ 1, ρ CI ∋ 0, LR p ≥ 0.05).
- Structural precondition (card; counted before any outcome): ≥ 60 hops among co-alive pairs and ≥ 8 co-alive pairs with n_ab + n_ba ≥ 4.
- **Declared before any outcome:** no unit-channel passes under the primary co-alive rule. Under the card's 80% variant, 51a|attention, 51c|attention, 51f|attention, 51g|attention, 51h|attention pass. These are run with the variant rule only. My expectation there: m_π and m_2^co inside the W0 band (P2, P3; credence 0.4 each), O1 passes (fact 1), ψ < 1 with ρ > 0 (habit; P4 credence 0.2).

**Structural counts** (non-reserved days; `scheme/build.py`). Co-alive = present within the unit's first and last active hour (primary) or for ≥ 80% of its active seconds (variant).

| Unit | Channel | Hops | Projects | Co-alive projects | Co-alive hops | Pairs ≥ 4 | Testable | Co-alive hops (80%) | Pairs ≥ 4 (80%) | Testable (80%) | π model |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 51a | work | 57 | 28 | 9 | 10 | 1 | no | 10 | 1 | no | M2 |
| 51b | work | 15 | 19 | 1 | 0 | 0 | no | 0 | 0 | no | M2 |
| 51c | work | 59 | 30 | 6 | 2 | 0 | no | 2 | 0 | no | M2 |
| 51d | work | 71 | 26 | 2 | 0 | 0 | no | 21 | 1 | no | M2 |
| 51e | work | 39 | 24 | 1 | 0 | 0 | no | 0 | 0 | no | M2 |
| 51f | work | 108 | 34 | 4 | 21 | 1 | no | 58 | 5 | no | M2 |
| 51g | work | 355 | 59 | 1 | 0 | 0 | no | 118 | 7 | no | M3 |
| 51h | work | 59 | 28 | 2 | 0 | 0 | no | 11 | 1 | no | M2 |
| 51i | work | 34 | 27 | 5 | 0 | 0 | no | 1 | 0 | no | M2 |
| 51j | work | 31 | 27 | 2 | 0 | 0 | no | 1 | 0 | no | M2 |
| 51k | work | 7 | 12 | 0 | 0 | 0 | no | 0 | 0 | no | M2 |
| 51l | work | 10 | 14 | 2 | 0 | 0 | no | 0 | 0 | no | M2 |
| 51a | attention | 243 | 53 | 9 | 39 | 4 | no | 134 | 12 | yes | M2 |
| 51b | attention | 72 | 41 | 13 | 11 | 0 | no | 11 | 0 | no | M2 |
| 51c | attention | 355 | 95 | 12 | 27 | 1 | no | 126 | 12 | yes | M2 |
| 51d | attention | 336 | 69 | 12 | 21 | 2 | no | 105 | 5 | no | M2 |
| 51e | attention | 273 | 58 | 11 | 7 | 0 | no | 82 | 5 | no | M2 |
| 51f | attention | 418 | 75 | 13 | 54 | 4 | no | 175 | 13 | yes | M2 |
| 51g | attention | 1040 | 146 | 11 | 86 | 6 | no | 406 | 27 | yes | M3 |
| 51h | attention | 321 | 67 | 16 | 72 | 5 | no | 156 | 10 | yes | M2 |
| 51i | attention | 120 | 49 | 13 | 27 | 3 | no | 40 | 4 | no | M2 |
| 51j | attention | 130 | 50 | 14 | 25 | 1 | no | 51 | 4 | no | M2 |
| 51k | attention | 82 | 40 | 15 | 17 | 2 | no | 25 | 3 | no | M2 |
| 51l | attention | 99 | 44 | 19 | 40 | 3 | no | 32 | 2 | no | M2 |

## Result
Not run.

## Notes
- 2026-10-07: folder created by the round-1 agent. Data: `data/processed/H135-detailed-balance-potts-walker/G51/`.
