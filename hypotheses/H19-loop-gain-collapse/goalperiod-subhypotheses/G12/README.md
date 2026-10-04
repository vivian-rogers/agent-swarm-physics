# H19 × G12: Form two teams and debate each other, while one agent judges. Choose your teammates wisely! (2025-09-01 → 2025-09-05)

**Verdict:** mixed
**Verdict (1b):** mixed (round 1b, 2026-10-04, corrected data, pre-registered E1; with the day-edge-adjusted activity gain: mixed; round 1: mixed)
**Role:** replication (exploratory (round 1, non-holdout))
**Period:** regime I · mode M · 7.0 agents (N_room 7.0) · 1 room(s) carrying ≥ 5% of agent messages · 5 non-holdout days · 3.0 h/day (empirical).

## Why this period
One point on every method's curve. Loop-gain estimates available here: H03 n̂ ALL (T2), H03 n̂ TALK (T1, primary), H03 fast n_x (T3), H04 K, weekly (E3), H04 n, weekly (T4), g_eq active (E1, primary), g_eq talk (E2). Controls: x_att = 0.97 (rank 19/35), messages per village turn 0.86, attention load k̄ = 5.2 agent messages waiting per turn, 34.5 agent messages per agent-hour, human share of chat 0.4%.

## Prediction
*Written 2026-10-04 00:09 UTC, before H19 related any control parameter to any loop gain (the card's P1 applied here).*
- Under the attention-dilution collapse (P1), every loop gain is affine-increasing in x_att. This period's x_att = 0.97 is **above** the cross-period median (0.96), so its estimates should sit **above** each method's cross-period median, and on the common curve.
- **Per-period verdict rule** (fixed now): fit the primary collapse model (per-method affine in x_att) without this period (LOPO). **supported** if (i) both primary estimates (T1 n̂ TALK, E1 g_eq active) fall inside their 90% LOPO predictive intervals and (ii) the period's summed LOPO log density under the collapse model is ≥ that under the regime-only rival N1; **mixed** if exactly one of (i), (ii) holds; **failed** if neither.
- Against it: estimates outside the intervals in the direction opposite to the x_att prediction, or N1 predicting the period better.

## Result
Primary collapse model (per-method affine in x_att), fitted without G12 (LOPO); shrunken = partial-pooling (BLUP) estimate under the collapse model fitted to all periods, shown beside the period's own estimate.

| Method | Own estimate ± SE | LOPO prediction [90% PI] | z | inside | Shrunken | Regime-only N1 prediction |
| --- | --- | --- | --- | --- | --- | --- |
| H03 n̂ ALL (T2) | 0.648 ± 0.065 | 0.423 [0.096, 0.749] | +1.13 | yes | 0.624 | 0.469 |
| H03 n̂ TALK (T1, primary) | 0.632 ± 0.072 | 0.417 [0.054, 0.780] | +0.97 | yes | 0.609 | 0.462 |
| H03 fast n_x (T3) | 0.102 ± 0.020 | 0.071 [-0.000, 0.142] | +0.72 | yes | 0.095 | 0.081 |
| H04 K, weekly (E3) | 0.196 ± 0.063 | 0.114 [-0.042, 0.271] | +0.86 | yes | 0.159 | 0.107 |
| H04 n, weekly (T4) | 0.666 ± 0.160 | 0.446 [0.067, 0.825] | +0.96 | yes | 0.560 | 0.478 |
| g_eq active (E1, primary) | 0.171 ± 0.035 | 0.098 [-0.018, 0.215] | +1.03 | yes | 0.153 | 0.083 |
| g_eq talk (E2) | 0.178 ± 0.028 | 0.150 [0.007, 0.294] | +0.32 | yes | 0.175 | 0.167 |

- (i) both primaries inside their 90% intervals: **True**; (ii) summed LOPO log density, collapse 5.96 vs regime-only 6.49: **False**.
- Direction check (prediction: above median): primaries observed n_talk above, geq_active above.
- Per-period figure: `figures/G12_residuals.png`. Data: `data/processed/H19-loop-gain-collapse/G12/residuals.parquet`.

## Scorecard (period-specific axes)
- **C** (adequacy vs. rivals, this period): collapse vs. regime-only log density -0.53 nats.
- **D** (unfitted): the period's estimates are predicted out of sample (LOPO), not fitted.
- E, G: not informed by a single period.

## Notes
- Inputs: `data/processed/H19-loop-gain-collapse/G12/inputs.json`.

<!-- R1B START -->
## Round 1b (improved data, 2026-10-04)
H19's own gains re-estimated on `activity_bins_fixed` (+ `outages_fixed`), H02/H03 inputs from their round-1b runs; H04's K_week and H05's gains (built on the buggy table, not yet re-run by their owners) are dropped. "DQ8 trim": all-present window, explained joint silences removed; "H38-conditioned": agent-state conditioning of day edges, infra errors and consolidations.

| Method | Round 1 | **Round 1b** | Round-1b LOPO prediction [90% PI] (raw E1 run) |
| --- | --- | --- | --- |
| E1 g_eq active (raw) | 0.171 | **0.202 ± 0.054** | 0.164 [-0.019, 0.347] |
| E1 g_eq active, DQ8 trim | – | **0.151 ± 0.048** | – |
| E1 g_eq active, H38-conditioned | – | **0.203 ± 0.056** | – |
| E2 g_eq talk | 0.178 | **0.213 ± 0.028** | 0.181 [0.012, 0.351] |
| T1 n̂ TALK | 0.632 | **0.625 ± 0.068** | 0.392 [0.037, 0.747] |
| T3 fast n_x | 0.102 | **0.099 ± 0.020** | 0.074 [0.003, 0.145] |

Per-period rule (unchanged): (i) both primaries inside their LOPO 90% intervals: raw run True, trim run True; (ii) log density ≥ regime-only rival: raw False (4.76 vs 5.53), trim False.
Source: `data/processed/H19-loop-gain-collapse/r1b/results*/explore.json`.
<!-- R1B END -->
