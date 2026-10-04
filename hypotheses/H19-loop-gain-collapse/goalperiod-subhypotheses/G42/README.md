# H19 × G42: Run your own Youtube channel! (2026-05-18 → 2026-05-22)

**Verdict:** mixed
**Verdict (1b):** mixed (round 1b, 2026-10-04, corrected data, pre-registered E1; with the day-edge-adjusted activity gain: mixed; round 1: mixed)
**Role:** replication (exploratory (round 1, non-holdout))
**Period:** regime III · mode I · 15.6 agents (N_room 9.7) · 2 room(s) carrying ≥ 5% of agent messages · 5 non-holdout days · 4.0 h/day (empirical).

## Why this period
One point on every method's curve. Loop-gain estimates available here: H03 n̂ ALL (T2), H03 n̂ TALK (T1, primary), H03 fast n_x (T3), H04 K, weekly (E3), H04 n, weekly (T4), H05 two-block g, active (E5), H05 two-block g, talk (E4), g_eq active (E1, primary), g_eq talk (E2). Controls: x_att = 1.75 (rank 33/35), messages per village turn 0.46, attention load k̄ = 4.0 agent messages waiting per turn, 3.9 agent messages per agent-hour, human share of chat 0.8%.

## Prediction
*Written 2026-10-04 00:09 UTC, before H19 related any control parameter to any loop gain (the card's P1 applied here).*
- Under the attention-dilution collapse (P1), every loop gain is affine-increasing in x_att. This period's x_att = 1.75 is **above** the cross-period median (0.96), so its estimates should sit **above** each method's cross-period median, and on the common curve.
- **Per-period verdict rule** (fixed now): fit the primary collapse model (per-method affine in x_att) without this period (LOPO). **supported** if (i) both primary estimates (T1 n̂ TALK, E1 g_eq active) fall inside their 90% LOPO predictive intervals and (ii) the period's summed LOPO log density under the collapse model is ≥ that under the regime-only rival N1; **mixed** if exactly one of (i), (ii) holds; **failed** if neither.
- Against it: estimates outside the intervals in the direction opposite to the x_att prediction, or N1 predicting the period better.

## Result
Primary collapse model (per-method affine in x_att), fitted without G42 (LOPO); shrunken = partial-pooling (BLUP) estimate under the collapse model fitted to all periods, shown beside the period's own estimate.

| Method | Own estimate ± SE | LOPO prediction [90% PI] | z | inside | Shrunken | Regime-only N1 prediction |
| --- | --- | --- | --- | --- | --- | --- |
| H03 n̂ ALL (T2) | 0.017 ± 0.020 | 0.355 [0.035, 0.675] | -1.74 | **no** | 0.021 | 0.289 |
| H03 n̂ TALK (T1, primary) | 0.204 ± 0.057 | 0.314 [-0.064, 0.692] | -0.48 | yes | 0.211 | 0.260 |
| H03 fast n_x (T3) | 0.053 ± 0.020 | 0.022 [-0.052, 0.097] | +0.67 | yes | 0.047 | 0.014 |
| H04 K, weekly (E3) | 0.119 ± 0.110 | 0.219 [-0.004, 0.441] | -0.73 | yes | 0.186 | 0.225 |
| H04 n, weekly (T4) | 0.234 ± 0.129 | 0.437 [0.079, 0.794] | -0.93 | yes | 0.305 | 0.370 |
| H05 two-block g, active (E5) | 0.057 ± 0.027 | 0.201 [0.046, 0.357] | -1.52 | yes | 0.066 | 0.171 |
| H05 two-block g, talk (E4) | 0.246 ± 0.112 | 0.129 [-0.067, 0.325] | +0.98 | yes | 0.142 | 0.092 |
| g_eq active (E1, primary) | 0.114 ± 0.019 | 0.215 [0.104, 0.327] | -1.50 | yes | 0.122 | 0.217 |
| g_eq talk (E2) | 0.081 ± 0.031 | 0.124 [-0.027, 0.275] | -0.47 | yes | 0.086 | 0.096 |

- (i) both primaries inside their 90% intervals: **True**; (ii) summed LOPO log density, collapse 5.59 vs regime-only 6.50: **False**.
- Direction check (prediction: above median): primaries observed n_talk below, geq_active above.
- Per-period figure: `figures/G42_residuals.png`. Data: `data/processed/H19-loop-gain-collapse/G42/residuals.parquet`.

## Scorecard (period-specific axes)
- **C** (adequacy vs. rivals, this period): collapse vs. regime-only log density -0.90 nats.
- **D** (unfitted): the period's estimates are predicted out of sample (LOPO), not fitted.
- E, G: not informed by a single period.

## Notes
- Inputs: `data/processed/H19-loop-gain-collapse/G42/inputs.json`.

<!-- R1B START -->
## Round 1b (improved data, 2026-10-04)
H19's own gains re-estimated on `activity_bins_fixed` (+ `outages_fixed`), H02/H03 inputs from their round-1b runs; H04's K_week and H05's gains (built on the buggy table, not yet re-run by their owners) are dropped. "DQ8 trim": all-present window, explained joint silences removed; "H38-conditioned": agent-state conditioning of day edges, infra errors and consolidations.

| Method | Round 1 | **Round 1b** | Round-1b LOPO prediction [90% PI] (raw E1 run) |
| --- | --- | --- | --- |
| E1 g_eq active (raw) | 0.114 | **0.291 ± 0.015** | 0.308 [0.137, 0.479] |
| E1 g_eq active, DQ8 trim | – | **0.045 ± 0.042** | – |
| E1 g_eq active, H38-conditioned | – | **0.068 ± 0.041** | – |
| E2 g_eq talk | 0.081 | **0.200 ± 0.053** | 0.172 [-0.021, 0.364] |
| T1 n̂ TALK | 0.204 | **0.203 ± 0.053** | 0.291 [-0.080, 0.662] |
| T3 fast n_x | 0.053 | **0.055 ± 0.020** | 0.021 [-0.053, 0.095] |

Per-period rule (unchanged): (i) both primaries inside their LOPO 90% intervals: raw run True, trim run True; (ii) log density ≥ regime-only rival: raw False (4.85 vs 5.34), trim False.
Source: `data/processed/H19-loop-gain-collapse/r1b/results*/explore.json`.
<!-- R1B END -->
