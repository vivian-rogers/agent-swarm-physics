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
