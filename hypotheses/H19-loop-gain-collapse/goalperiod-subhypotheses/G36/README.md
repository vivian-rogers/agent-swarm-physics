# H19 × G36: Interact with other AI agents outside the Village! (2026-03-23 → 2026-03-27)

**Verdict:** mixed
**Role:** exploratory (round 1, non-holdout)
**Period:** regime III (mixed) · mode C · 12.0 agents (N_room 6.0) · 3 room(s) carrying ≥ 5% of agent messages · 5 non-holdout days · 4.0 h/day (empirical).

## Why this period
One point on every method's curve. Loop-gain estimates available here: H03 n̂ ALL (T2), H03 n̂ TALK (T1, primary), H03 fast n_x (T3), H04 K, weekly (E3), H04 n, weekly (T4), H05 two-block g, active (E5), H05 two-block g, talk (E4), g_eq active (E1, primary), g_eq talk (E2). Controls: x_att = 1.13 (rank 26/35), messages per village turn 0.62, attention load k̄ = 3.4 agent messages waiting per turn, 6.5 agent messages per agent-hour, human share of chat 0.5%. Straddles the 03-24 perma-computer-use switch (1 day II, 4 days III); coded III by majority.

## Prediction
*Written 2026-10-04 00:09 UTC, before H19 related any control parameter to any loop gain (the card's P1 applied here).*
- Under the attention-dilution collapse (P1), every loop gain is affine-increasing in x_att. This period's x_att = 1.13 is **above** the cross-period median (0.96), so its estimates should sit **above** each method's cross-period median, and on the common curve.
- **Per-period verdict rule** (fixed now): fit the primary collapse model (per-method affine in x_att) without this period (LOPO). **supported** if (i) both primary estimates (T1 n̂ TALK, E1 g_eq active) fall inside their 90% LOPO predictive intervals and (ii) the period's summed LOPO log density under the collapse model is ≥ that under the regime-only rival N1; **mixed** if exactly one of (i), (ii) holds; **failed** if neither.
- Against it: estimates outside the intervals in the direction opposite to the x_att prediction, or N1 predicting the period better.

## Result
Primary collapse model (per-method affine in x_att), fitted without G36 (LOPO); shrunken = partial-pooling (BLUP) estimate under the collapse model fitted to all periods, shown beside the period's own estimate.

| Method | Own estimate ± SE | LOPO prediction [90% PI] | z | inside | Shrunken | Regime-only N1 prediction |
| --- | --- | --- | --- | --- | --- | --- |
| H03 n̂ ALL (T2) | 0.184 ± 0.101 | 0.409 [0.058, 0.760] | -1.06 | yes | 0.234 | 0.256 |
| H03 n̂ TALK (T1, primary) | 0.293 ± 0.057 | 0.402 [0.043, 0.762] | -0.50 | yes | 0.300 | 0.249 |
| H03 fast n_x (T3) | 0.008 ± 0.020 | 0.064 [-0.005, 0.134] | -1.33 | yes | 0.020 | 0.020 |
| H04 K, weekly (E3) | 0.161 ± 0.110 | 0.137 [-0.079, 0.353] | +0.19 | yes | 0.144 | 0.220 |
| H04 n, weekly (T4) | 0.381 ± 0.129 | 0.448 [0.098, 0.797] | -0.31 | yes | 0.407 | 0.351 |
| H05 two-block g, active (E5) | 0.102 ± 0.031 | 0.128 [-0.100, 0.356] | -0.19 | yes | 0.103 | 0.162 |
| H05 two-block g, talk (E4) | 0.045 ± 0.031 | 0.092 [0.012, 0.171] | -0.97 | yes | 0.064 | 0.130 |
| g_eq active (E1, primary) | 0.171 ± 0.037 | 0.121 [0.001, 0.241] | +0.70 | yes | 0.158 | 0.206 |
| g_eq talk (E2) | 0.080 ± 0.042 | 0.146 [-0.004, 0.297] | -0.72 | yes | 0.094 | 0.096 |

- (i) both primaries inside their 90% intervals: **True**; (ii) summed LOPO log density, collapse 8.93 vs regime-only 9.40: **False**.
- Direction check (prediction: above median): primaries observed n_talk below, geq_active above.
- Per-period figure: `figures/G36_residuals.png`. Data: `data/processed/H19-loop-gain-collapse/G36/residuals.parquet`.

## Scorecard (period-specific axes)
- **C** (adequacy vs. rivals, this period): collapse vs. regime-only log density -0.47 nats.
- **D** (unfitted): the period's estimates are predicted out of sample (LOPO), not fitted.
- E, G: not informed by a single period.

## Notes
- Inputs: `data/processed/H19-loop-gain-collapse/G36/inputs.json`.
