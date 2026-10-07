# H135 × G40: Connect your worlds into a 3D universe! (2026-05-04 → 05-08)

**Verdict:** descriptive
**Role:** exploratory (replication + native N3)
**Period:** regime III · mode C · 15 agents · #universe-coordination (NE42 merge) · 5 days. Units: `period_units` (40).

## Why this period
Native N3: NE42 merge. A named hub took 73% of the work quanta (H94). The flux into the hub on the first two active days should be one-way (R-sink); later co-alive pairs should balance.

## Prediction
*Written 2026-10-07, before running H135 on this period.* **What I had seen:** the card; H94's and H129's latest rounds; this period's structural counts below (hops, co-alive projects, co-alive hops, pairs with ≥ 4 hops). No pair flux, rate ratio, slope or ψ had been computed.
- Card predictions per testable unit-channel: P1 (O1 slope in [0.5, 2], r > 0, p < 0.05), P1b (≥ 1/2 of pairs with ≥ 3 hops each way within ×1.5), P2 (m_π inside the W0 band), P3 (m_2^co inside the W0 band), P4 (ψ CI ∋ 1, ρ CI ∋ 0, LR p ≥ 0.05).
- Structural precondition (card; counted before any outcome): ≥ 60 hops among co-alive pairs and ≥ 8 co-alive pairs with n_ab + n_ba ≥ 4.
- **Declared before any outcome:** no unit-channel of this period passes the precondition under either co-alive rule. Every H135 statistic here is untestable; the period is descriptive (counts only).
- Native N3 (credence 0.5): the net flux into the hub (the top-π repo, quanta share 0.73, kickoff-named in H94) on the first two active days, m_hub = (in − out)/(in + out), lies above the W0 band (97.5th percentile of 200 heat-bath runs on the G40 skeleton). Later days: co-alive pairs inside the band. The later-day part is untestable (co-alive hops 7 work, 5 attention; below the precondition).
- **Disclosure (2026-10-07):** while counting hub hops for N3's testability, I printed the in/out split on days 1–2 (work 5 in / 5 out; attention 12 / 11) and on later days (work 3 / 2; attention 7 / 6) before writing this prediction and before the W0 band existed. The prediction above is the card's, unchanged; N3's result is marked as seen before the band.

**Structural counts** (non-reserved days; `scheme/build.py`). Co-alive = present within the unit's first and last active hour (primary) or for ≥ 80% of its active seconds (variant).

| Unit | Channel | Hops | Projects | Co-alive projects | Co-alive hops | Pairs ≥ 4 | Testable | Co-alive hops (80%) | Pairs ≥ 4 (80%) | Testable (80%) | π model |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 40 | work | 15 | 9 | 3 | 7 | 1 | no | 7 | 1 | no | M2 |
| 40 | attention | 50 | 12 | 2 | 5 | 1 | no | 32 | 4 | no | M3 |

## Result
*Run 2026-10-07 (`analysis/run.py`, synthetic on the G40 skeleton, 200 runs per world).* Hub = the top-π repo (quanta share 0.73).

| Test | Observed | W0 band (2.5–97.5%) | Power (sink W2 beyond the band) | Verdict |
| --- | --- | --- | --- | --- |
| N3 hub flux days 1–2, work | 0.00 (5 in / 5 out) | [0.20, 1.00] | 0/200 | descriptive (below the band) |
| N3 hub flux days 1–2, attention | 0.04 (12 / 11) | [-0.00, 0.29] | 0/200 | descriptive (inside) |
| N3 later days, co-alive pairs | — | — | — | untestable (7 / 5 co-alive hops) |

No excess flux into the hub: as many agents left it as entered it on days 1–2. The test is unpowered (Amendment A1): a heat-bath walker that starts agents on their own worlds already gives a positive hub flux (W0 median 0.33 work, 0.09 attention), and the sink walker gives less, not more. The in/out counts were seen before the band (disclosed above).

O5 (descriptive; shares the occupancy term with π, not a test): 40 attention Spearman 0.96; 40 work Spearman 0.93.

## Scorecard (period-specific axes)
- E: 0 (unpowered).

## Notes
- 2026-10-07: folder created by the round-1 agent. Data: `data/processed/H135-detailed-balance-potts-walker/G40/`.
