# H99 × G08: goal period #8

**Verdict:** descriptive
**Role:** replication (exploratory)
**Period:** goal #8 · regime I · units 8 · N 4 · 2545 trimmed minutes.

## Why this period
Eligible for the replication layer (≥ 3 agents with ≥ 30 record minutes, ≥ 60 trimmed minutes per day).

## Prediction
*The card's rule, written 2026-10-04 20:22 UTC before any H99 statistic and amended before real data (A1, 20:41 UTC) and after the first run (A2, 20:45 UTC, post hoc for talk); this folder was written after the run and copies it.* Glauber consistency: no field call on the talk channel (A2 rule: |Δρ| < 0.03 or CI covering 0) in units with a resolved fluctuation gain. Supported if every resolved talk unit is consistent; failed if most resolved units carry a field call; descriptive if no unit has a resolved g_χ; mixed otherwise. Regime I is predicted to fail in the fast-field direction (P2).

## Result

| Unit | channel | g_χ [95%] | ρ_c(1) | ρ_⊥(1) | gap (Δρ₁ talk / Δg₁ other) [95%] | lag 2 | call |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 8 | act | 0.204 [0.039, 0.374] | 0.42 | 0.29 | 0.105 [0.019, 0.173] | 0.170 | slow |
| 8 | content | 0.407 [0.305, 0.495] | 0.60 | 0.48 | -0.100 [-0.206, 0.010] | -0.154 | consistent |
| 8 | talk | -0.023 [-0.082, 0.028] | 0.11 | 0.11 | 0.004 [-0.052, 0.051] | -0.038 | unresolved |

Talk kick layer (human messages as a field on the room; distributed-lag kernel of the room's talk count; decay ratio λ = Σβ₁…₅ / Σβ₀…₄; A2 estimator):

| Unit | kicks | response at lags 0–1 [95%] | λ_kick [95%] | Glauber λ_c | measured ρ_c(1) | ρ_⊥(1) |
| --- | --- | --- | --- | --- | --- | --- |
| 8 | 31 | 0.22 [-0.20, 0.71] | 1.07 [-3.57, 4.40] | 0.103 | 0.107 | 0.108 |

Period pool (random effects over units, talk): g_χ = -0.023 [-0.076, 0.029], Δρ₁ = 0.004 [-0.049, 0.057].

Data: `data/processed/H99-glauber-fluctuation-relaxation/results/units_called.parquet`, `periods.parquet`.

## Scorecard (period-specific axes)
C: g_χ against independence (bootstrap CI and block-shift null). D: the collective relaxation predicted from fluctuations (Δρ, Δg). H: Glauber against fast-field, slow-field and delayed-coupling readings.

## Round 2 (2026-10-04)

*Round-2 tests (card section "Round 2"; predictions written 21:20 UTC and Amendment B1 21:30 UTC, before real data). Exploratory, non-holdout. Talk statistics stay post hoc in the A2 sense.*

| Unit | Δρ₁ V0 (W0-corr.) | Δρ₁ V5 (W0-corr.) | ρ_s − W0 | g₁ room-gated | g₁ in-flight-gated | g₂ room-gated | g₁,fit (R2) | H67 g_lag |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 8 | +0.016 ± 0.027 | +0.050 ± 0.030 | +0.026 [-0.010, +0.062] | -0.004 [-0.023, +0.015] | +0.012 [-0.012, +0.036] | +0.000 [-0.009, +0.012] | – | +0.005 |

Regime I. ± is one SE (block bootstrap and W0 spread). Data: `data/processed/H99-glauber-fluctuation-relaxation/r2/results/r2_units.parquet`.

Reading (descriptive): regime-I reads and in-flight messages raise talk equally (no read-out gate), so any collective memory here is field-like.
