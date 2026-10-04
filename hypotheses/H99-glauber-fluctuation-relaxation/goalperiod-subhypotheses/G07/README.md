# H99 × G07: goal period #7

**Verdict:** descriptive
**Role:** replication (exploratory)
**Period:** goal #7 · regime I · units 7 · N 4 · 238 trimmed minutes.

## Why this period
Eligible for the replication layer (≥ 3 agents with ≥ 30 record minutes, ≥ 60 trimmed minutes per day).

## Prediction
*The card's rule, written 2026-10-04 20:22 UTC before any H99 statistic and amended before real data (A1, 20:41 UTC) and after the first run (A2, 20:45 UTC, post hoc for talk); this folder was written after the run and copies it.* Glauber consistency: no field call on the talk channel (A2 rule: |Δρ| < 0.03 or CI covering 0) in units with a resolved fluctuation gain. Supported if every resolved talk unit is consistent; failed if most resolved units carry a field call; descriptive if no unit has a resolved g_χ; mixed otherwise. Regime I is predicted to fail in the fast-field direction (P2).

## Result

| Unit | channel | g_χ [95%] | ρ_c(1) | ρ_⊥(1) | gap (Δρ₁ talk / Δg₁ other) [95%] | lag 2 | call |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 7 | act | 0.003 [-0.105, 0.090] | 0.09 | 0.17 | -0.350 [–, –] | -1.275 | unresolved |
| 7 | talk | 0.131 [-0.053, 0.272] | 0.29 | 0.22 | 0.021 [-0.134, 0.149] | 0.104 | unresolved |

Period pool (random effects over units, talk): g_χ = 0.131 [-0.024, 0.285], Δρ₁ = 0.021 [-0.123, 0.165].

Data: `data/processed/H99-glauber-fluctuation-relaxation/results/units_called.parquet`, `periods.parquet`.

## Scorecard (period-specific axes)
C: g_χ against independence (bootstrap CI and block-shift null). D: the collective relaxation predicted from fluctuations (Δρ, Δg). H: Glauber against fast-field, slow-field and delayed-coupling readings.
