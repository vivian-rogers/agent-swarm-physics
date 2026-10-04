# H99 × G12: goal period #12

**Verdict:** descriptive
**Role:** replication (exploratory)
**Period:** goal #12 · regime I · units 12a, 12b · N 7, 7 · 836 trimmed minutes.

## Why this period
Eligible for the replication layer (≥ 3 agents with ≥ 30 record minutes, ≥ 60 trimmed minutes per day).

## Prediction
*The card's rule, written 2026-10-04 20:22 UTC before any H99 statistic and amended before real data (A1, 20:41 UTC) and after the first run (A2, 20:45 UTC, post hoc for talk); this folder was written after the run and copies it.* Glauber consistency: no field call on the talk channel (A2 rule: |Δρ| < 0.03 or CI covering 0) in units with a resolved fluctuation gain. Supported if every resolved talk unit is consistent; failed if most resolved units carry a field call; descriptive if no unit has a resolved g_χ; mixed otherwise. Regime I is predicted to fail in the fast-field direction (P2).

## Result

| Unit | channel | g_χ [95%] | ρ_c(1) | ρ_⊥(1) | gap (Δρ₁ talk / Δg₁ other) [95%] | lag 2 | call |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 12a | act | 0.278 [0.178, 0.353] | 0.13 | 0.07 | -0.032 [-0.541, 0.274] | -0.495 | consistent (low power) |
| 12a | content | 0.758 [0.713, 0.792] | 0.20 | 0.19 | -0.722 [-1.049, -0.491] | – | fast |
| 12a | talk | 0.290 [0.205, 0.356] | 0.09 | 0.07 | -0.059 [-0.152, 0.046] | -0.129 | consistent (low power) |
| 12b | act | -0.004 [-0.427, 0.252] | 0.16 | 0.18 | -0.049 [-0.478, 0.232] | 0.287 | unresolved |
| 12b | talk | 0.119 [-0.059, 0.365] | 0.19 | 0.12 | 0.030 [-0.027, 0.061] | 0.149 | slow (g unresolved) |

Period pool (random effects over units, talk): g_χ = 0.234 [0.078, 0.391], Δρ₁ = -0.004 [-0.089, 0.081].

Data: `data/processed/H99-glauber-fluctuation-relaxation/results/units_called.parquet`, `periods.parquet`.

## Scorecard (period-specific axes)
C: g_χ against independence (bootstrap CI and block-shift null). D: the collective relaxation predicted from fluctuations (Δρ, Δg). H: Glauber against fast-field, slow-field and delayed-coupling readings.
