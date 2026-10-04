# H19 × G24: Do random acts of kindness! (2025-12-22 → 2025-12-26)

**Verdict:** supported
**Role:** exploratory (round 1, non-holdout)
**Period:** regime I · mode C · 10.0 agents (N_room 10.0) · 1 room(s) carrying ≥ 5% of agent messages · 5 non-holdout days · 4.0 h/day (empirical).

## Why this period
One point on every method's curve. Loop-gain estimates available here: H03 n̂ ALL (T2), H03 n̂ TALK (T1, primary), H03 fast n_x (T3), H04 K, weekly (E3), H04 n, weekly (T4), g_eq active (E1, primary), g_eq talk (E2). Controls: x_att = 0.94 (rank 17/35), messages per village turn 0.95, attention load k̄ = 8.6 agent messages waiting per turn, 8.3 agent messages per agent-hour, human share of chat 0.4%.

## Prediction
*Written 2026-10-04 00:09 UTC, before H19 related any control parameter to any loop gain (the card's P1 applied here).*
- Under the attention-dilution collapse (P1), every loop gain is affine-increasing in x_att. This period's x_att = 0.94 is **below** the cross-period median (0.96), so its estimates should sit **below** each method's cross-period median, and on the common curve.
- **Per-period verdict rule** (fixed now): fit the primary collapse model (per-method affine in x_att) without this period (LOPO). **supported** if (i) both primary estimates (T1 n̂ TALK, E1 g_eq active) fall inside their 90% LOPO predictive intervals and (ii) the period's summed LOPO log density under the collapse model is ≥ that under the regime-only rival N1; **mixed** if exactly one of (i), (ii) holds; **failed** if neither.
- Against it: estimates outside the intervals in the direction opposite to the x_att prediction, or N1 predicting the period better.

## Result
Primary collapse model (per-method affine in x_att), fitted without G24 (LOPO); shrunken = partial-pooling (BLUP) estimate under the collapse model fitted to all periods, shown beside the period's own estimate.

| Method | Own estimate ± SE | LOPO prediction [90% PI] | z | inside | Shrunken | Regime-only N1 prediction |
| --- | --- | --- | --- | --- | --- | --- |
| H03 n̂ ALL (T2) | 0.337 ± 0.053 | 0.438 [0.112, 0.765] | -0.51 | yes | 0.344 | 0.483 |
| H03 n̂ TALK (T1, primary) | 0.128 ± 0.059 | 0.441 [0.091, 0.791] | -1.47 | yes | 0.151 | 0.488 |
| H03 fast n_x (T3) | 0.113 ± 0.032 | 0.073 [-0.010, 0.155] | +0.80 | yes | 0.096 | 0.081 |
| H04 K, weekly (E3) | -0.011 ± 0.063 | 0.119 [-0.034, 0.273] | -1.40 | yes | 0.047 | 0.117 |
| H04 n, weekly (T4) | 0.174 ± 0.160 | 0.467 [0.090, 0.844] | -1.28 | yes | 0.316 | 0.500 |
| g_eq active (E1, primary) | -0.004 ± 0.069 | 0.100 [-0.053, 0.254] | -1.12 | yes | 0.054 | 0.091 |
| g_eq talk (E2) | 0.197 ± 0.030 | 0.151 [0.007, 0.295] | +0.53 | yes | 0.192 | 0.166 |

- (i) both primaries inside their 90% intervals: **True**; (ii) summed LOPO log density, collapse 4.28 vs regime-only 3.80: **True**.
- Direction check (prediction: below median): primaries observed n_talk below, geq_active below.
- Per-period figure: `figures/G24_residuals.png`. Data: `data/processed/H19-loop-gain-collapse/G24/residuals.parquet`.

## Scorecard (period-specific axes)
- **C** (adequacy vs. rivals, this period): collapse vs. regime-only log density +0.49 nats.
- **D** (unfitted): the period's estimates are predicted out of sample (LOPO), not fitted.
- E, G: not informed by a single period.

## Notes
- Inputs: `data/processed/H19-loop-gain-collapse/G24/inputs.json`.
