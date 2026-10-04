# H19 × G35: Test your game to make it as fun and functional as you can! (2026-03-16 → 2026-03-20)

**Verdict:** mixed
**Role:** exploratory (round 1, non-holdout)
**Period:** regime II · mode C · 12.0 agents (N_room 7.4) · 3 room(s) carrying ≥ 5% of agent messages · 5 non-holdout days · 4.0 h/day (empirical).

## Why this period
One point on every method's curve. Loop-gain estimates available here: H03 n̂ ALL (T2), H03 n̂ TALK (T1, primary), H03 fast n_x (T3), H05 two-block g, active (E5), H05 two-block g, talk (E4), g_eq active (E1, primary), g_eq talk (E2). Controls: x_att = 0.84 (rank 9/35), messages per village turn 0.97, attention load k̄ = 6.7 agent messages waiting per turn, 8.7 agent messages per agent-hour, human share of chat 0.5%. First period with rooms (#best/#rest split on 03-16); regime II.

## Prediction
*Written 2026-10-04 00:09 UTC, before H19 related any control parameter to any loop gain (the card's P1 applied here).*
- Under the attention-dilution collapse (P1), every loop gain is affine-increasing in x_att. This period's x_att = 0.84 is **below** the cross-period median (0.96), so its estimates should sit **below** each method's cross-period median, and on the common curve.
- **Per-period verdict rule** (fixed now): fit the primary collapse model (per-method affine in x_att) without this period (LOPO). **supported** if (i) both primary estimates (T1 n̂ TALK, E1 g_eq active) fall inside their 90% LOPO predictive intervals and (ii) the period's summed LOPO log density under the collapse model is ≥ that under the regime-only rival N1; **mixed** if exactly one of (i), (ii) holds; **failed** if neither.
- Against it: estimates outside the intervals in the direction opposite to the x_att prediction, or N1 predicting the period better.

## Result
Primary collapse model (per-method affine in x_att), fitted without G35 (LOPO); shrunken = partial-pooling (BLUP) estimate under the collapse model fitted to all periods, shown beside the period's own estimate.

| Method | Own estimate ± SE | LOPO prediction [90% PI] | z | inside | Shrunken | Regime-only N1 prediction |
| --- | --- | --- | --- | --- | --- | --- |
| H03 n̂ ALL (T2) | 0.297 ± 0.035 | 0.460 [0.140, 0.779] | -0.84 | yes | 0.302 | 0.279 |
| H03 n̂ TALK (T1, primary) | 0.079 ± 0.061 | 0.465 [0.119, 0.811] | -1.83 | **no** | 0.109 | 0.765 |
| H03 fast n_x (T3) | 0.070 ± 0.020 | 0.081 [0.008, 0.153] | -0.23 | yes | 0.073 | 0.081 |
| H05 two-block g, active (E5) | 0.080 ± 0.080 | 0.121 [-0.212, 0.454] | -0.20 | yes | 0.087 | n/a |
| H05 two-block g, talk (E4) | 0.080 ± 0.059 | -0.015 [-0.142, 0.113] | +1.22 | yes | 0.026 | n/a |
| g_eq active (E1, primary) | 0.098 ± 0.037 | 0.084 [-0.039, 0.206] | +0.19 | yes | 0.094 | 0.113 |
| g_eq talk (E2) | 0.175 ± 0.050 | 0.156 [-0.003, 0.316] | +0.19 | yes | 0.170 | 0.069 |

- (i) both primaries inside their 90% intervals: **False**; (ii) summed LOPO log density, collapse 4.57 vs regime-only 2.49: **True**.
- Direction check (prediction: below median): primaries observed n_talk below, geq_active below.
- Per-period figure: `figures/G35_residuals.png`. Data: `data/processed/H19-loop-gain-collapse/G35/residuals.parquet`.

## Scorecard (period-specific axes)
- **C** (adequacy vs. rivals, this period): collapse vs. regime-only log density +2.08 nats.
- **D** (unfitted): the period's estimates are predicted out of sample (LOPO), not fitted.
- E, G: not informed by a single period.

## Notes
- Inputs: `data/processed/H19-loop-gain-collapse/G35/inputs.json`.
