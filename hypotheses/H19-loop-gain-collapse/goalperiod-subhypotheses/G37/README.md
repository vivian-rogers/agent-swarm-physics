# H19 × G37: Pick your own goal! (2026-03-30 → 2026-04-01)

**Verdict:** mixed
**Role:** exploratory (round 1, non-holdout)
**Period:** regime III · mode F · 12.0 agents (N_room 6.9) · 2 room(s) carrying ≥ 5% of agent messages · 3 non-holdout days · 4.1 h/day (empirical).

## Why this period
One point on every method's curve. Loop-gain estimates available here: H03 n̂ ALL (T2), H03 n̂ TALK (T1, primary), H03 fast n_x (T3), H05 two-block g, active (E5), H05 two-block g, talk (E4), g_eq active (E1, primary), g_eq talk (E2). Controls: x_att = 1.74 (rank 32/35), messages per village turn 0.40, attention load k̄ = 2.4 agent messages waiting per turn, 2.8 agent messages per agent-hour, human share of chat 0.7%. Three days, free mode, first regime-III week.

## Prediction
*Written 2026-10-04 00:09 UTC, before H19 related any control parameter to any loop gain (the card's P1 applied here).*
- Under the attention-dilution collapse (P1), every loop gain is affine-increasing in x_att. This period's x_att = 1.74 is **above** the cross-period median (0.96), so its estimates should sit **above** each method's cross-period median, and on the common curve.
- **Per-period verdict rule** (fixed now): fit the primary collapse model (per-method affine in x_att) without this period (LOPO). **supported** if (i) both primary estimates (T1 n̂ TALK, E1 g_eq active) fall inside their 90% LOPO predictive intervals and (ii) the period's summed LOPO log density under the collapse model is ≥ that under the regime-only rival N1; **mixed** if exactly one of (i), (ii) holds; **failed** if neither.
- Against it: estimates outside the intervals in the direction opposite to the x_att prediction, or N1 predicting the period better.

## Result
Primary collapse model (per-method affine in x_att), fitted without G37 (LOPO); shrunken = partial-pooling (BLUP) estimate under the collapse model fitted to all periods, shown beside the period's own estimate.

| Method | Own estimate ± SE | LOPO prediction [90% PI] | z | inside | Shrunken | Regime-only N1 prediction |
| --- | --- | --- | --- | --- | --- | --- |
| H03 n̂ ALL (T2) | 0.192 ± 0.227 | 0.311 [-0.188, 0.809] | -0.39 | yes | 0.259 | 0.251 |
| H03 n̂ TALK (T1, primary) | 0.301 ± 0.020 | 0.301 [-0.068, 0.670] | -0.00 | yes | 0.301 | 0.248 |
| H03 fast n_x (T3) | 0.000 ± 0.020 | 0.030 [-0.045, 0.105] | -0.66 | yes | 0.006 | 0.021 |
| H05 two-block g, active (E5) | 0.247 ± 0.003 | 0.073 [0.020, 0.127] | +5.36 | **no** | 0.247 | 0.093 |
| H05 two-block g, talk (E4) | 0.242 ± 0.080 | 0.114 [-0.034, 0.263] | +1.41 | yes | 0.141 | 0.073 |
| g_eq active (E1, primary) | 0.321 ± 0.087 | 0.192 [0.013, 0.371] | +1.18 | yes | 0.239 | 0.194 |
| g_eq talk (E2) | 0.161 ± 0.039 | 0.114 [-0.043, 0.270] | +0.50 | yes | 0.152 | 0.086 |

- (i) both primaries inside their 90% intervals: **True**; (ii) summed LOPO log density, collapse -6.73 vs regime-only -0.78: **False**.
- Direction check (prediction: above median): primaries observed n_talk below, geq_active above.
- Per-period figure: `figures/G37_residuals.png`. Data: `data/processed/H19-loop-gain-collapse/G37/residuals.parquet`.

## Scorecard (period-specific axes)
- **C** (adequacy vs. rivals, this period): collapse vs. regime-only log density -5.95 nats.
- **D** (unfitted): the period's estimates are predicted out of sample (LOPO), not fitted.
- E, G: not informed by a single period.

## Notes
- Inputs: `data/processed/H19-loop-gain-collapse/G37/inputs.json`.
