# H19 × G06: Create your own merch store. Whichever agent's store makes the most profit wins! (2025-06-26 → 2025-07-15)

**Verdict:** supported
**Role:** exploratory (round 1, non-holdout)
**Period:** regime I · mode K · 4.0 agents (N_room 4.0) · 1 room(s) carrying ≥ 5% of agent messages · 15 non-holdout days · 2.0 h/day (empirical).

## Why this period
One point on every method's curve. Loop-gain estimates available here: H03 n̂ ALL (T2), H03 n̂ TALK (T1, primary), H03 fast n_x (T3), H04 K, weekly (E3), H04 n, weekly (T4), g_eq active (E1, primary), g_eq talk (E2). Controls: x_att = 0.81 (rank 4/35), messages per village turn 0.90, attention load k̄ = 2.7 agent messages waiting per turn, 12.7 agent messages per agent-hour, human share of chat 16.4%.

## Prediction
*Written 2026-10-04 00:09 UTC, before H19 related any control parameter to any loop gain (the card's P1 applied here).*
- Under the attention-dilution collapse (P1), every loop gain is affine-increasing in x_att. This period's x_att = 0.81 is **below** the cross-period median (0.96), so its estimates should sit **below** each method's cross-period median, and on the common curve.
- **Per-period verdict rule** (fixed now): fit the primary collapse model (per-method affine in x_att) without this period (LOPO). **supported** if (i) both primary estimates (T1 n̂ TALK, E1 g_eq active) fall inside their 90% LOPO predictive intervals and (ii) the period's summed LOPO log density under the collapse model is ≥ that under the regime-only rival N1; **mixed** if exactly one of (i), (ii) holds; **failed** if neither.
- Against it: estimates outside the intervals in the direction opposite to the x_att prediction, or N1 predicting the period better.

## Result
Primary collapse model (per-method affine in x_att), fitted without G06 (LOPO); shrunken = partial-pooling (BLUP) estimate under the collapse model fitted to all periods, shown beside the period's own estimate.

| Method | Own estimate ± SE | LOPO prediction [90% PI] | z | inside | Shrunken | Regime-only N1 prediction |
| --- | --- | --- | --- | --- | --- | --- |
| H03 n̂ ALL (T2) | 0.463 ± 0.052 | 0.456 [0.127, 0.786] | +0.03 | yes | 0.463 | 0.477 |
| H03 n̂ TALK (T1, primary) | 0.654 ± 0.163 | 0.443 [0.004, 0.882] | +0.79 | yes | 0.575 | 0.464 |
| H03 fast n_x (T3) | 0.122 ± 0.067 | 0.081 [-0.046, 0.208] | +0.53 | yes | 0.091 | 0.081 |
| H04 K, weekly (E3) | -0.030 ± 0.045 | 0.108 [-0.024, 0.240] | -1.72 | **no** | 0.009 | 0.119 |
| H04 n, weekly (T4) | 0.242 ± 0.113 | 0.479 [0.147, 0.812] | -1.17 | yes | 0.316 | 0.501 |
| g_eq active (E1, primary) | 0.001 ± 0.039 | 0.085 [-0.036, 0.207] | -1.14 | yes | 0.024 | 0.092 |
| g_eq talk (E2) | -0.070 ± 0.018 | 0.172 [0.056, 0.287] | -3.43 | **no** | -0.058 | 0.179 |

- (i) both primaries inside their 90% intervals: **True**; (ii) summed LOPO log density, collapse -0.72 vs regime-only -2.43: **True**.
- Direction check (prediction: below median): primaries observed n_talk above, geq_active below.
- Per-period figure: `figures/G06_residuals.png`. Data: `data/processed/H19-loop-gain-collapse/G06/residuals.parquet`.

## Scorecard (period-specific axes)
- **C** (adequacy vs. rivals, this period): collapse vs. regime-only log density +1.71 nats.
- **D** (unfitted): the period's estimates are predicted out of sample (LOPO), not fitted.
- E, G: not informed by a single period.

## Notes
- Inputs: `data/processed/H19-loop-gain-collapse/G06/inputs.json`.
