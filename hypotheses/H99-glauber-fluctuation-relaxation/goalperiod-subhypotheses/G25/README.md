# H99 × G25: goal period #25

**Verdict:** descriptive
**Role:** replication (exploratory)
**Period:** goal #25 · regime I · units 25 · N 10 · 987 trimmed minutes.

## Why this period
Eligible for the replication layer (≥ 3 agents with ≥ 30 record minutes, ≥ 60 trimmed minutes per day).

## Prediction
*The card's rule, written 2026-10-04 20:22 UTC before any H99 statistic and amended before real data (A1, 20:41 UTC) and after the first run (A2, 20:45 UTC, post hoc for talk); this folder was written after the run and copies it.* Glauber consistency: no field call on the talk channel (A2 rule: |Δρ| < 0.03 or CI covering 0) in units with a resolved fluctuation gain. Supported if every resolved talk unit is consistent; failed if most resolved units carry a field call; descriptive if no unit has a resolved g_χ; mixed otherwise. Regime I is predicted to fail in the fast-field direction (P2).

## Result

| Unit | channel | g_χ [95%] | ρ_c(1) | ρ_⊥(1) | gap (Δρ₁ talk / Δg₁ other) [95%] | lag 2 | call |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 25 | act | -0.008 [-0.083, 0.063] | 0.16 | 0.20 | -0.109 [-0.274, -0.000] | 0.089 | fast (g unresolved) |
| 25 | content | 0.734 [0.659, 0.786] | 0.50 | 0.29 | -0.298 [-0.420, -0.184] | -0.331 | fast |
| 25 | talk | 0.204 [0.090, 0.281] | 0.12 | 0.04 | 0.048 [-0.039, 0.138] | -0.016 | consistent (low power) |

Period pool (random effects over units, talk): g_χ = 0.204 [0.108, 0.299], Δρ₁ = 0.048 [-0.045, 0.141].

Data: `data/processed/H99-glauber-fluctuation-relaxation/results/units_called.parquet`, `periods.parquet`.

## Scorecard (period-specific axes)
C: g_χ against independence (bootstrap CI and block-shift null). D: the collective relaxation predicted from fluctuations (Δρ, Δg). H: Glauber against fast-field, slow-field and delayed-coupling readings.

## Round 2 (2026-10-04)

*Round-2 tests (card section "Round 2"; predictions written 21:20 UTC and Amendment B1 21:30 UTC, before real data). Exploratory, non-holdout. Talk statistics stay post hoc in the A2 sense.*

| Unit | Δρ₁ V0 (W0-corr.) | Δρ₁ V5 (W0-corr.) | ρ_s − W0 | g₁ room-gated | g₁ in-flight-gated | g₂ room-gated | g₁,fit (R2) | H67 g_lag |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 25 | -0.005 ± 0.049 | +0.054 ± 0.046 | +0.087 [+0.050, +0.121] | +0.039 [+0.009, +0.067] | +0.050 [+0.003, +0.089] | -0.017 [-0.044, -0.004] | – | +0.012 |

Regime I. ± is one SE (block bootstrap and W0 spread). Data: `data/processed/H99-glauber-fluctuation-relaxation/r2/results/r2_units.parquet`.

Reading (descriptive): regime-I reads and in-flight messages raise talk equally (no read-out gate), so any collective memory here is field-like.
