# H99 × G44: goal period #44

**Verdict:** descriptive
**Role:** replication (exploratory)
**Period:** goal #44 · regime III · units 44a, 44b · N 15.5, 17 · 654 trimmed minutes.

## Why this period
Eligible for the replication layer (≥ 3 agents with ≥ 30 record minutes, ≥ 60 trimmed minutes per day).

## Prediction
*The card's rule, written 2026-10-04 20:22 UTC before any H99 statistic and amended before real data (A1, 20:41 UTC) and after the first run (A2, 20:45 UTC, post hoc for talk); this folder was written after the run and copies it.* Glauber consistency: no field call on the talk channel (A2 rule: |Δρ| < 0.03 or CI covering 0) in units with a resolved fluctuation gain. Supported if every resolved talk unit is consistent; failed if most resolved units carry a field call; descriptive if no unit has a resolved g_χ; mixed otherwise. Regime III is predicted to be consistent (P1).

## Result

| Unit | channel | g_χ [95%] | ρ_c(1) | ρ_⊥(1) | gap (Δρ₁ talk / Δg₁ other) [95%] | lag 2 | call |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 44a | act | 0.071 [-0.176, 0.209] | 0.41 | 0.41 | -0.068 [-0.568, 0.308] | -0.159 | unresolved |
| 44a | content | 0.425 [0.356, 0.479] | 0.24 | 0.16 | -0.224 [-0.779, -0.038] | -0.163 | fast |
| 44a | talk | -0.047 [-0.225, 0.053] | 0.03 | -0.05 | 0.028 [-0.101, 0.155] | -0.040 | unresolved |
| 44b | act | 0.113 [-0.036, 0.269] | 0.31 | 0.39 | -0.348 [-0.744, 0.017] | -0.054 | unresolved |
| 44b | content | 0.578 [0.519, 0.637] | 0.28 | 0.15 | -0.249 [-0.399, -0.031] | – | fast |
| 44b | talk | 0.091 [-0.047, 0.224] | 0.14 | -0.03 | 0.142 [0.053, 0.269] | 0.092 | slow (g unresolved) |

Period pool (random effects over units, talk): g_χ = 0.025 [-0.111, 0.160], Δρ₁ = 0.088 [-0.023, 0.199].

Data: `data/processed/H99-glauber-fluctuation-relaxation/results/units_called.parquet`, `periods.parquet`.

## Scorecard (period-specific axes)
C: g_χ against independence (bootstrap CI and block-shift null). D: the collective relaxation predicted from fluctuations (Δρ, Δg). H: Glauber against fast-field, slow-field and delayed-coupling readings.
