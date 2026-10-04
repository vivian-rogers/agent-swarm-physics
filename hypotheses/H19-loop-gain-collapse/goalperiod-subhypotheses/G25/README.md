# H19 × G25: Create a digital museum of 2025 (2025-12-29 → 2026-01-02)

**Verdict:** mixed
**Verdict (1b):** mixed (round 1b, 2026-10-04, corrected data, pre-registered E1; with the day-edge-adjusted activity gain: mixed; round 1: mixed)
**Role:** exploratory (round 1, non-holdout)
**Period:** regime I · mode C · 10.0 agents (N_room 10.0) · 1 room(s) carrying ≥ 5% of agent messages · 5 non-holdout days · 4.0 h/day (empirical).

## Why this period
One point on every method's curve. Loop-gain estimates available here: H03 n̂ ALL (T2), H03 n̂ TALK (T1, primary), H03 fast n_x (T3), H04 K, weekly (E3), H04 n, weekly (T4), g_eq active (E1, primary), g_eq talk (E2). Controls: x_att = 0.99 (rank 22/35), messages per village turn 0.90, attention load k̄ = 8.1 agent messages waiting per turn, 13.0 agent messages per agent-hour, human share of chat 0.2%.

## Prediction
*Written 2026-10-04 00:09 UTC, before H19 related any control parameter to any loop gain (the card's P1 applied here).*
- Under the attention-dilution collapse (P1), every loop gain is affine-increasing in x_att. This period's x_att = 0.99 is **above** the cross-period median (0.96), so its estimates should sit **above** each method's cross-period median, and on the common curve.
- **Per-period verdict rule** (fixed now): fit the primary collapse model (per-method affine in x_att) without this period (LOPO). **supported** if (i) both primary estimates (T1 n̂ TALK, E1 g_eq active) fall inside their 90% LOPO predictive intervals and (ii) the period's summed LOPO log density under the collapse model is ≥ that under the regime-only rival N1; **mixed** if exactly one of (i), (ii) holds; **failed** if neither.
- Against it: estimates outside the intervals in the direction opposite to the x_att prediction, or N1 predicting the period better.

## Result
Primary collapse model (per-method affine in x_att), fitted without G25 (LOPO); shrunken = partial-pooling (BLUP) estimate under the collapse model fitted to all periods, shown beside the period's own estimate.

| Method | Own estimate ± SE | LOPO prediction [90% PI] | z | inside | Shrunken | Regime-only N1 prediction |
| --- | --- | --- | --- | --- | --- | --- |
| H03 n̂ ALL (T2) | 0.372 ± 0.128 | 0.429 [0.051, 0.807] | -0.25 | yes | 0.390 | 0.480 |
| H03 n̂ TALK (T1, primary) | 0.379 ± 0.103 | 0.424 [0.036, 0.811] | -0.19 | yes | 0.387 | 0.474 |
| H03 fast n_x (T3) | 0.107 ± 0.021 | 0.070 [-0.002, 0.142] | +0.85 | yes | 0.098 | 0.080 |
| H04 K, weekly (E3) | 0.051 ± 0.063 | 0.122 [-0.035, 0.280] | -0.74 | yes | 0.083 | 0.114 |
| H04 n, weekly (T4) | 0.389 ± 0.160 | 0.456 [0.072, 0.839] | -0.29 | yes | 0.421 | 0.490 |
| g_eq active (E1, primary) | 0.045 ± 0.033 | 0.106 [-0.011, 0.223] | -0.85 | yes | 0.059 | 0.091 |
| g_eq talk (E2) | 0.134 ± 0.026 | 0.151 [0.009, 0.294] | -0.20 | yes | 0.136 | 0.169 |

- (i) both primaries inside their 90% intervals: **True**; (ii) summed LOPO log density, collapse 7.40 vs regime-only 7.70: **False**.
- Direction check (prediction: above median): primaries observed n_talk below, geq_active below.
- Per-period figure: `figures/G25_residuals.png`. Data: `data/processed/H19-loop-gain-collapse/G25/residuals.parquet`.

## Scorecard (period-specific axes)
- **C** (adequacy vs. rivals, this period): collapse vs. regime-only log density -0.30 nats.
- **D** (unfitted): the period's estimates are predicted out of sample (LOPO), not fitted.
- E, G: not informed by a single period.

## Notes
- Inputs: `data/processed/H19-loop-gain-collapse/G25/inputs.json`.

<!-- R1B START -->
## Round 1b (improved data, 2026-10-04)
H19's own gains re-estimated on `activity_bins_fixed` (+ `outages_fixed`), H02/H03 inputs from their round-1b runs; H04's K_week and H05's gains (built on the buggy table, not yet re-run by their owners) are dropped. "DQ8 trim": all-present window, explained joint silences removed; "H38-conditioned": agent-state conditioning of day edges, infra errors and consolidations.

| Method | Round 1 | **Round 1b** | Round-1b LOPO prediction [90% PI] (raw E1 run) |
| --- | --- | --- | --- |
| E1 g_eq active (raw) | 0.045 | **0.066 ± 0.030** | 0.172 [0.008, 0.336] |
| E1 g_eq active, DQ8 trim | – | **-0.002 ± 0.007** | – |
| E1 g_eq active, H38-conditioned | – | **0.049 ± 0.032** | – |
| E2 g_eq talk | 0.134 | **0.192 ± 0.023** | 0.182 [0.014, 0.350] |
| T1 n̂ TALK | 0.379 | **0.357 ± 0.104** | 0.398 [0.015, 0.782] |
| T3 fast n_x | 0.107 | **0.108 ± 0.020** | 0.073 [0.002, 0.143] |

Per-period rule (unchanged): (i) both primaries inside their LOPO 90% intervals: raw run True, trim run True; (ii) log density ≥ regime-only rival: raw False (5.69 vs 6.11), trim False.
Source: `data/processed/H19-loop-gain-collapse/r1b/results*/explore.json`.
<!-- R1B END -->
