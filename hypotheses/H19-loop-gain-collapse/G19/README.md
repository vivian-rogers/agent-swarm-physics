# H19 × G19: Create a popular daily puzzle game like Wordle (2025-11-03 → 2025-11-14)

**Verdict:** mixed
**Role:** exploratory (round 1, non-holdout)
**Period:** regime I · mode C · 7.1 agents (N_room 7.1) · 1 room(s) carrying ≥ 5% of agent messages · 10 non-holdout days · 4.0 h/day (empirical).

## Why this period
One point on every method's curve. Loop-gain estimates available here: H03 n̂ ALL (T2), H03 n̂ TALK (T1, primary), H03 fast n_x (T3), H04 K, weekly (E3), H04 n, weekly (T4), g_eq active (E1, primary), g_eq talk (E2). Controls: x_att = 0.97 (rank 21/35), messages per village turn 0.87, attention load k̄ = 5.3 agent messages waiting per turn, 18.9 agent messages per agent-hour, human share of chat 0.2%.

## Prediction
*Written 2026-10-04 00:09 UTC, before H19 related any control parameter to any loop gain (the card's P1 applied here).*
- Under the attention-dilution collapse (P1), every loop gain is affine-increasing in x_att. This period's x_att = 0.97 is **above** the cross-period median (0.96), so its estimates should sit **above** each method's cross-period median, and on the common curve.
- **Per-period verdict rule** (fixed now): fit the primary collapse model (per-method affine in x_att) without this period (LOPO). **supported** if (i) both primary estimates (T1 n̂ TALK, E1 g_eq active) fall inside their 90% LOPO predictive intervals and (ii) the period's summed LOPO log density under the collapse model is ≥ that under the regime-only rival N1; **mixed** if exactly one of (i), (ii) holds; **failed** if neither.
- Against it: estimates outside the intervals in the direction opposite to the x_att prediction, or N1 predicting the period better.

## Result
Primary collapse model (per-method affine in x_att), fitted without G19 (LOPO); shrunken = partial-pooling (BLUP) estimate under the collapse model fitted to all periods, shown beside the period's own estimate.

| Method | Own estimate ± SE | LOPO prediction [90% PI] | z | inside | Shrunken | Regime-only N1 prediction |
| --- | --- | --- | --- | --- | --- | --- |
| H03 n̂ ALL (T2) | 0.656 ± 0.054 | 0.422 [0.102, 0.742] | +1.20 | yes | 0.639 | 0.469 |
| H03 n̂ TALK (T1, primary) | 0.691 ± 0.052 | 0.414 [0.065, 0.763] | +1.31 | yes | 0.675 | 0.459 |
| H03 fast n_x (T3) | 0.107 ± 0.020 | 0.071 [-0.000, 0.142] | +0.84 | yes | 0.099 | 0.080 |
| H04 K, weekly (E3) | 0.110 ± 0.045 | 0.119 [-0.023, 0.260] | -0.10 | yes | 0.112 | 0.112 |
| H04 n, weekly (T4) | 0.643 ± 0.113 | 0.444 [0.115, 0.774] | +0.99 | yes | 0.580 | 0.476 |
| g_eq active (E1, primary) | 0.109 ± 0.038 | 0.101 [-0.021, 0.224] | +0.11 | yes | 0.107 | 0.087 |
| g_eq talk (E2) | 0.264 ± 0.025 | 0.147 [0.010, 0.284] | +1.41 | yes | 0.254 | 0.162 |

- (i) both primaries inside their 90% intervals: **True**; (ii) summed LOPO log density, collapse 5.62 vs regime-only 6.63: **False**.
- Direction check (prediction: above median): primaries observed n_talk above, geq_active below.
- Per-period figure: `figures/G19_residuals.png`. Data: `data/processed/H19-loop-gain-collapse/G19/residuals.parquet`.

## Scorecard (period-specific axes)
- **C** (adequacy vs. rivals, this period): collapse vs. regime-only log density -1.02 nats.
- **D** (unfitted): the period's estimates are predicted out of sample (LOPO), not fitted.
- E, G: not informed by a single period.

## Notes
- Inputs: `data/processed/H19-loop-gain-collapse/G19/inputs.json`.
