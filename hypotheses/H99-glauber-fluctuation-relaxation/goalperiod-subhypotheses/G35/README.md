# H99 × G35: goal period #35

**Verdict:** failed
**Role:** replication (exploratory)
**Period:** goal #35 · regime II · units 35 · N 12 · 1170 trimmed minutes.

## Why this period
Eligible for the replication layer (≥ 3 agents with ≥ 30 record minutes, ≥ 60 trimmed minutes per day).

## Prediction
*The card's rule, written 2026-10-04 20:22 UTC before any H99 statistic and amended before real data (A1, 20:41 UTC) and after the first run (A2, 20:45 UTC, post hoc for talk); this folder was written after the run and copies it.* Glauber consistency: no field call on the talk channel (A2 rule: |Δρ| < 0.03 or CI covering 0) in units with a resolved fluctuation gain. Supported if every resolved talk unit is consistent; failed if most resolved units carry a field call; descriptive if no unit has a resolved g_χ; mixed otherwise. 

## Result

| Unit | channel | g_χ [95%] | ρ_c(1) | ρ_⊥(1) | gap (Δρ₁ talk / Δg₁ other) [95%] | lag 2 | call |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 35 | act | 0.187 [-0.045, 0.389] | 0.34 | 0.22 | 0.103 [-0.021, 0.204] | 0.141 | unresolved |
| 35 | content | 0.752 [0.703, 0.793] | 0.50 | 0.28 | -0.282 [-0.357, -0.182] | -0.282 | fast |
| 35 | talk | 0.128 [0.032, 0.214] | 0.15 | 0.05 | 0.086 [0.035, 0.134] | -0.032 | slow |

Period pool (random effects over units, talk): g_χ = 0.128 [0.034, 0.222], Δρ₁ = 0.086 [0.037, 0.136].

Data: `data/processed/H99-glauber-fluctuation-relaxation/results/units_called.parquet`, `periods.parquet`.

## Scorecard (period-specific axes)
C: g_χ against independence (bootstrap CI and block-shift null). D: the collective relaxation predicted from fluctuations (Δρ, Δg). H: Glauber against fast-field, slow-field and delayed-coupling readings.

## Round 2 (2026-10-04)

*Round-2 tests (card section "Round 2"; predictions written 21:20 UTC and Amendment B1 21:30 UTC, before real data). Exploratory, non-holdout. Talk statistics stay post hoc in the A2 sense.*

| Unit | Δρ₁ V0 (W0-corr.) | Δρ₁ V5 (W0-corr.) | ρ_s − W0 | g₁ room-gated | g₁ in-flight-gated | g₂ room-gated | g₁,fit (R2) | H67 g_lag |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 35 | +0.127 ± 0.027 | +0.108 ± 0.039 | +0.157 [+0.121, +0.195] | +0.092 [+0.056, +0.135] | +0.050 [+0.018, +0.080] | -0.009 [-0.039, +0.022] | +0.28 [+0.22, +0.38] | +0.046 |

Regime II. ± is one SE (block bootstrap and W0 spread). Data: `data/processed/H99-glauber-fluctuation-relaxation/r2/results/r2_units.parquet`.

Reading (descriptive): regime II, three units in all; see the card.
