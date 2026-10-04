# H99 × G26: goal period #26

**Verdict:** descriptive
**Role:** replication (exploratory)
**Period:** goal #26 · regime I · units 26 · N 10 · 723 trimmed minutes.

## Why this period
Eligible for the replication layer (≥ 3 agents with ≥ 30 record minutes, ≥ 60 trimmed minutes per day).

## Prediction
*The card's rule, written 2026-10-04 20:22 UTC before any H99 statistic and amended before real data (A1, 20:41 UTC) and after the first run (A2, 20:45 UTC, post hoc for talk); this folder was written after the run and copies it.* Glauber consistency: no field call on the talk channel (A2 rule: |Δρ| < 0.03 or CI covering 0) in units with a resolved fluctuation gain. Supported if every resolved talk unit is consistent; failed if most resolved units carry a field call; descriptive if no unit has a resolved g_χ; mixed otherwise. Regime I is predicted to fail in the fast-field direction (P2).

## Result

| Unit | channel | g_χ [95%] | ρ_c(1) | ρ_⊥(1) | gap (Δρ₁ talk / Δg₁ other) [95%] | lag 2 | call |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 26 | act | 0.396 [0.076, 0.590] | 0.45 | 0.25 | 0.029 [-0.267, 0.163] | 0.017 | consistent |
| 26 | content | 0.850 [0.794, 0.890] | 0.58 | 0.27 | -0.266 [-0.395, -0.183] | -0.464 | fast |
| 26 | talk | 0.375 [0.209, 0.519] | 0.23 | 0.04 | 0.093 [-0.021, 0.210] | 0.076 | consistent (low power) |

Period pool (random effects over units, talk): g_χ = 0.375 [0.224, 0.527], Δρ₁ = 0.093 [-0.020, 0.207].

Data: `data/processed/H99-glauber-fluctuation-relaxation/results/units_called.parquet`, `periods.parquet`.

## Scorecard (period-specific axes)
C: g_χ against independence (bootstrap CI and block-shift null). D: the collective relaxation predicted from fluctuations (Δρ, Δg). H: Glauber against fast-field, slow-field and delayed-coupling readings.

## Round 2 (2026-10-04)

*Round-2 tests (card section "Round 2"; predictions written 21:20 UTC and Amendment B1 21:30 UTC, before real data). Exploratory, non-holdout. Talk statistics stay post hoc in the A2 sense.*

| Unit | Δρ₁ V0 (W0-corr.) | Δρ₁ V5 (W0-corr.) | ρ_s − W0 | g₁ room-gated | g₁ in-flight-gated | g₂ room-gated | g₁,fit (R2) | H67 g_lag |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 26 | +0.007 ± 0.059 | +0.076 ± 0.037 | +0.054 [+0.023, +0.082] | +0.107 [+0.052, +0.160] | +0.027 [-0.025, +0.074] | -0.006 [-0.022, +0.010] | – | +0.012 |

Regime I. ± is one SE (block bootstrap and W0 spread). Data: `data/processed/H99-glauber-fluctuation-relaxation/r2/results/r2_units.parquet`.

Reading (descriptive): regime-I reads and in-flight messages raise talk equally (no read-out gate), so any collective memory here is field-like.
