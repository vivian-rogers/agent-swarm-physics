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
