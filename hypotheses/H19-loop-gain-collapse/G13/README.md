# H19 × G13: Design, run and write up a human subjects experiment (2025-09-08 → 2025-09-19)

**Verdict:** supported
**Role:** exploratory (round 1, non-holdout)
**Period:** regime I · mode C · 6.0 agents (N_room 6.0) · 1 room(s) carrying ≥ 5% of agent messages · 10 non-holdout days · 3.0 h/day (empirical).

## Why this period
One point on every method's curve. Loop-gain estimates available here: H03 n̂ ALL (T2), H03 n̂ TALK (T1, primary), H03 fast n_x (T3), H04 K, weekly (E3), H04 n, weekly (T4), g_eq active (E1, primary), g_eq talk (E2). Controls: x_att = 0.85 (rank 12/35), messages per village turn 0.97, attention load k̄ = 4.9 agent messages waiting per turn, 25.5 agent messages per agent-hour, human share of chat 1.1%.

## Prediction
*Written 2026-10-04 00:09 UTC, before H19 related any control parameter to any loop gain (the card's P1 applied here).*
- Under the attention-dilution collapse (P1), every loop gain is affine-increasing in x_att. This period's x_att = 0.85 is **below** the cross-period median (0.96), so its estimates should sit **below** each method's cross-period median, and on the common curve.
- **Per-period verdict rule** (fixed now): fit the primary collapse model (per-method affine in x_att) without this period (LOPO). **supported** if (i) both primary estimates (T1 n̂ TALK, E1 g_eq active) fall inside their 90% LOPO predictive intervals and (ii) the period's summed LOPO log density under the collapse model is ≥ that under the regime-only rival N1; **mixed** if exactly one of (i), (ii) holds; **failed** if neither.
- Against it: estimates outside the intervals in the direction opposite to the x_att prediction, or N1 predicting the period better.

## Result
Primary collapse model (per-method affine in x_att), fitted without G13 (LOPO); shrunken = partial-pooling (BLUP) estimate under the collapse model fitted to all periods, shown beside the period's own estimate.

| Method | Own estimate ± SE | LOPO prediction [90% PI] | z | inside | Shrunken | Regime-only N1 prediction |
| --- | --- | --- | --- | --- | --- | --- |
| H03 n̂ ALL (T2) | 0.518 ± 0.034 | 0.446 [0.124, 0.768] | +0.37 | yes | 0.516 | 0.475 |
| H03 n̂ TALK (T1, primary) | 0.574 ± 0.028 | 0.437 [0.085, 0.789] | +0.64 | yes | 0.572 | 0.464 |
| H03 fast n_x (T3) | 0.024 ± 0.020 | 0.082 [0.012, 0.152] | -1.37 | yes | 0.036 | 0.085 |
| H04 K, weekly (E3) | 0.002 ± 0.045 | 0.110 [-0.025, 0.246] | -1.31 | yes | 0.033 | 0.118 |
| H04 n, weekly (T4) | 0.556 ± 0.113 | 0.454 [0.116, 0.792] | +0.50 | yes | 0.524 | 0.482 |
| g_eq active (E1, primary) | 0.030 ± 0.014 | 0.090 [-0.016, 0.197] | -0.93 | yes | 0.033 | 0.092 |
| g_eq talk (E2) | 0.121 ± 0.015 | 0.158 [0.020, 0.297] | -0.45 | yes | 0.122 | 0.170 |

- (i) both primaries inside their 90% intervals: **True**; (ii) summed LOPO log density, collapse 6.44 vs regime-only 6.39: **True**.
- Direction check (prediction: below median): primaries observed n_talk above, geq_active below.
- Per-period figure: `figures/G13_residuals.png`. Data: `data/processed/H19-loop-gain-collapse/G13/residuals.parquet`.

## Scorecard (period-specific axes)
- **C** (adequacy vs. rivals, this period): collapse vs. regime-only log density +0.05 nats.
- **D** (unfitted): the period's estimates are predicted out of sample (LOPO), not fitted.
- E, G: not informed by a single period.

## Notes
- Inputs: `data/processed/H19-loop-gain-collapse/G13/inputs.json`.
