# H16 × G41: Perform novel research (2026-05-11 → 2026-05-15)

**Verdict:** mixed
**Role:** exploratory (round 1, non-holdout)
**Period:** regime III · mode I · 15 agents · 5 days. Splits or exclusions: see the main card's period table.

## Why this period
Individual research projects: long solo work, plausible theory spirals and error loops.

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

## Result
Run 2026-10-03 with `analysis/run_period.py --period G41`; numbers in `data/processed/H16-metastable-traps-kramers/G41/results.json`; figure `figures/period.pdf`.

Data: 5 days, 15 agents; TS1 912 / TS1r 894 spells, TS2 329 gates, TS3 5051 and TS4 231 loop-turn rows; kicks {'A_und': 15376, 'A_men': 2689, 'H_und': 70, 'H_men': 10, 'N_tgt': 72, 'N_by': 346}.

| Prediction | Statement | Observed | Verdict |
| --- | --- | --- | --- |
| P-a1 | TS1r deep slope < −0.3 (aging) | β = -0.62; boot CI [-1.21, 0.42]; Wald CI [-1.19, -0.04] [Wald verdict: inconclusive]; 56 deep escapes; pooled β -0.92 | inconclusive |
| P-a4 (TS2r, amended) | gate escape falls with k (agent FE) | β_lnk = -0.44; boot CI [-0.54, 0.43]; Wald CI [-0.77, -0.10] [Wald verdict: supported]; 316 gates; pooled -0.68 | inconclusive |
| P-a4b (TS2r, amended) | re-pause keeps/lengthens declared duration | median ln(next/cur) = 0.00; longer 0.33, shorter 0.22 | supported |
| P-a4 | gate escape falls with k (agent FE), strict TS2 | β_lnk = -0.56; boot CI [-0.91, 1.04]; Wald CI [-1.89, 0.76]; 317 gates | inconclusive |
| P-a4b | re-pause keeps/lengthens declared duration | median ln(next/cur) = 0.00; longer 0.33, shorter 0.15 | supported |
| P-a5 | TS3 loop aging (k ≥ 3) | β = -0.72; boot CI [-0.91, -0.09]; Wald CI [-1.16, -0.28] [Wald verdict: inconclusive]; 223 escapes | inconclusive |
| P-a6 | TS4 loop aging (k ≥ 3) | β = 0.12; boot CI [-0.68, 0.39]; Wald CI [-0.82, 1.07] [Wald verdict: inconclusive]; 19 escapes | inconclusive |
| P-b0 | ≥ 50% agents double well | – of 0 agents | n/a (not diagnostic: coordinate artifact) |
| P-b2 | MSM2 closure | n = 0 agents with ≥ 15 passages | n/a |
| P-b1 | Arrhenius slope | n = 0 eligible agents (< 6) | n/a |
| P-c2 | undirected ≈ 1 (TS1) | HR 1.70 (ln 0.53 ± 0.16) | failed |
| P-c2b | directed HR ≥ 1.3, > null p95 (TS1) | HR 1.17 (ln 0.15 ± 0.18); null p95 ln 0.20 | failed |
| P-c5 | N_tgt 15-min window ln HR > 0 | ln HR -0.14 ± 0.36 (283 bins) | failed |
| P-c4 | dose law directed (TS1): not Kramers | best additive; κ = 2.70; escapes at dose ≥ 2: 44 | supported |
| P-c4 | dose law undirected (TS1): not Kramers | best saturating; κ = 1.39; escapes at dose ≥ 2: 335 | supported |
| P-c3 (TS2r, amended) | directed kick during pause: gate OR ≥ 1.5 | OR(dose 1) 2.35 (ln 0.86 ± 0.66); kicked gates by dose [61, 13, 13] | supported |
| P-c3b (TS2r, amended) | undirected kick during pause: gate OR CI includes 1 | ln OR(dose 1) 0.39 ± 0.72 | supported |
| P-c3 | directed kick during pause: gate OR ≥ 1.5 | OR(dose 1) 1.25 (ln 0.23 ± 1.35); gates kicked [62, 13, 13] | failed |
| A2 (post hoc) | exact-time kick model: directed / undirected ln HR vs null p95 | dir 0.07 ± 0.18 (null p95 0.16); und 0.51 ± 0.17 (null p95 0.32) | sensitivity |
| A4 (post hoc) | valley bimodality vs within-day circular-shift null | p = 1.00 | sensitivity |
| A5 (post hoc) | valley with ≥ 5% mass per mode (stalls excl. / incl.) | 0.00 (1 mode) / 0.00 (1 modes) | sensitivity |
| P-c6 | directed kicks break error loops (HR > 1) | ln HR -0.10 ± 0.17 (248 rows) | failed |
| P-d1 | βJ₀ < 1 | βJ₀ = 0.35 (stalls excl.; 0.35 incl.) | supported |
| P-d2 | no valley bimodality (stalls excl.) | p = 1.00 (incl.: 1.00); stall minutes 0.000 | supported |
| P-d3 | no branch-memory excess | ACF30 0.26 vs null p95 0.19 | failed |

Period verdict rule: core predictions (P-a1/a2, P-a4, P-c1/c2/c3, P-d1, P-d2): all supported → supported; none → failed; otherwise mixed. Underpowered rows are n/a.

## Scorecard (period-specific axes)
- **C (adequacy):** kick effects vs. the day-swap null and the memoryless null within agent (rows P-a*, P-c*).
- **D (unfitted):** dwell-law shape and the swarm bimodality prediction from βJ₀ (P-d*).
- **G (ground truth):** the regime difference in what ends idling (H09) is the known structure tested by P-c1/P-c2.

## Notes
