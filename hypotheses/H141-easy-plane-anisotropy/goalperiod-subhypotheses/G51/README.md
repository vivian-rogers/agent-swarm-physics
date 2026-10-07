# H141 × G51: one plane per agent (#51 main body, units 51a–51l)

**Verdict:** failed
**Role:** exploratory (replication over 12 units + native N2)
**Period:** regime III · mode I/K (private roles) · up to 21 agents · #general (and #focus from 08-05) · non-reserved days 2026-07-06 → 2026-09-04. The tail (2026-09-07 → 09-21) is reserved and not used.

## Why this period
Each agent has its own goal text (DQ6 roles; `agent_goal` vectors), so each agent has its own text plane: the field differs by agent in the same room and days. H54 found agents sit on their own goal (role-swap accuracy 0.95). H130 measured the full-space own memory here (≈ 100 calls), which sets the scale for the along-plane test.

## Prediction
*Written 2026-10-07 ~11:40 UTC, before running on this period. Seen: H54's and H130's #51 numbers; no projection on any agent's plane.*
- **N2 (native):** pooled over agents and units, ρ_A of the own plane ≥ 3 and above the random-plane 95th percentile. Credence 0.25.
- **Cross-agent control:** the plane of another agent's goal (a swap, as H54's swap null) is not slower than random for the focal agent. Credence 0.6.
- **P4 (kick):** the across-plane kick coefficient at lag 1 is ≤ ¼ of lag 0. Credence 0.2.
- Counts against: pooled ρ_A 90% CI inside [⅓, 3].

## Result
*Round 1, 2026-10-07 (exploratory, non-reserved days; Amendment A1 estimators). Data: `data/processed/H141-easy-plane-anisotropy/results/` (`units.pkl`, `summary.json`); estimates rows `hypothesis == "H141"`.*

| Unit | days | agents | d_E | ρ_A bge (90% CI) | ρ_A gte (90% CI) | random-plane pct (bge) | V_A / V_A′ (bge) | P_∥(1) / P_⊥(1), variogram (bge) | ρ_A of cross-fitted principal subspace (bge) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 51a | 3 | 21 | 2 | 0.47 [0.13, 4.31] | 5.51 [0.74, 146.21] | 0.21 | 1.51 / 1.49 | 0.44 / 0.28 (Δ 0.16 [-0.19, 0.39]) | 95.19 |
| 51b | 1 | 24 | 2 | 0.52 [0.00, 34.86] | 0.38 [0.01, 232.29] | 0.40 | 1.27 / 1.83 | n/a (< 3 days) | — |
| 51c | 5 | 25 | 2 | 1.42 [0.62, 3.61] | 1.04 [0.43, 2.50] | 0.68 | 1.20 / 1.05 | 0.46 / 0.34 (Δ 0.12 [-0.16, 0.49]) | 2.16 |
| 51d | 5 | 26 | 2 | 1.71 [0.96, 8.77] | 1.15 [0.61, 1.58] | 0.88 | 1.18 / 1.43 | 0.31 / 0.26 (Δ 0.05 [-0.37, 0.33]) | 1.01 |
| 51e | 3 | 27 | 2 | 0.19 [0.09, 0.54] | 0.24 [0.12, 0.53] | 0.04 | 1.26 / 1.57 | 0.28 / 0.14 (Δ 0.14 [-2.25, 0.58]) | 0.07 |
| 51f | 5 | 26 | 2 | 0.97 [0.22, 2.45] | 0.71 [0.45, 1.19] | 0.42 | 1.23 / 1.65 | 0.08 / 0.31 (Δ -0.23 [-0.68, 0.04]) | 1.19 |
| 51g | 13 | 27 | 2 | 0.50 [0.32, 0.90] | 0.76 [0.42, 1.35] | 0.04 | 1.26 / 1.45 | 0.27 / 0.40 (Δ -0.14 [-0.31, 0.04]) | 9.96 |
| 51h | 4 | 26 | 2 | 0.64 [0.18, 2.01] | 0.70 [0.01, 64.50] | 0.26 | 1.14 / 0.95 | -0.03 / 0.16 (Δ -0.18 [-0.87, 0.29]) | 0.01 |
| 51i | 2 | 27 | 2 | 0.00 [0.00, 71.65] | 1.45 [0.00, 61.97] | 0.07 | 1.28 / 0.50 | n/a (< 3 days) | 0.00 |
| 51j | 2 | 27 | 2 | 1.44 [0.41, 43.74] | 60.98 [0.00, 89.42] | 0.61 | 1.22 / 1.49 | n/a (< 3 days) | 2.40 |
| 51k | 1 | 28 | 2 | 0.86 [0.01, 28.26] | 0.07 [0.00, 13.97] | 0.54 | 1.37 / 4.70 | n/a (< 3 days) | — |
| 51l | 1 | 27 | 2 | 7.30 [0.07, 438.78] | 2.17 [0.00, 67.03] | 0.92 | 1.19 / 2.23 | n/a (< 3 days) | — |

- **N2 (native):** own-plane pooled ρ_A 0.67 [0.45, 0.99] (bge, 90%); gte 0.75 [0.55, 1.02]; white32 0.73 [0.44, 1.20]. Inside [⅓, 3] in every variant; 0/7 testable units above the random 95th percentile (bge). **N2 fails** (its counts-against clause fires).
- **Own goal axis alone (variant, d = 1):** pooled ρ_A 0.60 [0.36, 0.99] (bge), 0.44 [0.30, 0.63] (gte): if anything faster along the agent's own goal than across it (the H97 direction), but not below ⅓.
- **Cross-agent swap control:** median random-plane percentile of another role's plane 0.56 (20 derangements × 12 units): consistent (not slower than random). The own plane is not slower either.
- **P4 (kick, across the plane):** pooled lag-1/lag-0 ratio 0.42, 95% CI [0.17, 0.75]; lag-0 coefficient 0.0027 (SE 0.0006). Neither ≤ ¼ nor ≥ ½: **inconclusive**. The along-plane clause is untestable (A1 point 4; pooled along-plane lag-0 coefficient 0.0004).
- **P5:** variogram contrast positive with CI in 0/7 testable #51 units (bge); 51g −0.14 [−0.31, 0.04].

Pool and kill are decided on the card's pool over all 25 units (kill fires: ρ_A 0.68 [0.50, 0.94] bge). A unit's P1 miss is inconclusive (P1 power 0.37, A1); P2 (power 0.84) and P5 (power 0.945) are informative per unit.

## Scorecard (period-specific axes)
C 0 (own plane not beyond the random band); D 0; G 0 (role texts do not set slow directions, although H54 shows agents sit on them); H 1 (beats nothing; consistent with R-iso).

## Notes
- Prior arithmetic (card): along-plane memory ≥ 10× 100 calls exceeds a median agent-day (761 calls); the day-scale test O3 may carry the along-plane part.
