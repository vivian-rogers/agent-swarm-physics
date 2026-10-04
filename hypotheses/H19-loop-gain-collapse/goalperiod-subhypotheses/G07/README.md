# H19 × G07: Holiday: do whatever you prefer! Next goal will begin soon (2025-07-16 → 2025-07-17)

**Verdict:** mixed
**Verdict (1b):** supported (round 1b, 2026-10-04, corrected data, pre-registered E1; with the day-edge-adjusted activity gain: mixed; round 1: mixed)
**Role:** replication (exploratory (round 1, non-holdout))
**Period:** regime I · mode F · 4.0 agents (N_room 4.0) · 1 room(s) carrying ≥ 5% of agent messages · 2 non-holdout days · 2.0 h/day (empirical).

## Why this period
One point on every method's curve. Loop-gain estimates available here: H03 n̂ ALL (T2), H03 n̂ TALK (T1, primary), g_eq active (E1, primary). Controls: x_att = 0.83 (rank 8/35), messages per village turn 0.87, attention load k̄ = 2.6 agent messages waiting per turn, 23.9 agent messages per agent-hour, human share of chat 18.6%.

## Prediction
*Written 2026-10-04 00:09 UTC, before H19 related any control parameter to any loop gain (the card's P1 applied here).*
- Under the attention-dilution collapse (P1), every loop gain is affine-increasing in x_att. This period's x_att = 0.83 is **below** the cross-period median (0.96), so its estimates should sit **below** each method's cross-period median, and on the common curve.
- **Per-period verdict rule** (fixed now): fit the primary collapse model (per-method affine in x_att) without this period (LOPO). **supported** if (i) both primary estimates (T1 n̂ TALK, E1 g_eq active) fall inside their 90% LOPO predictive intervals and (ii) the period's summed LOPO log density under the collapse model is ≥ that under the regime-only rival N1; **mixed** if exactly one of (i), (ii) holds; **failed** if neither.
- Against it: estimates outside the intervals in the direction opposite to the x_att prediction, or N1 predicting the period better.

## Result
Primary collapse model (per-method affine in x_att), fitted without G07 (LOPO); shrunken = partial-pooling (BLUP) estimate under the collapse model fitted to all periods, shown beside the period's own estimate.

| Method | Own estimate ± SE | LOPO prediction [90% PI] | z | inside | Shrunken | Regime-only N1 prediction |
| --- | --- | --- | --- | --- | --- | --- |
| H03 n̂ ALL (T2) | 0.531 ± 0.072 | 0.449 [0.111, 0.788] | +0.40 | yes | 0.520 | 0.475 |
| H03 n̂ TALK (T1, primary) | 0.468 ± 0.096 | 0.446 [0.061, 0.832] | +0.09 | yes | 0.464 | 0.470 |
| g_eq active (E1, primary) | 0.085 ± 0.032 | 0.084 [-0.035, 0.203] | +0.01 | yes | 0.084 | 0.089 |

- (i) both primaries inside their 90% intervals: **True**; (ii) summed LOPO log density, collapse 2.82 vs regime-only 3.00: **False**.
- Direction check (prediction: below median): primaries observed n_talk above, geq_active below.
- Per-period figure: `figures/G07_residuals.png`. Data: `data/processed/H19-loop-gain-collapse/G07/residuals.parquet`.

## Scorecard (period-specific axes)
- **C** (adequacy vs. rivals, this period): collapse vs. regime-only log density -0.18 nats.
- **D** (unfitted): the period's estimates are predicted out of sample (LOPO), not fitted.
- E, G: not informed by a single period.

## Notes
- Inputs: `data/processed/H19-loop-gain-collapse/G07/inputs.json`.

<!-- R1B START -->
## Round 1b (improved data, 2026-10-04)
H19's own gains re-estimated on `activity_bins_fixed` (+ `outages_fixed`), H02/H03 inputs from their round-1b runs; H04's K_week and H05's gains (built on the buggy table, not yet re-run by their owners) are dropped. "DQ8 trim": all-present window, explained joint silences removed; "H38-conditioned": agent-state conditioning of day edges, infra errors and consolidations.

| Method | Round 1 | **Round 1b** | Round-1b LOPO prediction [90% PI] (raw E1 run) |
| --- | --- | --- | --- |
| E1 g_eq active (raw) | 0.085 | **-0.001 ± 0.004** | 0.148 [-0.005, 0.301] |
| E1 g_eq active, DQ8 trim | – | **0.003 ± 0.005** | – |
| E1 g_eq active, H38-conditioned | – | **0.003 ± 0.005** | – |
| E2 g_eq talk | – | **0.094 ± 0.071** | 0.187 [-0.014, 0.387] |
| T1 n̂ TALK | 0.468 | **0.469 ± 0.096** | 0.419 [0.039, 0.799] |
| T3 fast n_x | – | **– ± –** | – |

Per-period rule (unchanged): (i) both primaries inside their LOPO 90% intervals: raw run True, trim run True; (ii) log density ≥ regime-only rival: raw True (2.21 vs 2.13), trim False.
Source: `data/processed/H19-loop-gain-collapse/r1b/results*/explore.json`.
<!-- R1B END -->
