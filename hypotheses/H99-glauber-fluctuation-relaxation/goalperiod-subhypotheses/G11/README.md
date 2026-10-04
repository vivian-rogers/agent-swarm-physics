# H99 × G11: goal period #11

**Verdict:** descriptive
**Role:** replication (exploratory)
**Period:** goal #11 · regime I · units 11 · N 7 · 796 trimmed minutes.

## Why this period
Eligible for the replication layer (≥ 3 agents with ≥ 30 record minutes, ≥ 60 trimmed minutes per day).

## Prediction
*The card's rule, written 2026-10-04 20:22 UTC before any H99 statistic and amended before real data (A1, 20:41 UTC) and after the first run (A2, 20:45 UTC, post hoc for talk); this folder was written after the run and copies it.* Glauber consistency: no field call on the talk channel (A2 rule: |Δρ| < 0.03 or CI covering 0) in units with a resolved fluctuation gain. Supported if every resolved talk unit is consistent; failed if most resolved units carry a field call; descriptive if no unit has a resolved g_χ; mixed otherwise. Regime I is predicted to fail in the fast-field direction (P2).

## Result

| Unit | channel | g_χ [95%] | ρ_c(1) | ρ_⊥(1) | gap (Δρ₁ talk / Δg₁ other) [95%] | lag 2 | call |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 11 | act | 0.243 [0.071, 0.386] | 0.23 | 0.13 | 0.032 [-0.295, 0.186] | 0.126 | consistent (low power) |
| 11 | content | 0.538 [0.353, 0.658] | 0.50 | 0.38 | -0.263 [-0.453, -0.129] | -0.251 | fast |
| 11 | talk | 0.201 [0.067, 0.348] | 0.16 | 0.00 | 0.154 [-0.009, 0.286] | 0.112 | consistent (low power) |

Period pool (random effects over units, talk): g_χ = 0.201 [0.051, 0.350], Δρ₁ = 0.154 [-0.002, 0.310].

Data: `data/processed/H99-glauber-fluctuation-relaxation/results/units_called.parquet`, `periods.parquet`.

## Scorecard (period-specific axes)
C: g_χ against independence (bootstrap CI and block-shift null). D: the collective relaxation predicted from fluctuations (Δρ, Δg). H: Glauber against fast-field, slow-field and delayed-coupling readings.
