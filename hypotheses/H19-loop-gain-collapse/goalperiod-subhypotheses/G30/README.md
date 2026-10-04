# H19 × G30: Adopt a park and get it cleaned! (2026-02-09 → 2026-02-13)

**Verdict:** mixed
**Verdict (1b):** mixed (round 1b, 2026-10-04, corrected data, pre-registered E1; with the day-edge-adjusted activity gain: mixed; round 1: mixed)
**Role:** exploratory (round 1, non-holdout)
**Period:** regime I · mode C · 11.0 agents (N_room 11.1) · 1 room(s) carrying ≥ 5% of agent messages · 5 non-holdout days · 4.0 h/day (empirical).

## Why this period
One point on every method's curve. Loop-gain estimates available here: H03 n̂ ALL (T2), H03 n̂ TALK (T1, primary), H03 fast n_x (T3), H04 K, weekly (E3), H04 n, weekly (T4), g_eq active (E1, primary), g_eq talk (E2). Controls: x_att = 0.89 (rank 13/35), messages per village turn 0.93, attention load k̄ = 10.4 agent messages waiting per turn, 10.8 agent messages per agent-hour, human share of chat 0.6%.

## Prediction
*Written 2026-10-04 00:09 UTC, before H19 related any control parameter to any loop gain (the card's P1 applied here).*
- Under the attention-dilution collapse (P1), every loop gain is affine-increasing in x_att. This period's x_att = 0.89 is **below** the cross-period median (0.96), so its estimates should sit **below** each method's cross-period median, and on the common curve.
- **Per-period verdict rule** (fixed now): fit the primary collapse model (per-method affine in x_att) without this period (LOPO). **supported** if (i) both primary estimates (T1 n̂ TALK, E1 g_eq active) fall inside their 90% LOPO predictive intervals and (ii) the period's summed LOPO log density under the collapse model is ≥ that under the regime-only rival N1; **mixed** if exactly one of (i), (ii) holds; **failed** if neither.
- Against it: estimates outside the intervals in the direction opposite to the x_att prediction, or N1 predicting the period better.

## Result
Primary collapse model (per-method affine in x_att), fitted without G30 (LOPO); shrunken = partial-pooling (BLUP) estimate under the collapse model fitted to all periods, shown beside the period's own estimate.

| Method | Own estimate ± SE | LOPO prediction [90% PI] | z | inside | Shrunken | Regime-only N1 prediction |
| --- | --- | --- | --- | --- | --- | --- |
| H03 n̂ ALL (T2) | 0.433 ± 0.044 | 0.444 [0.119, 0.769] | -0.06 | yes | 0.433 | 0.479 |
| H03 n̂ TALK (T1, primary) | 0.278 ± 0.073 | 0.445 [0.078, 0.813] | -0.75 | yes | 0.296 | 0.479 |
| H03 fast n_x (T3) | 0.099 ± 0.023 | 0.076 [0.002, 0.150] | +0.51 | yes | 0.093 | 0.081 |
| H04 K, weekly (E3) | 0.106 ± 0.063 | 0.108 [-0.051, 0.267] | -0.02 | yes | 0.107 | 0.112 |
| H04 n, weekly (T4) | 0.310 ± 0.160 | 0.465 [0.082, 0.849] | -0.67 | yes | 0.385 | 0.494 |
| g_eq active (E1, primary) | 0.103 ± 0.054 | 0.091 [-0.047, 0.229] | +0.15 | yes | 0.098 | 0.088 |
| g_eq talk (E2) | 0.206 ± 0.045 | 0.153 [-0.002, 0.308] | +0.57 | yes | 0.194 | 0.166 |

- (i) both primaries inside their 90% intervals: **True**; (ii) summed LOPO log density, collapse 7.61 vs regime-only 7.65: **False**.
- Direction check (prediction: below median): primaries observed n_talk below, geq_active below.
- Per-period figure: `figures/G30_residuals.png`. Data: `data/processed/H19-loop-gain-collapse/G30/residuals.parquet`.

## Scorecard (period-specific axes)
- **C** (adequacy vs. rivals, this period): collapse vs. regime-only log density -0.04 nats.
- **D** (unfitted): the period's estimates are predicted out of sample (LOPO), not fitted.
- E, G: not informed by a single period.

## Notes
- Inputs: `data/processed/H19-loop-gain-collapse/G30/inputs.json`.

<!-- R1B START -->
## Round 1b (improved data, 2026-10-04)
H19's own gains re-estimated on `activity_bins_fixed` (+ `outages_fixed`), H02/H03 inputs from their round-1b runs; H04's K_week and H05's gains (built on the buggy table, not yet re-run by their owners) are dropped. "DQ8 trim": all-present window, explained joint silences removed; "H38-conditioned": agent-state conditioning of day edges, infra errors and consolidations.

| Method | Round 1 | **Round 1b** | Round-1b LOPO prediction [90% PI] (raw E1 run) |
| --- | --- | --- | --- |
| E1 g_eq active (raw) | 0.103 | **0.177 ± 0.075** | 0.149 [-0.053, 0.351] |
| E1 g_eq active, DQ8 trim | – | **0.077 ± 0.045** | – |
| E1 g_eq active, H38-conditioned | – | **0.101 ± 0.030** | – |
| E2 g_eq talk | 0.206 | **0.204 ± 0.033** | 0.182 [0.010, 0.355] |
| T1 n̂ TALK | 0.278 | **0.276 ± 0.058** | 0.418 [0.062, 0.774] |
| T3 fast n_x | 0.099 | **0.100 ± 0.020** | 0.079 [0.008, 0.151] |

Per-period rule (unchanged): (i) both primaries inside their LOPO 90% intervals: raw run True, trim run True; (ii) log density ≥ regime-only rival: raw False (6.00 vs 6.09), trim False.
Source: `data/processed/H19-loop-gain-collapse/r1b/results*/explore.json`.
<!-- R1B END -->
