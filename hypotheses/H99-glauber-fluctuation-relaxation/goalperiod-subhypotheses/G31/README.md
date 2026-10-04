# H99 × G31: goal period #31

**Verdict:** descriptive
**Role:** replication (exploratory)
**Period:** goal #31 · regime I · units 31a, 31b, 31c, 31d · N 11, 12, 11, 11 · 1180 trimmed minutes.

## Why this period
Eligible for the replication layer (≥ 3 agents with ≥ 30 record minutes, ≥ 60 trimmed minutes per day).

## Prediction
*The card's rule, written 2026-10-04 20:22 UTC before any H99 statistic and amended before real data (A1, 20:41 UTC) and after the first run (A2, 20:45 UTC, post hoc for talk); this folder was written after the run and copies it.* Glauber consistency: no field call on the talk channel (A2 rule: |Δρ| < 0.03 or CI covering 0) in units with a resolved fluctuation gain. Supported if every resolved talk unit is consistent; failed if most resolved units carry a field call; descriptive if no unit has a resolved g_χ; mixed otherwise. Regime I is predicted to fail in the fast-field direction (P2).

## Result

| Unit | channel | g_χ [95%] | ρ_c(1) | ρ_⊥(1) | gap (Δρ₁ talk / Δg₁ other) [95%] | lag 2 | call |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 31a | act | 0.084 [-0.082, 0.199] | 0.14 | 0.13 | -0.044 [-0.624, 0.325] | -0.244 | unresolved |
| 31a | content | 0.815 [0.724, 0.860] | 0.52 | 0.18 | -0.205 [-0.355, -0.126] | -0.312 | fast |
| 31a | talk | 0.104 [-0.001, 0.183] | 0.15 | 0.03 | 0.114 [0.032, 0.186] | 0.036 | slow (g unresolved) |
| 31b | act | 0.397 [0.201, 0.574] | 0.36 | 0.11 | 0.151 [-1.349, 0.235] | -0.016 | consistent (low power) |
| 31b | content | 0.669 [0.559, 0.727] | 0.20 | 0.08 | -0.309 [-0.392, -0.110] | – | fast |
| 31b | talk | 0.126 [-0.026, 0.278] | 0.08 | -0.05 | 0.078 [-0.036, 0.222] | 0.023 | unresolved |
| 31c | act | -0.102 [-0.431, 0.143] | 0.13 | 0.08 | 0.312 [-0.106, 0.545] | 0.282 | slow (g unresolved) |
| 31c | talk | -0.010 [-0.137, 0.090] | -0.03 | -0.07 | -0.031 [-0.085, 0.023] | 0.034 | unresolved |
| 31d | act | 0.068 [-0.033, 0.134] | 0.18 | 0.10 | 0.197 [-0.078, 0.384] | – | unresolved |
| 31d | talk | 0.109 [0.052, 0.154] | 0.04 | -0.03 | 0.039 [-0.139, 0.204] | -0.039 | consistent (low power) |

Period pool (random effects over units, talk): g_χ = 0.092 [0.044, 0.141], Δρ₁ = 0.047 [-0.039, 0.132].

Data: `data/processed/H99-glauber-fluctuation-relaxation/results/units_called.parquet`, `periods.parquet`.

## Scorecard (period-specific axes)
C: g_χ against independence (bootstrap CI and block-shift null). D: the collective relaxation predicted from fluctuations (Δρ, Δg). H: Glauber against fast-field, slow-field and delayed-coupling readings.
