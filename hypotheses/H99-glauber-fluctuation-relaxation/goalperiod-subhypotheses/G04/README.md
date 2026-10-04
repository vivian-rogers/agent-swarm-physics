# H99 × G04: goal period #4

**Verdict:** mixed
**Role:** replication (exploratory)
**Period:** goal #4 · regime I · units 4a, 4b, 4c, 4d · N 4, 4, 4, 4 · 3579 trimmed minutes.

## Why this period
Eligible for the replication layer (≥ 3 agents with ≥ 30 record minutes, ≥ 60 trimmed minutes per day).

## Prediction
*The card's rule, written 2026-10-04 20:22 UTC before any H99 statistic and amended before real data (A1, 20:41 UTC) and after the first run (A2, 20:45 UTC, post hoc for talk); this folder was written after the run and copies it.* Glauber consistency: no field call on the talk channel (A2 rule: |Δρ| < 0.03 or CI covering 0) in units with a resolved fluctuation gain. Supported if every resolved talk unit is consistent; failed if most resolved units carry a field call; descriptive if no unit has a resolved g_χ; mixed otherwise. Regime I is predicted to fail in the fast-field direction (P2).

## Result

| Unit | channel | g_χ [95%] | ρ_c(1) | ρ_⊥(1) | gap (Δρ₁ talk / Δg₁ other) [95%] | lag 2 | call |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 4a | act | 0.386 [0.160, 0.523] | 0.29 | 0.24 | -0.240 [-0.411, -0.098] | -0.101 | fast |
| 4a | content | 0.566 [0.436, 0.682] | 0.48 | 0.25 | -0.088 [-0.181, -0.019] | -0.441 | fast |
| 4a | talk | 0.467 [0.334, 0.583] | 0.20 | 0.13 | -0.142 [-0.249, -0.013] | -0.174 | fast |
| 4b | act | -0.272 [–, –] | 0.02 | 0.04 | 0.048 [–, –] | -0.061 | undefined |
| 4b | talk | -0.212 [–, –] | 0.07 | 0.13 | -0.020 [–, –] | 0.066 | undefined |
| 4c | act | 0.202 [0.100, 0.304] | 0.26 | 0.24 | -0.133 [-0.322, -0.012] | -0.110 | fast |
| 4c | content | 0.646 [0.586, 0.706] | 0.58 | 0.32 | -0.135 [-0.217, -0.080] | -0.156 | fast |
| 4c | talk | 0.330 [0.246, 0.392] | 0.09 | 0.06 | -0.061 [-0.130, 0.010] | -0.096 | consistent (low power) |
| 4d | act | 0.134 [-0.145, 0.263] | 0.18 | 0.13 | 0.015 [-0.834, 0.328] | – | unresolved |
| 4d | content | 0.701 [0.673, 0.730] | 0.42 | 0.19 | -0.236 [-0.471, -0.124] | -2.057 | fast |
| 4d | talk | 0.176 [-0.513, 0.421] | 0.07 | 0.05 | -0.009 [-0.319, 0.206] | 0.085 | unresolved |

Talk kick layer (human messages as a field on the room; distributed-lag kernel of the room's talk count; decay ratio λ = Σβ₁…₅ / Σβ₀…₄; A2 estimator):

| Unit | kicks | response at lags 0–1 [95%] | λ_kick [95%] | Glauber λ_c | measured ρ_c(1) | ρ_⊥(1) |
| --- | --- | --- | --- | --- | --- | --- |
| 4a | 115 | 0.66 [0.41, 0.99] | 0.02 [-0.67, 0.44] | 0.341 | 0.199 | 0.133 |
| 4c | 1182 | 0.27 [0.16, 0.39] | 0.54 [0.21, 0.86] | 0.153 | 0.092 | 0.061 |
| 4d | 85 | 0.17 [-0.85, 0.50] | -2.37 [-14.69, 0.61] | 0.080 | 0.071 | 0.047 |

Period pool (random effects over units, talk): g_χ = 0.375 [0.258, 0.492], Δρ₁ = -0.078 [-0.136, -0.020].

Data: `data/processed/H99-glauber-fluctuation-relaxation/results/units_called.parquet`, `periods.parquet`.

## Scorecard (period-specific axes)
C: g_χ against independence (bootstrap CI and block-shift null). D: the collective relaxation predicted from fluctuations (Δρ, Δg). H: Glauber against fast-field, slow-field and delayed-coupling readings.

## Round 2 (2026-10-04)

*Round-2 tests (card section "Round 2"; predictions written 21:20 UTC and Amendment B1 21:30 UTC, before real data). Exploratory, non-holdout. Talk statistics stay post hoc in the A2 sense.*

| Unit | Δρ₁ V0 (W0-corr.) | Δρ₁ V5 (W0-corr.) | ρ_s − W0 | g₁ room-gated | g₁ in-flight-gated | g₂ room-gated | g₁,fit (R2) | H67 g_lag |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 4a | -0.158 ± 0.071 | +0.079 | +0.336 [+0.263, +0.410] | -0.004 [-0.034, +0.037] | -0.029 [-0.076, +0.028] | +0.009 [-0.013, +0.021] | – | -0.007 |
| 4b | +0.108 | – | +0.143 | -0.011 | +0.107 | -0.094 | – | – |
| 4c | -0.095 ± 0.039 | +0.597 | +0.047 [+0.006, +0.089] | +0.029 [-0.004, +0.063] | +0.021 [-0.022, +0.072] | -0.018 [-0.033, +0.001] | – | +0.021 |

Regime I. ± is one SE (block bootstrap and W0 spread). Data: `data/processed/H99-glauber-fluctuation-relaxation/r2/results/r2_units.parquet`.

Reading (descriptive): regime-I reads and in-flight messages raise talk equally (no read-out gate), so any collective memory here is field-like.
