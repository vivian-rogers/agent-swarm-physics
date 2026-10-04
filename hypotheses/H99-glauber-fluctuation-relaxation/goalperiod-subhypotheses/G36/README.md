# H99 × G36: goal period #36

**Verdict:** failed
**Role:** replication (exploratory)
**Period:** goal #36 · regime II · units 36a, 36b, 36c · N 12, 12, 12 · 1184 trimmed minutes.

## Why this period
Eligible for the replication layer (≥ 3 agents with ≥ 30 record minutes, ≥ 60 trimmed minutes per day).

## Prediction
*The card's rule, written 2026-10-04 20:22 UTC before any H99 statistic and amended before real data (A1, 20:41 UTC) and after the first run (A2, 20:45 UTC, post hoc for talk); this folder was written after the run and copies it.* Glauber consistency: no field call on the talk channel (A2 rule: |Δρ| < 0.03 or CI covering 0) in units with a resolved fluctuation gain. Supported if every resolved talk unit is consistent; failed if most resolved units carry a field call; descriptive if no unit has a resolved g_χ; mixed otherwise. 

## Result

| Unit | channel | g_χ [95%] | ρ_c(1) | ρ_⊥(1) | gap (Δρ₁ talk / Δg₁ other) [95%] | lag 2 | call |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 36a | act | 0.086 [0.011, 0.197] | 0.31 | 0.24 | 0.093 [-0.099, 0.303] | 0.326 | consistent |
| 36a | talk | 0.139 [-0.038, 0.251] | 0.07 | 0.01 | 0.046 [-0.037, 0.078] | 0.060 | unresolved |
| 36b | act | 0.010 [-0.190, 0.155] | 0.44 | 0.43 | 0.014 [-0.072, 0.143] | 0.050 | unresolved |
| 36b | content | 0.422 [0.374, 0.451] | 0.38 | 0.12 | 0.116 [0.031, 0.205] | 0.308 | slow |
| 36b | talk | 0.124 [-0.036, 0.264] | 0.08 | 0.05 | 0.011 [-0.051, 0.073] | 0.066 | unresolved |
| 36c | act | 0.093 [-0.007, 0.182] | 0.48 | 0.46 | -0.054 [-0.155, 0.070] | 0.061 | unresolved |
| 36c | content | 0.439 [0.271, 0.549] | 0.39 | 0.16 | 0.046 [-0.037, 0.093] | 0.153 | consistent |
| 36c | talk | 0.226 [0.067, 0.329] | 0.22 | 0.04 | 0.137 [0.017, 0.244] | 0.093 | slow |

Period pool (random effects over units, talk): g_χ = 0.171 [0.088, 0.253], Δρ₁ = 0.049 [-0.008, 0.106].

Data: `data/processed/H99-glauber-fluctuation-relaxation/results/units_called.parquet`, `periods.parquet`.

## Scorecard (period-specific axes)
C: g_χ against independence (bootstrap CI and block-shift null). D: the collective relaxation predicted from fluctuations (Δρ, Δg). H: Glauber against fast-field, slow-field and delayed-coupling readings.

## Round 2 (2026-10-04)

*Round-2 tests (card section "Round 2"; predictions written 21:20 UTC and Amendment B1 21:30 UTC, before real data). Exploratory, non-holdout. Talk statistics stay post hoc in the A2 sense.*

| Unit | Δρ₁ V0 (W0-corr.) | Δρ₁ V5 (W0-corr.) | ρ_s − W0 | g₁ room-gated | g₁ in-flight-gated | g₂ room-gated | g₁,fit (R2) | H67 g_lag |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 36a | +0.083 ± 0.043 | -0.007 ± 0.046 | +0.114 [+0.095, +0.149] | -0.028 [-0.082, +0.019] | -0.030 [-0.085, +0.025] | -0.065 [-0.191, +0.011] | +0.33 [+0.11, +0.57] | -0.060 |
| 36b | -0.014 ± 0.038 | +0.077 ± 0.088 | -0.054 [-0.117, +0.048] | +0.112 [+0.031, +0.209] | +0.149 [+0.077, +0.220] | +0.088 [+0.025, +0.155] | +0.13 [+0.00, +0.32] | +0.094 |
| 36c | +0.116 ± 0.068 | +0.238 ± 0.061 | -0.042 [-0.058, -0.028] | +0.213 [+0.152, +0.275] | +0.193 [+0.129, +0.277] | +0.049 [-0.003, +0.102] | +0.39 [+0.00, +0.74] | +0.151 |

Regime II. ± is one SE (block bootstrap and W0 spread). Data: `data/processed/H99-glauber-fluctuation-relaxation/r2/results/r2_units.parquet`.

Reading (descriptive): regime II, three units in all; see the card.
