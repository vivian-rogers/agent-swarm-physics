# H99 × G21: goal period #21

**Verdict:** descriptive
**Role:** replication (exploratory)
**Period:** goal #21 · regime I · units 21a, 21b · N 8, 9 · 1181 trimmed minutes.

## Why this period
Eligible for the replication layer (≥ 3 agents with ≥ 30 record minutes, ≥ 60 trimmed minutes per day).

## Prediction
*The card's rule, written 2026-10-04 20:22 UTC before any H99 statistic and amended before real data (A1, 20:41 UTC) and after the first run (A2, 20:45 UTC, post hoc for talk); this folder was written after the run and copies it.* Glauber consistency: no field call on the talk channel (A2 rule: |Δρ| < 0.03 or CI covering 0) in units with a resolved fluctuation gain. Supported if every resolved talk unit is consistent; failed if most resolved units carry a field call; descriptive if no unit has a resolved g_χ; mixed otherwise. Regime I is predicted to fail in the fast-field direction (P2).

## Result

| Unit | channel | g_χ [95%] | ρ_c(1) | ρ_⊥(1) | gap (Δρ₁ talk / Δg₁ other) [95%] | lag 2 | call |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 21a | act | -0.027 [-0.142, 0.064] | 0.02 | 0.11 | -0.721 [–, –] | -0.138 | fast (g unresolved) |
| 21a | content | 0.761 [0.681, 0.802] | 0.64 | 0.29 | -0.125 [-0.172, -0.079] | -0.221 | fast |
| 21a | talk | 0.278 [0.189, 0.348] | -0.00 | -0.04 | -0.007 [-0.074, 0.027] | -0.067 | consistent (low power) |
| 21b | act | 0.173 [0.015, 0.279] | 0.20 | 0.10 | 0.146 [-0.202, 0.336] | 0.322 | slow |
| 21b | content | 0.587 [0.481, 0.671] | 0.42 | 0.31 | -0.314 [-0.697, -0.109] | -0.854 | fast |
| 21b | talk | 0.144 [0.037, 0.226] | -0.02 | -0.01 | -0.019 [-0.126, 0.059] | -0.041 | consistent (low power) |

Period pool (random effects over units, talk): g_χ = 0.214 [0.083, 0.345], Δρ₁ = -0.010 [-0.054, 0.034].

Data: `data/processed/H99-glauber-fluctuation-relaxation/results/units_called.parquet`, `periods.parquet`.

## Scorecard (period-specific axes)
C: g_χ against independence (bootstrap CI and block-shift null). D: the collective relaxation predicted from fluctuations (Δρ, Δg). H: Glauber against fast-field, slow-field and delayed-coupling readings.

## Round 2 (2026-10-04)

*Round-2 tests (card section "Round 2"; predictions written 21:20 UTC and Amendment B1 21:30 UTC, before real data). Exploratory, non-holdout. Talk statistics stay post hoc in the A2 sense.*

| Unit | Δρ₁ V0 (W0-corr.) | Δρ₁ V5 (W0-corr.) | ρ_s − W0 | g₁ room-gated | g₁ in-flight-gated | g₂ room-gated | g₁,fit (R2) | H67 g_lag |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 21a | +0.001 ± 0.028 | +0.022 ± 0.029 | +0.076 [+0.018, +0.123] | -0.012 [-0.031, +0.007] | -0.019 [-0.053, +0.011] | +0.003 [-0.031, +0.035] | – | -0.025 |
| 21b | +0.002 ± 0.055 | +0.026 ± 0.044 | +0.131 [+0.043, +0.190] | +0.008 [-0.028, +0.044] | -0.029 [-0.082, +0.026] | -0.032 [-0.062, -0.002] | – | +0.003 |

Regime I. ± is one SE (block bootstrap and W0 spread). Data: `data/processed/H99-glauber-fluctuation-relaxation/r2/results/r2_units.parquet`.

Reading (descriptive): regime-I reads and in-flight messages raise talk equally (no read-out gate), so any collective memory here is field-like.
