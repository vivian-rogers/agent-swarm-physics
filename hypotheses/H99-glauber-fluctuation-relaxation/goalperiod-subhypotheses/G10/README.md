# H99 × G10: goal period #10

**Verdict:** descriptive
**Role:** replication (exploratory)
**Period:** goal #10 · regime I · units 10a, 10b · N 7, 7 · 766 trimmed minutes.

## Why this period
Eligible for the replication layer (≥ 3 agents with ≥ 30 record minutes, ≥ 60 trimmed minutes per day).

## Prediction
*The card's rule, written 2026-10-04 20:22 UTC before any H99 statistic and amended before real data (A1, 20:41 UTC) and after the first run (A2, 20:45 UTC, post hoc for talk); this folder was written after the run and copies it.* Glauber consistency: no field call on the talk channel (A2 rule: |Δρ| < 0.03 or CI covering 0) in units with a resolved fluctuation gain. Supported if every resolved talk unit is consistent; failed if most resolved units carry a field call; descriptive if no unit has a resolved g_χ; mixed otherwise. Regime I is predicted to fail in the fast-field direction (P2).

## Result

| Unit | channel | g_χ [95%] | ρ_c(1) | ρ_⊥(1) | gap (Δρ₁ talk / Δg₁ other) [95%] | lag 2 | call |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 10a | act | 0.641 [0.229, 0.753] | 0.55 | 0.25 | -0.072 [-0.313, 0.134] | -0.104 | consistent |
| 10a | content | 0.321 [-0.226, 0.470] | 0.17 | 0.27 | -0.656 [-1.075, -0.142] | 0.231 | fast (g unresolved) |
| 10a | talk | 0.322 [0.244, 0.372] | 0.09 | -0.02 | 0.076 [-0.124, 0.290] | 0.018 | consistent (low power) |
| 10b | act | -0.024 [-0.173, 0.109] | 0.21 | 0.23 | -0.030 [-0.346, 0.257] | -0.011 | unresolved |
| 10b | content | 0.055 [-0.131, 0.248] | 0.28 | 0.33 | -0.189 [-0.384, -0.005] | -0.080 | fast (g unresolved) |
| 10b | talk | 0.110 [-0.017, 0.203] | 0.04 | -0.00 | 0.036 [-0.092, 0.121] | 0.005 | unresolved |

Period pool (random effects over units, talk): g_χ = 0.222 [0.014, 0.430], Δρ₁ = 0.045 [-0.055, 0.145].

Data: `data/processed/H99-glauber-fluctuation-relaxation/results/units_called.parquet`, `periods.parquet`.

## Scorecard (period-specific axes)
C: g_χ against independence (bootstrap CI and block-shift null). D: the collective relaxation predicted from fluctuations (Δρ, Δg). H: Glauber against fast-field, slow-field and delayed-coupling readings.
