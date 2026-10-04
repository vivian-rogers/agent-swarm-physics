# H19 × G38: Choose a charity and raise as much money as you can for it (2026-04-02 → 2026-04-24)

**Verdict:** supported
**Verdict (1b):** mixed (round 1b, 2026-10-04, corrected data, pre-registered E1; with the day-edge-adjusted activity gain: mixed; round 1: supported)
**Role:** exploratory (round 1, non-holdout)
**Period:** regime III · mode C · 12.5 agents (N_room 6.4) · 2 room(s) carrying ≥ 5% of agent messages · 17 non-holdout days · 4.0 h/day (empirical).

## Why this period
One point on every method's curve. Loop-gain estimates available here: H03 n̂ ALL (T2), H03 n̂ TALK (T1, primary), H03 fast n_x (T3), H04 K, weekly (E3), H04 n, weekly (T4), H05 two-block g, active (E5), H05 two-block g, talk (E4), g_eq active (E1, primary), g_eq talk (E2). Controls: x_att = 1.53 (rank 29/35), messages per village turn 0.47, attention load k̄ = 2.5 agent messages waiting per turn, 5.1 agent messages per agent-hour, human share of chat 0.6%. Longest exploratory regime-III period (17 days, 4 step changes inside per H03).

## Prediction
*Written 2026-10-04 00:09 UTC, before H19 related any control parameter to any loop gain (the card's P1 applied here).*
- Under the attention-dilution collapse (P1), every loop gain is affine-increasing in x_att. This period's x_att = 1.53 is **above** the cross-period median (0.96), so its estimates should sit **above** each method's cross-period median, and on the common curve.
- **Per-period verdict rule** (fixed now): fit the primary collapse model (per-method affine in x_att) without this period (LOPO). **supported** if (i) both primary estimates (T1 n̂ TALK, E1 g_eq active) fall inside their 90% LOPO predictive intervals and (ii) the period's summed LOPO log density under the collapse model is ≥ that under the regime-only rival N1; **mixed** if exactly one of (i), (ii) holds; **failed** if neither.
- Against it: estimates outside the intervals in the direction opposite to the x_att prediction, or N1 predicting the period better.

## Result
Primary collapse model (per-method affine in x_att), fitted without G38 (LOPO); shrunken = partial-pooling (BLUP) estimate under the collapse model fitted to all periods, shown beside the period's own estimate.

| Method | Own estimate ± SE | LOPO prediction [90% PI] | z | inside | Shrunken | Regime-only N1 prediction |
| --- | --- | --- | --- | --- | --- | --- |
| H03 n̂ ALL (T2) | 0.569 ± 0.132 | 0.324 [-0.061, 0.709] | +1.05 | yes | 0.492 | 0.215 |
| H03 n̂ TALK (T1, primary) | 0.321 ± 0.135 | 0.336 [-0.082, 0.754] | -0.06 | yes | 0.325 | 0.248 |
| H03 fast n_x (T3) | 0.020 ± 0.020 | 0.040 [-0.033, 0.113] | -0.46 | yes | 0.024 | 0.018 |
| H04 K, weekly (E3) | 0.146 ± 0.064 | 0.189 [0.026, 0.352] | -0.43 | yes | 0.164 | 0.230 |
| H04 n, weekly (T4) | 0.388 ± 0.074 | 0.427 [0.114, 0.740] | -0.21 | yes | 0.394 | 0.348 |
| H05 two-block g, active (E5) | 0.259 ± 0.111 | 0.135 [-0.114, 0.383] | +0.82 | yes | 0.191 | 0.139 |
| H05 two-block g, talk (E4) | 0.084 ± 0.055 | 0.125 [0.017, 0.232] | -0.63 | yes | 0.114 | 0.118 |
| g_eq active (E1, primary) | 0.123 ± 0.018 | 0.178 [0.066, 0.289] | -0.80 | yes | 0.128 | 0.215 |
| g_eq talk (E2) | 0.040 ± 0.011 | 0.135 [-0.001, 0.272] | -1.15 | yes | 0.042 | 0.103 |

- (i) both primaries inside their 90% intervals: **True**; (ii) summed LOPO log density, collapse 9.15 vs regime-only 7.97: **True**.
- Direction check (prediction: above median): primaries observed n_talk below, geq_active above.
- Per-period figure: `figures/G38_residuals.png`. Data: `data/processed/H19-loop-gain-collapse/G38/residuals.parquet`.

## Scorecard (period-specific axes)
- **C** (adequacy vs. rivals, this period): collapse vs. regime-only log density +1.18 nats.
- **D** (unfitted): the period's estimates are predicted out of sample (LOPO), not fitted.
- E, G: not informed by a single period.

## Notes
- Inputs: `data/processed/H19-loop-gain-collapse/G38/inputs.json`.

<!-- R1B START -->
## Round 1b (improved data, 2026-10-04)
H19's own gains re-estimated on `activity_bins_fixed` (+ `outages_fixed`), H02/H03 inputs from their round-1b runs; H04's K_week and H05's gains (built on the buggy table, not yet re-run by their owners) are dropped. "DQ8 trim": all-present window, explained joint silences removed; "H38-conditioned": agent-state conditioning of day edges, infra errors and consolidations.

| Method | Round 1 | **Round 1b** | Round-1b LOPO prediction [90% PI] (raw E1 run) |
| --- | --- | --- | --- |
| E1 g_eq active (raw) | 0.123 | **0.270 ± 0.016** | 0.266 [0.100, 0.433] |
| E1 g_eq active, DQ8 trim | – | **0.006 ± 0.022** | – |
| E1 g_eq active, H38-conditioned | – | **0.042 ± 0.028** | – |
| E2 g_eq talk | 0.040 | **0.107 ± 0.025** | 0.182 [0.012, 0.353] |
| T1 n̂ TALK | 0.321 | **0.140 ± 0.035** | 0.327 [-0.024, 0.678] |
| T3 fast n_x | 0.020 | **0.010 ± 0.020** | 0.041 [-0.031, 0.113] |

Per-period rule (unchanged): (i) both primaries inside their LOPO 90% intervals: raw run True, trim run True; (ii) log density ≥ regime-only rival: raw False (5.96 vs 6.26), trim False.
Source: `data/processed/H19-loop-gain-collapse/r1b/results*/explore.json`.
<!-- R1B END -->
