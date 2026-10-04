# H99 × G05: goal period #5

**Verdict:** descriptive
**Role:** replication (exploratory)
**Period:** goal #5 · regime I · units 5 · N 4 · 541 trimmed minutes.

## Why this period
Eligible for the replication layer (≥ 3 agents with ≥ 30 record minutes, ≥ 60 trimmed minutes per day).

## Prediction
*The card's rule, written 2026-10-04 20:22 UTC before any H99 statistic and amended before real data (A1, 20:41 UTC) and after the first run (A2, 20:45 UTC, post hoc for talk); this folder was written after the run and copies it.* Glauber consistency: no field call on the talk channel (A2 rule: |Δρ| < 0.03 or CI covering 0) in units with a resolved fluctuation gain. Supported if every resolved talk unit is consistent; failed if most resolved units carry a field call; descriptive if no unit has a resolved g_χ; mixed otherwise. Regime I is predicted to fail in the fast-field direction (P2).

## Result

| Unit | channel | g_χ [95%] | ρ_c(1) | ρ_⊥(1) | gap (Δρ₁ talk / Δg₁ other) [95%] | lag 2 | call |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 5 | act | 0.034 [-0.092, 0.152] | 0.13 | 0.15 | -0.106 [-0.354, 0.149] | 0.136 | unresolved |
| 5 | content | 0.569 [0.490, 0.653] | 0.39 | 0.28 | -0.326 [-0.516, -0.082] | -0.848 | fast |
| 5 | talk | 0.115 [-0.043, 0.219] | 0.13 | 0.08 | 0.020 [-0.100, 0.121] | 0.029 | unresolved |

Talk kick layer (human messages as a field on the room; distributed-lag kernel of the room's talk count; decay ratio λ = Σβ₁…₅ / Σβ₀…₄; A2 estimator):

| Unit | kicks | response at lags 0–1 [95%] | λ_kick [95%] | Glauber λ_c | measured ρ_c(1) | ρ_⊥(1) |
| --- | --- | --- | --- | --- | --- | --- |
| 5 | 818 | 0.05 [-0.01, 0.12] | -1.56 [-33.15, 1.46] | 0.112 | 0.131 | 0.084 |

Period pool (random effects over units, talk): g_χ = 0.115 [-0.022, 0.252], Δρ₁ = 0.020 [-0.090, 0.130].

Data: `data/processed/H99-glauber-fluctuation-relaxation/results/units_called.parquet`, `periods.parquet`.

## Scorecard (period-specific axes)
C: g_χ against independence (bootstrap CI and block-shift null). D: the collective relaxation predicted from fluctuations (Δρ, Δg). H: Glauber against fast-field, slow-field and delayed-coupling readings.

## Round 2 (2026-10-04)

*Round-2 tests (card section "Round 2"; predictions written 21:20 UTC and Amendment B1 21:30 UTC, before real data). Exploratory, non-holdout. Talk statistics stay post hoc in the A2 sense.*

| Unit | Δρ₁ V0 (W0-corr.) | Δρ₁ V5 (W0-corr.) | ρ_s − W0 | g₁ room-gated | g₁ in-flight-gated | g₂ room-gated | g₁,fit (R2) | H67 g_lag |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 5 | -0.003 ± 0.062 | – | +0.036 [-0.014, +0.089] | +0.031 [-0.013, +0.083] | +0.043 [+0.002, +0.089] | -0.000 [-0.019, +0.023] | – | +0.052 |

Regime I. ± is one SE (block bootstrap and W0 spread). Data: `data/processed/H99-glauber-fluctuation-relaxation/r2/results/r2_units.parquet`.

Reading (descriptive): regime-I reads and in-flight messages raise talk equally (no read-out gate), so any collective memory here is field-like.
