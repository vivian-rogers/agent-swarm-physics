# H19 × G16: Choose your own goal! (2025-10-06 → 2025-10-10)

**Verdict:** mixed
**Role:** exploratory (round 1, non-holdout)
**Period:** regime I · mode F · 7.0 agents (N_room 7.0) · 1 room(s) carrying ≥ 5% of agent messages · 5 non-holdout days · 3.0 h/day (empirical).

## Why this period
One point on every method's curve. Loop-gain estimates available here: H03 n̂ ALL (T2), H03 n̂ TALK (T1, primary), H03 fast n_x (T3), H04 K, weekly (E3), H04 n, weekly (T4), g_eq active (E1, primary), g_eq talk (E2). Controls: x_att = 0.97 (rank 20/35), messages per village turn 0.86, attention load k̄ = 5.2 agent messages waiting per turn, 18.4 agent messages per agent-hour, human share of chat 1.4%.

## Prediction
*Written 2026-10-04 00:09 UTC, before H19 related any control parameter to any loop gain (the card's P1 applied here).*
- Under the attention-dilution collapse (P1), every loop gain is affine-increasing in x_att. This period's x_att = 0.97 is **above** the cross-period median (0.96), so its estimates should sit **above** each method's cross-period median, and on the common curve.
- **Per-period verdict rule** (fixed now): fit the primary collapse model (per-method affine in x_att) without this period (LOPO). **supported** if (i) both primary estimates (T1 n̂ TALK, E1 g_eq active) fall inside their 90% LOPO predictive intervals and (ii) the period's summed LOPO log density under the collapse model is ≥ that under the regime-only rival N1; **mixed** if exactly one of (i), (ii) holds; **failed** if neither.
- Against it: estimates outside the intervals in the direction opposite to the x_att prediction, or N1 predicting the period better.

## Result
Primary collapse model (per-method affine in x_att), fitted without G16 (LOPO); shrunken = partial-pooling (BLUP) estimate under the collapse model fitted to all periods, shown beside the period's own estimate.

| Method | Own estimate ± SE | LOPO prediction [90% PI] | z | inside | Shrunken | Regime-only N1 prediction |
| --- | --- | --- | --- | --- | --- | --- |
| H03 n̂ ALL (T2) | 0.447 ± 0.059 | 0.430 [0.099, 0.760] | +0.08 | yes | 0.445 | 0.478 |
| H03 n̂ TALK (T1, primary) | 0.588 ± 0.124 | 0.420 [0.019, 0.821] | +0.69 | yes | 0.544 | 0.465 |
| H03 fast n_x (T3) | 0.075 ± 0.026 | 0.072 [-0.005, 0.149] | +0.06 | yes | 0.074 | 0.082 |
| H04 K, weekly (E3) | 0.266 ± 0.063 | 0.111 [-0.039, 0.261] | +1.69 | **no** | 0.197 | 0.104 |
| H04 n, weekly (T4) | 0.594 ± 0.160 | 0.449 [0.067, 0.830] | +0.62 | yes | 0.523 | 0.481 |
| g_eq active (E1, primary) | 0.276 ± 0.112 | 0.099 [-0.111, 0.309] | +1.39 | yes | 0.141 | 0.085 |
| g_eq talk (E2) | 0.251 ± 0.032 | 0.148 [0.005, 0.290] | +1.20 | yes | 0.237 | 0.163 |

- (i) both primaries inside their 90% intervals: **True**; (ii) summed LOPO log density, collapse 4.46 vs regime-only 4.77: **False**.
- Direction check (prediction: above median): primaries observed n_talk above, geq_active above.
- Per-period figure: `figures/G16_residuals.png`. Data: `data/processed/H19-loop-gain-collapse/G16/residuals.parquet`.

## Scorecard (period-specific axes)
- **C** (adequacy vs. rivals, this period): collapse vs. regime-only log density -0.31 nats.
- **D** (unfitted): the period's estimates are predicted out of sample (LOPO), not fitted.
- E, G: not informed by a single period.

## Notes
- Inputs: `data/processed/H19-loop-gain-collapse/G16/inputs.json`.
