# H99 × G23: goal period #23

**Verdict:** descriptive
**Role:** replication (exploratory)
**Period:** goal #23 · regime I · units 23 · N 10 · 1142 trimmed minutes.

## Why this period
Eligible for the replication layer (≥ 3 agents with ≥ 30 record minutes, ≥ 60 trimmed minutes per day).

## Prediction
*The card's rule, written 2026-10-04 20:22 UTC before any H99 statistic and amended before real data (A1, 20:41 UTC) and after the first run (A2, 20:45 UTC, post hoc for talk); this folder was written after the run and copies it.* Glauber consistency: no field call on the talk channel (A2 rule: |Δρ| < 0.03 or CI covering 0) in units with a resolved fluctuation gain. Supported if every resolved talk unit is consistent; failed if most resolved units carry a field call; descriptive if no unit has a resolved g_χ; mixed otherwise. Regime I is predicted to fail in the fast-field direction (P2).

## Result

| Unit | channel | g_χ [95%] | ρ_c(1) | ρ_⊥(1) | gap (Δρ₁ talk / Δg₁ other) [95%] | lag 2 | call |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 23 | act | -0.011 [-0.125, 0.099] | 0.21 | 0.24 | -0.095 [-0.476, 0.127] | 0.063 | unresolved |
| 23 | content | 0.512 [0.327, 0.649] | 0.56 | 0.36 | -0.092 [-0.180, 0.006] | -0.129 | consistent |
| 23 | talk | 0.222 [0.160, 0.279] | 0.04 | 0.04 | -0.038 [-0.104, 0.032] | 0.013 | consistent (low power) |

Period pool (random effects over units, talk): g_χ = 0.222 [0.163, 0.281], Δρ₁ = -0.038 [-0.108, 0.032].

Data: `data/processed/H99-glauber-fluctuation-relaxation/results/units_called.parquet`, `periods.parquet`.

## Scorecard (period-specific axes)
C: g_χ against independence (bootstrap CI and block-shift null). D: the collective relaxation predicted from fluctuations (Δρ, Δg). H: Glauber against fast-field, slow-field and delayed-coupling readings.

## Round 2 (2026-10-04)

*Round-2 tests (card section "Round 2"; predictions written 21:20 UTC and Amendment B1 21:30 UTC, before real data). Exploratory, non-holdout. Talk statistics stay post hoc in the A2 sense.*

| Unit | Δρ₁ V0 (W0-corr.) | Δρ₁ V5 (W0-corr.) | ρ_s − W0 | g₁ room-gated | g₁ in-flight-gated | g₂ room-gated | g₁,fit (R2) | H67 g_lag |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 23 | -0.026 ± 0.036 | -0.074 ± 0.039 | +0.085 [+0.044, +0.133] | -0.003 [-0.024, +0.015] | -0.044 [-0.066, -0.018] | -0.001 [-0.016, +0.013] | – | -0.038 |

Regime I. ± is one SE (block bootstrap and W0 spread). Data: `data/processed/H99-glauber-fluctuation-relaxation/r2/results/r2_units.parquet`.

Reading (descriptive): regime-I reads and in-flight messages raise talk equally (no read-out gate), so any collective memory here is field-like.
