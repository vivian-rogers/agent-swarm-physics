# H123 × NE14: perma computer use (regime II → III, 2026-03-11 → 03-24)

**Verdict:** failed
**Role:** exploratory
**Period:** regime II units 33, 35, 36a (non-holdout; 34 is held out) vs regime III units 36b, 36c, 37. N 11–12, two rooms from 03-16.

## Why this period
Native N1. The update loop changes from discrete sessions plus scheduled chat-mode calls to continuous computer use with a pause tool. Model 02's update-rule question has a before and an after here.

## Prediction
*Written 2026-10-04 ~22:03 UTC, before running.*
- The audit class is self-clocked asynchronous on both sides (credence 0.6).
- Concurrency κ_par rises in regime III (0.6).
- σ_sweep ≈ σ_rand ≈ 0 on both sides (< 10⁻⁴ nats/step).
- Against: a sweep or state-dependent class on either side.

## Result
*Run 2026-10-04 22:06 UTC (audit) and 22:16 UTC (EP); data `data/processed/H123-regime1-turn-sweep/results/{audit,ep}.parquet`.* EP in 10⁻³ nats per call step.

| Unit | Regime | Class | η_ord | CV_gap (shuffle ≈ 1.05) | κ_par | L_name [95% CI] | σ×(2) talk (above floor?) | σ_sweep − σ_rand (lag 2) | RMS J_s (talk) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 33 | II | self-clocked asynchronous | 0.013 | 1.83 | 1.00 | 0.96 [0.89, 1.07] | +0.01 (no) | −0.15 | 0.064 |
| 35 | II | self-clocked asynchronous | 0.025 | 1.53 | 1.00 | 0.94 [0.90, 0.97] | −0.20 (no) | +0.03 | 0.077 |
| 36a | II | self-clocked asynchronous | 0.031 | 1.52 | 1.00 | 0.99 (1 day) | — | — | — |
| 36b | III | self-clocked asynchronous | 0.022 | 2.06 | 1.00 | 0.85 [0.73, 0.90] | −0.78 (no) | +0.18 | 0.140 |
| 36c | III | self-clocked asynchronous | 0.026 | 1.97 | 1.00 | 0.92 [0.87, 1.00] | −0.97 (no) | +0.16 | 0.134 |
| 37 | III | self-clocked asynchronous | 0.024 | 1.95 | 1.00 | 0.98 [0.87, 1.08] | −0.67 (no) | +0.21 | 0.116 |

| Prediction | Observed | Verdict |
| --- | --- | --- |
| Class self-clocked asynchronous on both sides | 6/6 units; no sweep, no state dependence | supported |
| κ_par rises in regime III | κ_par is already 1.00 in regime II (saturated); no rise possible | failed (ceiling) |
| σ_sweep ≈ σ_rand ≈ 0 | abs(σ_sweep − σ_rand) ≤ 0.21×10⁻³; σ× at the floor on both sides | supported |
| HH (sweep on either side) | absent | failed |

**Descriptive, not predicted:** two things change at NE14. (1) Return gaps get burstier (CV_gap 1.5–1.8 → 1.95–2.06): agents run longer streaks of their own calls in continuous computer use. (2) The named-next lift falls from 1.1–1.3 in regime I to 0.94–0.96 in regime II and 0.85–0.98 in regime III. In regime III a named agent is not called sooner in event order, consistent with H40's per-call clock (the call happens on the agent's own timer, and the name is read at that call).

## Scorecard (period-specific axes)
B 2 (update rule audited on both sides) · E 1 (predicted invariance of the class holds; κ prediction hit a ceiling).

## Notes
- 36a is a single day: audit only.
