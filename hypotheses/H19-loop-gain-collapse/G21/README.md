# H19 × G21: Forecast the abilities and effects of AI (2025-12-01 → 2025-12-05)

**Verdict:** mixed
**Role:** exploratory (round 1, non-holdout)
**Period:** regime I · mode I · 8.4 agents (N_room 8.4) · 1 room(s) carrying ≥ 5% of agent messages · 5 non-holdout days · 4.0 h/day (empirical).

## Why this period
One point on every method's curve. Loop-gain estimates available here: H03 n̂ ALL (T2), H03 n̂ TALK (T1, primary), H03 fast n_x (T3), H04 K, weekly (E3), H04 n, weekly (T4), g_eq active (E1, primary), g_eq talk (E2). Controls: x_att = 1.08 (rank 25/35), messages per village turn 0.79, attention load k̄ = 5.9 agent messages waiting per turn, 14.5 agent messages per agent-hour, human share of chat 0.2%.

## Prediction
*Written 2026-10-04 00:09 UTC, before H19 related any control parameter to any loop gain (the card's P1 applied here).*
- Under the attention-dilution collapse (P1), every loop gain is affine-increasing in x_att. This period's x_att = 1.08 is **above** the cross-period median (0.96), so its estimates should sit **above** each method's cross-period median, and on the common curve.
- **Per-period verdict rule** (fixed now): fit the primary collapse model (per-method affine in x_att) without this period (LOPO). **supported** if (i) both primary estimates (T1 n̂ TALK, E1 g_eq active) fall inside their 90% LOPO predictive intervals and (ii) the period's summed LOPO log density under the collapse model is ≥ that under the regime-only rival N1; **mixed** if exactly one of (i), (ii) holds; **failed** if neither.
- Against it: estimates outside the intervals in the direction opposite to the x_att prediction, or N1 predicting the period better.

## Result
Primary collapse model (per-method affine in x_att), fitted without G21 (LOPO); shrunken = partial-pooling (BLUP) estimate under the collapse model fitted to all periods, shown beside the period's own estimate.

| Method | Own estimate ± SE | LOPO prediction [90% PI] | z | inside | Shrunken | Regime-only N1 prediction |
| --- | --- | --- | --- | --- | --- | --- |
| H03 n̂ ALL (T2) | 0.308 ± 0.133 | 0.414 [0.032, 0.795] | -0.46 | yes | 0.343 | 0.482 |
| H03 n̂ TALK (T1, primary) | 0.684 ± 0.233 | 0.402 [-0.112, 0.917] | +0.90 | yes | 0.527 | 0.465 |
| H03 fast n_x (T3) | 0.070 ± 0.021 | 0.065 [-0.008, 0.138] | +0.12 | yes | 0.069 | 0.082 |
| H04 K, weekly (E3) | 0.100 ± 0.063 | 0.133 [-0.026, 0.291] | -0.33 | yes | 0.115 | 0.112 |
| H04 n, weekly (T4) | 0.563 ± 0.160 | 0.444 [0.063, 0.826] | +0.51 | yes | 0.505 | 0.482 |
| g_eq active (E1, primary) | 0.087 ± 0.095 | 0.116 [-0.070, 0.303] | -0.25 | yes | 0.108 | 0.088 |
| g_eq talk (E2) | 0.174 ± 0.018 | 0.146 [0.007, 0.285] | +0.33 | yes | 0.173 | 0.167 |

- (i) both primaries inside their 90% intervals: **True**; (ii) summed LOPO log density, collapse 6.97 vs regime-only 7.25: **False**.
- Direction check (prediction: above median): primaries observed n_talk above, geq_active below.
- Per-period figure: `figures/G21_residuals.png`. Data: `data/processed/H19-loop-gain-collapse/G21/residuals.parquet`.

## Scorecard (period-specific axes)
- **C** (adequacy vs. rivals, this period): collapse vs. regime-only log density -0.28 nats.
- **D** (unfitted): the period's estimates are predicted out of sample (LOPO), not fitted.
- E, G: not informed by a single period.

## Notes
- Inputs: `data/processed/H19-loop-gain-collapse/G21/inputs.json`.
