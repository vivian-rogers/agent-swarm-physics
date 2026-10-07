# H138 × G51: private roles, own repos (#51 main body, 2026-07-06 → 2026-09-04, units 51a–51l)

**Verdict:** failed
**Role:** exploratory (replication over 12 units + native N3)
**Period:** regime III · mode I/K (private roles) · up to 21 agents · #general (and #focus from 08-05) · non-reserved days 2026-07-06 → 2026-09-04. The tail (2026-09-07 → 09-21) is reserved and not used.

## Why this period
Own-role units with a high ownership price (H94: λ_own 5.5–18 across the 12 units) and the most work-label switches (930, H11 round 2). The stay field is strong and measured, so Glauber predicts a low base rate and an unchanged elasticity to the options on offer.

## Prediction
*Written 2026-10-07 ~09:10 UTC, before running on this period. Seen: the switch total, H94's λ_own range, H129's own-role hop rate (≈ 0.11 per 100 own calls); no q count and no hazard statistic.*
- **N3 (native):** pooled ε_q over 51a–51l has CI above 0, and owner visits leave less than non-owner visits (β̂_own < 0 with CI). Credence 0.35.
- **P4 (secondary):** R_own = β̂_own / (−λ̂_own) ∈ [0.5, 2] in ≥ 1/2 of units with both visit kinds. Credence 0.2.
- **P3 (lead placebo):** pooled ε_q − ε_lead > 0 with CI above 0. Credence 0.3.
- Counts against: pooled ε_q CI includes 0 with synthetic power ≥ 0.8.

## Result
*Round 1, 2026-10-07 (exploration). Estimator: cloglog hazard per own call, agent effects, active-time spline, agent-cluster sandwich (card Amendment A1). Power from the real-skeleton synthetic (W1 worlds, 200 replicates). The work power at ε_q = 0.5 is below 0.8 in every unit (card A2), so a work null is unpowered.*

| Channel · unit | Leaves | ε̂_q [95% CI] | permutation p | ε̂_q − ε̂_lead [boot CI] | ε̂_Z [CI] | β̂_own [CI] | power at ε 0.5 / 1 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| work · 51a | 38 | 2.06 [−1.83, 5.95] | 0.202 | 1.95 [−5.79, 5.85] | 0.87 [0.35, 1.39] | −1.43 [−2.81, −0.06] | 0.12 / 0.11 |
| work · 51b | 13 | not testable (< 25 leaves); fitted −4.39 | — | — | — | — | — |
| work · 51c | 46 | −3.23 [−7.12, 0.66] | 0.126 | −3.13 [−18.33, −1.32] | 0.63 [−0.62, 1.88] | −1.28 [−2.81, 0.26] | 0.07 / 0.10 |
| work · 51d | 47 | −1.30 [−6.04, 3.44] | 0.481 | −1.36 [−6.41, 7.87] | −0.19 [−1.29, 0.90] | 1.27 [−1.88, 4.42] | 0.09 / 0.12 |
| work · 51e | 25 | 0.25 [−13.22, 13.71] | 0.957 | 0.69 [−12.92, 9.67] | 0.37 [−0.48, 1.22] | 2.51 [−1.19, 6.20] | 0.06 / 0.06 |
| work · 51f | 88 | −0.45 [−7.13, 6.23] | 0.764 | −0.81 [−7.04, 5.19] | 0.24 [−0.23, 0.71] | −0.68 [−3.21, 1.86] | 0.10 / 0.15 |
| work · 51g | 282 | −2.07 [−3.72, −0.41] | 0.095 | −2.08 [−3.31, −0.91] | 0.18 [−0.05, 0.42] | 0.60 [−0.16, 1.36] | 0.16 / 0.36 |
| work · 51h | 44 | −3.98 [−11.16, 3.20] | 0.105 | −2.97 [−9.73, 7.58] | −0.49 [−1.50, 0.51] | −2.94 [−5.95, 0.06] | 0.10 / 0.07 |
| work · 51i | 31 | −3.52 [−15.24, 8.19] | 0.351 | −5.03 [−31.90, 17.65] | 1.44 [0.02, 2.87] | −0.78 [−6.35, 4.79] | 0.07 / 0.06 |
| work · 51j | 27 | −2.56 [−5.74, 0.61] | 0.407 | −3.07 [−5.71, 8.45] | −0.60 [−2.65, 1.44] | −3.47 [−5.64, −1.30] | 0.06 / 0.07 |
| work · 51k | 7 | not testable (< 25 leaves); fitted −52.03 | — | — | — | — | — |
| work · 51l | 11 | not testable (< 25 leaves); fitted −22.64 | — | — | — | — | — |
| attention · 51a | 212 | 0.38 [−0.76, 1.52] | 0.439 | 0.38 [−0.70, 1.44] | −0.40 [−1.07, 0.27] | −0.77 [−1.38, −0.15] | 0.14 / 0.48 |
| attention · 51b | 71 | 2.69 [−4.12, 9.50] | 0.005 | 2.39 [−6.89, 9.25] | −4.17 [−13.55, 5.21] | −0.33 [−0.97, 0.31] | 0.07 / 0.10 |
| attention · 51c | 331 | −0.09 [−1.02, 0.84] | 0.824 | −0.15 [−1.32, 0.75] | 0.24 [−0.30, 0.79] | −0.87 [−1.51, −0.23] | 0.25 / 0.59 |
| attention · 51d | 305 | 0.11 [−0.96, 1.18] | 0.833 | −0.10 [−1.23, 0.90] | 0.11 [−0.11, 0.33] | −1.06 [−1.57, −0.55] | 0.15 / 0.48 |
| attention · 51e | 274 | −2.29 [−4.31, −0.27] | 0.002 | −2.08 [−4.37, 0.03] | −0.19 [−0.67, 0.28] | −0.35 [−0.95, 0.26] | 0.08 / 0.14 |
| attention · 51f | 398 | −0.30 [−1.59, 0.98] | 0.658 | −0.31 [−1.51, 0.98] | −0.32 [−0.71, 0.08] | −0.72 [−1.22, −0.22] | 0.18 / 0.31 |
| attention · 51g | 961 | −0.49 [−1.27, 0.28] | 0.202 | −0.64 [−1.35, 0.17] | 0.28 [−0.11, 0.67] | −0.52 [−1.00, −0.04] | 0.40 / 0.84 |
| attention · 51h | 315 | −0.68 [−2.27, 0.91] | 0.389 | −0.74 [−2.35, 1.05] | −0.33 [−0.71, 0.05] | −0.59 [−1.08, −0.10] | 0.14 / 0.36 |
| attention · 51i | 122 | −0.70 [−3.27, 1.87] | 0.602 | −0.48 [−3.72, 1.52] | 0.11 [−0.30, 0.53] | −0.12 [−0.79, 0.56] | 0.07 / 0.10 |
| attention · 51j | 139 | −0.80 [−3.15, 1.55] | 0.396 | −0.62 [−3.22, 1.86] | 0.12 [−0.31, 0.55] | −0.71 [−1.86, 0.43] | 0.09 / 0.20 |
| attention · 51k | 89 | −2.86 [−5.82, 0.10] | 0.009 | −3.34 [−7.23, −0.57] | −4.93 [−10.24, 0.37] | −0.66 [−1.74, 0.42] | 0.09 / 0.14 |
| attention · 51l | 107 | 2.11 [−1.42, 5.63] | 0.010 | 1.84 [−1.85, 5.13] | 2.34 [−2.10, 6.78] | −0.76 [−1.41, −0.11] | 0.09 / 0.12 |

| Prediction | Observed | Verdict |
| --- | --- | --- |
| N3a: pooled ε_q over 51a–51l, CI above 0 | **−1.83 [−3.19, −0.46]** (12 units, DerSimonian–Laird, τ² 0.94); testable 9 units −1.83 [−2.86, −0.79] (τ² 0) | **failed** (sign reversed) |
| N3b: owners leave less, β̂_own < 0 with CI | pooled −1.63 [−3.27, 0.00] (12 units, τ² 6.7) | not established (CI touches 0) |
| P4: R_own ∈ [0.5, 2] in ≥ 1/2 of units | work 0/9 (−0.29 to 0.43); attention 0/12 (0.02 to 0.14) | failed |
| P3: pooled ε_q − ε_lead CI above 0 | work −1.95 [−3.10, −0.80] (9 testable units); attention −0.35 [−0.75, 0.05] | failed |
| Attention (secondary): pooled ε_q | −0.33 [−0.78, 0.12] (12 units) | fails |

- Period verdict: **failed** (N3 as registered). In the own-role weeks, more open options (others' own repos, q̄ 12–21) go with *fewer* direct leaves.
- **Fragility.** Every #51 work unit has a within-agent-day permutation p ≥ 0.095 (51g 0.095). The Wald CIs may be too narrow, so the size of the negative is uncertain. Post hoc, adding ln N_active leaves it at −1.73 [−2.81, −0.66].
- Descriptive: work leaves 0.06–0.20 per 100 own calls; 9–45% of leaves go to a project born in the 2 h before. Attention owners leave less in all 12 units (β̂_own −0.12 to −1.06), about 1/10 of λ_own or less.
- The reserved tail (2026-09-07 → 09-21) was not read.

## Scorecard (period-specific axes)
C 0 (sign reversed); D 1 (R_own checked: 0/9); G 1 (attention owners leave less in 12/12 units, as H94 in sign); H 0 (R-finish fits better).

## Notes
- Units with < 25 leaves are descriptive and enter only through the random-effects pool (exception (d)).
