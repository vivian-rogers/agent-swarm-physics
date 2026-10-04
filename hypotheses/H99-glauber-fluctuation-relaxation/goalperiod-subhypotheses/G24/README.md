# H99 × G24: goal period #24

**Verdict:** descriptive
**Role:** replication (exploratory)
**Period:** goal #24 · regime I · units 24 · N 10 · 935 trimmed minutes.

## Why this period
Eligible for the replication layer (≥ 3 agents with ≥ 30 record minutes, ≥ 60 trimmed minutes per day).

## Prediction
*The card's rule, written 2026-10-04 20:22 UTC before any H99 statistic and amended before real data (A1, 20:41 UTC) and after the first run (A2, 20:45 UTC, post hoc for talk); this folder was written after the run and copies it.* Glauber consistency: no field call on the talk channel (A2 rule: |Δρ| < 0.03 or CI covering 0) in units with a resolved fluctuation gain. Supported if every resolved talk unit is consistent; failed if most resolved units carry a field call; descriptive if no unit has a resolved g_χ; mixed otherwise. Regime I is predicted to fail in the fast-field direction (P2).

## Result

| Unit | channel | g_χ [95%] | ρ_c(1) | ρ_⊥(1) | gap (Δρ₁ talk / Δg₁ other) [95%] | lag 2 | call |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 24 | act | -0.041 [-0.137, 0.030] | 0.17 | 0.18 | 0.004 [-0.405, 0.261] | 0.049 | unresolved |
| 24 | content | 0.600 [0.415, 0.709] | 0.60 | 0.41 | -0.186 [-0.270, -0.051] | -0.372 | fast |
| 24 | talk | 0.221 [0.142, 0.287] | 0.06 | -0.01 | 0.059 [-0.023, 0.124] | -0.019 | consistent (low power) |

Period pool (random effects over units, talk): g_χ = 0.221 [0.146, 0.295], Δρ₁ = 0.059 [-0.014, 0.132].

Data: `data/processed/H99-glauber-fluctuation-relaxation/results/units_called.parquet`, `periods.parquet`.

## Scorecard (period-specific axes)
C: g_χ against independence (bootstrap CI and block-shift null). D: the collective relaxation predicted from fluctuations (Δρ, Δg). H: Glauber against fast-field, slow-field and delayed-coupling readings.
