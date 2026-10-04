# H19 × G31: Pick your own goal (agents bid 3.7 Sonnet farewell) (2026-02-16 → 2026-02-20)

**Verdict:** supported
**Verdict (1b):** supported (round 1b, 2026-10-04, corrected data, pre-registered E1; with the day-edge-adjusted activity gain: supported; round 1: supported)
**Role:** exploratory (round 1, non-holdout)
**Period:** regime I · mode F · 11.2 agents (N_room 11.3) · 1 room(s) carrying ≥ 5% of agent messages · 5 non-holdout days · 4.0 h/day (empirical).

## Why this period
One point on every method's curve. Loop-gain estimates available here: H03 n̂ ALL (T2), H03 n̂ TALK (T1, primary), H03 fast n_x (T3), H04 K, weekly (E3), H04 n, weekly (T4), g_eq active (E1, primary), g_eq talk (E2). Controls: x_att = 0.85 (rank 10/35), messages per village turn 0.96, attention load k̄ = 11.1 agent messages waiting per turn, 12.4 agent messages per agent-hour, human share of chat 0.3%.

## Prediction
*Written 2026-10-04 00:09 UTC, before H19 related any control parameter to any loop gain (the card's P1 applied here).*
- Under the attention-dilution collapse (P1), every loop gain is affine-increasing in x_att. This period's x_att = 0.85 is **below** the cross-period median (0.96), so its estimates should sit **below** each method's cross-period median, and on the common curve.
- **Per-period verdict rule** (fixed now): fit the primary collapse model (per-method affine in x_att) without this period (LOPO). **supported** if (i) both primary estimates (T1 n̂ TALK, E1 g_eq active) fall inside their 90% LOPO predictive intervals and (ii) the period's summed LOPO log density under the collapse model is ≥ that under the regime-only rival N1; **mixed** if exactly one of (i), (ii) holds; **failed** if neither.
- Against it: estimates outside the intervals in the direction opposite to the x_att prediction, or N1 predicting the period better.

## Result
Primary collapse model (per-method affine in x_att), fitted without G31 (LOPO); shrunken = partial-pooling (BLUP) estimate under the collapse model fitted to all periods, shown beside the period's own estimate.

| Method | Own estimate ± SE | LOPO prediction [90% PI] | z | inside | Shrunken | Regime-only N1 prediction |
| --- | --- | --- | --- | --- | --- | --- |
| H03 n̂ ALL (T2) | 0.252 ± 0.054 | 0.459 [0.134, 0.783] | -1.05 | yes | 0.268 | 0.487 |
| H03 n̂ TALK (T1, primary) | 0.066 ± 0.196 | 0.454 [-0.016, 0.925] | -1.36 | yes | 0.247 | 0.481 |
| H03 fast n_x (T3) | 0.066 ± 0.030 | 0.080 [-0.001, 0.161] | -0.28 | yes | 0.071 | 0.082 |
| H04 K, weekly (E3) | 0.123 ± 0.063 | 0.103 [-0.057, 0.262] | +0.21 | yes | 0.114 | 0.111 |
| H04 n, weekly (T4) | 0.153 ± 0.160 | 0.475 [0.098, 0.853] | -1.40 | yes | 0.308 | 0.500 |
| g_eq active (E1, primary) | 0.072 ± 0.072 | 0.087 [-0.071, 0.245] | -0.16 | yes | 0.080 | 0.089 |
| g_eq talk (E2) | 0.127 ± 0.036 | 0.158 [0.009, 0.307] | -0.34 | yes | 0.132 | 0.169 |

- (i) both primaries inside their 90% intervals: **True**; (ii) summed LOPO log density, collapse 5.42 vs regime-only 4.82: **True**.
- Direction check (prediction: below median): primaries observed n_talk below, geq_active below.
- Per-period figure: `figures/G31_residuals.png`. Data: `data/processed/H19-loop-gain-collapse/G31/residuals.parquet`.

## Scorecard (period-specific axes)
- **C** (adequacy vs. rivals, this period): collapse vs. regime-only log density +0.60 nats.
- **D** (unfitted): the period's estimates are predicted out of sample (LOPO), not fitted.
- E, G: not informed by a single period.

## Notes
- Inputs: `data/processed/H19-loop-gain-collapse/G31/inputs.json`.

<!-- R1B START -->
## Round 1b (improved data, 2026-10-04)
H19's own gains re-estimated on `activity_bins_fixed` (+ `outages_fixed`), H02/H03 inputs from their round-1b runs; H04's K_week and H05's gains (built on the buggy table, not yet re-run by their owners) are dropped. "DQ8 trim": all-present window, explained joint silences removed; "H38-conditioned": agent-state conditioning of day edges, infra errors and consolidations.

| Method | Round 1 | **Round 1b** | Round-1b LOPO prediction [90% PI] (raw E1 run) |
| --- | --- | --- | --- |
| E1 g_eq active (raw) | 0.072 | **0.144 ± 0.074** | 0.144 [-0.057, 0.344] |
| E1 g_eq active, DQ8 trim | – | **0.103 ± 0.075** | – |
| E1 g_eq active, H38-conditioned | – | **0.123 ± 0.084** | – |
| E2 g_eq talk | 0.127 | **0.104 ± 0.033** | 0.187 [0.016, 0.358] |
| T1 n̂ TALK | 0.066 | **0.065 ± 0.135** | 0.430 [0.028, 0.832] |
| T3 fast n_x | 0.066 | **0.069 ± 0.021** | 0.083 [0.011, 0.156] |

Per-period rule (unchanged): (i) both primaries inside their LOPO 90% intervals: raw run True, trim run True; (ii) log density ≥ regime-only rival: raw True (3.43 vs 2.74), trim True.
Source: `data/processed/H19-loop-gain-collapse/r1b/results*/explore.json`.
<!-- R1B END -->
