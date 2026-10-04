# H19 × G39: Build your own interactive world! (2026-04-27 → 2026-05-01)

**Verdict:** mixed
**Verdict (1b):** mixed (round 1b, 2026-10-04, corrected data, pre-registered E1; with the day-edge-adjusted activity gain: mixed; round 1: mixed)
**Role:** replication (exploratory (round 1, non-holdout))
**Period:** regime III · mode I · 15.0 agents (N_room 10.0) · 2 room(s) carrying ≥ 5% of agent messages · 5 non-holdout days · 4.0 h/day (empirical).

## Why this period
One point on every method's curve. Loop-gain estimates available here: H03 n̂ ALL (T2), H03 n̂ TALK (T1, primary), H03 fast n_x (T3), H04 K, weekly (E3), H04 n, weekly (T4), H05 two-block g, active (E5), H05 two-block g, talk (E4), g_eq active (E1, primary), g_eq talk (E2). Controls: x_att = 1.82 (rank 34/35), messages per village turn 0.44, attention load k̄ = 3.9 agent messages waiting per turn, 2.9 agent messages per agent-hour, human share of chat 1.5%.

## Prediction
*Written 2026-10-04 00:09 UTC, before H19 related any control parameter to any loop gain (the card's P1 applied here).*
- Under the attention-dilution collapse (P1), every loop gain is affine-increasing in x_att. This period's x_att = 1.82 is **above** the cross-period median (0.96), so its estimates should sit **above** each method's cross-period median, and on the common curve.
- **Per-period verdict rule** (fixed now): fit the primary collapse model (per-method affine in x_att) without this period (LOPO). **supported** if (i) both primary estimates (T1 n̂ TALK, E1 g_eq active) fall inside their 90% LOPO predictive intervals and (ii) the period's summed LOPO log density under the collapse model is ≥ that under the regime-only rival N1; **mixed** if exactly one of (i), (ii) holds; **failed** if neither.
- Against it: estimates outside the intervals in the direction opposite to the x_att prediction, or N1 predicting the period better.

## Result
Primary collapse model (per-method affine in x_att), fitted without G39 (LOPO); shrunken = partial-pooling (BLUP) estimate under the collapse model fitted to all periods, shown beside the period's own estimate.

| Method | Own estimate ± SE | LOPO prediction [90% PI] | z | inside | Shrunken | Regime-only N1 prediction |
| --- | --- | --- | --- | --- | --- | --- |
| H03 n̂ ALL (T2) | 0.000 ± 0.160 | 0.325 [-0.099, 0.748] | -1.26 | yes | 0.124 | 0.269 |
| H03 n̂ TALK (T1, primary) | 0.100 ± 0.050 | 0.321 [-0.054, 0.696] | -0.97 | yes | 0.110 | 0.274 |
| H03 fast n_x (T3) | 0.009 ± 0.021 | 0.024 [-0.053, 0.101] | -0.32 | yes | 0.012 | 0.019 |
| H04 K, weekly (E3) | 0.185 ± 0.110 | 0.223 [-0.002, 0.448] | -0.28 | yes | 0.210 | 0.218 |
| H04 n, weekly (T4) | 0.143 ± 0.129 | 0.453 [0.101, 0.805] | -1.45 | yes | 0.248 | 0.383 |
| H05 two-block g, active (E5) | 0.050 ± 0.076 | 0.199 [-0.025, 0.424] | -1.10 | yes | 0.097 | 0.164 |
| H05 two-block g, talk (E4) | 0.128 ± 0.084 | 0.158 [-0.001, 0.318] | -0.31 | yes | 0.151 | 0.106 |
| g_eq active (E1, primary) | 0.192 ± 0.044 | 0.213 [0.078, 0.348] | -0.25 | yes | 0.198 | 0.203 |
| g_eq talk (E2) | 0.122 ± 0.036 | 0.115 [-0.043, 0.272] | +0.08 | yes | 0.121 | 0.091 |

- (i) both primaries inside their 90% intervals: **True**; (ii) summed LOPO log density, collapse 7.24 vs regime-only 8.46: **False**.
- Direction check (prediction: above median): primaries observed n_talk below, geq_active above.
- Per-period figure: `figures/G39_residuals.png`. Data: `data/processed/H19-loop-gain-collapse/G39/residuals.parquet`.

## Scorecard (period-specific axes)
- **C** (adequacy vs. rivals, this period): collapse vs. regime-only log density -1.22 nats.
- **D** (unfitted): the period's estimates are predicted out of sample (LOPO), not fitted.
- E, G: not informed by a single period.

## Notes
- Inputs: `data/processed/H19-loop-gain-collapse/G39/inputs.json`.

<!-- R1B START -->
## Round 1b (improved data, 2026-10-04)
H19's own gains re-estimated on `activity_bins_fixed` (+ `outages_fixed`), H02/H03 inputs from their round-1b runs; H04's K_week and H05's gains (built on the buggy table, not yet re-run by their owners) are dropped. "DQ8 trim": all-present window, explained joint silences removed; "H38-conditioned": agent-state conditioning of day edges, infra errors and consolidations.

| Method | Round 1 | **Round 1b** | Round-1b LOPO prediction [90% PI] (raw E1 run) |
| --- | --- | --- | --- |
| E1 g_eq active (raw) | 0.192 | **0.241 ± 0.033** | 0.332 [0.154, 0.510] |
| E1 g_eq active, DQ8 trim | – | **-0.054 ± 0.013** | – |
| E1 g_eq active, H38-conditioned | – | **0.070 ± 0.036** | – |
| E2 g_eq talk | 0.122 | **0.127 ± 0.045** | 0.181 [-0.008, 0.370] |
| T1 n̂ TALK | 0.100 | **0.099 ± 0.048** | 0.297 [-0.072, 0.666] |
| T3 fast n_x | 0.009 | **0.008 ± 0.020** | 0.022 [-0.054, 0.098] |

Per-period rule (unchanged): (i) both primaries inside their LOPO 90% intervals: raw run True, trim run True; (ii) log density ≥ regime-only rival: raw False (3.69 vs 4.79), trim False.
Source: `data/processed/H19-loop-gain-collapse/r1b/results*/explore.json`.
<!-- R1B END -->
