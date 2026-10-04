# H99 × G02: goal period #2

**Verdict:** descriptive
**Role:** replication (exploratory)
**Period:** goal #2 · regime I · units 2 · N 3.5 · 175 trimmed minutes.

## Why this period
Eligible for the replication layer (≥ 3 agents with ≥ 30 record minutes, ≥ 60 trimmed minutes per day).

## Prediction
*The card's rule, written 2026-10-04 20:22 UTC before any H99 statistic and amended before real data (A1, 20:41 UTC) and after the first run (A2, 20:45 UTC, post hoc for talk); this folder was written after the run and copies it.* Glauber consistency: no field call on the talk channel (A2 rule: |Δρ| < 0.03 or CI covering 0) in units with a resolved fluctuation gain. Supported if every resolved talk unit is consistent; failed if most resolved units carry a field call; descriptive if no unit has a resolved g_χ; mixed otherwise. Regime I is predicted to fail in the fast-field direction (P2).

## Result

| Unit | channel | g_χ [95%] | ρ_c(1) | ρ_⊥(1) | gap (Δρ₁ talk / Δg₁ other) [95%] | lag 2 | call |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 2 | act | 0.435 [0.224, 0.573] | 0.34 | 0.29 | -0.312 [-0.900, -0.056] | -0.081 | fast |
| 2 | talk | 0.572 [0.330, 0.678] | 0.28 | 0.10 | -0.096 [-0.173, 0.251] | -0.182 | consistent (low power) |

Period pool (random effects over units, talk): g_χ = 0.572 [0.385, 0.759], Δρ₁ = -0.096 [-0.398, 0.205].

Data: `data/processed/H99-glauber-fluctuation-relaxation/results/units_called.parquet`, `periods.parquet`.

## Scorecard (period-specific axes)
C: g_χ against independence (bootstrap CI and block-shift null). D: the collective relaxation predicted from fluctuations (Δρ, Δg). H: Glauber against fast-field, slow-field and delayed-coupling readings.
