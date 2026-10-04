# H99 × G18: goal period #18

**Verdict:** descriptive
**Role:** replication (exploratory)
**Period:** goal #18 · regime I · units 18a, 18b, 18c · N 7, 8, 7 · 2098 trimmed minutes.

## Why this period
Eligible for the replication layer (≥ 3 agents with ≥ 30 record minutes, ≥ 60 trimmed minutes per day).

## Prediction
*The card's rule, written 2026-10-04 20:22 UTC before any H99 statistic and amended before real data (A1, 20:41 UTC) and after the first run (A2, 20:45 UTC, post hoc for talk); this folder was written after the run and copies it.* Glauber consistency: no field call on the talk channel (A2 rule: |Δρ| < 0.03 or CI covering 0) in units with a resolved fluctuation gain. Supported if every resolved talk unit is consistent; failed if most resolved units carry a field call; descriptive if no unit has a resolved g_χ; mixed otherwise. Regime I is predicted to fail in the fast-field direction (P2).

## Result

| Unit | channel | g_χ [95%] | ρ_c(1) | ρ_⊥(1) | gap (Δρ₁ talk / Δg₁ other) [95%] | lag 2 | call |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 18a | act | 0.345 [0.137, 0.560] | 0.32 | 0.26 | -0.200 [-0.712, -0.096] | -0.406 | fast |
| 18a | content | 0.728 [0.577, 0.803] | 0.45 | 0.22 | -0.264 [-0.335, -0.179] | – | fast |
| 18a | talk | 0.431 [0.340, 0.529] | 0.11 | -0.01 | 0.090 [-0.105, 0.203] | -0.140 | consistent (low power) |
| 18b | act | 0.182 [0.081, 0.266] | 0.13 | 0.18 | -0.344 [-0.862, -0.126] | -0.360 | fast |
| 18b | content | 0.842 [0.782, 0.884] | 0.58 | 0.33 | -0.337 [-0.464, -0.222] | -0.455 | fast |
| 18b | talk | 0.265 [0.117, 0.369] | 0.11 | 0.07 | -0.039 [-0.084, 0.013] | -0.035 | consistent (low power) |
| 18c | act | 0.106 [-0.021, 0.201] | 0.20 | 0.21 | -0.128 [-0.619, 0.118] | -0.027 | unresolved |
| 18c | content | 0.702 [0.653, 0.737] | 0.55 | 0.36 | -0.289 [-0.441, -0.107] | -0.435 | fast |
| 18c | talk | 0.300 [0.228, 0.365] | 0.11 | 0.07 | -0.045 [-0.128, 0.048] | -0.066 | consistent (low power) |

Period pool (random effects over units, talk): g_χ = 0.335 [0.239, 0.430], Δρ₁ = -0.026 [-0.079, 0.027].

Data: `data/processed/H99-glauber-fluctuation-relaxation/results/units_called.parquet`, `periods.parquet`.

## Scorecard (period-specific axes)
C: g_χ against independence (bootstrap CI and block-shift null). D: the collective relaxation predicted from fluctuations (Δρ, Δg). H: Glauber against fast-field, slow-field and delayed-coupling readings.

## Round 2 (2026-10-04)

*Round-2 tests (card section "Round 2"; predictions written 21:20 UTC and Amendment B1 21:30 UTC, before real data). Exploratory, non-holdout. Talk statistics stay post hoc in the A2 sense.*

| Unit | Δρ₁ V0 (W0-corr.) | Δρ₁ V5 (W0-corr.) | ρ_s − W0 | g₁ room-gated | g₁ in-flight-gated | g₂ room-gated | g₁,fit (R2) | H67 g_lag |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 18a | +0.020 ± 0.076 | +0.026 ± 0.078 | +0.073 [-0.056, +0.189] | +0.042 [-0.016, +0.097] | -0.005 [-0.126, +0.104] | -0.026 [-0.051, -0.003] | – | +0.004 |
| 18b | -0.105 ± 0.029 | -0.033 ± 0.052 | +0.051 [+0.012, +0.090] | -0.017 [-0.071, +0.027] | -0.012 [-0.083, +0.051] | +0.004 [-0.006, +0.010] | – | +0.018 |
| 18c | -0.087 ± 0.051 | +0.062 ± 0.066 | +0.052 [-0.042, +0.119] | +0.036 [+0.009, +0.063] | +0.064 [+0.002, +0.108] | -0.016 [-0.036, +0.008] | – | +0.082 |

Regime I. ± is one SE (block bootstrap and W0 spread). Data: `data/processed/H99-glauber-fluctuation-relaxation/r2/results/r2_units.parquet`.

Reading (descriptive): regime-I reads and in-flight messages raise talk equally (no read-out gate), so any collective memory here is field-like.
