# H16 × G40: Connect your worlds into a 3D universe (2026-05-04 → 2026-05-08)

**Verdict:** mixed
**Verdict (1b):** mixed (unchanged under the round-1 rule; its core predictions did not change). Error loops on real failures: β +0.09 (stderr loops in round 1: -0.89); Jev blocked spells β +2.95; loop spells β -0.94
**Role:** exploratory (round 1, non-holdout)
**Period:** regime III · mode C · 15 agents · #universe-coordination · 5 days. Splits or exclusions: see the main card's period table.

## Why this period
Shared objective with one coordination room: the most directed chat in regime III (H02/H05 found the strongest collective co-activation here), so the best regime-III case for kick effects and for any swarm bimodality.

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
- Period-specific: the strongest collective co-activation in regime III (H02/H05) → the largest βJ₀ of regime III expected here, still < 1.

## Result
Run 2026-10-03 with `analysis/run_period.py --period G40`; numbers in `data/processed/H16-metastable-traps-kramers/G40/results.json`; figure `figures/period.pdf`.

Data: 5 days, 15 agents; TS1 934 / TS1r 916 spells, TS2 207 gates, TS3 7362 and TS4 365 loop-turn rows; kicks {'A_und': 20906, 'A_men': 1482, 'H_und': 29, 'H_men': 1, 'N_tgt': 11, 'N_by': 143}.

| Prediction | Statement | Observed | Verdict |
| --- | --- | --- | --- |
| P-a1 | TS1r deep slope < −0.3 (aging) | β = 0.12; boot CI [-0.96, 1.50]; Wald CI [-0.90, 1.13] [Wald verdict: inconclusive]; 28 deep escapes; pooled β -1.57 | inconclusive |
| P-a4 | gate escape falls with k, strict TS2 | n/a: fewer than 10 re-pauses: chains do not exist under this definition (1 re-pauses) | n/a (no strict chains) |
| P-a4 (TS2r, amended) | gate escape falls with k (agent FE) | β_lnk = -0.04; boot CI [-0.32, 0.71]; Wald CI [-0.62, 0.54] [Wald verdict: inconclusive]; 205 gates; pooled -0.70 | inconclusive |
| P-a4b (TS2r, amended) | re-pause keeps/lengthens declared duration | median ln(next/cur) = 0.00; longer 0.18, shorter 0.15 | supported |
| P-a5 | TS3 loop aging (k ≥ 3) | β = -0.89; boot CI [-1.30, -0.15]; Wald CI [-1.17, -0.61] [Wald verdict: supported]; 432 escapes | inconclusive |
| P-a6 | TS4 loop aging (k ≥ 3) | β = -1.23; boot CI [-1.29, 2.48]; Wald CI [-2.05, -0.41] [Wald verdict: supported]; 49 escapes | inconclusive |
| P-b0 | ≥ 50% agents double well | – of 0 agents | n/a (not diagnostic: coordinate artifact) |
| P-b2 | MSM2 closure | n = 0 agents with ≥ 15 passages | n/a |
| P-b1 | Arrhenius slope | n = 0 eligible agents (< 6) | n/a |
| P-c2 | undirected ≈ 1 (TS1) | HR 2.43 (ln 0.89 ± 0.25) | failed |
| P-c2b | directed HR ≥ 1.3, > null p95 (TS1) | HR 1.00 (ln 0.00 ± 0.24); null p95 ln 0.22 | failed |
| P-c5 | N_tgt 15-min window ln HR > 0 | ln HR -0.47 ± 0.89 (36 bins) | failed |
| P-c4 | dose law undirected (TS1): not Kramers | best saturating; κ = 1.03; escapes at dose ≥ 2: 564 | supported |
| P-c3 (TS2r, amended) | directed kick during pause: gate OR ≥ 1.5 | OR(dose 1) 1.84 (ln 0.61 ± 1.42); kicked gates by dose [13, 1, 0] | failed |
| P-c3b (TS2r, amended) | undirected kick during pause: gate OR CI includes 1 | ln OR(dose 1) -0.36 ± 0.81 | supported |
| A2 (post hoc) | exact-time kick model: directed / undirected ln HR vs null p95 | dir 0.08 ± 0.25 (null p95 0.18); und 0.94 ± 0.26 (null p95 0.93) | sensitivity |
| A4 (post hoc) | valley bimodality vs within-day circular-shift null | p = 1.00 | sensitivity |
| A5 (post hoc) | valley with ≥ 5% mass per mode (stalls excl. / incl.) | 0.00 (1 mode) / 0.00 (1 modes) | sensitivity |
| P-c6 | directed kicks break error loops (HR > 1) | ln HR 0.08 ± 0.16 (263 rows) | inconclusive |
| P-d1 | βJ₀ < 1 | βJ₀ = 0.12 (stalls excl.; 0.11 incl.) | supported |
| P-d2 | no valley bimodality (stalls excl.) | p = 1.00 (incl.: 1.00); stall minutes 0.000 | supported |
| P-d3 | no branch-memory excess | ACF30 0.11 vs null p95 0.14 | supported |

Period verdict rule: core predictions (P-a1/a2, P-a4, P-c1/c2/c3, P-d1, P-d2): all supported → supported; none → failed; otherwise mixed. Underpowered rows are n/a.

## Scorecard (period-specific axes)
- **C (adequacy):** kick effects vs. the day-swap null and the memoryless null within agent (rows P-a*, P-c*).
- **D (unfitted):** dwell-law shape and the swarm bimodality prediction from βJ₀ (P-d*).
- **G (ground truth):** the regime difference in what ends idling (H09) is the known structure tested by P-c1/P-c2.

## Notes

## Round 1b (improved data, 2026-10-04)
*Replication layer (templated across periods). Predictions: the card's "Round 1b" predictions as they apply here. Numbers: `data/processed/H16-metastable-traps-kramers/r1b/G40/results.json`; tables built by `scheme/build.py --r1b`.*

| Statistic | Round 1 | Round 1b |
| --- | --- | --- |
| TS1r deep slope (inputs unchanged) | +0.12 | +0.12 |
| TS2r gate slope on ln k (inputs unchanged) | -0.04 | -0.04 |
| error-loop rows | 7362 (stderr non-empty) | 1458 (real failures) |
| error-loop aging β (boot CI), deep escapes | -0.89 [-1.30, -0.15], 432 | +0.09 [-0.10, +5.33], 27 |
| Jev blocked spells (p_blocked ≥ 0.5): β (Wald CI), spells | – | +2.95 [+0.61, +5.28], 113 |
| Jev loop spells (longest_run ≥ 5): β (Wald CI), spells | – | -0.94 [-2.14, +0.26], 123 |
| directed kick at the gate (TS2r OR, dose 1) | 1.84 | 1.84 (leading-@ nudge targets) |
| undirected kick ln HR vs day-swap null p95 (TS1) | +0.89 | +0.89 vs +0.84 |
| directed kick on real-failure loops, ln HR (SE) | +0.08 (stderr loops) | -0.13 (0.24) |
| N_tgt kicks | 11 (every named agent) | 11 (leading @) |
