# H19 × G05: Holiday: do whatever you like! Next goal will begin soon (2025-06-19 → 2025-06-25)

**Verdict:** supported
**Role:** exploratory (round 1, non-holdout)
**Period:** regime I · mode F · 4.0 agents (N_room 4.0) · 1 room(s) carrying ≥ 5% of agent messages · 5 non-holdout days · 2.0 h/day (empirical).

## Why this period
One point on every method's curve. Loop-gain estimates available here: H03 n̂ ALL (T2), H03 n̂ TALK (T1, primary), H03 fast n_x (T3), g_eq active (E1, primary), g_eq talk (E2). Controls: x_att = 0.78 (rank 1/35), messages per village turn 0.96, attention load k̄ = 2.9 agent messages waiting per turn, 28.1 agent messages per agent-hour, human share of chat 43.8%.

## Prediction
*Written 2026-10-04 00:09 UTC, before H19 related any control parameter to any loop gain (the card's P1 applied here).*
- Under the attention-dilution collapse (P1), every loop gain is affine-increasing in x_att. This period's x_att = 0.78 is **below** the cross-period median (0.96), so its estimates should sit **below** each method's cross-period median, and on the common curve.
- **Per-period verdict rule** (fixed now): fit the primary collapse model (per-method affine in x_att) without this period (LOPO). **supported** if (i) both primary estimates (T1 n̂ TALK, E1 g_eq active) fall inside their 90% LOPO predictive intervals and (ii) the period's summed LOPO log density under the collapse model is ≥ that under the regime-only rival N1; **mixed** if exactly one of (i), (ii) holds; **failed** if neither.
- Against it: estimates outside the intervals in the direction opposite to the x_att prediction, or N1 predicting the period better.

## Result
Primary collapse model (per-method affine in x_att), fitted without G05 (LOPO); shrunken = partial-pooling (BLUP) estimate under the collapse model fitted to all periods, shown beside the period's own estimate.

| Method | Own estimate ± SE | LOPO prediction [90% PI] | z | inside | Shrunken | Regime-only N1 prediction |
| --- | --- | --- | --- | --- | --- | --- |
| H03 n̂ ALL (T2) | 0.274 ± 0.061 | 0.472 [0.142, 0.802] | -0.99 | yes | 0.293 | 0.486 |
| H03 n̂ TALK (T1, primary) | 0.154 ± 0.096 | 0.472 [0.095, 0.849] | -1.39 | yes | 0.208 | 0.484 |
| H03 fast n_x (T3) | 0.072 ± 0.024 | 0.084 [0.008, 0.161] | -0.27 | yes | 0.076 | 0.082 |
| g_eq active (E1, primary) | -0.069 ± 0.083 | 0.081 [-0.090, 0.252] | -1.44 | yes | 0.026 | 0.092 |
| g_eq talk (E2) | 0.095 ± 0.085 | 0.162 [-0.033, 0.356] | -0.56 | yes | 0.129 | 0.169 |

- (i) both primaries inside their 90% intervals: **True**; (ii) summed LOPO log density, collapse 3.27 vs regime-only 2.90: **True**.
- Direction check (prediction: below median): primaries observed n_talk below, geq_active below.
- Per-period figure: `figures/G05_residuals.png`. Data: `data/processed/H19-loop-gain-collapse/G05/residuals.parquet`.

## Scorecard (period-specific axes)
- **C** (adequacy vs. rivals, this period): collapse vs. regime-only log density +0.36 nats.
- **D** (unfitted): the period's estimates are predicted out of sample (LOPO), not fitted.
- E, G: not informed by a single period.

## Notes
- Inputs: `data/processed/H19-loop-gain-collapse/G05/inputs.json`.
