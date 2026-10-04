# H19 × G26: Elect a village leader. They choose this week’s goal! (2026-01-05 → 2026-01-09)

**Verdict:** supported
**Role:** exploratory (round 1, non-holdout)
**Period:** regime I · mode C · 10.0 agents (N_room 10.0) · 1 room(s) carrying ≥ 5% of agent messages · 5 non-holdout days · 4.0 h/day (empirical).

## Why this period
One point on every method's curve. Loop-gain estimates available here: H03 n̂ ALL (T2), H03 n̂ TALK (T1, primary), H03 fast n_x (T3), H04 K, weekly (E3), H04 n, weekly (T4), g_eq active (E1, primary), g_eq talk (E2). Controls: x_att = 0.96 (rank 18/35), messages per village turn 0.93, attention load k̄ = 8.4 agent messages waiting per turn, 13.3 agent messages per agent-hour, human share of chat 0.1%.

## Prediction
*Written 2026-10-04 00:09 UTC, before H19 related any control parameter to any loop gain (the card's P1 applied here).*
- Under the attention-dilution collapse (P1), every loop gain is affine-increasing in x_att. This period's x_att = 0.96 is **below** the cross-period median (0.96), so its estimates should sit **below** each method's cross-period median, and on the common curve.
- **Per-period verdict rule** (fixed now): fit the primary collapse model (per-method affine in x_att) without this period (LOPO). **supported** if (i) both primary estimates (T1 n̂ TALK, E1 g_eq active) fall inside their 90% LOPO predictive intervals and (ii) the period's summed LOPO log density under the collapse model is ≥ that under the regime-only rival N1; **mixed** if exactly one of (i), (ii) holds; **failed** if neither.
- Against it: estimates outside the intervals in the direction opposite to the x_att prediction, or N1 predicting the period better.

## Result
Primary collapse model (per-method affine in x_att), fitted without G26 (LOPO); shrunken = partial-pooling (BLUP) estimate under the collapse model fitted to all periods, shown beside the period's own estimate.

| Method | Own estimate ± SE | LOPO prediction [90% PI] | z | inside | Shrunken | Regime-only N1 prediction |
| --- | --- | --- | --- | --- | --- | --- |
| H03 n̂ ALL (T2) | 0.579 ± 0.108 | 0.428 [0.068, 0.788] | +0.69 | yes | 0.541 | 0.473 |
| H03 n̂ TALK (T1, primary) | 0.564 ± 0.085 | 0.422 [0.048, 0.796] | +0.63 | yes | 0.544 | 0.466 |
| H03 fast n_x (T3) | 0.211 ± 0.020 | 0.066 [0.011, 0.120] | +4.38 | **no** | 0.180 | 0.073 |
| H04 K, weekly (E3) | 0.190 ± 0.063 | 0.113 [-0.043, 0.270] | +0.80 | yes | 0.155 | 0.108 |
| H04 n, weekly (T4) | 0.563 ± 0.160 | 0.451 [0.068, 0.833] | +0.48 | yes | 0.508 | 0.482 |
| g_eq active (E1, primary) | 0.209 ± 0.115 | 0.099 [-0.116, 0.314] | +0.84 | yes | 0.124 | 0.086 |
| g_eq talk (E2) | 0.240 ± 0.050 | 0.149 [-0.008, 0.306] | +0.95 | yes | 0.215 | 0.165 |

- (i) both primaries inside their 90% intervals: **True**; (ii) summed LOPO log density, collapse -3.11 vs regime-only -3.76: **True**.
- Direction check (prediction: below median): primaries observed n_talk above, geq_active above.
- Per-period figure: `figures/G26_residuals.png`. Data: `data/processed/H19-loop-gain-collapse/G26/residuals.parquet`.

## Scorecard (period-specific axes)
- **C** (adequacy vs. rivals, this period): collapse vs. regime-only log density +0.65 nats.
- **D** (unfitted): the period's estimates are predicted out of sample (LOPO), not fitted.
- E, G: not informed by a single period.

## Notes
- Inputs: `data/processed/H19-loop-gain-collapse/G26/inputs.json`.
