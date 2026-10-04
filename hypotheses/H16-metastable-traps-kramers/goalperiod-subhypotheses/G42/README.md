# H16 × G42: Run your own YouTube channel (2026-05-18 → 2026-05-22)

**Verdict:** mixed
**Verdict (1b):** mixed (unchanged under the round-1 rule; its core predictions did not change). Error loops on real failures: β +0.16 (stderr loops in round 1: -0.31); Jev blocked spells β +0.09; loop spells β -0.07
**Role:** exploratory (round 1, non-holdout)
**Period:** regime III · mode I · 15–16 agents · 5 days. Splits or exclusions: see the main card's period table.

## Why this period
Individual production work with tooling (video pipelines): a candidate for error and command loops.

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
Run 2026-10-03 with `analysis/run_period.py --period G42`; numbers in `data/processed/H16-metastable-traps-kramers/G42/results.json`; figure `figures/period.pdf`.

Data: 5 days, 16 agents; TS1 1006 / TS1r 1007 spells, TS2 102 gates, TS3 3205 and TS4 102 loop-turn rows; kicks {'A_und': 9336, 'A_men': 1205, 'H_und': 83, 'H_men': 6, 'N_tgt': 28, 'N_by': 198}.

| Prediction | Statement | Observed | Verdict |
| --- | --- | --- | --- |
| P-a1 | TS1r deep slope < −0.3 (aging) | β = 0.21; boot CI [-0.38, 4.43]; Wald CI [-1.18, 1.61] [Wald verdict: inconclusive]; 22 deep escapes; pooled β -1.04 | inconclusive |
| P-a4 | gate escape falls with k, strict TS2 | n/a: fewer than 10 re-pauses: chains do not exist under this definition (8 re-pauses) | n/a (no strict chains) |
| P-a4 (TS2r, amended) | gate escape falls with k (agent FE) | β_lnk = 0.32; boot CI [-0.37, 4.50]; Wald CI [-0.75, 1.40] [Wald verdict: inconclusive]; 96 gates; pooled -1.07 | inconclusive |
| P-a4b (TS2r, amended) | re-pause keeps/lengthens declared duration | median ln(next/cur) = 0.19; longer 0.53, shorter 0.27 | supported |
| P-a5 | TS3 loop aging (k ≥ 3) | β = -0.31; boot CI [-0.65, 1.36]; Wald CI [-1.07, 0.45] [Wald verdict: inconclusive]; 91 escapes | inconclusive |
| P-a6 | TS4 loop aging | too few | n/a |
| P-b0 | ≥ 50% agents double well | – of 0 agents | n/a (not diagnostic: coordinate artifact) |
| P-b2 | MSM2 closure | n = 0 agents with ≥ 15 passages | n/a |
| P-b1 | Arrhenius slope | n = 0 eligible agents (< 6) | n/a |
| P-c2 | undirected ≈ 1 (TS1) | HR 1.01 (ln 0.01 ± 0.15) | supported |
| P-c2b | directed HR ≥ 1.3, > null p95 (TS1) | HR 1.01 (ln 0.01 ± 0.24); null p95 ln 0.13 | failed |
| P-c5 | N_tgt 15-min window ln HR > 0 | ln HR -0.48 ± 0.46 (163 bins) | failed |
| P-c4 | dose law undirected (TS1): not Kramers | best additive; κ = -0.11; escapes at dose ≥ 2: 209 | supported |
| P-c3 (TS2r, amended) | directed kick during pause: gate OR ≥ 1.5 | OR(dose 1) 8.12 (ln 2.09 ± 1.84); kicked gates by dose [20, 2, 0] | supported |
| P-c3b (TS2r, amended) | undirected kick during pause: gate OR CI includes 1 | ln OR(dose 1) 0.59 ± 1.93 | supported |
| A2 (post hoc) | exact-time kick model: directed / undirected ln HR vs null p95 | dir 0.06 ± 0.25 (null p95 0.03); und -0.02 ± 0.16 (null p95 0.19) | sensitivity |
| A4 (post hoc) | valley bimodality vs within-day circular-shift null | p = 1.00 | sensitivity |
| A5 (post hoc) | valley with ≥ 5% mass per mode (stalls excl. / incl.) | 0.00 (1 mode) / 0.00 (1 modes) | sensitivity |
| P-c6 | directed kicks break error loops (HR > 1) | ln HR 0.12 ± 0.29 (78 rows) | inconclusive |
| P-d1 | βJ₀ < 1 | βJ₀ = 0.09 (stalls excl.; 0.08 incl.) | supported |
| P-d2 | no valley bimodality (stalls excl.) | p = 1.00 (incl.: 1.00); stall minutes 0.000 | supported |
| P-d3 | no branch-memory excess | ACF30 0.07 vs null p95 0.12 | supported |

Period verdict rule: core predictions (P-a1/a2, P-a4, P-c1/c2/c3, P-d1, P-d2): all supported → supported; none → failed; otherwise mixed. Underpowered rows are n/a.

## Scorecard (period-specific axes)
- **C (adequacy):** kick effects vs. the day-swap null and the memoryless null within agent (rows P-a*, P-c*).
- **D (unfitted):** dwell-law shape and the swarm bimodality prediction from βJ₀ (P-d*).
- **G (ground truth):** the regime difference in what ends idling (H09) is the known structure tested by P-c1/P-c2.

## Notes

## Round 1b (improved data, 2026-10-04)
*Replication layer (templated across periods). Predictions: the card's "Round 1b" predictions as they apply here. Numbers: `data/processed/H16-metastable-traps-kramers/r1b/G42/results.json`; tables built by `scheme/build.py --r1b`.*

| Statistic | Round 1 | Round 1b |
| --- | --- | --- |
| TS1r deep slope (inputs unchanged) | +0.21 | +0.21 |
| TS2r gate slope on ln k (inputs unchanged) | +0.32 | +0.32 |
| error-loop rows | 3205 (stderr non-empty) | 1673 (real failures) |
| error-loop aging β (boot CI), deep escapes | -0.31 [-0.65, +1.36], 91 | +0.16 [-0.13, +5.10], 25 |
| Jev blocked spells (p_blocked ≥ 0.5): β (Wald CI), spells | – | +0.09 [-1.12, +1.31], 145 |
| Jev loop spells (longest_run ≥ 5): β (Wald CI), spells | – | -0.07 [-1.03, +0.88], 270 |
| directed kick at the gate (TS2r OR, dose 1) | 8.12 | 17.35 (leading-@ nudge targets) |
| undirected kick ln HR vs day-swap null p95 (TS1) | +0.01 | +0.01 vs +0.19 |
| directed kick on real-failure loops, ln HR (SE) | +0.12 (stderr loops) | +0.11 (0.21) |
| N_tgt kicks | 28 (every named agent) | 25 (leading @) |
