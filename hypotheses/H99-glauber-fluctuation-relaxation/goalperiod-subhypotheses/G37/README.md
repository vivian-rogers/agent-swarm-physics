# H99 × G37: goal period #37

**Verdict:** failed
**Role:** replication (exploratory)
**Period:** goal #37 · regime III · units 37 · N 12 · 705 trimmed minutes.

## Why this period
Eligible for the replication layer (≥ 3 agents with ≥ 30 record minutes, ≥ 60 trimmed minutes per day).

## Prediction
*The card's rule, written 2026-10-04 20:22 UTC before any H99 statistic and amended before real data (A1, 20:41 UTC) and after the first run (A2, 20:45 UTC, post hoc for talk); this folder was written after the run and copies it.* Glauber consistency: no field call on the talk channel (A2 rule: |Δρ| < 0.03 or CI covering 0) in units with a resolved fluctuation gain. Supported if every resolved talk unit is consistent; failed if most resolved units carry a field call; descriptive if no unit has a resolved g_χ; mixed otherwise. Regime III is predicted to be consistent (P1).

## Result

| Unit | channel | g_χ [95%] | ρ_c(1) | ρ_⊥(1) | gap (Δρ₁ talk / Δg₁ other) [95%] | lag 2 | call |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 37 | act | 0.157 [0.025, 0.269] | 0.48 | 0.40 | 0.047 [-0.071, 0.120] | 0.061 | consistent |
| 37 | content | 0.532 [0.406, 0.613] | 0.42 | 0.22 | -0.108 [-0.189, -0.023] | -0.082 | fast |
| 37 | talk | 0.262 [0.195, 0.321] | 0.16 | 0.03 | 0.098 [0.012, 0.178] | 0.029 | slow |

Period pool (random effects over units, talk): g_χ = 0.262 [0.199, 0.324], Δρ₁ = 0.098 [0.014, 0.181].

Data: `data/processed/H99-glauber-fluctuation-relaxation/results/units_called.parquet`, `periods.parquet`.

## Scorecard (period-specific axes)
C: g_χ against independence (bootstrap CI and block-shift null). D: the collective relaxation predicted from fluctuations (Δρ, Δg). H: Glauber against fast-field, slow-field and delayed-coupling readings.

## Round 2 (2026-10-04)

*Round-2 tests (card section "Round 2"; predictions written 21:20 UTC and Amendment B1 21:30 UTC, before real data). Exploratory, non-holdout. Talk statistics stay post hoc in the A2 sense.*

| Unit | Δρ₁ V0 (W0-corr.) | Δρ₁ V5 (W0-corr.) | ρ_s − W0 | g₁ room-gated | g₁ in-flight-gated | g₂ room-gated | g₁,fit (R2) | H67 g_lag |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 37 | +0.093 ± 0.043 | +0.191 ± 0.058 | -0.067 [-0.084, -0.045] | +0.172 [+0.101, +0.237] | +0.235 [+0.144, +0.325] | +0.023 [-0.028, +0.087] | +0.40 [+0.10, +0.50] | +0.220 |

Regime III. ± is one SE (block bootstrap and W0 spread). Data: `data/processed/H99-glauber-fluctuation-relaxation/r2/results/r2_units.parquet`.

Reading: the collective talk memory survives scheduler removal where it was present in round 1; reads couple at the next call (room-gated g₁ ≈ H67's g_lag), mostly through named messages. See the card for pooled tests.
