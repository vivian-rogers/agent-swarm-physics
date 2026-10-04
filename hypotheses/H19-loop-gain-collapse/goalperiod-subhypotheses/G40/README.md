# H19 × G40: Connect your worlds into a 3D universe! (2026-05-04 → 2026-05-08)

**Verdict:** failed
**Verdict (1b):** failed (round 1b, 2026-10-04, corrected data, pre-registered E1; with the day-edge-adjusted activity gain: mixed; round 1: failed)
**Role:** replication (exploratory (round 1, non-holdout))
**Period:** regime III · mode C · 15.0 agents (N_room 13.9) · 1 room(s) carrying ≥ 5% of agent messages · 5 non-holdout days · 4.1 h/day (empirical).

## Why this period
One point on every method's curve. Loop-gain estimates available here: H03 n̂ ALL (T2), H03 n̂ TALK (T1, primary), H03 fast n_x (T3), H04 K, weekly (E3), H04 n, weekly (T4), g_eq active (E1, primary), g_eq talk (E2). Controls: x_att = 1.56 (rank 30/35), messages per village turn 0.56, attention load k̄ = 7.3 agent messages waiting per turn, 5.7 agent messages per agent-hour, human share of chat 0.2%. #best and #rest merged into one room for the week (05-04).

## Prediction
*Written 2026-10-04 00:09 UTC, before H19 related any control parameter to any loop gain (the card's P1 applied here).*
- Under the attention-dilution collapse (P1), every loop gain is affine-increasing in x_att. This period's x_att = 1.56 is **above** the cross-period median (0.96), so its estimates should sit **above** each method's cross-period median, and on the common curve.
- **Per-period verdict rule** (fixed now): fit the primary collapse model (per-method affine in x_att) without this period (LOPO). **supported** if (i) both primary estimates (T1 n̂ TALK, E1 g_eq active) fall inside their 90% LOPO predictive intervals and (ii) the period's summed LOPO log density under the collapse model is ≥ that under the regime-only rival N1; **mixed** if exactly one of (i), (ii) holds; **failed** if neither.
- Against it: estimates outside the intervals in the direction opposite to the x_att prediction, or N1 predicting the period better.

## Result
Primary collapse model (per-method affine in x_att), fitted without G40 (LOPO); shrunken = partial-pooling (BLUP) estimate under the collapse model fitted to all periods, shown beside the period's own estimate.

| Method | Own estimate ± SE | LOPO prediction [90% PI] | z | inside | Shrunken | Regime-only N1 prediction |
| --- | --- | --- | --- | --- | --- | --- |
| H03 n̂ ALL (T2) | 0.000 ± 0.025 | 0.369 [0.063, 0.675] | -1.98 | **no** | 0.006 | 0.291 |
| H03 n̂ TALK (T1, primary) | 0.000 ± 0.020 | 0.360 [0.021, 0.699] | -1.75 | **no** | 0.003 | 0.289 |
| H03 fast n_x (T3) | 0.000 ± 0.020 | 0.040 [-0.032, 0.113] | -0.92 | yes | 0.008 | 0.021 |
| H04 K, weekly (E3) | 0.330 ± 0.110 | 0.181 [-0.037, 0.399] | +1.12 | yes | 0.227 | 0.203 |
| H04 n, weekly (T4) | 0.150 ± 0.129 | 0.445 [0.104, 0.787] | -1.42 | yes | 0.258 | 0.382 |
| g_eq active (E1, primary) | 0.350 ± 0.037 | 0.157 [0.055, 0.258] | +3.12 | **no** | 0.302 | 0.177 |
| g_eq talk (E2) | 0.016 ± 0.068 | 0.132 [-0.044, 0.309] | -1.08 | yes | 0.063 | 0.101 |

- (i) both primaries inside their 90% intervals: **False**; (ii) summed LOPO log density, collapse -2.45 vs regime-only 1.48: **False**.
- Direction check (prediction: above median): primaries observed n_talk below, geq_active above.
- Per-period figure: `figures/G40_residuals.png`. Data: `data/processed/H19-loop-gain-collapse/G40/residuals.parquet`.

## Scorecard (period-specific axes)
- **C** (adequacy vs. rivals, this period): collapse vs. regime-only log density -3.93 nats.
- **D** (unfitted): the period's estimates are predicted out of sample (LOPO), not fitted.
- E, G: not informed by a single period.

## Notes
- Inputs: `data/processed/H19-loop-gain-collapse/G40/inputs.json`.

<!-- R1B START -->
## Round 1b (improved data, 2026-10-04)
H19's own gains re-estimated on `activity_bins_fixed` (+ `outages_fixed`), H02/H03 inputs from their round-1b runs; H04's K_week and H05's gains (built on the buggy table, not yet re-run by their owners) are dropped. "DQ8 trim": all-present window, explained joint silences removed; "H38-conditioned": agent-state conditioning of day edges, infra errors and consolidations.

| Method | Round 1 | **Round 1b** | Round-1b LOPO prediction [90% PI] (raw E1 run) |
| --- | --- | --- | --- |
| E1 g_eq active (raw) | 0.350 | **0.429 ± 0.028** | 0.257 [0.098, 0.417] |
| E1 g_eq active, DQ8 trim | – | **0.074 ± 0.043** | – |
| E1 g_eq active, H38-conditioned | – | **0.020 ± 0.027** | – |
| E2 g_eq talk | 0.016 | **0.020 ± 0.062** | 0.187 [-0.005, 0.378] |
| T1 n̂ TALK | 0.000 | **0.000 ± 0.020** | 0.335 [-0.001, 0.672] |
| T3 fast n_x | 0.000 | **0.000 ± 0.020** | 0.040 [-0.032, 0.112] |

Per-period rule (unchanged): (i) both primaries inside their LOPO 90% intervals: raw run False, trim run True; (ii) log density ≥ regime-only rival: raw False (0.08 vs 2.86), trim False.
Source: `data/processed/H19-loop-gain-collapse/r1b/results*/explore.json`.
<!-- R1B END -->
