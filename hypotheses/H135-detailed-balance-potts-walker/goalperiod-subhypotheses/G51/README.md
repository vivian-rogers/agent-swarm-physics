# H135 × G51: Each agent: Maximize your assigned goal! (2026-07-06 → 09-04 (non-reserved; tail reserved))

**Verdict:** mixed
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
*Run 2026-10-07 (`analysis/run.py`; 80% co-alive variant; attention channel).* Pair-bootstrap 95% CIs; ψ, ρ Wald CIs; W0 bands from 200 heat-bath runs on each unit's skeleton; LR p calibrated on 100 W0 runs (Amendment A1).

| Unit | Hops / co-alive | O1 slope (identity) | m_π; W0 band | m_2^co; W0 band | ψ | ρ | LR p (cal.) | Reading |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 51a | 243 / 134 | 1.58 [0.93, 2.68] | 0.015 [-0.11, 0.15]; band [-0.06, 0.09] | -0.015 [-0.13, 0.11]; band [-0.05, 0.09] | 0.49 [0.41, 0.58] | 1.21 [0.87, 1.55] | 0.01 | P2 in, P3 in, P4 fails |
| 51c | 355 / 126 | 1.37 [0.56, 3.76] | -0.042 [-0.20, 0.09]; band [-0.05, 0.09] | 0.095 [-0.03, 0.23]; band [-0.06, 0.08] | 0.50 [0.43, 0.57] | 1.18 [0.88, 1.48] | 0.01 | P2 in, P3 above, P4 fails |
| 51f | 418 / 175 | 1.60 [1.03, 2.31] | -0.029 [-0.11, 0.04]; band [-0.04, 0.08] | 0.006 [-0.07, 0.09]; band [-0.07, 0.05] | 0.39 [0.33, 0.45] | 2.21 [1.94, 2.48] | 0.01 | P2 in, P3 in, P4 fails |
| 51g | 1040 / 406 | 1.11 [0.96, 1.33] | -0.005 [-0.06, 0.05]; band [-0.03, 0.05] | -0.044 [-0.10, 0.01]; band [-0.04, 0.05] | 0.44 [0.40, 0.47] | 2.35 [2.19, 2.51] | 0.01 | P2 in, P3 in, P4 fails |
| 51h | 321 / 156 | 1.37 [0.99, 2.07] | 0.051 [-0.03, 0.16]; band [-0.05, 0.07] | 0.026 [-0.05, 0.13]; band [-0.07, 0.06] | 0.43 [0.36, 0.50] | 2.56 [2.22, 2.90] | 0.01 | P2 in, P3 in, P4 fails |

- Zero flux (P2, P3) holds as written in 5/5 and 4/5, but the test is unpowered (power ≤ 0.29 against the age-drift and sink walkers; A1).
- Heat-bath destinations (P4) fail in 5/5: agents' destinations respond to π_i with ψ ≈ 0.44 of the heat-bath exponent, and they return to projects they held (ρ 1.2–2.6 nats).
- Work channel and the other seven units: untestable.
- Verdict "mixed": the powered test (P4) fails; the zero-flux predictions hold only as unpowered descriptions.

O5 (descriptive; shares the occupancy term with π, not a test): 51a attention Spearman 0.95; 51a work Spearman 0.84; 51b attention Spearman 0.59; 51b work Spearman 0.43; 51c attention Spearman 0.92; 51c work Spearman 0.60; 51d attention Spearman 0.92; 51d work Spearman 0.80; 51e attention Spearman 0.96; 51e work Spearman 0.64; 51f attention Spearman 0.86; 51f work Spearman 0.86; 51g attention Spearman 0.85; 51g work Spearman 0.93; 51h attention Spearman 0.92; 51h work Spearman 0.84; 51i attention Spearman 0.87; 51i work Spearman 0.63; 51j attention Spearman 0.88; 51j work Spearman 0.51; 51k attention Spearman 0.84; 51k work Spearman 0.55; 51l attention Spearman 0.88; 51l work Spearman 0.48.

## Scorecard (period-specific axes)
- C: 0 (heat-bath destination law rejected 5/5). F: 1 (O4 valid on these skeletons; flux unpowered). H: 1 (R-habit beats heat-bath).

## Notes
- 2026-10-07: folder created by the round-1 agent. Data: `data/processed/H135-detailed-balance-potts-walker/G51/`.
