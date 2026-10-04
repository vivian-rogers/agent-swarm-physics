# H19 × G08: Design the AI Village benchmark for open-ended goal pursuit – and test yourselves on it! (2025-07-18 → 2025-08-12)

**Verdict:** supported
**Role:** exploratory (round 1, non-holdout)
**Period:** regime I · mode C · 4.0 agents (N_room 4.0) · 1 room(s) carrying ≥ 5% of agent messages · 18 non-holdout days · 3.0 h/day (empirical).

## Why this period
One point on every method's curve. Loop-gain estimates available here: H03 n̂ ALL (T2), H03 n̂ TALK (T1, primary), H03 fast n_x (T3), H04 K, weekly (E3), H04 n, weekly (T4), g_eq active (E1, primary), g_eq talk (E2). Controls: x_att = 0.82 (rank 7/35), messages per village turn 0.89, attention load k̄ = 2.7 agent messages waiting per turn, 15.2 agent messages per agent-hour, human share of chat 1.2%.

## Prediction
*Written 2026-10-04 00:09 UTC, before H19 related any control parameter to any loop gain (the card's P1 applied here).*
- Under the attention-dilution collapse (P1), every loop gain is affine-increasing in x_att. This period's x_att = 0.82 is **below** the cross-period median (0.96), so its estimates should sit **below** each method's cross-period median, and on the common curve.
- **Per-period verdict rule** (fixed now): fit the primary collapse model (per-method affine in x_att) without this period (LOPO). **supported** if (i) both primary estimates (T1 n̂ TALK, E1 g_eq active) fall inside their 90% LOPO predictive intervals and (ii) the period's summed LOPO log density under the collapse model is ≥ that under the regime-only rival N1; **mixed** if exactly one of (i), (ii) holds; **failed** if neither.
- Against it: estimates outside the intervals in the direction opposite to the x_att prediction, or N1 predicting the period better.

## Result
Primary collapse model (per-method affine in x_att), fitted without G08 (LOPO); shrunken = partial-pooling (BLUP) estimate under the collapse model fitted to all periods, shown beside the period's own estimate.

| Method | Own estimate ± SE | LOPO prediction [90% PI] | z | inside | Shrunken | Regime-only N1 prediction |
| --- | --- | --- | --- | --- | --- | --- |
| H03 n̂ ALL (T2) | 0.397 ± 0.027 | 0.458 [0.137, 0.779] | -0.31 | yes | 0.398 | 0.481 |
| H03 n̂ TALK (T1, primary) | 0.274 ± 0.083 | 0.458 [0.084, 0.832] | -0.81 | yes | 0.299 | 0.479 |
| H03 fast n_x (T3) | 0.000 ± 0.020 | 0.086 [0.018, 0.153] | -2.09 | **no** | 0.018 | 0.086 |
| H04 K, weekly (E3) | 0.039 ± 0.037 | 0.105 [-0.029, 0.239] | -0.81 | yes | 0.052 | 0.116 |
| H04 n, weekly (T4) | 0.237 ± 0.093 | 0.481 [0.169, 0.792] | -1.28 | yes | 0.294 | 0.503 |
| g_eq active (E1, primary) | 0.034 ± 0.025 | 0.086 [-0.027, 0.199] | -0.76 | yes | 0.041 | 0.092 |
| g_eq talk (E2) | -0.014 ± 0.018 | 0.168 [0.040, 0.295] | -2.35 | **no** | -0.006 | 0.177 |

- (i) both primaries inside their 90% intervals: **True**; (ii) summed LOPO log density, collapse 2.53 vs regime-only 1.00: **True**.
- Direction check (prediction: below median): primaries observed n_talk below, geq_active below.
- Per-period figure: `figures/G08_residuals.png`. Data: `data/processed/H19-loop-gain-collapse/G08/residuals.parquet`.

## Scorecard (period-specific axes)
- **C** (adequacy vs. rivals, this period): collapse vs. regime-only log density +1.52 nats.
- **D** (unfitted): the period's estimates are predicted out of sample (LOPO), not fitted.
- E, G: not informed by a single period.

## Notes
- Inputs: `data/processed/H19-loop-gain-collapse/G08/inputs.json`.
