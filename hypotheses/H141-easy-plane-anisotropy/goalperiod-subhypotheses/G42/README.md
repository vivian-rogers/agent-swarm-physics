# H141 × G42: shared-goal week #42 (2026-05-18 → 2026-05-22)

**Verdict:** failed
**Role:** exploratory (replication)
**Period:** regime III · shared goal · up to 16 agents · 5 non-reserved days · units 42a, 42b (`period_units`).

## Why this period
A regime-III shared-goal unit with ≥ 3 days and ≥ 4 agents, so it enters the replication layer (O1–O4, O6). Its text plane E is the Gram–Schmidt span of the goal text and the kickoff (d_E = 2); the room kickoffs carry the same text here, so they add no axis.

## Prediction
*Copied from the card's replication table on 2026-10-07 (about 12:40 UTC), before running on this period. Seen: no H141 statistic on any period.*
- **P1:** ρ_A(E) ≥ 10 with the lower 90% bound ≥ 3 (credence 0.1). Counts against: the 90% CI inside [⅓, 3] (descriptive for one unit; the pool decides the kill).
- **P2:** ρ_A(E) above the random-plane 95th percentile (credence 0.25).
- **P3:** V_A within ×2 of ρ̂_A (credence 0.3).
- **P5:** P_∥(1) > P_⊥(1) with CI (credence 0.4).

## Result
*Round 1, 2026-10-07 (exploratory, non-reserved days; Amendment A1 estimators). Data: `data/processed/H141-easy-plane-anisotropy/results/` (`units.pkl`, `summary.json`); estimates rows `hypothesis == "H141"`.*

| Unit | days | agents | d_E | ρ_A bge (90% CI) | ρ_A gte (90% CI) | random-plane pct (bge) | V_A / V_A′ (bge) | P_∥(1) / P_⊥(1), variogram (bge) | ρ_A of cross-fitted principal subspace (bge) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 42a | 2 | 13 | 2 | 0.00 [0.00, 829.78] | 1.00 [0.00, 20000.00] | 0.07 | 1.28 / -3.17 | n/a (< 3 days) | 0.01 |
| 42b | 3 | 14 | 2 | 1.45 [0.23, 45.30] | 0.91 [0.26, 4.52] | 0.71 | 0.94 / 0.58 | 0.71 / 0.46 (Δ 0.25 [-0.71, 0.78]) | 4.20 |

- **P1:** 42b ρ_A 1.45 [0.23, 45.30]; 42a (2 days) unresolved: inconclusive.
- **P2:** 42b percentile 0.71: failed.
- **P3 (V_A′):** 42b 0.58 vs ρ̂ 1.45: outside ×2.
- **P5:** 42b variogram contrast 0.25 [-0.71, 0.78]: not supported.

Pool and kill are decided on the card's pool over all 25 units (kill fires: ρ_A 0.68 [0.50, 0.94] bge). A unit's P1 miss is inconclusive (P1 power 0.37, A1); P2 (power 0.84) and P5 (power 0.945) are informative per unit.

## Scorecard (period-specific axes)
C 0; D 0.

## Notes
- The drive correction uses the cross-agent covariance in the same room and day.
