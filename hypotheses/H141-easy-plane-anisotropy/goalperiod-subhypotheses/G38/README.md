# H141 × G38: the long shared week with room-specific kickoffs (#38, 2026-04-02 → 2026-04-27)

**Verdict:** failed
**Role:** exploratory (replication + native N1)
**Period:** regime III · mode C · 12 agents · two rooms (#best / #rest) with room-specific kickoffs · 17 days. Units from `period_units`. Operator mover at the goal start (Sonnet 4.6, 04-02; H100).

## Why this period
The text plane has four axes here (goal text, kickoff, two room kickoffs), and 17 days give the day-scale test (O3) many lags. H108 measured the data room direction: P(1) 0.95, P(ℓ) ≈ 0.85 out to six days. H100 found the room-kickoff text directions carry a chance share of the room separation (0.18 vs null 0.16). So #38 separates "a text axis" from "a slow axis".

## Prediction
*Written 2026-10-07 ~11:40 UTC, before running on this period. Seen: H108's and H100's #38 numbers above; no projection on the text plane.*
- **P1 (replication):** ρ_A(E) ≥ 10, lower 90% bound ≥ 3. Credence 0.1.
- **N1 (native):** the room-kickoff difference axis alone is below the random-plane 90th percentile of ρ_A (R-text-room), while the cross-fitted data room direction m̂ is above the 95th percentile with ρ_A(m̂) ≥ 3. Credence 0.45.
- **P5 (day scale):** P_∥(1) > P_⊥(1) with CI. Credence 0.4.
- Counts against: ρ_A(E) 90% CI inside [⅓, 3] (kill on this unit, descriptive; the pool decides).

## Result
*Round 1, 2026-10-07 (exploratory, non-reserved days; Amendment A1 estimators). Data: `data/processed/H141-easy-plane-anisotropy/results/` (`units.pkl`, `summary.json`); estimates rows `hypothesis == "H141"`.*

| Unit | days | agents | d_E | ρ_A bge (90% CI) | ρ_A gte (90% CI) | random-plane pct (bge) | V_A / V_A′ (bge) | P_∥(1) / P_⊥(1), variogram (bge) | ρ_A of cross-fitted principal subspace (bge) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 38a | 8 | 11 | 4 | 0.93 [0.00, 2.62] | 0.63 [0.23, 1.61] | 0.48 | 1.16 / 0.72 | 0.46 / 0.48 (Δ -0.01 [-0.23, 0.13]) | 1.07 |
| 38b | 3 | 11 | 4 | 84.80 [0.00, 193.27] | 1.03 [0.01, 8.82] | 0.96 | 1.30 / 0.82 | 0.49 / -0.00 (Δ 0.49 [-0.10, 0.88]) | 0.01 |
| 38c | 1 | 12 | 4 | 0.80 [0.00, 3.57] | 0.32 [0.16, 202.23] | 0.41 | 1.29 / -1.60 | n/a (< 3 days) | — |
| 38d | 2 | 12 | 4 | 1.21 [0.37, 11.33] | 1.46 [0.40, 4.58] | 0.52 | 1.14 / 0.98 | n/a (< 3 days) | 1.08 |
| 38e | 3 | 13 | 4 | 0.72 [0.32, 67.03] | 1.53 [0.05, 219.50] | 0.39 | 1.24 / 0.70 | 0.57 / 0.38 (Δ 0.19 [-0.14, 0.47]) | 0.33 |

- **P1:** 38a ρ_A 0.93 [0.00, 2.62]; no unit ≥ 10 with a bounded CI; inconclusive per unit (A1).
- **P2:** percentile > 0.95 only in 38b (0.96, with γ_∥ at the slow fit edge; gte 0.47): 1/3 testable units.
- **P5:** no unit with P_∥ > P_⊥ (CI); 38a variogram −0.01 [−0.23, 0.13].
- **N1 (native, rule units 38a, 38b, 38e):** the text room axis is below the random 90th percentile in 3/3 units in every variant (first clause holds: R-text-room). The cross-fitted data room direction m̂ is above the 95th percentile with ρ_A ≥ 3 in 0/3 units in every variant (second clause fails; best: 38a gte ρ 24 at pct 0.935). **N1 fails**: on the call clock neither room axis is slow.

| Unit | text room axis ρ_A (pct) bge | data room axis m̂ ρ_A (pct) bge | text room axis gte | m̂ gte |
| --- | --- | --- | --- | --- |
| 38a | 1.05 (0.62) | 0.93 (0.59) | 0.34 (0.23) | 24.24 (0.94) |
| 38b | 0.10 (0.27) | 5.81 (0.76) | 0.20 (0.38) | 0.03 (0.24) |
| 38c | 0.01 (0.03) | 0.36 (0.26) | 2.53 (0.67) | 0.31 (0.29) |
| 38d | 0.01 (0.02) | 4.89 (0.79) | 0.27 (0.26) | 1.46 (0.69) |
| 38e | 0.74 (0.55) | 0.32 (0.30) | 3.62 (0.83) | 0.99 (0.54) |

N1 compares call-clock memory. H108's day-scale persistence of m̂ (P(1) 0.95) is a different object: a room split that is static within a day probably enters the plateau B of the call-clock fit, not γ.

Pool and kill are decided on the card's pool over all 25 units (kill fires: ρ_A 0.68 [0.50, 0.94] bge). A unit's P1 miss is inconclusive (P1 power 0.37, A1); P2 (power 0.84) and P5 (power 0.945) are informative per unit.

## Scorecard (period-specific axes)
C 0 (text plane inside the random band); D 0; G 1 (the room-kickoff text axis is not where content is slow, as H100 found for the room split); H 1 (R-text-room's first clause holds; its m̂ clause fails).

## Notes
- The drive correction is done within each room (cross-agent covariance among the agent's room-mates).
