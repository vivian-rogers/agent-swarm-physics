# H99 × G13: goal period #13

**Verdict:** supported
**Role:** replication (exploratory)
**Period:** goal #13 · regime I · units 13 · N 6 · 1613 trimmed minutes.

## Why this period
Eligible for the replication layer (≥ 3 agents with ≥ 30 record minutes, ≥ 60 trimmed minutes per day).

## Prediction
*The card's rule, written 2026-10-04 20:22 UTC before any H99 statistic and amended before real data (A1, 20:41 UTC) and after the first run (A2, 20:45 UTC, post hoc for talk); this folder was written after the run and copies it.* Glauber consistency: no field call on the talk channel (A2 rule: |Δρ| < 0.03 or CI covering 0) in units with a resolved fluctuation gain. Supported if every resolved talk unit is consistent; failed if most resolved units carry a field call; descriptive if no unit has a resolved g_χ; mixed otherwise. Regime I is predicted to fail in the fast-field direction (P2).

## Result

| Unit | channel | g_χ [95%] | ρ_c(1) | ρ_⊥(1) | gap (Δρ₁ talk / Δg₁ other) [95%] | lag 2 | call |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 13 | act | 0.069 [-0.024, 0.164] | 0.29 | 0.28 | -0.036 [-0.182, 0.079] | -0.206 | unresolved |
| 13 | content | 0.581 [0.513, 0.647] | 0.60 | 0.42 | -0.174 [-0.277, -0.099] | -0.178 | fast |
| 13 | talk | 0.104 [0.014, 0.181] | 0.13 | 0.17 | -0.070 [-0.136, 0.001] | -0.076 | consistent |

Talk kick layer (human messages as a field on the room; distributed-lag kernel of the room's talk count; decay ratio λ = Σβ₁…₅ / Σβ₀…₄; A2 estimator):

| Unit | kicks | response at lags 0–1 [95%] | λ_kick [95%] | Glauber λ_c | measured ρ_c(1) | ρ_⊥(1) |
| --- | --- | --- | --- | --- | --- | --- |
| 13 | 39 | 0.64 [0.06, 1.16] | 0.71 [-6.27, 3.19] | 0.205 | 0.135 | 0.171 |

Period pool (random effects over units, talk): g_χ = 0.104 [0.020, 0.187], Δρ₁ = -0.070 [-0.142, 0.001].

Data: `data/processed/H99-glauber-fluctuation-relaxation/results/units_called.parquet`, `periods.parquet`.

## Scorecard (period-specific axes)
C: g_χ against independence (bootstrap CI and block-shift null). D: the collective relaxation predicted from fluctuations (Δρ, Δg). H: Glauber against fast-field, slow-field and delayed-coupling readings.

## Round 2 (2026-10-04)

*Round-2 tests (card section "Round 2"; predictions written 21:20 UTC and Amendment B1 21:30 UTC, before real data). Exploratory, non-holdout. Talk statistics stay post hoc in the A2 sense.*

| Unit | Δρ₁ V0 (W0-corr.) | Δρ₁ V5 (W0-corr.) | ρ_s − W0 | g₁ room-gated | g₁ in-flight-gated | g₂ room-gated | g₁,fit (R2) | H67 g_lag |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 13 | -0.033 ± 0.035 | +0.097 ± 0.029 | -0.092 [-0.156, -0.035] | +0.004 [-0.018, +0.030] | -0.048 [-0.082, -0.006] | -0.029 [-0.043, -0.015] | – | -0.002 |

Regime I. ± is one SE (block bootstrap and W0 spread). Data: `data/processed/H99-glauber-fluctuation-relaxation/r2/results/r2_units.parquet`.

Reading (descriptive): regime-I reads and in-flight messages raise talk equally (no read-out gate), so any collective memory here is field-like.
