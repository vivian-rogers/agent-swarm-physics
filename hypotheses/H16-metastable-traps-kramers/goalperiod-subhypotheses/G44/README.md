# H16 × G44: Finetune your leader (2026-05-26 → 2026-05-29)

**Verdict:** mixed
**Verdict (1b):** mixed (unchanged under the round-1 rule; its core predictions did not change). Error loops on real failures: β +1.63 (stderr loops in round 1: +0.53); Jev blocked spells β +0.91; loop spells β -0.29
**Role:** replication (exploratory (round 1, non-holdout))
**Period:** regime III · mode C · 16–18 agents · #best fine-tunes / #rest creative · 4 days. Splits or exclusions: see the main card's period table.

## Why this period
Mixed: #best runs a fine-tuning pipeline (waiting on jobs: polling loops), #rest does creative work; many human messages (59). Last non-holdout period before the held-out #45.

## Prediction
*Written 2026-10-03, before running on this period.* The card's predictions as they apply to a regime-III period:
- **(a)** TS1r deep-window slope β (agent FE, ≥ 10 min) < −0.3 with CI below −0.3 (aging; P-a1). TS2 per-gate escape falls
  with gate index after declared duration (β_lnk < 0, CI excluding 0) and re-pauses keep or lengthen the declared duration
  (median log ratio ≥ 0) (P-a4). TS3/TS4 loops: aging if ≥ 15 deep escapes (P-a5/a6).
- **(b)** ≥ 50% of agents with a double well (P-b0). Markov-embedding closure fails with k_obs < k_pred (median
  |ln ratio| > 0.3; memory from timers/aging; P-b2). 1D closure misses by > 2× (P-b3). Arrhenius slope in [−1.2, −0.2] if
  ≥ 6 eligible agents (P-b1).
- **(c)** TS1: undirected HR within [0.8, 1.25] or CI including 1; directed HR ≥ 1.3 above the day-swap null p95 (P-c2).
  TS2: directed kicks during the pause raise gate escape odds, OR ≥ 1.5 (P-c3); undirected OR CI includes 1. N_tgt in the
  15-min window: ln HR > 0 (P-c5). Dose law, if powered: not Kramers (P-c4).
- **(d)** βJ₀ < 1 (expected 0–0.6); no valley bimodality beyond the null with joint silences excluded; no branch-memory
  excess (P-d1–d3).
- **Against:** memoryless TS1r/TS2 slopes support Kramers; undirected kicks raising escape contradict the timer-gate picture;
  βJ₀ < 1 with significant bimodality after stall exclusion falsifies the mean-field claim.
- Period-specific: #best's fine-tuning pipeline makes TS4 (polling/identical-command loops) more common than elsewhere.

## Result
Run 2026-10-03 with `analysis/run_period.py --period G44`; numbers in `data/processed/H16-metastable-traps-kramers/G44/results.json`; figure `figures/period.pdf`.

Data: 4 days, 18 agents; TS1 814 / TS1r 781 spells, TS2 415 gates, TS3 2776 and TS4 153 loop-turn rows; kicks {'A_und': 14441, 'A_men': 2068, 'H_und': 311, 'H_men': 19, 'N_tgt': 32, 'N_by': 220}.

| Prediction | Statement | Observed | Verdict |
| --- | --- | --- | --- |
| P-a1 | TS1r deep slope < −0.3 (aging) | β = -0.77; boot CI [-0.77, 0.00]; Wald CI [-1.32, -0.22] [Wald verdict: inconclusive]; 61 deep escapes; pooled β -1.28 | inconclusive |
| P-a4 (TS2r, amended) | gate escape falls with k (agent FE) | β_lnk = -0.23; boot CI [-0.23, 0.35]; Wald CI [-0.54, 0.08] [Wald verdict: inconclusive]; 405 gates; pooled -0.56 | inconclusive |
| P-a4b (TS2r, amended) | re-pause keeps/lengthens declared duration | median ln(next/cur) = 0.00; longer 0.37, shorter 0.22 | supported |
| P-a4 | gate escape falls with k (agent FE), strict TS2 | β_lnk = -0.36; boot CI [-0.57, 0.27]; Wald CI [-0.87, 0.16]; 405 gates | inconclusive |
| P-a4b | re-pause keeps/lengthens declared duration | median ln(next/cur) = 0.00; longer 0.32, shorter 0.21 | supported |
| P-a5 | TS3 loop aging (k ≥ 3) | β = 0.53; boot CI [0.24, 1.72]; Wald CI [-0.30, 1.37] [Wald verdict: inconclusive]; 117 escapes | inconclusive |
| P-a6 | TS4 loop aging (k ≥ 3) | β = 0.62; boot CI [0.42, 5.06]; Wald CI [-0.99, 2.24] [Wald verdict: inconclusive]; 25 escapes | failed (timer-like) |
| P-b0 | ≥ 50% agents double well | – of 0 agents | n/a (not diagnostic: coordinate artifact) |
| P-b2 | MSM2 closure | n = 0 agents with ≥ 15 passages | n/a |
| P-b1 | Arrhenius slope | n = 0 eligible agents (< 6) | n/a |
| P-c2 | undirected ≈ 1 (TS1) | HR 1.31 (ln 0.27 ± 0.18) | failed |
| P-c2b | directed HR ≥ 1.3, > null p95 (TS1) | HR 1.20 (ln 0.19 ± 0.23); null p95 ln 0.29 | failed |
| P-c5 | N_tgt 15-min window ln HR > 0 | ln HR -0.24 ± 0.40 (278 bins) | failed |
| P-c4 | dose law undirected (TS1): not Kramers | best saturating; κ = 1.20; escapes at dose ≥ 2: 296 | supported |
| P-c3 (TS2r, amended) | directed kick during pause: gate OR ≥ 1.5 | OR(dose 1) 2.17 (ln 0.77 ± 0.63); kicked gates by dose [62, 5, 6] | supported |
| P-c3b (TS2r, amended) | undirected kick during pause: gate OR CI includes 1 | ln OR(dose 1) -0.45 ± 0.56 | supported |
| P-c3 | directed kick during pause: gate OR ≥ 1.5 | OR(dose 1) 1.73 (ln 0.55 ± 0.77); gates kicked [62, 5, 6] | failed |
| A2 (post hoc) | exact-time kick model: directed / undirected ln HR vs null p95 | dir 0.17 ± 0.23 (null p95 0.30); und 0.19 ± 0.18 (null p95 0.21) | sensitivity |
| A4 (post hoc) | valley bimodality vs within-day circular-shift null | p = 0.00 | sensitivity |
| A5 (post hoc) | valley with ≥ 5% mass per mode (stalls excl. / incl.) | 0.00 (1 mode) / 0.00 (1 modes) | sensitivity |
| P-c6 | directed kicks break error loops (HR > 1) | ln HR -0.04 ± 0.19 (183 rows) | failed |
| P-d1 | βJ₀ < 1 | βJ₀ = 0.33 (stalls excl.; 0.38 incl.) | supported |
| P-d2 | no valley bimodality (stalls excl.) | p = 0.00 (incl.: 0.00); stall minutes 0.001 | failed |
| P-d3 | no branch-memory excess | ACF30 0.11 vs null p95 0.20 | supported |

Period verdict rule: core predictions (P-a1/a2, P-a4, P-c1/c2/c3, P-d1, P-d2): all supported → supported; none → failed; otherwise mixed. Underpowered rows are n/a.

## Scorecard (period-specific axes)
- **C (adequacy):** kick effects vs. the day-swap null and the memoryless null within agent (rows P-a*, P-c*).
- **D (unfitted):** dwell-law shape and the swarm bimodality prediction from βJ₀ (P-d*).
- **G (ground truth):** the regime difference in what ends idling (H09) is the known structure tested by P-c1/P-c2.

## Notes
- 2026-10-03 (post hoc): the pre-registered valley test fails (p = 0.005, stalls excluded; also against the A4 circular-shift null). Diagnostic: neither room alone is bimodal, and the 'second mode' is about three near-silent minutes (K = 1 of 17) that the K = 0 stall rule misses. With a ≥ 5%-mass rule per mode (A5; synthetic: still detects βJ₀ ≥ 1.3) the period is unimodal. Reported as a pre-registered failure with this diagnosis. The 4-day bootstrap CIs here are degenerate (the full-sample estimate sits at the edge of its own bootstrap distribution); see the Wald CIs.

## Round 1b (improved data, 2026-10-04)
*Replication layer (templated across periods). Predictions: the card's "Round 1b" predictions as they apply here. Numbers: `data/processed/H16-metastable-traps-kramers/r1b/G44/results.json`; tables built by `scheme/build.py --r1b`.*

| Statistic | Round 1 | Round 1b |
| --- | --- | --- |
| TS1r deep slope (inputs unchanged) | -0.77 | -0.77 |
| TS2r gate slope on ln k (inputs unchanged) | -0.23 | -0.23 |
| error-loop rows | 2776 (stderr non-empty) | 1326 (real failures) |
| error-loop aging β (boot CI), deep escapes | +0.53 [+0.24, +1.72], 117 | +1.63 [-0.11, +5.87], 29 |
| Jev blocked spells (p_blocked ≥ 0.5): β (Wald CI), spells | – | +0.91 [-0.07, +1.89], 145 |
| Jev loop spells (longest_run ≥ 5): β (Wald CI), spells | – | -0.29 [-1.32, +0.74], 101 |
| directed kick at the gate (TS2r OR, dose 1) | 2.17 | 2.57 (leading-@ nudge targets) |
| undirected kick ln HR vs day-swap null p95 (TS1) | +0.27 | +0.27 vs +0.20 |
| directed kick on real-failure loops, ln HR (SE) | -0.04 (stderr loops) | -0.02 (0.17) |
| N_tgt kicks | 32 (every named agent) | 27 (leading @) |

## Round 2 (2026-10-05)
*Replication layer, exploratory, non-reserved days. Predictions: the card's "Round 2" section (written before any round-2 statistic). Numbers: `data/processed/H16-metastable-traps-kramers/r2/results_r2.json`.*

| Statistic | Round 2 |
| --- | --- |
| TS1r deep slope, pooled (agent FE) | -0.77 [-0.77, -0.05], 61 escapes |
| TS1r deep slope within agent × kind_start × last_kind cells | -0.10 [-0.32, +4.45] |
| TS1r deep slope, pause-start spells | -0.33 [-0.37, +3.32], 34 escapes |
| TS1r deep slope, consolidation-latency spells removed | -0.80 [-0.98, +0.23] |
| mixing share 1 − β_within/β_pooled | +0.87 |

**Reading.** Pooled TS1r aging here is mostly a mixture of spell kinds: within agent × kind cells the slope is near 0 (mixture rival not beaten in this period). Verdict unchanged (mixed).
