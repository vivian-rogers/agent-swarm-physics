# H19 × G27: Hack the OWASP Juice Shop hacking playground. Compete to see which agent can complete the most challenges (2026-01-12 → 2026-01-23)

**Verdict:** supported
**Role:** exploratory (round 1, non-holdout)
**Period:** regime I · mode K · 10.0 agents (N_room 10.0) · 1 room(s) carrying ≥ 5% of agent messages · 10 non-holdout days · 4.0 h/day (empirical).

## Why this period
One point on every method's curve. Loop-gain estimates available here: H03 n̂ ALL (T2), H03 n̂ TALK (T1, primary), H03 fast n_x (T3), H04 K, weekly (E3), H04 n, weekly (T4), g_eq active (E1, primary), g_eq talk (E2). Controls: x_att = 0.94 (rank 16/35), messages per village turn 0.96, attention load k̄ = 8.6 agent messages waiting per turn, 9.3 agent messages per agent-hour, human share of chat 0.2%.

## Prediction
*Written 2026-10-04 00:09 UTC, before H19 related any control parameter to any loop gain (the card's P1 applied here).*
- Under the attention-dilution collapse (P1), every loop gain is affine-increasing in x_att. This period's x_att = 0.94 is **below** the cross-period median (0.96), so its estimates should sit **below** each method's cross-period median, and on the common curve.
- **Per-period verdict rule** (fixed now): fit the primary collapse model (per-method affine in x_att) without this period (LOPO). **supported** if (i) both primary estimates (T1 n̂ TALK, E1 g_eq active) fall inside their 90% LOPO predictive intervals and (ii) the period's summed LOPO log density under the collapse model is ≥ that under the regime-only rival N1; **mixed** if exactly one of (i), (ii) holds; **failed** if neither.
- Against it: estimates outside the intervals in the direction opposite to the x_att prediction, or N1 predicting the period better.

## Result
Primary collapse model (per-method affine in x_att), fitted without G27 (LOPO); shrunken = partial-pooling (BLUP) estimate under the collapse model fitted to all periods, shown beside the period's own estimate.

| Method | Own estimate ± SE | LOPO prediction [90% PI] | z | inside | Shrunken | Regime-only N1 prediction |
| --- | --- | --- | --- | --- | --- | --- |
| H03 n̂ ALL (T2) | 0.207 ± 0.038 | 0.444 [0.130, 0.758] | -1.24 | yes | 0.217 | 0.490 |
| H03 n̂ TALK (T1, primary) | 0.406 ± 0.251 | 0.430 [-0.108, 0.969] | -0.08 | yes | 0.420 | 0.471 |
| H03 fast n_x (T3) | 0.010 ± 0.020 | 0.077 [0.008, 0.146] | -1.59 | yes | 0.025 | 0.086 |
| H04 K, weekly (E3) | 0.132 ± 0.045 | 0.113 [-0.028, 0.255] | +0.22 | yes | 0.127 | 0.110 |
| H04 n, weekly (T4) | 0.282 ± 0.113 | 0.465 [0.133, 0.798] | -0.91 | yes | 0.340 | 0.498 |
| g_eq active (E1, primary) | 0.136 ± 0.023 | 0.095 [-0.015, 0.206] | +0.60 | yes | 0.131 | 0.085 |
| g_eq talk (E2) | 0.122 ± 0.006 | 0.154 [0.018, 0.291] | -0.39 | yes | 0.122 | 0.170 |

- (i) both primaries inside their 90% intervals: **True**; (ii) summed LOPO log density, collapse 6.03 vs regime-only 4.54: **True**.
- Direction check (prediction: below median): primaries observed n_talk below, geq_active above.
- Per-period figure: `figures/G27_residuals.png`. Data: `data/processed/H19-loop-gain-collapse/G27/residuals.parquet`.

## Scorecard (period-specific axes)
- **C** (adequacy vs. rivals, this period): collapse vs. regime-only log density +1.49 nats.
- **D** (unfitted): the period's estimates are predicted out of sample (LOPO), not fitted.
- E, G: not informed by a single period.

## Notes
- Inputs: `data/processed/H19-loop-gain-collapse/G27/inputs.json`.
