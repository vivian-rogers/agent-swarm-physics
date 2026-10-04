# H99 × G41: goal period #41

**Verdict:** failed
**Role:** replication (exploratory)
**Period:** goal #41 · regime III · units 41 · N 15 · 1024 trimmed minutes.

## Why this period
Eligible for the replication layer (≥ 3 agents with ≥ 30 record minutes, ≥ 60 trimmed minutes per day).

## Prediction
*The card's rule, written 2026-10-04 20:22 UTC before any H99 statistic and amended before real data (A1, 20:41 UTC) and after the first run (A2, 20:45 UTC, post hoc for talk); this folder was written after the run and copies it.* Glauber consistency: no field call on the talk channel (A2 rule: |Δρ| < 0.03 or CI covering 0) in units with a resolved fluctuation gain. Supported if every resolved talk unit is consistent; failed if most resolved units carry a field call; descriptive if no unit has a resolved g_χ; mixed otherwise. Regime III is predicted to be consistent (P1).

## Result

| Unit | channel | g_χ [95%] | ρ_c(1) | ρ_⊥(1) | gap (Δρ₁ talk / Δg₁ other) [95%] | lag 2 | call |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 41 | act | 0.010 [-0.089, 0.091] | 0.33 | 0.34 | -0.018 [-0.223, 0.133] | 0.260 | slow (g unresolved) |
| 41 | content | 0.620 [0.563, 0.672] | 0.48 | 0.34 | -0.307 [-0.423, -0.214] | -0.330 | fast |
| 41 | talk | 0.206 [0.092, 0.311] | 0.09 | -0.03 | 0.086 [-0.017, 0.199] | 0.080 | slow |

Period pool (random effects over units, talk): g_χ = 0.206 [0.098, 0.315], Δρ₁ = 0.086 [-0.023, 0.196].

Data: `data/processed/H99-glauber-fluctuation-relaxation/results/units_called.parquet`, `periods.parquet`.

## Scorecard (period-specific axes)
C: g_χ against independence (bootstrap CI and block-shift null). D: the collective relaxation predicted from fluctuations (Δρ, Δg). H: Glauber against fast-field, slow-field and delayed-coupling readings.
