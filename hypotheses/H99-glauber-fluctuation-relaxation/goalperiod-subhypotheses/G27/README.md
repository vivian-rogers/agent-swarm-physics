# H99 × G27: goal period #27

**Verdict:** descriptive
**Role:** replication (exploratory)
**Period:** goal #27 · regime I · units 27 · N 10 · 2328 trimmed minutes.

## Why this period
Eligible for the replication layer (≥ 3 agents with ≥ 30 record minutes, ≥ 60 trimmed minutes per day).

## Prediction
*The card's rule, written 2026-10-04 20:22 UTC before any H99 statistic and amended before real data (A1, 20:41 UTC) and after the first run (A2, 20:45 UTC, post hoc for talk); this folder was written after the run and copies it.* Glauber consistency: no field call on the talk channel (A2 rule: |Δρ| < 0.03 or CI covering 0) in units with a resolved fluctuation gain. Supported if every resolved talk unit is consistent; failed if most resolved units carry a field call; descriptive if no unit has a resolved g_χ; mixed otherwise. Regime I is predicted to fail in the fast-field direction (P2).

## Result

| Unit | channel | g_χ [95%] | ρ_c(1) | ρ_⊥(1) | gap (Δρ₁ talk / Δg₁ other) [95%] | lag 2 | call |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 27 | act | 0.086 [0.026, 0.141] | 0.16 | 0.20 | -0.217 [-0.384, -0.063] | -0.114 | fast |
| 27 | content | 0.690 [0.636, 0.738] | 0.59 | 0.34 | -0.176 [-0.275, -0.103] | -0.324 | fast |
| 27 | talk | 0.080 [0.016, 0.135] | -0.01 | 0.00 | -0.016 [-0.059, 0.016] | -0.070 | consistent (low power) |

Period pool (random effects over units, talk): g_χ = 0.080 [0.017, 0.142], Δρ₁ = -0.016 [-0.053, 0.021].

Data: `data/processed/H99-glauber-fluctuation-relaxation/results/units_called.parquet`, `periods.parquet`.

## Scorecard (period-specific axes)
C: g_χ against independence (bootstrap CI and block-shift null). D: the collective relaxation predicted from fluctuations (Δρ, Δg). H: Glauber against fast-field, slow-field and delayed-coupling readings.
