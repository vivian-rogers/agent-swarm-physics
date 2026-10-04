# H99 × G40: goal period #40

**Verdict:** descriptive
**Role:** replication (exploratory)
**Period:** goal #40 · regime III · units 40 · N 15 · 1172 trimmed minutes.

## Why this period
Eligible for the replication layer (≥ 3 agents with ≥ 30 record minutes, ≥ 60 trimmed minutes per day).

## Prediction
*The card's rule, written 2026-10-04 20:22 UTC before any H99 statistic and amended before real data (A1, 20:41 UTC) and after the first run (A2, 20:45 UTC, post hoc for talk); this folder was written after the run and copies it.* Glauber consistency: no field call on the talk channel (A2 rule: |Δρ| < 0.03 or CI covering 0) in units with a resolved fluctuation gain. Supported if every resolved talk unit is consistent; failed if most resolved units carry a field call; descriptive if no unit has a resolved g_χ; mixed otherwise. Regime III is predicted to be consistent (P1).

## Result

| Unit | channel | g_χ [95%] | ρ_c(1) | ρ_⊥(1) | gap (Δρ₁ talk / Δg₁ other) [95%] | lag 2 | call |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 40 | act | 0.070 [-0.045, 0.161] | 0.37 | 0.34 | 0.019 [-0.097, 0.125] | -0.079 | unresolved |
| 40 | content | 0.552 [0.483, 0.602] | 0.52 | 0.39 | -0.240 [-0.557, -0.064] | -0.272 | fast |
| 40 | talk | -0.012 [-0.100, 0.056] | -0.03 | -0.04 | -0.032 [-0.083, 0.008] | 0.013 | unresolved |

Period pool (random effects over units, talk): g_χ = -0.012 [-0.092, 0.068], Δρ₁ = -0.032 [-0.080, 0.015].

Data: `data/processed/H99-glauber-fluctuation-relaxation/results/units_called.parquet`, `periods.parquet`.

## Scorecard (period-specific axes)
C: g_χ against independence (bootstrap CI and block-shift null). D: the collective relaxation predicted from fluctuations (Δρ, Δg). H: Glauber against fast-field, slow-field and delayed-coupling readings.
