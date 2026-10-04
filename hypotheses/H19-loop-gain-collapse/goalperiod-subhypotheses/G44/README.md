# H19 × G44: Finetune your leader! (2026-05-26 → 2026-05-29)

**Verdict:** mixed
**Verdict (1b):** mixed (round 1b, 2026-10-04, corrected data, pre-registered E1; with the day-edge-adjusted activity gain: supported; round 1: mixed)
**Role:** replication (exploratory (round 1, non-holdout))
**Period:** regime III · mode C · 17.0 agents (N_room 10.5) · 2 room(s) carrying ≥ 5% of agent messages · 4 non-holdout days · 4.0 h/day (empirical).

## Why this period
One point on every method's curve. Loop-gain estimates available here: H03 n̂ ALL (T2), H03 n̂ TALK (T1, primary), H03 fast n_x (T3), H04 K, weekly (E3), H04 n, weekly (T4), H05 two-block g, active (E5), H05 two-block g, talk (E4), g_eq active (E1, primary), g_eq talk (E2). Controls: x_att = 1.59 (rank 31/35), messages per village turn 0.52, attention load k̄ = 4.9 agent messages waiting per turn, 6.3 agent messages per agent-hour, human share of chat 3.2%. Room-specific goals (#best fine-tunes a leader; #rest picks its own).

## Prediction
*Written 2026-10-04 00:09 UTC, before H19 related any control parameter to any loop gain (the card's P1 applied here).*
- Under the attention-dilution collapse (P1), every loop gain is affine-increasing in x_att. This period's x_att = 1.59 is **above** the cross-period median (0.96), so its estimates should sit **above** each method's cross-period median, and on the common curve.
- **Per-period verdict rule** (fixed now): fit the primary collapse model (per-method affine in x_att) without this period (LOPO). **supported** if (i) both primary estimates (T1 n̂ TALK, E1 g_eq active) fall inside their 90% LOPO predictive intervals and (ii) the period's summed LOPO log density under the collapse model is ≥ that under the regime-only rival N1; **mixed** if exactly one of (i), (ii) holds; **failed** if neither.
- Against it: estimates outside the intervals in the direction opposite to the x_att prediction, or N1 predicting the period better.

## Result
Primary collapse model (per-method affine in x_att), fitted without G44 (LOPO); shrunken = partial-pooling (BLUP) estimate under the collapse model fitted to all periods, shown beside the period's own estimate.

| Method | Own estimate ± SE | LOPO prediction [90% PI] | z | inside | Shrunken | Regime-only N1 prediction |
| --- | --- | --- | --- | --- | --- | --- |
| H03 n̂ ALL (T2) | 0.506 ± 0.105 | 0.313 [-0.054, 0.679] | +0.87 | yes | 0.462 | 0.216 |
| H03 n̂ TALK (T1, primary) | 0.249 ± 0.077 | 0.332 [-0.048, 0.711] | -0.36 | yes | 0.258 | 0.255 |
| H03 fast n_x (T3) | 0.009 ± 0.020 | 0.038 [-0.036, 0.111] | -0.65 | yes | 0.015 | 0.019 |
| H04 K, weekly (E3) | 0.352 ± 0.110 | 0.183 [-0.035, 0.402] | +1.27 | yes | 0.236 | 0.201 |
| H04 n, weekly (T4) | 0.357 ± 0.129 | 0.426 [0.069, 0.783] | -0.32 | yes | 0.382 | 0.354 |
| H05 two-block g, active (E5) | 0.397 ± 0.130 | 0.131 [-0.132, 0.394] | +1.66 | **no** | 0.230 | 0.131 |
| H05 two-block g, talk (E4) | 0.062 ± 0.077 | 0.132 [-0.005, 0.269] | -0.85 | yes | 0.122 | 0.117 |
| g_eq active (E1, primary) | 0.362 ± 0.136 | 0.177 [-0.070, 0.424] | +1.23 | yes | 0.210 | 0.196 |
| g_eq talk (E2) | 0.147 ± 0.049 | 0.123 [-0.037, 0.284] | +0.24 | yes | 0.141 | 0.089 |

- (i) both primaries inside their 90% intervals: **True**; (ii) summed LOPO log density, collapse 5.86 vs regime-only 5.95: **False**.
- Direction check (prediction: above median): primaries observed n_talk below, geq_active above.
- Per-period figure: `figures/G44_residuals.png`. Data: `data/processed/H19-loop-gain-collapse/G44/residuals.parquet`.

## Scorecard (period-specific axes)
- **C** (adequacy vs. rivals, this period): collapse vs. regime-only log density -0.09 nats.
- **D** (unfitted): the period's estimates are predicted out of sample (LOPO), not fitted.
- E, G: not informed by a single period.

## Notes
- Inputs: `data/processed/H19-loop-gain-collapse/G44/inputs.json`.

<!-- R1B START -->
## Round 1b (improved data, 2026-10-04)
H19's own gains re-estimated on `activity_bins_fixed` (+ `outages_fixed`), H02/H03 inputs from their round-1b runs; H04's K_week and H05's gains (built on the buggy table, not yet re-run by their owners) are dropped. "DQ8 trim": all-present window, explained joint silences removed; "H38-conditioned": agent-state conditioning of day edges, infra errors and consolidations.

| Method | Round 1 | **Round 1b** | Round-1b LOPO prediction [90% PI] (raw E1 run) |
| --- | --- | --- | --- |
| E1 g_eq active (raw) | 0.362 | **0.447 ± 0.061** | 0.266 [0.080, 0.451] |
| E1 g_eq active, DQ8 trim | – | **0.330 ± 0.222** | – |
| E1 g_eq active, H38-conditioned | – | **0.471 ± 0.166** | – |
| E2 g_eq talk | 0.147 | **0.084 ± 0.050** | 0.184 [-0.001, 0.369] |
| T1 n̂ TALK | 0.249 | **0.246 ± 0.078** | 0.309 [-0.067, 0.684] |
| T3 fast n_x | 0.009 | **0.006 ± 0.020** | 0.037 [-0.035, 0.110] |

Per-period rule (unchanged): (i) both primaries inside their LOPO 90% intervals: raw run True, trim run True; (ii) log density ≥ regime-only rival: raw False (3.88 vs 4.21), trim True.
Source: `data/processed/H19-loop-gain-collapse/r1b/results*/explore.json`.
<!-- R1B END -->
