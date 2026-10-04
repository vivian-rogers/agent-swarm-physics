# H99 × G20: goal period #20

**Verdict:** descriptive
**Role:** replication (exploratory)
**Period:** goal #20 · regime I · units 20a, 20b, 20c, 20d · N 8, 9, 9, 10 · 2048 trimmed minutes.

## Why this period
Eligible for the replication layer (≥ 3 agents with ≥ 30 record minutes, ≥ 60 trimmed minutes per day).

## Prediction
*The card's rule, written 2026-10-04 20:22 UTC before any H99 statistic and amended before real data (A1, 20:41 UTC) and after the first run (A2, 20:45 UTC, post hoc for talk); this folder was written after the run and copies it.* Glauber consistency: no field call on the talk channel (A2 rule: |Δρ| < 0.03 or CI covering 0) in units with a resolved fluctuation gain. Supported if every resolved talk unit is consistent; failed if most resolved units carry a field call; descriptive if no unit has a resolved g_χ; mixed otherwise. Regime I is predicted to fail in the fast-field direction (P2).

## Result

| Unit | channel | g_χ [95%] | ρ_c(1) | ρ_⊥(1) | gap (Δρ₁ talk / Δg₁ other) [95%] | lag 2 | call |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 20a | act | 0.024 [-0.138, 0.151] | 0.11 | 0.11 | -0.037 [-0.700, 0.280] | -0.243 | unresolved |
| 20a | content | 0.776 [0.661, 0.856] | 0.65 | 0.32 | -0.146 [-0.164, -0.132] | -0.188 | fast |
| 20a | talk | 0.194 [-0.013, 0.341] | 0.16 | 0.02 | 0.109 [0.036, 0.175] | -0.056 | slow (g unresolved) |
| 20b | act | -0.093 [-0.137, -0.029] | 0.10 | 0.25 | -0.528 [-1.816, 0.096] | -0.157 | unresolved |
| 20b | talk | 0.126 [-0.184, 0.330] | 0.07 | -0.02 | 0.071 [-0.016, 0.135] | 0.060 | unresolved |
| 20c | act | -0.003 [-0.105, 0.096] | 0.17 | 0.16 | 0.024 [-0.517, 0.256] | -0.005 | unresolved |
| 20c | content | 0.458 [0.324, 0.547] | 0.44 | 0.37 | -0.287 [-0.420, -0.130] | -0.506 | fast |
| 20c | talk | 0.167 [0.050, 0.275] | 0.02 | 0.01 | -0.006 [-0.091, 0.098] | -0.041 | consistent (low power) |
| 20d | act | 0.058 [-0.031, 0.118] | 0.17 | 0.16 | -0.015 [-0.596, 0.245] | -0.120 | unresolved |
| 20d | content | 0.797 [0.756, 0.831] | 0.65 | 0.36 | -0.217 [-0.322, -0.130] | -0.272 | fast |
| 20d | talk | 0.188 [0.098, 0.269] | 0.13 | 0.04 | 0.061 [-0.025, 0.144] | 0.066 | consistent (low power) |

Period pool (random effects over units, talk): g_χ = 0.180 [0.116, 0.243], Δρ₁ = 0.066 [0.020, 0.111].

Data: `data/processed/H99-glauber-fluctuation-relaxation/results/units_called.parquet`, `periods.parquet`.

## Scorecard (period-specific axes)
C: g_χ against independence (bootstrap CI and block-shift null). D: the collective relaxation predicted from fluctuations (Δρ, Δg). H: Glauber against fast-field, slow-field and delayed-coupling readings.
