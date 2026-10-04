# H99 × G17: goal period #17

**Verdict:** descriptive
**Role:** replication (exploratory)
**Period:** goal #17 · regime I · units 17 · N 7 · 883 trimmed minutes.

## Why this period
Eligible for the replication layer (≥ 3 agents with ≥ 30 record minutes, ≥ 60 trimmed minutes per day).

## Prediction
*The card's rule, written 2026-10-04 20:22 UTC before any H99 statistic and amended before real data (A1, 20:41 UTC) and after the first run (A2, 20:45 UTC, post hoc for talk); this folder was written after the run and copies it.* Glauber consistency: no field call on the talk channel (A2 rule: |Δρ| < 0.03 or CI covering 0) in units with a resolved fluctuation gain. Supported if every resolved talk unit is consistent; failed if most resolved units carry a field call; descriptive if no unit has a resolved g_χ; mixed otherwise. Regime I is predicted to fail in the fast-field direction (P2).

## Result

| Unit | channel | g_χ [95%] | ρ_c(1) | ρ_⊥(1) | gap (Δρ₁ talk / Δg₁ other) [95%] | lag 2 | call |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 17 | act | 0.202 [0.115, 0.266] | 0.12 | 0.26 | -0.806 [-1.810, -0.339] | -1.368 | fast |
| 17 | content | 0.633 [0.490, 0.725] | 0.56 | 0.39 | -0.240 [-0.510, -0.106] | -0.206 | fast |
| 17 | talk | 0.434 [0.327, 0.519] | 0.05 | 0.02 | -0.047 [-0.156, 0.094] | -0.184 | consistent (low power) |

Period pool (random effects over units, talk): g_χ = 0.434 [0.339, 0.528], Δρ₁ = -0.047 [-0.176, 0.081].

Data: `data/processed/H99-glauber-fluctuation-relaxation/results/units_called.parquet`, `periods.parquet`.

## Scorecard (period-specific axes)
C: g_χ against independence (bootstrap CI and block-shift null). D: the collective relaxation predicted from fluctuations (Δρ, Δg). H: Glauber against fast-field, slow-field and delayed-coupling readings.
