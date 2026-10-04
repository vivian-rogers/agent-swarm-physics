# H19 × G11: Pursue whatever you'd like to (2025-08-25 → 2025-08-29)

**Verdict:** failed
**Verdict (1b):** mixed (round 1b, 2026-10-04, corrected data, pre-registered E1; with the day-edge-adjusted activity gain: mixed; round 1: failed)
**Role:** replication (exploratory (round 1, non-holdout))
**Period:** regime I · mode F · 7.0 agents (N_room 7.0) · 1 room(s) carrying ≥ 5% of agent messages · 5 non-holdout days · 3.0 h/day (empirical).

## Why this period
One point on every method's curve. Loop-gain estimates available here: H03 n̂ ALL (T2), H03 n̂ TALK (T1, primary), H03 fast n_x (T3), H04 K, weekly (E3), H04 n, weekly (T4), g_eq active (E1, primary), g_eq talk (E2). Controls: x_att = 0.92 (rank 14/35), messages per village turn 0.92, attention load k̄ = 5.5 agent messages waiting per turn, 23.0 agent messages per agent-hour, human share of chat 0.4%.

## Prediction
*Written 2026-10-04 00:09 UTC, before H19 related any control parameter to any loop gain (the card's P1 applied here).*
- Under the attention-dilution collapse (P1), every loop gain is affine-increasing in x_att. This period's x_att = 0.92 is **below** the cross-period median (0.96), so its estimates should sit **below** each method's cross-period median, and on the common curve.
- **Per-period verdict rule** (fixed now): fit the primary collapse model (per-method affine in x_att) without this period (LOPO). **supported** if (i) both primary estimates (T1 n̂ TALK, E1 g_eq active) fall inside their 90% LOPO predictive intervals and (ii) the period's summed LOPO log density under the collapse model is ≥ that under the regime-only rival N1; **mixed** if exactly one of (i), (ii) holds; **failed** if neither.
- Against it: estimates outside the intervals in the direction opposite to the x_att prediction, or N1 predicting the period better.

## Result
Primary collapse model (per-method affine in x_att), fitted without G11 (LOPO); shrunken = partial-pooling (BLUP) estimate under the collapse model fitted to all periods, shown beside the period's own estimate.

| Method | Own estimate ± SE | LOPO prediction [90% PI] | z | inside | Shrunken | Regime-only N1 prediction |
| --- | --- | --- | --- | --- | --- | --- |
| H03 n̂ ALL (T2) | 0.630 ± 0.076 | 0.432 [0.097, 0.767] | +0.97 | yes | 0.602 | 0.470 |
| H03 n̂ TALK (T1, primary) | 0.610 ± 0.082 | 0.426 [0.055, 0.797] | +0.81 | yes | 0.585 | 0.463 |
| H03 fast n_x (T3) | 0.067 ± 0.026 | 0.076 [-0.001, 0.152] | -0.19 | yes | 0.069 | 0.083 |
| H04 K, weekly (E3) | 0.289 ± 0.063 | 0.103 [-0.044, 0.250] | +2.09 | **no** | 0.207 | 0.103 |
| H04 n, weekly (T4) | 0.600 ± 0.160 | 0.451 [0.069, 0.833] | +0.64 | yes | 0.528 | 0.481 |
| g_eq active (E1, primary) | 0.302 ± 0.071 | 0.089 [-0.061, 0.239] | +2.33 | **no** | 0.182 | 0.081 |
| g_eq talk (E2) | 0.217 ± 0.043 | 0.151 [-0.001, 0.303] | +0.71 | yes | 0.203 | 0.165 |

- (i) both primaries inside their 90% intervals: **False**; (ii) summed LOPO log density, collapse 2.20 vs regime-only 2.65: **False**.
- Direction check (prediction: below median): primaries observed n_talk above, geq_active above.
- Per-period figure: `figures/G11_residuals.png`. Data: `data/processed/H19-loop-gain-collapse/G11/residuals.parquet`.

## Scorecard (period-specific axes)
- **C** (adequacy vs. rivals, this period): collapse vs. regime-only log density -0.45 nats.
- **D** (unfitted): the period's estimates are predicted out of sample (LOPO), not fitted.
- E, G: not informed by a single period.

## Notes
- Inputs: `data/processed/H19-loop-gain-collapse/G11/inputs.json`.

<!-- R1B START -->
## Round 1b (improved data, 2026-10-04)
H19's own gains re-estimated on `activity_bins_fixed` (+ `outages_fixed`), H02/H03 inputs from their round-1b runs; H04's K_week and H05's gains (built on the buggy table, not yet re-run by their owners) are dropped. "DQ8 trim": all-present window, explained joint silences removed; "H38-conditioned": agent-state conditioning of day edges, infra errors and consolidations.

| Method | Round 1 | **Round 1b** | Round-1b LOPO prediction [90% PI] (raw E1 run) |
| --- | --- | --- | --- |
| E1 g_eq active (raw) | 0.302 | **0.326 ± 0.083** | 0.151 [-0.055, 0.357] |
| E1 g_eq active, DQ8 trim | – | **0.200 ± 0.089** | – |
| E1 g_eq active, H38-conditioned | – | **0.239 ± 0.072** | – |
| E2 g_eq talk | 0.217 | **0.192 ± 0.052** | 0.183 [-0.002, 0.367] |
| T1 n̂ TALK | 0.610 | **0.601 ± 0.078** | 0.400 [0.037, 0.763] |
| T3 fast n_x | 0.067 | **0.067 ± 0.020** | 0.079 [0.007, 0.150] |

Per-period rule (unchanged): (i) both primaries inside their LOPO 90% intervals: raw run True, trim run True; (ii) log density ≥ regime-only rival: raw False (4.37 vs 4.60), trim False.
Source: `data/processed/H19-loop-gain-collapse/r1b/results*/explore.json`.
<!-- R1B END -->
