# H141 × G44: two rooms with different kickoffs (#44, 2026-05-26 → 2026-06-01)

**Verdict:** descriptive
**Role:** exploratory (replication + native N1)
**Period:** regime III · mode C · 16 agents · two rooms (#best planned, #rest free) with room-specific kickoffs · 4 days. Operator mover at the goal start (Gemini 3.1 Pro; H100). The fine-tuned leader (NE31) is present.

## Why this period
The second period with room-specific kickoffs. H108: P(1) 0.78 [0.67, 0.81]; H100: room-kickoff field share 0.08 vs null 0.03 (p 0.088). Four days limit the day-scale test.

## Prediction
*Written 2026-10-07 ~11:40 UTC, before running on this period. Seen: H108's and H100's #44 numbers above; no projection on the text plane.*
- **P1:** ρ_A(E) ≥ 10, lower 90% bound ≥ 3. Credence 0.1.
- **N1:** as in G38: text room axis below the random 90th percentile; cross-fitted m̂ above the 95th percentile with ρ_A(m̂) ≥ 3. Credence 0.35 (shorter week).
- Counts against: ρ_A(E) 90% CI inside [⅓, 3].

## Result
*Round 1, 2026-10-07 (exploratory, non-reserved days; Amendment A1 estimators). Data: `data/processed/H141-easy-plane-anisotropy/results/` (`units.pkl`, `summary.json`); estimates rows `hypothesis == "H141"`.*

| Unit | days | agents | d_E | ρ_A bge (90% CI) | ρ_A gte (90% CI) | random-plane pct (bge) | V_A / V_A′ (bge) | P_∥(1) / P_⊥(1), variogram (bge) | ρ_A of cross-fitted principal subspace (bge) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 44a | 2 | 13 | 3 | 0.19 [0.06, 142.70] | 1.48 [0.01, 310.85] | 0.14 | 1.06 / 1.10 | n/a (< 3 days) | 0.19 |
| 44b | 2 | 16 | 3 | 0.49 [0.01, 148.48] | 189.69 [0.01, 228.77] | 0.24 | 0.97 / 0.24 | n/a (< 3 days) | 126.84 |

Both units have 2 days, so no unit is testable (A1 rule: ≥ 3 days); d_E = 3 (A1 point 5).
- **P1:** 44a ρ_A 0.19 [0.06, 143]; 44b 0.49 [0.01, 148]: unresolved.
- **N1 (descriptive):** text room axis below the 90th percentile in 2/2 units (bge 0.86, 0.50; gte 0.63, 0.14); m̂ above the 95th percentile in 0/2.
- O3 needs ≥ 3 days per unit: not computed.

Pool and kill are decided on the card's pool over all 25 units (kill fires: ρ_A 0.68 [0.50, 0.94] bge). A unit's P1 miss is inconclusive (P1 power 0.37, A1); P2 (power 0.84) and P5 (power 0.945) are informative per unit.

## Scorecard (period-specific axes)
C, D: descriptive only (0).

## Notes
- With 4 days, O3 (day-to-day persistence) has at most 3 lag-1 pairs per agent; it is descriptive here.
