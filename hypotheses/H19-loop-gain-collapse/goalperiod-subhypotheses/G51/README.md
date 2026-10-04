# H19 × G51: Each agent: Maximize your assigned goal! (2026-07-06 → 2026-09-04)

**Verdict:** failed
**Verdict (1b):** failed (round 1b, 2026-10-04, corrected data, pre-registered E1; with the day-edge-adjusted activity gain: failed; round 1: failed)
**Role:** exploratory (round 1, non-holdout)
**Period:** regime III · mode I/K · 26.5 agents (N_room 23.7) · 2 room(s) carrying ≥ 5% of agent messages · 45 non-holdout days · 8.1 h/day (empirical).

## Why this period
One point on every method's curve. Loop-gain estimates available here: H03 n̂ ALL (T2), H03 n̂ TALK (T1, primary), H03 fast n_x (T3), H04 K, weekly (E3), H04 n, weekly (T4), g_eq active (E1, primary), g_eq talk (E2). Controls: x_att = 2.24 (rank 35/35), messages per village turn 0.40, attention load k̄ = 9.1 agent messages waiting per turn, 4.1 agent messages per agent-hour, human share of chat 0.3%. Only 8 h/day exploratory period; 45 non-holdout days (the 09-07 → 09-21 tail is held out); N grows 21 → 32.

## Prediction
*Written 2026-10-04 00:09 UTC, before H19 related any control parameter to any loop gain (the card's P1 applied here).*
- Under the attention-dilution collapse (P1), every loop gain is affine-increasing in x_att. This period's x_att = 2.24 is **above** the cross-period median (0.96), so its estimates should sit **above** each method's cross-period median, and on the common curve.
- **Per-period verdict rule** (fixed now): fit the primary collapse model (per-method affine in x_att) without this period (LOPO). **supported** if (i) both primary estimates (T1 n̂ TALK, E1 g_eq active) fall inside their 90% LOPO predictive intervals and (ii) the period's summed LOPO log density under the collapse model is ≥ that under the regime-only rival N1; **mixed** if exactly one of (i), (ii) holds; **failed** if neither.
- Against it: estimates outside the intervals in the direction opposite to the x_att prediction, or N1 predicting the period better.

## Result
Primary collapse model (per-method affine in x_att), fitted without G51 (LOPO); shrunken = partial-pooling (BLUP) estimate under the collapse model fitted to all periods, shown beside the period's own estimate.

| Method | Own estimate ± SE | LOPO prediction [90% PI] | z | inside | Shrunken | Regime-only N1 prediction |
| --- | --- | --- | --- | --- | --- | --- |
| H03 n̂ ALL (T2) | 0.592 ± 0.048 | 0.003 [-0.358, 0.364] | +2.69 | **no** | 0.569 | 0.189 |
| H03 n̂ TALK (T1, primary) | 0.542 ± 0.044 | 0.067 [-0.330, 0.464] | +1.97 | **no** | 0.527 | 0.215 |
| H03 fast n_x (T3) | 0.026 ± 0.020 | -0.017 [-0.101, 0.068] | +0.83 | yes | 0.019 | 0.017 |
| H04 K, weekly (E3) | 0.271 ± 0.037 | 0.269 [0.071, 0.467] | +0.02 | yes | 0.271 | 0.195 |
| H04 n, weekly (T4) | 0.633 ± 0.043 | 0.176 [-0.152, 0.504] | +2.29 | **no** | 0.617 | 0.297 |
| g_eq active (E1, primary) | 0.237 ± 0.015 | 0.282 [0.142, 0.422] | -0.53 | yes | 0.238 | 0.195 |
| g_eq talk (E2) | 0.112 ± 0.009 | 0.090 [-0.078, 0.257] | +0.22 | yes | 0.112 | 0.092 |

- (i) both primaries inside their 90% intervals: **False**; (ii) summed LOPO log density, collapse -0.72 vs regime-only 2.35: **False**.
- Direction check (prediction: above median): primaries observed n_talk above, geq_active above.
- Per-period figure: `figures/G51_residuals.png`. Data: `data/processed/H19-loop-gain-collapse/G51/residuals.parquet`.

## Scorecard (period-specific axes)
- **C** (adequacy vs. rivals, this period): collapse vs. regime-only log density -3.07 nats.
- **D** (unfitted): the period's estimates are predicted out of sample (LOPO), not fitted.
- E, G: not informed by a single period.

## Notes
- Inputs: `data/processed/H19-loop-gain-collapse/G51/inputs.json`.

## Round 1b native test (2026-10-04): the within-period N sweep
**Role (1b):** native (+ replication)
**Why native.** #51 changes N from 21 to 32 in dated steps at a fixed goal, hours and room (DQ9 cross-index: H19 → #51). Round 1's dilution result (P4: per-pair fast cross-triggering ∝ (N_active − 1)^−1.02 *across* periods, a fixed budget per message) can be tested *inside* one period, where nothing but the roster changes.

*Prediction written 2026-10-04 06:50 UTC, before any round-1b per-unit fit.*
- **N51-a (P4 inside one period).** Across the shared `period_units` 51a–51l, per-pair fast cross-triggering n_c (H03 M3, TALK, round-1b inputs) scales as (N_active − 1)^−α with α's 95% CI covering 1 and excluding 0.
- **N51-b (activity gain).** The DQ8-trimmed activity gain g_eq (all-present window, explained joint silences removed) has no positive slope on N across the same units (95% CI of the slope covers 0 or is negative) and stays < 0.15 in every unit.
- Counts against: α CI excluding 1 (per-pair coupling that does not dilute, α ≈ 0, or dilutes faster), or a significant positive slope of the trimmed activity gain on N (a fixed per-pair activity coupling).

**Result (run 2026-10-04).** 12 units, N_active 21 → 32; source `data/processed/H19-loop-gain-collapse/r1b/native_g51.json` (`analysis/r1b_native.py g51`).

| Unit | N | per-pair fast n_c (TALK) | total fast n_x | g_eq active raw → **DQ8 trim** | g_eq talk raw |
| --- | --- | --- | --- | --- | --- |
| 51a | 21 | 0.0020 | 0.041 | 0.36 → **−0.03** | 0.23 |
| 51b | 24 | 0.0034 | 0.079 | 0.69 → – (1 day) | 0.29 |
| 51c | 25 | 0.0006 | 0.014 | 0.24 → **−0.01** | 0.15 |
| 51d | 26 | 0.0014 | 0.035 | 0.39 → **0.08** | 0.23 |
| 51e–51h | 27 | 0.0000–0.0023 | 0.000–0.059 | 0.28–0.41 → **0.05–0.15** | 0.13–0.20 |
| 51i–51l | 28–32 | 0.0000–0.0003 | 0.000–0.011 | 0.23–0.38 → **−0.03–0.17** | 0.07–0.25 |

- **N51-a: failed.** Per-pair fast cross-triggering does fall with N (Spearman −0.69, p = 0.013), but much faster than 1/(N − 1): the card's P4 power-law fit runs to the edge of its grid (α = 3.0, 95% interval [2.5, 3.0]); total cross-triggering per message is not conserved but vanishes (0.04–0.08 at N = 21–24, ≈ 0 from N = 28). The log-WLS fit on the 8 non-zero units is uninformative (−5.1 [−17, +7]). In #51, N is collinear with calendar time, the NE43 drive withdrawal and the #focus room.
- **N51-b: failed.** The trimmed activity gain rises with N (WLS slope +0.025 per agent [+0.012, +0.038]) and reaches 0.15–0.17 in the largest units. That is what a small fixed per-pair activity correlation does as N grows (g = (N−1)r/(1+(N−1)r) with r ≈ 0.005: 0.09 → 0.13 from N = 21 to 31; H50's within-window per-pair activity correlation in regime III is 0.005), not attention-diluted coupling.
- **Post hoc (round 1's k_llm channel model, not this README's prediction):** inside #51, n̂ TALK does not track messages delivered per LLM step (Spearman 0.10, p = 0.75; g_eq talk 0.22, p = 0.50), so the cross-period k_llm curve does not hold within the period.

<!-- R1B START -->
## Round 1b (improved data, 2026-10-04)
H19's own gains re-estimated on `activity_bins_fixed` (+ `outages_fixed`), H02/H03 inputs from their round-1b runs; H04's K_week and H05's gains (built on the buggy table, not yet re-run by their owners) are dropped. "DQ8 trim": all-present window, explained joint silences removed; "H38-conditioned": agent-state conditioning of day edges, infra errors and consolidations.

| Method | Round 1 | **Round 1b** | Round-1b LOPO prediction [90% PI] (raw E1 run) |
| --- | --- | --- | --- |
| E1 g_eq active (raw) | 0.237 | **0.285 ± 0.010** | 0.453 [0.266, 0.641] |
| E1 g_eq active, DQ8 trim | – | **0.075 ± 0.012** | – |
| E1 g_eq active, H38-conditioned | – | **0.148 ± 0.013** | – |
| E2 g_eq talk | 0.112 | **0.186 ± 0.007** | 0.161 [-0.038, 0.361] |
| T1 n̂ TALK | 0.542 | **0.474 ± 0.023** | 0.076 [-0.317, 0.468] |
| T3 fast n_x | 0.026 | **0.019 ± 0.020** | -0.020 [-0.104, 0.064] |

Per-period rule (unchanged): (i) both primaries inside their LOPO 90% intervals: raw run False, trim run False; (ii) log density ≥ regime-only rival: raw False (-2.53 vs 1.94), trim False.
Source: `data/processed/H19-loop-gain-collapse/r1b/results*/explore.json`.
<!-- R1B END -->
