# H99 × G06: goal period #6

**Verdict:** descriptive
**Role:** replication (exploratory)
**Period:** goal #6 · regime I · units 6a, 6b · N 4, 4 · 2593 trimmed minutes.

## Why this period
Eligible for the replication layer (≥ 3 agents with ≥ 30 record minutes, ≥ 60 trimmed minutes per day).

## Prediction
*The card's rule, written 2026-10-04 20:22 UTC before any H99 statistic and amended before real data (A1, 20:41 UTC) and after the first run (A2, 20:45 UTC, post hoc for talk); this folder was written after the run and copies it.* Glauber consistency: no field call on the talk channel (A2 rule: |Δρ| < 0.03 or CI covering 0) in units with a resolved fluctuation gain. Supported if every resolved talk unit is consistent; failed if most resolved units carry a field call; descriptive if no unit has a resolved g_χ; mixed otherwise. Regime I is predicted to fail in the fast-field direction (P2).

## Result

| Unit | channel | g_χ [95%] | ρ_c(1) | ρ_⊥(1) | gap (Δρ₁ talk / Δg₁ other) [95%] | lag 2 | call |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 6a | act | 0.451 [0.238, 0.626] | 0.44 | 0.28 | -0.099 [-0.343, 0.046] | -0.062 | consistent |
| 6a | content | 0.530 [0.294, 0.681] | 0.62 | 0.40 | -0.058 [-0.300, 0.079] | -0.083 | consistent |
| 6a | talk | 0.324 [0.168, 0.462] | 0.22 | 0.07 | 0.063 [-0.032, 0.167] | -0.056 | consistent (low power) |
| 6b | act | -0.034 [-0.150, 0.069] | 0.08 | 0.16 | -0.377 [-1.674, 0.118] | -0.232 | unresolved |
| 6b | content | 0.280 [0.159, 0.376] | 0.55 | 0.46 | -0.061 [-0.184, 0.033] | 0.045 | consistent |
| 6b | talk | 0.133 [-0.045, 0.282] | 0.08 | 0.07 | -0.025 [-0.091, 0.048] | 0.016 | unresolved |

Talk kick layer (human messages as a field on the room; distributed-lag kernel of the room's talk count; decay ratio λ = Σβ₁…₅ / Σβ₀…₄; A2 estimator):

| Unit | kicks | response at lags 0–1 [95%] | λ_kick [95%] | Glauber λ_c | measured ρ_c(1) | ρ_⊥(1) |
| --- | --- | --- | --- | --- | --- | --- |
| 6a | 386 | 0.08 [-0.04, 0.32] | 0.02 [-3.75, 0.74] | 0.161 | 0.224 | 0.067 |
| 6b | 45 | 0.43 [0.05, 1.14] | -0.30 [-20.65, 1.46] | 0.105 | 0.080 | 0.074 |

Period pool (random effects over units, talk): g_χ = 0.233 [0.046, 0.420], Δρ₁ = 0.011 [-0.074, 0.095].

Data: `data/processed/H99-glauber-fluctuation-relaxation/results/units_called.parquet`, `periods.parquet`.

## Scorecard (period-specific axes)
C: g_χ against independence (bootstrap CI and block-shift null). D: the collective relaxation predicted from fluctuations (Δρ, Δg). H: Glauber against fast-field, slow-field and delayed-coupling readings.
