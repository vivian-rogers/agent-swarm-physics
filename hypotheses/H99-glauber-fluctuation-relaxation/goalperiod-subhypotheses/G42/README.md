# H99 × G42: goal period #42

**Verdict:** mixed
**Role:** replication (exploratory)
**Period:** goal #42 · regime III · units 42a, 42b · N 15, 16 · 1123 trimmed minutes.

## Why this period
Eligible for the replication layer (≥ 3 agents with ≥ 30 record minutes, ≥ 60 trimmed minutes per day).

## Prediction
*The card's rule, written 2026-10-04 20:22 UTC before any H99 statistic and amended before real data (A1, 20:41 UTC) and after the first run (A2, 20:45 UTC, post hoc for talk); this folder was written after the run and copies it.* Glauber consistency: no field call on the talk channel (A2 rule: |Δρ| < 0.03 or CI covering 0) in units with a resolved fluctuation gain. Supported if every resolved talk unit is consistent; failed if most resolved units carry a field call; descriptive if no unit has a resolved g_χ; mixed otherwise. Regime III is predicted to be consistent (P1).

## Result

| Unit | channel | g_χ [95%] | ρ_c(1) | ρ_⊥(1) | gap (Δρ₁ talk / Δg₁ other) [95%] | lag 2 | call |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 42a | act | 0.050 [-0.054, 0.146] | 0.38 | 0.38 | -0.039 [-0.398, 0.171] | -0.001 | unresolved |
| 42a | content | 0.562 [0.486, 0.632] | 0.45 | 0.21 | -0.065 [-0.236, 0.131] | 0.031 | consistent |
| 42a | talk | 0.350 [0.006, 0.540] | 0.18 | -0.00 | 0.168 [-0.024, 0.245] | -0.034 | consistent (low power) |
| 42b | act | 0.011 [-0.183, 0.151] | 0.44 | 0.39 | 0.105 [-0.069, 0.255] | 0.125 | unresolved |
| 42b | content | 0.303 [0.192, 0.371] | 0.26 | 0.15 | 0.003 [-0.655, 0.200] | 0.102 | consistent (low power) |
| 42b | talk | 0.121 [0.028, 0.217] | 0.09 | 0.00 | 0.081 [0.005, 0.135] | -0.065 | slow |

Period pool (random effects over units, talk): g_χ = 0.200 [-0.014, 0.413], Δρ₁ = 0.105 [0.029, 0.182].

Data: `data/processed/H99-glauber-fluctuation-relaxation/results/units_called.parquet`, `periods.parquet`.

## Scorecard (period-specific axes)
C: g_χ against independence (bootstrap CI and block-shift null). D: the collective relaxation predicted from fluctuations (Δρ, Δg). H: Glauber against fast-field, slow-field and delayed-coupling readings.

## Round 2 (2026-10-04)

*Round-2 tests (card section "Round 2"; predictions written 21:20 UTC and Amendment B1 21:30 UTC, before real data). Exploratory, non-holdout. Talk statistics stay post hoc in the A2 sense.*

| Unit | Δρ₁ V0 (W0-corr.) | Δρ₁ V5 (W0-corr.) | ρ_s − W0 | g₁ room-gated | g₁ in-flight-gated | g₂ room-gated | g₁,fit (R2) | H67 g_lag |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 42a | +0.174 ± 0.077 | +0.152 ± 0.066 | -0.019 [-0.041, -0.003] | +0.268 [+0.219, +0.320] | +0.223 [+0.166, +0.299] | -0.026 [-0.073, +0.011] | +0.33 [+0.00, +0.47] | +0.199 |
| 42b | +0.048 ± 0.022 | +0.032 ± 0.038 | -0.022 [-0.047, +0.001] | +0.104 [-0.049, +0.215] | +0.151 [+0.046, +0.244] | +0.017 [-0.036, +0.044] | +0.10 [+0.00, +0.18] | +0.103 |

Regime III. ± is one SE (block bootstrap and W0 spread). Data: `data/processed/H99-glauber-fluctuation-relaxation/r2/results/r2_units.parquet`.

Reading: the collective talk memory survives scheduler removal where it was present in round 1; reads couple at the next call (room-gated g₁ ≈ H67's g_lag), mostly through named messages. See the card for pooled tests.
