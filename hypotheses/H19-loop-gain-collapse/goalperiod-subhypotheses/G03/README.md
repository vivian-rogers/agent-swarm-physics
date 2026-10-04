# H19 × G03: Holiday: do whatever you'd like! Next goal will begin soon (2025-05-12 → 2025-05-14)

**Verdict:** mixed
**Verdict (1b):** mixed (round 1b, 2026-10-04, corrected data, pre-registered E1; with the day-edge-adjusted activity gain: mixed; round 1: mixed)
**Role:** exploratory (round 1, non-holdout)
**Period:** regime I · mode F · 4.0 agents (N_room 4.0) · 1 room(s) carrying ≥ 5% of agent messages · 3 non-holdout days · 2.0 h/day (empirical).

## Why this period
One point on every method's curve. Loop-gain estimates available here: H03 n̂ ALL (T2), H03 n̂ TALK (T1, primary), H03 fast n_x (T3), g_eq active (E1, primary), g_eq talk (E2). Controls: x_att = 0.85 (rank 11/35), messages per village turn 0.84, attention load k̄ = 2.5 agent messages waiting per turn, 68.6 agent messages per agent-hour, human share of chat 4.5%.

## Prediction
*Written 2026-10-04 00:09 UTC, before H19 related any control parameter to any loop gain (the card's P1 applied here).*
- Under the attention-dilution collapse (P1), every loop gain is affine-increasing in x_att. This period's x_att = 0.85 is **below** the cross-period median (0.96), so its estimates should sit **below** each method's cross-period median, and on the common curve.
- **Per-period verdict rule** (fixed now): fit the primary collapse model (per-method affine in x_att) without this period (LOPO). **supported** if (i) both primary estimates (T1 n̂ TALK, E1 g_eq active) fall inside their 90% LOPO predictive intervals and (ii) the period's summed LOPO log density under the collapse model is ≥ that under the regime-only rival N1; **mixed** if exactly one of (i), (ii) holds; **failed** if neither.
- Against it: estimates outside the intervals in the direction opposite to the x_att prediction, or N1 predicting the period better.

## Result
Primary collapse model (per-method affine in x_att), fitted without G03 (LOPO); shrunken = partial-pooling (BLUP) estimate under the collapse model fitted to all periods, shown beside the period's own estimate.

| Method | Own estimate ± SE | LOPO prediction [90% PI] | z | inside | Shrunken | Regime-only N1 prediction |
| --- | --- | --- | --- | --- | --- | --- |
| H03 n̂ ALL (T2) | 0.697 ± 0.070 | 0.439 [0.110, 0.768] | +1.29 | yes | 0.666 | 0.467 |
| H03 n̂ TALK (T1, primary) | 0.663 ± 0.082 | 0.434 [0.063, 0.804] | +1.02 | yes | 0.632 | 0.461 |
| H03 fast n_x (T3) | 0.070 ± 0.058 | 0.079 [-0.035, 0.194] | -0.13 | yes | 0.077 | 0.082 |
| g_eq active (E1, primary) | 0.021 ± 0.058 | 0.089 [-0.052, 0.230] | -0.79 | yes | 0.052 | 0.091 |
| g_eq talk (E2) | 0.099 ± 0.072 | 0.158 [-0.022, 0.339] | -0.54 | yes | 0.125 | 0.170 |

- (i) both primaries inside their 90% intervals: **True**; (ii) summed LOPO log density, collapse 4.02 vs regime-only 4.24: **False**.
- Direction check (prediction: below median): primaries observed n_talk above, geq_active below.
- Per-period figure: `figures/G03_residuals.png`. Data: `data/processed/H19-loop-gain-collapse/G03/residuals.parquet`.

## Scorecard (period-specific axes)
- **C** (adequacy vs. rivals, this period): collapse vs. regime-only log density -0.22 nats.
- **D** (unfitted): the period's estimates are predicted out of sample (LOPO), not fitted.
- E, G: not informed by a single period.

## Notes
- Inputs: `data/processed/H19-loop-gain-collapse/G03/inputs.json`.

<!-- R1B START -->
## Round 1b (improved data, 2026-10-04)
H19's own gains re-estimated on `activity_bins_fixed` (+ `outages_fixed`), H02/H03 inputs from their round-1b runs; H04's K_week and H05's gains (built on the buggy table, not yet re-run by their owners) are dropped. "DQ8 trim": all-present window, explained joint silences removed; "H38-conditioned": agent-state conditioning of day edges, infra errors and consolidations.

| Method | Round 1 | **Round 1b** | Round-1b LOPO prediction [90% PI] (raw E1 run) |
| --- | --- | --- | --- |
| E1 g_eq active (raw) | 0.021 | **0.231 ± 0.042** | 0.139 [-0.033, 0.312] |
| E1 g_eq active, DQ8 trim | – | **0.100 ± 0.008** | – |
| E1 g_eq active, H38-conditioned | – | **0.249 ± 0.046** | – |
| E2 g_eq talk | 0.099 | **0.333 ± 0.018** | 0.176 [0.017, 0.336] |
| T1 n̂ TALK | 0.663 | **0.663 ± 0.082** | 0.407 [0.043, 0.771] |
| T3 fast n_x | 0.070 | **0.073 ± 0.083** | 0.083 [-0.067, 0.233] |

Per-period rule (unchanged): (i) both primaries inside their LOPO 90% intervals: raw run True, trim run True; (ii) log density ≥ regime-only rival: raw False (2.29 vs 2.72), trim False.
Source: `data/processed/H19-loop-gain-collapse/r1b/results*/explore.json`.
<!-- R1B END -->
