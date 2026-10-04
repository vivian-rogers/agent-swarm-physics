# H19 × G18: Reduce global poverty as much as you can (2025-10-20 → 2025-10-31)

**Verdict:** mixed
**Role:** exploratory (round 1, non-holdout)
**Period:** regime I · mode C · 7.5 agents (N_room 7.6) · 1 room(s) carrying ≥ 5% of agent messages · 10 non-holdout days · 4.0 h/day (empirical).

## Why this period
One point on every method's curve. Loop-gain estimates available here: H03 n̂ ALL (T2), H03 n̂ TALK (T1, primary), H03 fast n_x (T3), H04 K, weekly (E3), H04 n, weekly (T4), g_eq active (E1, primary), g_eq talk (E2). Controls: x_att = 1.02 (rank 24/35), messages per village turn 0.83, attention load k̄ = 5.5 agent messages waiting per turn, 24.7 agent messages per agent-hour, human share of chat 0.3%.

## Prediction
*Written 2026-10-04 00:09 UTC, before H19 related any control parameter to any loop gain (the card's P1 applied here).*
- Under the attention-dilution collapse (P1), every loop gain is affine-increasing in x_att. This period's x_att = 1.02 is **above** the cross-period median (0.96), so its estimates should sit **above** each method's cross-period median, and on the common curve.
- **Per-period verdict rule** (fixed now): fit the primary collapse model (per-method affine in x_att) without this period (LOPO). **supported** if (i) both primary estimates (T1 n̂ TALK, E1 g_eq active) fall inside their 90% LOPO predictive intervals and (ii) the period's summed LOPO log density under the collapse model is ≥ that under the regime-only rival N1; **mixed** if exactly one of (i), (ii) holds; **failed** if neither.
- Against it: estimates outside the intervals in the direction opposite to the x_att prediction, or N1 predicting the period better.

## Result
Primary collapse model (per-method affine in x_att), fitted without G18 (LOPO); shrunken = partial-pooling (BLUP) estimate under the collapse model fitted to all periods, shown beside the period's own estimate.

| Method | Own estimate ± SE | LOPO prediction [90% PI] | z | inside | Shrunken | Regime-only N1 prediction |
| --- | --- | --- | --- | --- | --- | --- |
| H03 n̂ ALL (T2) | 0.695 ± 0.049 | 0.412 [0.098, 0.726] | +1.48 | yes | 0.677 | 0.467 |
| H03 n̂ TALK (T1, primary) | 0.696 ± 0.073 | 0.407 [0.048, 0.765] | +1.33 | yes | 0.664 | 0.459 |
| H03 fast n_x (T3) | 0.075 ± 0.020 | 0.069 [-0.003, 0.141] | +0.13 | yes | 0.073 | 0.082 |
| H04 K, weekly (E3) | 0.137 ± 0.045 | 0.124 [-0.017, 0.265] | +0.15 | yes | 0.133 | 0.110 |
| H04 n, weekly (T4) | 0.687 ± 0.113 | 0.440 [0.116, 0.765] | +1.25 | yes | 0.608 | 0.473 |
| g_eq active (E1, primary) | 0.079 ± 0.036 | 0.110 [-0.011, 0.230] | -0.42 | yes | 0.087 | 0.089 |
| g_eq talk (E2) | 0.236 ± 0.033 | 0.146 [0.003, 0.290] | +1.03 | yes | 0.223 | 0.164 |

- (i) both primaries inside their 90% intervals: **True**; (ii) summed LOPO log density, collapse 5.61 vs regime-only 6.68: **False**.
- Direction check (prediction: above median): primaries observed n_talk above, geq_active below.
- Per-period figure: `figures/G18_residuals.png`. Data: `data/processed/H19-loop-gain-collapse/G18/residuals.parquet`.

## Scorecard (period-specific axes)
- **C** (adequacy vs. rivals, this period): collapse vs. regime-only log density -1.07 nats.
- **D** (unfitted): the period's estimates are predicted out of sample (LOPO), not fitted.
- E, G: not informed by a single period.

## Notes
- Inputs: `data/processed/H19-loop-gain-collapse/G18/inputs.json`.
