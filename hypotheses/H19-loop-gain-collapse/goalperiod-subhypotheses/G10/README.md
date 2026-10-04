# H19 × G10: Complete as many games as you can in a week! (2025-08-18 → 2025-08-22)

**Verdict:** mixed
**Role:** exploratory (round 1, non-holdout)
**Period:** regime I · mode I · 7.0 agents (N_room 7.0) · 1 room(s) carrying ≥ 5% of agent messages · 5 non-holdout days · 3.0 h/day (empirical).

## Why this period
One point on every method's curve. Loop-gain estimates available here: H03 n̂ ALL (T2), H03 n̂ TALK (T1, primary), H03 fast n_x (T3), H04 K, weekly (E3), H04 n, weekly (T4), g_eq active (E1, primary), g_eq talk (E2). Controls: x_att = 0.78 (rank 2/35), messages per village turn 1.11, attention load k̄ = 6.6 agent messages waiting per turn, 12.6 agent messages per agent-hour, human share of chat 1.6%.

## Prediction
*Written 2026-10-04 00:09 UTC, before H19 related any control parameter to any loop gain (the card's P1 applied here).*
- Under the attention-dilution collapse (P1), every loop gain is affine-increasing in x_att. This period's x_att = 0.78 is **below** the cross-period median (0.96), so its estimates should sit **below** each method's cross-period median, and on the common curve.
- **Per-period verdict rule** (fixed now): fit the primary collapse model (per-method affine in x_att) without this period (LOPO). **supported** if (i) both primary estimates (T1 n̂ TALK, E1 g_eq active) fall inside their 90% LOPO predictive intervals and (ii) the period's summed LOPO log density under the collapse model is ≥ that under the regime-only rival N1; **mixed** if exactly one of (i), (ii) holds; **failed** if neither.
- Against it: estimates outside the intervals in the direction opposite to the x_att prediction, or N1 predicting the period better.

## Result
Primary collapse model (per-method affine in x_att), fitted without G10 (LOPO); shrunken = partial-pooling (BLUP) estimate under the collapse model fitted to all periods, shown beside the period's own estimate.

| Method | Own estimate ± SE | LOPO prediction [90% PI] | z | inside | Shrunken | Regime-only N1 prediction |
| --- | --- | --- | --- | --- | --- | --- |
| H03 n̂ ALL (T2) | 0.475 ± 0.112 | 0.460 [0.093, 0.828] | +0.07 | yes | 0.471 | 0.477 |
| H03 n̂ TALK (T1, primary) | 0.223 ± 0.106 | 0.467 [0.078, 0.855] | -1.03 | yes | 0.272 | 0.480 |
| H03 fast n_x (T3) | 0.069 ± 0.041 | 0.084 [-0.009, 0.177] | -0.26 | yes | 0.077 | 0.082 |
| H04 K, weekly (E3) | 0.298 ± 0.063 | 0.081 [-0.063, 0.225] | +2.48 | **no** | 0.204 | 0.102 |
| H04 n, weekly (T4) | 0.481 ± 0.160 | 0.463 [0.075, 0.851] | +0.08 | yes | 0.473 | 0.486 |
| g_eq active (E1, primary) | 0.293 ± 0.136 | 0.074 [-0.172, 0.321] | +1.45 | yes | 0.113 | 0.085 |
| g_eq talk (E2) | 0.154 ± 0.042 | 0.160 [0.006, 0.313] | -0.06 | yes | 0.155 | 0.168 |

- (i) both primaries inside their 90% intervals: **True**; (ii) summed LOPO log density, collapse 2.83 vs regime-only 3.74: **False**.
- Direction check (prediction: below median): primaries observed n_talk below, geq_active above.
- Per-period figure: `figures/G10_residuals.png`. Data: `data/processed/H19-loop-gain-collapse/G10/residuals.parquet`.

## Scorecard (period-specific axes)
- **C** (adequacy vs. rivals, this period): collapse vs. regime-only log density -0.91 nats.
- **D** (unfitted): the period's estimates are predicted out of sample (LOPO), not fitted.
- E, G: not informed by a single period.

## Notes
- Inputs: `data/processed/H19-loop-gain-collapse/G10/inputs.json`.
