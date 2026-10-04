# H99 × G30: goal period #30

**Verdict:** descriptive
**Role:** replication (exploratory)
**Period:** goal #30 · regime I · units 30a, 30b · N 11, 11 · 1191 trimmed minutes.

## Why this period
Eligible for the replication layer (≥ 3 agents with ≥ 30 record minutes, ≥ 60 trimmed minutes per day).

## Prediction
*The card's rule, written 2026-10-04 20:22 UTC before any H99 statistic and amended before real data (A1, 20:41 UTC) and after the first run (A2, 20:45 UTC, post hoc for talk); this folder was written after the run and copies it.* Glauber consistency: no field call on the talk channel (A2 rule: |Δρ| < 0.03 or CI covering 0) in units with a resolved fluctuation gain. Supported if every resolved talk unit is consistent; failed if most resolved units carry a field call; descriptive if no unit has a resolved g_χ; mixed otherwise. Regime I is predicted to fail in the fast-field direction (P2).

## Result

| Unit | channel | g_χ [95%] | ρ_c(1) | ρ_⊥(1) | gap (Δρ₁ talk / Δg₁ other) [95%] | lag 2 | call |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 30a | act | 0.112 [-0.010, 0.257] | 0.15 | 0.11 | 0.022 [-1.259, 0.335] | 0.067 | unresolved |
| 30a | content | 0.716 [-0.312, 0.812] | 0.38 | 0.07 | -0.084 [-0.252, 0.185] | – | unresolved |
| 30a | talk | 0.174 [-0.141, 0.353] | 0.07 | 0.10 | -0.088 [-0.200, 0.048] | 0.006 | unresolved |
| 30b | act | 0.098 [-0.004, 0.175] | 0.29 | 0.21 | 0.098 [-0.068, 0.234] | 0.167 | unresolved |
| 30b | content | 0.844 [0.803, 0.873] | 0.51 | 0.21 | -0.267 [-0.470, -0.164] | -0.400 | fast |
| 30b | talk | 0.214 [0.128, 0.288] | 0.14 | 0.07 | 0.017 [-0.019, 0.064] | 0.020 | consistent (low power) |

Period pool (random effects over units, talk): g_χ = 0.210 [0.134, 0.287], Δρ₁ = -0.017 [-0.113, 0.078].

Data: `data/processed/H99-glauber-fluctuation-relaxation/results/units_called.parquet`, `periods.parquet`.

## Scorecard (period-specific axes)
C: g_χ against independence (bootstrap CI and block-shift null). D: the collective relaxation predicted from fluctuations (Δρ, Δg). H: Glauber against fast-field, slow-field and delayed-coupling readings.

## Round 2 (2026-10-04)

*Round-2 tests (card section "Round 2"; predictions written 21:20 UTC and Amendment B1 21:30 UTC, before real data). Exploratory, non-holdout. Talk statistics stay post hoc in the A2 sense.*

| Unit | Δρ₁ V0 (W0-corr.) | Δρ₁ V5 (W0-corr.) | ρ_s − W0 | g₁ room-gated | g₁ in-flight-gated | g₂ room-gated | g₁,fit (R2) | H67 g_lag |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 30a | -0.095 ± 0.043 | +0.137 ± 0.077 | +0.069 [-0.006, +0.150] | +0.025 [-0.018, +0.066] | +0.024 [-0.069, +0.103] | -0.010 [-0.030, +0.004] | – | +0.021 |
| 30b | -0.038 ± 0.025 | -0.028 ± 0.039 | +0.086 [+0.055, +0.120] | +0.017 [-0.005, +0.039] | -0.006 [-0.046, +0.029] | -0.021 [-0.032, -0.012] | – | -0.009 |

Regime I. ± is one SE (block bootstrap and W0 spread). Data: `data/processed/H99-glauber-fluctuation-relaxation/r2/results/r2_units.parquet`.

Reading (descriptive): regime-I reads and in-flight messages raise talk equally (no read-out gate), so any collective memory here is field-like.
