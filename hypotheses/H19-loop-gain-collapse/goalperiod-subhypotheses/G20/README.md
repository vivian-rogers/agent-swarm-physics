# H19 × G20: Start a Substack and join the blogosphere (2025-11-17 → 2025-11-28)

**Verdict:** mixed
**Verdict (1b):** mixed (round 1b, 2026-10-04, corrected data, pre-registered E1; with the day-edge-adjusted activity gain: mixed; round 1: mixed)
**Role:** replication (exploratory (round 1, non-holdout))
**Period:** regime I · mode I · 9.2 agents (N_room 9.4) · 1 room(s) carrying ≥ 5% of agent messages · 10 non-holdout days · 4.0 h/day (empirical).

## Why this period
One point on every method's curve. Loop-gain estimates available here: H03 n̂ ALL (T2), H03 n̂ TALK (T1, primary), H03 fast n_x (T3), H04 K, weekly (E3), H04 n, weekly (T4), g_eq active (E1, primary), g_eq talk (E2). Controls: x_att = 1.00 (rank 23/35), messages per village turn 0.88, attention load k̄ = 7.4 agent messages waiting per turn, 12.3 agent messages per agent-hour, human share of chat 0.3%.

## Prediction
*Written 2026-10-04 00:09 UTC, before H19 related any control parameter to any loop gain (the card's P1 applied here).*
- Under the attention-dilution collapse (P1), every loop gain is affine-increasing in x_att. This period's x_att = 1.00 is **above** the cross-period median (0.96), so its estimates should sit **above** each method's cross-period median, and on the common curve.
- **Per-period verdict rule** (fixed now): fit the primary collapse model (per-method affine in x_att) without this period (LOPO). **supported** if (i) both primary estimates (T1 n̂ TALK, E1 g_eq active) fall inside their 90% LOPO predictive intervals and (ii) the period's summed LOPO log density under the collapse model is ≥ that under the regime-only rival N1; **mixed** if exactly one of (i), (ii) holds; **failed** if neither.
- Against it: estimates outside the intervals in the direction opposite to the x_att prediction, or N1 predicting the period better.

## Result
Primary collapse model (per-method affine in x_att), fitted without G20 (LOPO); shrunken = partial-pooling (BLUP) estimate under the collapse model fitted to all periods, shown beside the period's own estimate.

| Method | Own estimate ± SE | LOPO prediction [90% PI] | z | inside | Shrunken | Regime-only N1 prediction |
| --- | --- | --- | --- | --- | --- | --- |
| H03 n̂ ALL (T2) | 0.417 ± 0.064 | 0.425 [0.093, 0.758] | -0.04 | yes | 0.418 | 0.479 |
| H03 n̂ TALK (T1, primary) | 0.616 ± 0.085 | 0.413 [0.042, 0.784] | +0.90 | yes | 0.587 | 0.463 |
| H03 fast n_x (T3) | 0.112 ± 0.030 | 0.069 [-0.011, 0.149] | +0.88 | yes | 0.095 | 0.080 |
| H04 K, weekly (E3) | 0.032 ± 0.045 | 0.126 [-0.011, 0.262] | -1.13 | yes | 0.059 | 0.116 |
| H04 n, weekly (T4) | 0.458 ± 0.113 | 0.452 [0.115, 0.789] | +0.03 | yes | 0.456 | 0.488 |
| g_eq active (E1, primary) | 0.041 ± 0.023 | 0.108 [-0.001, 0.218] | -1.02 | yes | 0.049 | 0.091 |
| g_eq talk (E2) | 0.169 ± 0.028 | 0.149 [0.006, 0.293] | +0.23 | yes | 0.167 | 0.167 |

- (i) both primaries inside their 90% intervals: **True**; (ii) summed LOPO log density, collapse 6.93 vs regime-only 7.79: **False**.
- Direction check (prediction: above median): primaries observed n_talk above, geq_active below.
- Per-period figure: `figures/G20_residuals.png`. Data: `data/processed/H19-loop-gain-collapse/G20/residuals.parquet`.

## Scorecard (period-specific axes)
- **C** (adequacy vs. rivals, this period): collapse vs. regime-only log density -0.86 nats.
- **D** (unfitted): the period's estimates are predicted out of sample (LOPO), not fitted.
- E, G: not informed by a single period.

## Notes
- Inputs: `data/processed/H19-loop-gain-collapse/G20/inputs.json`.

<!-- R1B START -->
## Round 1b (improved data, 2026-10-04)
H19's own gains re-estimated on `activity_bins_fixed` (+ `outages_fixed`), H02/H03 inputs from their round-1b runs; H04's K_week and H05's gains (built on the buggy table, not yet re-run by their owners) are dropped. "DQ8 trim": all-present window, explained joint silences removed; "H38-conditioned": agent-state conditioning of day edges, infra errors and consolidations.

| Method | Round 1 | **Round 1b** | Round-1b LOPO prediction [90% PI] (raw E1 run) |
| --- | --- | --- | --- |
| E1 g_eq active (raw) | 0.041 | **0.060 ± 0.018** | 0.175 [0.016, 0.333] |
| E1 g_eq active, DQ8 trim | – | **-0.007 ± 0.020** | – |
| E1 g_eq active, H38-conditioned | – | **0.007 ± 0.017** | – |
| E2 g_eq talk | 0.169 | **0.151 ± 0.015** | 0.183 [0.018, 0.348] |
| T1 n̂ TALK | 0.616 | **0.558 ± 0.105** | 0.390 [0.009, 0.771] |
| T3 fast n_x | 0.112 | **0.109 ± 0.020** | 0.072 [0.001, 0.142] |

Per-period rule (unchanged): (i) both primaries inside their LOPO 90% intervals: raw run True, trim run True; (ii) log density ≥ regime-only rival: raw False (5.56 vs 6.29), trim False.
Source: `data/processed/H19-loop-gain-collapse/r1b/results*/explore.json`.
<!-- R1B END -->
