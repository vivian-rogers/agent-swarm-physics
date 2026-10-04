# H19 × G17: Each agent: build your own personal website (2025-10-13 → 2025-10-17)

**Verdict:** mixed
**Role:** exploratory (round 1, non-holdout)
**Period:** regime I · mode I · 7.0 agents (N_room 7.0) · 1 room(s) carrying ≥ 5% of agent messages · 5 non-holdout days · 3.0 h/day (empirical).

## Why this period
One point on every method's curve. Loop-gain estimates available here: H03 n̂ ALL (T2), H03 n̂ TALK (T1, primary), H03 fast n_x (T3), H04 K, weekly (E3), H04 n, weekly (T4), g_eq active (E1, primary), g_eq talk (E2). Controls: x_att = 1.22 (rank 27/35), messages per village turn 0.66, attention load k̄ = 3.9 agent messages waiting per turn, 19.0 agent messages per agent-hour, human share of chat 0.8%.

## Prediction
*Written 2026-10-04 00:09 UTC, before H19 related any control parameter to any loop gain (the card's P1 applied here).*
- Under the attention-dilution collapse (P1), every loop gain is affine-increasing in x_att. This period's x_att = 1.22 is **above** the cross-period median (0.96), so its estimates should sit **above** each method's cross-period median, and on the common curve.
- **Per-period verdict rule** (fixed now): fit the primary collapse model (per-method affine in x_att) without this period (LOPO). **supported** if (i) both primary estimates (T1 n̂ TALK, E1 g_eq active) fall inside their 90% LOPO predictive intervals and (ii) the period's summed LOPO log density under the collapse model is ≥ that under the regime-only rival N1; **mixed** if exactly one of (i), (ii) holds; **failed** if neither.
- Against it: estimates outside the intervals in the direction opposite to the x_att prediction, or N1 predicting the period better.

## Result
Primary collapse model (per-method affine in x_att), fitted without G17 (LOPO); shrunken = partial-pooling (BLUP) estimate under the collapse model fitted to all periods, shown beside the period's own estimate.

| Method | Own estimate ± SE | LOPO prediction [90% PI] | z | inside | Shrunken | Regime-only N1 prediction |
| --- | --- | --- | --- | --- | --- | --- |
| H03 n̂ ALL (T2) | 0.572 ± 0.065 | 0.384 [0.055, 0.712] | +0.94 | yes | 0.552 | 0.473 |
| H03 n̂ TALK (T1, primary) | 0.481 ± 0.086 | 0.383 [0.008, 0.757] | +0.43 | yes | 0.467 | 0.469 |
| H03 fast n_x (T3) | 0.130 ± 0.041 | 0.056 [-0.035, 0.148] | +1.34 | yes | 0.090 | 0.080 |
| H04 K, weekly (E3) | 0.123 ± 0.063 | 0.148 [-0.010, 0.307] | -0.26 | yes | 0.134 | 0.111 |
| H04 n, weekly (T4) | 0.678 ± 0.160 | 0.434 [0.057, 0.811] | +1.07 | yes | 0.559 | 0.477 |
| g_eq active (E1, primary) | 0.125 ± 0.070 | 0.133 [-0.022, 0.288] | -0.09 | yes | 0.129 | 0.087 |
| g_eq talk (E2) | 0.379 ± 0.099 | 0.137 [-0.071, 0.346] | +1.90 | **no** | 0.234 | 0.163 |

- (i) both primaries inside their 90% intervals: **True**; (ii) summed LOPO log density, collapse 3.94 vs regime-only 5.42: **False**.
- Direction check (prediction: above median): primaries observed n_talk above, geq_active above.
- Per-period figure: `figures/G17_residuals.png`. Data: `data/processed/H19-loop-gain-collapse/G17/residuals.parquet`.

## Scorecard (period-specific axes)
- **C** (adequacy vs. rivals, this period): collapse vs. regime-only log density -1.48 nats.
- **D** (unfitted): the period's estimates are predicted out of sample (LOPO), not fitted.
- E, G: not informed by a single period.

## Notes
- Inputs: `data/processed/H19-loop-gain-collapse/G17/inputs.json`.
