# H99 × G16: goal period #16

**Verdict:** failed
**Role:** replication (exploratory)
**Period:** goal #16 · regime I · units 16 · N 7 · 884 trimmed minutes.

## Why this period
Eligible for the replication layer (≥ 3 agents with ≥ 30 record minutes, ≥ 60 trimmed minutes per day).

## Prediction
*The card's rule, written 2026-10-04 20:22 UTC before any H99 statistic and amended before real data (A1, 20:41 UTC) and after the first run (A2, 20:45 UTC, post hoc for talk); this folder was written after the run and copies it.* Glauber consistency: no field call on the talk channel (A2 rule: |Δρ| < 0.03 or CI covering 0) in units with a resolved fluctuation gain. Supported if every resolved talk unit is consistent; failed if most resolved units carry a field call; descriptive if no unit has a resolved g_χ; mixed otherwise. Regime I is predicted to fail in the fast-field direction (P2).

## Result

| Unit | channel | g_χ [95%] | ρ_c(1) | ρ_⊥(1) | gap (Δρ₁ talk / Δg₁ other) [95%] | lag 2 | call |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 16 | act | 0.330 [0.145, 0.494] | 0.34 | 0.26 | -0.124 [-0.345, 0.001] | -0.368 | consistent |
| 16 | content | 0.417 [0.267, 0.573] | 0.56 | 0.43 | -0.113 [-0.283, 0.016] | -0.218 | consistent |
| 16 | talk | 0.319 [0.243, 0.385] | 0.06 | 0.07 | -0.111 [-0.177, -0.037] | -0.136 | fast |

Period pool (random effects over units, talk): g_χ = 0.319 [0.247, 0.391], Δρ₁ = -0.111 [-0.182, -0.039].

Data: `data/processed/H99-glauber-fluctuation-relaxation/results/units_called.parquet`, `periods.parquet`.

## Scorecard (period-specific axes)
C: g_χ against independence (bootstrap CI and block-shift null). D: the collective relaxation predicted from fluctuations (Δρ, Δg). H: Glauber against fast-field, slow-field and delayed-coupling readings.
