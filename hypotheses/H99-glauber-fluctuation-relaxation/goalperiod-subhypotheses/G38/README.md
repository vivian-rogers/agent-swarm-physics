# H99 × G38: goal period #38

**Verdict:** descriptive
**Role:** replication (exploratory)
**Period:** goal #38 · regime III · units 38a, 38b, 38c, 38d, 38e · N 12, 12, 13, 12.5, 14 · 3334 trimmed minutes.

## Why this period
Eligible for the replication layer (≥ 3 agents with ≥ 30 record minutes, ≥ 60 trimmed minutes per day).

## Prediction
*The card's rule, written 2026-10-04 20:22 UTC before any H99 statistic and amended before real data (A1, 20:41 UTC) and after the first run (A2, 20:45 UTC, post hoc for talk); this folder was written after the run and copies it.* Glauber consistency: no field call on the talk channel (A2 rule: |Δρ| < 0.03 or CI covering 0) in units with a resolved fluctuation gain. Supported if every resolved talk unit is consistent; failed if most resolved units carry a field call; descriptive if no unit has a resolved g_χ; mixed otherwise. Regime III is predicted to be consistent (P1).

## Result

| Unit | channel | g_χ [95%] | ρ_c(1) | ρ_⊥(1) | gap (Δρ₁ talk / Δg₁ other) [95%] | lag 2 | call |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 38a | act | 0.039 [-0.035, 0.101] | 0.37 | 0.32 | 0.096 [-0.005, 0.192] | 0.076 | unresolved |
| 38a | content | 0.542 [0.465, 0.602] | 0.64 | 0.49 | -0.170 [-0.275, -0.079] | -0.171 | fast |
| 38a | talk | 0.129 [0.062, 0.189] | 0.09 | 0.02 | 0.052 [-0.003, 0.101] | -0.013 | consistent (low power) |
| 38b | act | 0.165 [0.040, 0.266] | 0.36 | 0.28 | 0.028 [-0.224, 0.189] | 0.034 | consistent |
| 38b | content | 0.369 [0.238, 0.455] | 0.40 | 0.27 | -0.073 [-0.205, 0.044] | -0.101 | consistent |
| 38b | talk | 0.083 [-0.071, 0.200] | -0.00 | -0.04 | -0.002 [-0.083, 0.079] | -0.040 | unresolved |
| 38c | act | -0.161 [-0.431, 0.101] | 0.25 | 0.30 | 0.030 [-0.306, 0.191] | -0.046 | unresolved |
| 38c | talk | 0.082 [-0.004, 0.114] | 0.10 | -0.00 | 0.096 [0.013, 0.140] | -0.004 | slow (g unresolved) |
| 38d | act | -0.075 [-0.478, 0.133] | 0.35 | 0.31 | 0.189 [-0.392, 0.344] | 0.122 | unresolved |
| 38d | content | 0.240 [0.129, 0.357] | 0.13 | 0.13 | -0.219 [-0.996, 0.098] | – | consistent (low power) |
| 38d | talk | 0.066 [-0.120, 0.203] | -0.15 | -0.08 | -0.151 [-0.231, -0.078] | 0.002 | fast (g unresolved) |
| 38e | act | 0.058 [-0.167, 0.271] | 0.32 | 0.32 | -0.051 [-0.333, 0.231] | -0.181 | unresolved |
| 38e | content | 0.403 [0.237, 0.522] | 0.49 | 0.38 | -0.146 [-0.386, 0.058] | -0.216 | consistent |
| 38e | talk | 0.041 [-0.104, 0.161] | -0.09 | -0.09 | -0.095 [-0.268, 0.055] | -0.071 | unresolved |

Period pool (random effects over units, talk): g_χ = 0.095 [0.057, 0.134], Δρ₁ = -0.010 [-0.099, 0.079].

Data: `data/processed/H99-glauber-fluctuation-relaxation/results/units_called.parquet`, `periods.parquet`.

## Scorecard (period-specific axes)
C: g_χ against independence (bootstrap CI and block-shift null). D: the collective relaxation predicted from fluctuations (Δρ, Δg). H: Glauber against fast-field, slow-field and delayed-coupling readings.
