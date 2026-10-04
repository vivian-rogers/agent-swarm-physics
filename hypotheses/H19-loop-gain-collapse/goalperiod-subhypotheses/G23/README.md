# H19 × G23: Compete against each other in an online chess tournament (2025-12-15 → 2025-12-19)

**Verdict:** supported
**Verdict (1b):** supported (round 1b, 2026-10-04, corrected data, pre-registered E1; with the day-edge-adjusted activity gain: supported; round 1: supported)
**Role:** exploratory (round 1, non-holdout)
**Period:** regime I · mode K · 10.0 agents (N_room 10.0) · 1 room(s) carrying ≥ 5% of agent messages · 5 non-holdout days · 4.0 h/day (empirical).

## Why this period
One point on every method's curve. Loop-gain estimates available here: H03 n̂ ALL (T2), H03 n̂ TALK (T1, primary), H03 fast n_x (T3), H04 K, weekly (E3), H04 n, weekly (T4), g_eq active (E1, primary), g_eq talk (E2). Controls: x_att = 0.93 (rank 15/35), messages per village turn 0.96, attention load k̄ = 8.6 agent messages waiting per turn, 8.9 agent messages per agent-hour, human share of chat 1.3%.

## Prediction
*Written 2026-10-04 00:09 UTC, before H19 related any control parameter to any loop gain (the card's P1 applied here).*
- Under the attention-dilution collapse (P1), every loop gain is affine-increasing in x_att. This period's x_att = 0.93 is **below** the cross-period median (0.96), so its estimates should sit **below** each method's cross-period median, and on the common curve.
- **Per-period verdict rule** (fixed now): fit the primary collapse model (per-method affine in x_att) without this period (LOPO). **supported** if (i) both primary estimates (T1 n̂ TALK, E1 g_eq active) fall inside their 90% LOPO predictive intervals and (ii) the period's summed LOPO log density under the collapse model is ≥ that under the regime-only rival N1; **mixed** if exactly one of (i), (ii) holds; **failed** if neither.
- Against it: estimates outside the intervals in the direction opposite to the x_att prediction, or N1 predicting the period better.

## Result
Primary collapse model (per-method affine in x_att), fitted without G23 (LOPO); shrunken = partial-pooling (BLUP) estimate under the collapse model fitted to all periods, shown beside the period's own estimate.

| Method | Own estimate ± SE | LOPO prediction [90% PI] | z | inside | Shrunken | Regime-only N1 prediction |
| --- | --- | --- | --- | --- | --- | --- |
| H03 n̂ ALL (T2) | 0.256 ± 0.026 | 0.443 [0.129, 0.757] | -0.98 | yes | 0.259 | 0.488 |
| H03 n̂ TALK (T1, primary) | 0.104 ± 0.058 | 0.444 [0.096, 0.791] | -1.61 | yes | 0.129 | 0.489 |
| H03 fast n_x (T3) | 0.062 ± 0.020 | 0.075 [0.003, 0.147] | -0.28 | yes | 0.065 | 0.083 |
| H04 K, weekly (E3) | 0.032 ± 0.063 | 0.117 [-0.040, 0.274] | -0.89 | yes | 0.070 | 0.115 |
| H04 n, weekly (T4) | 0.978 ± 0.160 | 0.434 [0.077, 0.791] | +2.51 | **no** | 0.716 | 0.464 |
| g_eq active (E1, primary) | 0.040 ± 0.024 | 0.100 [-0.011, 0.211] | -0.89 | yes | 0.048 | 0.091 |
| g_eq talk (E2) | 0.197 ± 0.071 | 0.152 [-0.027, 0.330] | +0.42 | yes | 0.177 | 0.167 |

- (i) both primaries inside their 90% intervals: **True**; (ii) summed LOPO log density, collapse 2.86 vs regime-only 2.32: **True**.
- Direction check (prediction: below median): primaries observed n_talk below, geq_active below.
- Per-period figure: `figures/G23_residuals.png`. Data: `data/processed/H19-loop-gain-collapse/G23/residuals.parquet`.

## Scorecard (period-specific axes)
- **C** (adequacy vs. rivals, this period): collapse vs. regime-only log density +0.54 nats.
- **D** (unfitted): the period's estimates are predicted out of sample (LOPO), not fitted.
- E, G: not informed by a single period.

## Notes
- Inputs: `data/processed/H19-loop-gain-collapse/G23/inputs.json`.

<!-- R1B START -->
## Round 1b (improved data, 2026-10-04)
H19's own gains re-estimated on `activity_bins_fixed` (+ `outages_fixed`), H02/H03 inputs from their round-1b runs; H04's K_week and H05's gains (built on the buggy table, not yet re-run by their owners) are dropped. "DQ8 trim": all-present window, explained joint silences removed; "H38-conditioned": agent-state conditioning of day edges, infra errors and consolidations.

| Method | Round 1 | **Round 1b** | Round-1b LOPO prediction [90% PI] (raw E1 run) |
| --- | --- | --- | --- |
| E1 g_eq active (raw) | 0.040 | **0.018 ± 0.036** | 0.164 [-0.002, 0.329] |
| E1 g_eq active, DQ8 trim | – | **-0.009 ± 0.033** | – |
| E1 g_eq active, H38-conditioned | – | **-0.020 ± 0.039** | – |
| E2 g_eq talk | 0.197 | **0.212 ± 0.040** | 0.182 [0.006, 0.357] |
| T1 n̂ TALK | 0.104 | **0.107 ± 0.051** | 0.417 [0.075, 0.759] |
| T3 fast n_x | 0.062 | **0.063 ± 0.020** | 0.078 [0.007, 0.149] |

Per-period rule (unchanged): (i) both primaries inside their LOPO 90% intervals: raw run True, trim run True; (ii) log density ≥ regime-only rival: raw True (1.05 vs 0.64), trim True.
Source: `data/processed/H19-loop-gain-collapse/r1b/results*/explore.json`.
<!-- R1B END -->
