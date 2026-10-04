# H19 × G33: Discuss, debate, and act on your views about the recent Pentagon-AI company news (2026-03-02 → 2026-03-04)

**Verdict:** supported
**Role:** exploratory (round 1, non-holdout)
**Period:** regime II · mode C · 11.0 agents (N_room 11.2) · 1 room(s) carrying ≥ 5% of agent messages · 3 non-holdout days · 4.0 h/day (empirical).

## Why this period
One point on every method's curve. Loop-gain estimates available here: H03 n̂ ALL (T2), H03 n̂ TALK (T1, primary), H03 fast n_x (T3), g_eq active (E1, primary), g_eq talk (E2). Controls: x_att = 0.82 (rank 6/35), messages per village turn 0.95, attention load k̄ = 11.4 agent messages waiting per turn, 13.4 agent messages per agent-hour, human share of chat 0.0%.

## Prediction
*Written 2026-10-04 00:09 UTC, before H19 related any control parameter to any loop gain (the card's P1 applied here).*
- Under the attention-dilution collapse (P1), every loop gain is affine-increasing in x_att. This period's x_att = 0.82 is **below** the cross-period median (0.96), so its estimates should sit **below** each method's cross-period median, and on the common curve.
- **Per-period verdict rule** (fixed now): fit the primary collapse model (per-method affine in x_att) without this period (LOPO). **supported** if (i) both primary estimates (T1 n̂ TALK, E1 g_eq active) fall inside their 90% LOPO predictive intervals and (ii) the period's summed LOPO log density under the collapse model is ≥ that under the regime-only rival N1; **mixed** if exactly one of (i), (ii) holds; **failed** if neither.
- Against it: estimates outside the intervals in the direction opposite to the x_att prediction, or N1 predicting the period better.

## Result
Primary collapse model (per-method affine in x_att), fitted without G33 (LOPO); shrunken = partial-pooling (BLUP) estimate under the collapse model fitted to all periods, shown beside the period's own estimate.

| Method | Own estimate ± SE | LOPO prediction [90% PI] | z | inside | Shrunken | Regime-only N1 prediction |
| --- | --- | --- | --- | --- | --- | --- |
| H03 n̂ ALL (T2) | 0.279 ± 0.048 | 0.464 [0.141, 0.787] | -0.94 | yes | 0.290 | 0.297 |
| H03 n̂ TALK (T1, primary) | 0.765 ± 0.213 | 0.441 [-0.051, 0.933] | +1.08 | yes | 0.601 | 0.079 |
| H03 fast n_x (T3) | 0.081 ± 0.030 | 0.081 [0.000, 0.163] | -0.01 | yes | 0.081 | 0.070 |
| g_eq active (E1, primary) | 0.113 ± 0.058 | 0.081 [-0.061, 0.223] | +0.37 | yes | 0.098 | 0.098 |
| g_eq talk (E2) | 0.069 ± 0.048 | 0.162 [0.006, 0.318] | -0.98 | yes | 0.093 | 0.175 |

- (i) both primaries inside their 90% intervals: **True**; (ii) summed LOPO log density, collapse 4.48 vs regime-only 2.50: **True**.
- Direction check (prediction: below median): primaries observed n_talk above, geq_active below.
- Per-period figure: `figures/G33_residuals.png`. Data: `data/processed/H19-loop-gain-collapse/G33/residuals.parquet`.

## Scorecard (period-specific axes)
- **C** (adequacy vs. rivals, this period): collapse vs. regime-only log density +1.98 nats.
- **D** (unfitted): the period's estimates are predicted out of sample (LOPO), not fitted.
- E, G: not informed by a single period.

## Notes
- Inputs: `data/processed/H19-loop-gain-collapse/G33/inputs.json`.
