# H141 × G39: shared-goal week #39 (2026-04-27 → 2026-05-01)

**Verdict:** failed
**Role:** exploratory (replication)
**Period:** regime III · shared goal · up to 15 agents · 5 non-reserved days · units 39 (`period_units`).

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
| 39 | 5 | 12 | 2 | 1.38 [0.63, 14.61] | 1.25 [0.40, 3.58] | 0.72 | 1.06 / 0.81 | 0.32 / 0.34 (Δ -0.03 [-0.47, 0.29]) | 0.73 |

- **P1:** ρ_A 1.38 [0.63, 14.61]: the point is not ≥ 10 (inconclusive by A1, but the CI covers isotropy).
- **P2:** percentile 0.72 (rule > 0.95): failed.
- **P3 (V_A′):** 0.81 vs ρ̂ 1.38: within ×2.
- **P5:** variogram contrast -0.03 [-0.47, 0.29]: not supported.

Pool and kill are decided on the card's pool over all 25 units (kill fires: ρ_A 0.68 [0.50, 0.94] bge). A unit's P1 miss is inconclusive (P1 power 0.37, A1); P2 (power 0.84) and P5 (power 0.945) are informative per unit.

## Scorecard (period-specific axes)
C 0 (text plane inside the random-plane band); D 0 (no slowness along E on either clock).

## Notes
- The drive correction uses the cross-agent covariance in the same room and day.
