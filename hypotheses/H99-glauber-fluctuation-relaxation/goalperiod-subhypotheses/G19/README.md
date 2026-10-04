# H99 × G19: goal period #19

**Verdict:** descriptive
**Role:** replication (exploratory)
**Period:** goal #19 · regime I · units 19a, 19b · N 7, 8 · 2275 trimmed minutes.

## Why this period
Eligible for the replication layer (≥ 3 agents with ≥ 30 record minutes, ≥ 60 trimmed minutes per day).

## Prediction
*The card's rule, written 2026-10-04 20:22 UTC before any H99 statistic and amended before real data (A1, 20:41 UTC) and after the first run (A2, 20:45 UTC, post hoc for talk); this folder was written after the run and copies it.* Glauber consistency: no field call on the talk channel (A2 rule: |Δρ| < 0.03 or CI covering 0) in units with a resolved fluctuation gain. Supported if every resolved talk unit is consistent; failed if most resolved units carry a field call; descriptive if no unit has a resolved g_χ; mixed otherwise. Regime I is predicted to fail in the fast-field direction (P2).

## Result

| Unit | channel | g_χ [95%] | ρ_c(1) | ρ_⊥(1) | gap (Δρ₁ talk / Δg₁ other) [95%] | lag 2 | call |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 19a | act | 0.123 [0.010, 0.230] | 0.18 | 0.20 | -0.204 [-0.475, -0.025] | -0.104 | fast |
| 19a | content | 0.782 [0.733, 0.823] | 0.61 | 0.43 | -0.373 [-0.479, -0.285] | -0.530 | fast |
| 19a | talk | 0.318 [0.251, 0.390] | 0.20 | 0.08 | 0.021 [-0.028, 0.069] | -0.031 | consistent (low power) |
| 19b | act | 0.128 [-0.001, 0.256] | 0.24 | 0.16 | 0.102 [-0.166, 0.324] | 0.122 | unresolved |
| 19b | content | 0.728 [0.559, 0.815] | 0.29 | 0.16 | -0.394 [-0.587, -0.157] | – | fast |
| 19b | talk | 0.231 [-0.211, 0.505] | 0.06 | -0.05 | 0.050 [-0.156, 0.129] | -0.004 | unresolved |

Period pool (random effects over units, talk): g_χ = 0.315 [0.244, 0.386], Δρ₁ = 0.024 [-0.024, 0.072].

Data: `data/processed/H99-glauber-fluctuation-relaxation/results/units_called.parquet`, `periods.parquet`.

## Scorecard (period-specific axes)
C: g_χ against independence (bootstrap CI and block-shift null). D: the collective relaxation predicted from fluctuations (Δρ, Δg). H: Glauber against fast-field, slow-field and delayed-coupling readings.

## Round 2 (2026-10-04)

*Round-2 tests (card section "Round 2"; predictions written 21:20 UTC and Amendment B1 21:30 UTC, before real data). Exploratory, non-holdout. Talk statistics stay post hoc in the A2 sense.*

| Unit | Δρ₁ V0 (W0-corr.) | Δρ₁ V5 (W0-corr.) | ρ_s − W0 | g₁ room-gated | g₁ in-flight-gated | g₂ room-gated | g₁,fit (R2) | H67 g_lag |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 19a | -0.061 ± 0.025 | -0.020 ± 0.036 | +0.043 [+0.010, +0.073] | +0.015 [-0.003, +0.034] | -0.002 [-0.031, +0.025] | -0.000 [-0.007, +0.006] | – | +0.003 |
| 19b | +0.106 ± 0.088 | +0.070 ± 0.081 | +0.047 [-0.045, +0.134] | +0.037 [-0.027, +0.083] | -0.041 [-0.107, +0.025] | +0.009 [-0.060, +0.026] | – | -0.019 |

Regime I. ± is one SE (block bootstrap and W0 spread). Data: `data/processed/H99-glauber-fluctuation-relaxation/r2/results/r2_units.parquet`.

Reading (descriptive): regime-I reads and in-flight messages raise talk equally (no read-out gate), so any collective memory here is field-like.
