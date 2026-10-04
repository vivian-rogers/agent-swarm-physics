# H99 × G39: goal period #39

**Verdict:** descriptive
**Role:** replication (exploratory)
**Period:** goal #39 · regime III · units 39 · N 15 · 852 trimmed minutes.

## Why this period
Eligible for the replication layer (≥ 3 agents with ≥ 30 record minutes, ≥ 60 trimmed minutes per day).

## Prediction
*The card's rule, written 2026-10-04 20:22 UTC before any H99 statistic and amended before real data (A1, 20:41 UTC) and after the first run (A2, 20:45 UTC, post hoc for talk); this folder was written after the run and copies it.* Glauber consistency: no field call on the talk channel (A2 rule: |Δρ| < 0.03 or CI covering 0) in units with a resolved fluctuation gain. Supported if every resolved talk unit is consistent; failed if most resolved units carry a field call; descriptive if no unit has a resolved g_χ; mixed otherwise. Regime III is predicted to be consistent (P1).

## Result

| Unit | channel | g_χ [95%] | ρ_c(1) | ρ_⊥(1) | gap (Δρ₁ talk / Δg₁ other) [95%] | lag 2 | call |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 39 | act | -0.041 [-0.169, 0.058] | 0.24 | 0.30 | -0.156 [-0.355, -0.003] | 0.016 | fast (g unresolved) |
| 39 | content | 0.292 [0.183, 0.374] | 0.43 | 0.35 | -0.089 [-0.218, 0.047] | 0.013 | consistent |
| 39 | talk | 0.114 [0.028, 0.213] | -0.01 | -0.09 | -0.010 [-0.069, 0.051] | 0.025 | consistent (low power) |

Period pool (random effects over units, talk): g_χ = 0.114 [0.020, 0.208], Δρ₁ = -0.010 [-0.071, 0.051].

Data: `data/processed/H99-glauber-fluctuation-relaxation/results/units_called.parquet`, `periods.parquet`.

## Scorecard (period-specific axes)
C: g_χ against independence (bootstrap CI and block-shift null). D: the collective relaxation predicted from fluctuations (Δρ, Δg). H: Glauber against fast-field, slow-field and delayed-coupling readings.

## Round 2 (2026-10-04)

*Round-2 tests (card section "Round 2"; predictions written 21:20 UTC and Amendment B1 21:30 UTC, before real data). Exploratory, non-holdout. Talk statistics stay post hoc in the A2 sense.*

| Unit | Δρ₁ V0 (W0-corr.) | Δρ₁ V5 (W0-corr.) | ρ_s − W0 | g₁ room-gated | g₁ in-flight-gated | g₂ room-gated | g₁,fit (R2) | H67 g_lag |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 39 | -0.009 ± 0.038 | +0.057 ± 0.043 | -0.059 [-0.104, -0.015] | +0.175 [+0.114, +0.239] | +0.277 [+0.210, +0.384] | +0.030 [-0.005, +0.057] | +0.00 [+0.00, +0.26] | +0.144 |

Regime III. ± is one SE (block bootstrap and W0 spread). Data: `data/processed/H99-glauber-fluctuation-relaxation/r2/results/r2_units.parquet`.

Reading: the collective talk memory survives scheduler removal where it was present in round 1; reads couple at the next call (room-gated g₁ ≈ H67's g_lag), mostly through named messages. See the card for pooled tests.
