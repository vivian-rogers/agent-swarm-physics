# H19 × G02: Unsupervised agents look back on their previous goal and forward to their next (2025-05-10 → 2025-05-11)

**Verdict:** failed
**Role:** exploratory (round 1, non-holdout)
**Period:** regime I · mode F · 4.0 agents (N_room 4.0) · 1 room(s) carrying ≥ 5% of agent messages · 2 non-holdout days · 1.9 h/day (empirical).

## Why this period
One point on every method's curve. Loop-gain estimates available here: H03 n̂ ALL (T2), H03 n̂ TALK (T1, primary), g_eq active (E1, primary), g_eq talk (E2). Controls: x_att = 0.81 (rank 5/35), messages per village turn 0.90, attention load k̄ = 2.7 agent messages waiting per turn, 37.1 agent messages per agent-hour, human share of chat 0.0%. Two weekend days, 'unsupervised'; the profile CI is used for n̂.

## Prediction
*Written 2026-10-04 00:09 UTC, before H19 related any control parameter to any loop gain (the card's P1 applied here).*
- Under the attention-dilution collapse (P1), every loop gain is affine-increasing in x_att. This period's x_att = 0.81 is **below** the cross-period median (0.96), so its estimates should sit **below** each method's cross-period median, and on the common curve.
- **Per-period verdict rule** (fixed now): fit the primary collapse model (per-method affine in x_att) without this period (LOPO). **supported** if (i) both primary estimates (T1 n̂ TALK, E1 g_eq active) fall inside their 90% LOPO predictive intervals and (ii) the period's summed LOPO log density under the collapse model is ≥ that under the regime-only rival N1; **mixed** if exactly one of (i), (ii) holds; **failed** if neither.
- Against it: estimates outside the intervals in the direction opposite to the x_att prediction, or N1 predicting the period better.

## Result
Primary collapse model (per-method affine in x_att), fitted without G02 (LOPO); shrunken = partial-pooling (BLUP) estimate under the collapse model fitted to all periods, shown beside the period's own estimate.

| Method | Own estimate ± SE | LOPO prediction [90% PI] | z | inside | Shrunken | Regime-only N1 prediction |
| --- | --- | --- | --- | --- | --- | --- |
| H03 n̂ ALL (T2) | 0.724 ± 0.055 | 0.443 [0.123, 0.762] | +1.45 | yes | 0.702 | 0.465 |
| H03 n̂ TALK (T1, primary) | 0.722 ± 0.058 | 0.435 [0.081, 0.789] | +1.34 | yes | 0.702 | 0.457 |
| g_eq active (E1, primary) | 0.225 ± 0.052 | 0.074 [-0.056, 0.203] | +1.92 | **no** | 0.163 | 0.082 |
| g_eq talk (E2) | 0.278 ± 0.069 | 0.154 [-0.022, 0.330] | +1.16 | yes | 0.226 | 0.164 |

- (i) both primaries inside their 90% intervals: **False**; (ii) summed LOPO log density, collapse -0.18 vs regime-only 0.28: **False**.
- Direction check (prediction: below median): primaries observed n_talk above, geq_active above.
- Per-period figure: `figures/G02_residuals.png`. Data: `data/processed/H19-loop-gain-collapse/G02/residuals.parquet`.

## Scorecard (period-specific axes)
- **C** (adequacy vs. rivals, this period): collapse vs. regime-only log density -0.46 nats.
- **D** (unfitted): the period's estimates are predicted out of sample (LOPO), not fitted.
- E, G: not informed by a single period.

## Notes
- Inputs: `data/processed/H19-loop-gain-collapse/G02/inputs.json`.
