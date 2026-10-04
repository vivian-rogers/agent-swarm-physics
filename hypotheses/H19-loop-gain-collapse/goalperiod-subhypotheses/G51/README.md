# H19 × G51: Each agent: Maximize your assigned goal! (2026-07-06 → 2026-09-04)

**Verdict:** failed
**Role:** exploratory (round 1, non-holdout)
**Period:** regime III · mode I/K · 26.5 agents (N_room 23.7) · 2 room(s) carrying ≥ 5% of agent messages · 45 non-holdout days · 8.1 h/day (empirical).

## Why this period
One point on every method's curve. Loop-gain estimates available here: H03 n̂ ALL (T2), H03 n̂ TALK (T1, primary), H03 fast n_x (T3), H04 K, weekly (E3), H04 n, weekly (T4), g_eq active (E1, primary), g_eq talk (E2). Controls: x_att = 2.24 (rank 35/35), messages per village turn 0.40, attention load k̄ = 9.1 agent messages waiting per turn, 4.1 agent messages per agent-hour, human share of chat 0.3%. Only 8 h/day exploratory period; 45 non-holdout days (the 09-07 → 09-21 tail is held out); N grows 21 → 32.

## Prediction
*Written 2026-10-04 00:09 UTC, before H19 related any control parameter to any loop gain (the card's P1 applied here).*
- Under the attention-dilution collapse (P1), every loop gain is affine-increasing in x_att. This period's x_att = 2.24 is **above** the cross-period median (0.96), so its estimates should sit **above** each method's cross-period median, and on the common curve.
- **Per-period verdict rule** (fixed now): fit the primary collapse model (per-method affine in x_att) without this period (LOPO). **supported** if (i) both primary estimates (T1 n̂ TALK, E1 g_eq active) fall inside their 90% LOPO predictive intervals and (ii) the period's summed LOPO log density under the collapse model is ≥ that under the regime-only rival N1; **mixed** if exactly one of (i), (ii) holds; **failed** if neither.
- Against it: estimates outside the intervals in the direction opposite to the x_att prediction, or N1 predicting the period better.

## Result
Primary collapse model (per-method affine in x_att), fitted without G51 (LOPO); shrunken = partial-pooling (BLUP) estimate under the collapse model fitted to all periods, shown beside the period's own estimate.

| Method | Own estimate ± SE | LOPO prediction [90% PI] | z | inside | Shrunken | Regime-only N1 prediction |
| --- | --- | --- | --- | --- | --- | --- |
| H03 n̂ ALL (T2) | 0.592 ± 0.048 | 0.003 [-0.358, 0.364] | +2.69 | **no** | 0.569 | 0.189 |
| H03 n̂ TALK (T1, primary) | 0.542 ± 0.044 | 0.067 [-0.330, 0.464] | +1.97 | **no** | 0.527 | 0.215 |
| H03 fast n_x (T3) | 0.026 ± 0.020 | -0.017 [-0.101, 0.068] | +0.83 | yes | 0.019 | 0.017 |
| H04 K, weekly (E3) | 0.271 ± 0.037 | 0.269 [0.071, 0.467] | +0.02 | yes | 0.271 | 0.195 |
| H04 n, weekly (T4) | 0.633 ± 0.043 | 0.176 [-0.152, 0.504] | +2.29 | **no** | 0.617 | 0.297 |
| g_eq active (E1, primary) | 0.237 ± 0.015 | 0.282 [0.142, 0.422] | -0.53 | yes | 0.238 | 0.195 |
| g_eq talk (E2) | 0.112 ± 0.009 | 0.090 [-0.078, 0.257] | +0.22 | yes | 0.112 | 0.092 |

- (i) both primaries inside their 90% intervals: **False**; (ii) summed LOPO log density, collapse -0.72 vs regime-only 2.35: **False**.
- Direction check (prediction: above median): primaries observed n_talk above, geq_active above.
- Per-period figure: `figures/G51_residuals.png`. Data: `data/processed/H19-loop-gain-collapse/G51/residuals.parquet`.

## Scorecard (period-specific axes)
- **C** (adequacy vs. rivals, this period): collapse vs. regime-only log density -3.07 nats.
- **D** (unfitted): the period's estimates are predicted out of sample (LOPO), not fitted.
- E, G: not informed by a single period.

## Notes
- Inputs: `data/processed/H19-loop-gain-collapse/G51/inputs.json`.
