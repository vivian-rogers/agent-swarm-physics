# H99 × G33: goal period #33

**Verdict:** descriptive
**Role:** replication (exploratory)
**Period:** goal #33 · regime II · units 33 · N 11 · 574 trimmed minutes.

## Why this period
Eligible for the replication layer (≥ 3 agents with ≥ 30 record minutes, ≥ 60 trimmed minutes per day).

## Prediction
*The card's rule, written 2026-10-04 20:22 UTC before any H99 statistic and amended before real data (A1, 20:41 UTC) and after the first run (A2, 20:45 UTC, post hoc for talk); this folder was written after the run and copies it.* Glauber consistency: no field call on the talk channel (A2 rule: |Δρ| < 0.03 or CI covering 0) in units with a resolved fluctuation gain. Supported if every resolved talk unit is consistent; failed if most resolved units carry a field call; descriptive if no unit has a resolved g_χ; mixed otherwise. 

## Result

| Unit | channel | g_χ [95%] | ρ_c(1) | ρ_⊥(1) | gap (Δρ₁ talk / Δg₁ other) [95%] | lag 2 | call |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 33 | act | 0.126 [-0.044, 0.248] | 0.20 | 0.08 | 0.237 [0.034, 0.421] | 0.222 | slow (g unresolved) |
| 33 | content | 0.861 [0.832, 0.883] | 0.56 | 0.22 | -0.240 [-0.341, -0.153] | -0.280 | fast |
| 33 | talk | 0.098 [-0.025, 0.197] | 0.02 | -0.07 | 0.020 [-0.062, 0.092] | 0.019 | unresolved |

Period pool (random effects over units, talk): g_χ = 0.098 [-0.018, 0.214], Δρ₁ = 0.020 [-0.062, 0.101].

Data: `data/processed/H99-glauber-fluctuation-relaxation/results/units_called.parquet`, `periods.parquet`.

## Scorecard (period-specific axes)
C: g_χ against independence (bootstrap CI and block-shift null). D: the collective relaxation predicted from fluctuations (Δρ, Δg). H: Glauber against fast-field, slow-field and delayed-coupling readings.
