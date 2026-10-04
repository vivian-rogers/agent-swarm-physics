# H16 × G38: Choose a charity and raise money (2026-04-02 → 2026-04-24)

**Verdict:** mixed
**Verdict (1b):** mixed (unchanged under the round-1 rule; its core predictions did not change). Error loops on real failures: β -0.07 (stderr loops in round 1: -0.41); Jev blocked spells β -0.17; loop spells β -0.77
**Role:** replication (exploratory (round 1, non-holdout))
**Period:** regime III · mode C · 12–14 agents · #best / #rest · 17 days. Splits or exclusions: see the main card's period table.

## Why this period
Longest 4-h regime-III period; a shared objective with outreach waiting (approval system from 04-14, NE17), a natural source of waiting traps. NE17 split is a sensitivity check.

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
- Period-specific: the NE17 split (04-14) is a sensitivity check; same sign of the TS1r and TS2 slopes is expected on both sides.

## Result
Run 2026-10-03 with `analysis/run_period.py --period G38`; numbers in `data/processed/H16-metastable-traps-kramers/G38/results.json`; figure `figures/period.pdf`.

Data: 17 days, 14 agents; TS1 2597 / TS1r 2581 spells, TS2 1601 gates, TS3 6741 and TS4 1878 loop-turn rows; kicks {'A_und': 21813, 'A_men': 2812, 'H_und': 139, 'H_men': 11, 'N_tgt': 120, 'N_by': 665}.

| Prediction | Statement | Observed | Verdict |
| --- | --- | --- | --- |
| P-a1 | TS1r deep slope < −0.3 (aging) | β = -1.71; boot CI [-2.30, -0.74]; Wald CI [-2.10, -1.32] [Wald verdict: supported]; 230 deep escapes; pooled β -2.38 | supported |
| P-a4 (TS2r, amended) | gate escape falls with k (agent FE) | β_lnk = -0.44; boot CI [-0.58, -0.28]; Wald CI [-0.59, -0.30] [Wald verdict: supported]; 1591 gates; pooled -0.61 | supported |
| P-a4b (TS2r, amended) | re-pause keeps/lengthens declared duration | median ln(next/cur) = 0.00; longer 0.31, shorter 0.22 | supported |
| P-a4 | gate escape falls with k (agent FE), strict TS2 | β_lnk = -1.89; boot CI [-2.21, -1.47]; Wald CI [-2.24, -1.55]; 1591 gates | supported |
| P-a4b | re-pause keeps/lengthens declared duration | median ln(next/cur) = 0.00; longer 0.10, shorter 0.14 | supported |
| P-a5 | TS3 loop aging (k ≥ 3) | β = -0.41; boot CI [-0.59, 0.64]; Wald CI [-1.04, 0.22] [Wald verdict: inconclusive]; 218 escapes | inconclusive |
| P-a6 | TS4 loop aging (k ≥ 3) | β = -0.49; boot CI [-0.85, 0.08]; Wald CI [-0.90, -0.08] [Wald verdict: inconclusive]; 295 escapes | inconclusive |
| P-b0 | ≥ 50% agents double well | 1.00 of 12 agents | supported (not diagnostic: coordinate artifact) |
| P-b2 | MSM2 closure | n = 2 agents with ≥ 15 passages | n/a |
| P-b1 | Arrhenius slope in [−1.2, −0.2] | slope -0.40 (n = 7, Spearman -0.07) | supported (weak: largely mechanical) |
| P-c2 | undirected ≈ 1 (TS1) | HR 1.22 (ln 0.20 ± 0.09) | supported |
| P-c2b | directed HR ≥ 1.3, > null p95 (TS1) | HR 1.08 (ln 0.08 ± 0.16); null p95 ln 0.19 | failed |
| P-c5 | N_tgt 15-min window ln HR > 0 | ln HR 0.12 ± 0.20 (629 bins) | inconclusive |
| P-c4 | dose law undirected (TS1): not Kramers | best saturating; κ = 1.61; escapes at dose ≥ 2: 487 | supported |
| P-c3 (TS2r, amended) | directed kick during pause: gate OR ≥ 1.5 | OR(dose 1) 2.90 (ln 1.07 ± 0.40); kicked gates by dose [133, 23, 8] | supported |
| P-c3b (TS2r, amended) | undirected kick during pause: gate OR CI includes 1 | ln OR(dose 1) 0.04 ± 0.29 | supported |
| P-c3 | directed kick during pause: gate OR ≥ 1.5 | OR(dose 1) 2.33 (ln 0.84 ± 0.98); gates kicked [133, 23, 8] | failed |
| P-c4 | dose law directed (TS2): not Kramers | best additive; κ = – | supported |
| A2 (post hoc) | exact-time kick model: directed / undirected ln HR vs null p95 | dir 0.13 ± 0.16 (null p95 0.16); und 0.23 ± 0.09 (null p95 0.11) | sensitivity |
| A3 (post hoc) | outage-censored TS1r deep slope | 1 outages (213 min); β = -1.71 Wald CI [-2.10, -1.32] | sensitivity |
| A4 (post hoc) | valley bimodality vs within-day circular-shift null | p = 1.00 | sensitivity |
| A5 (post hoc) | valley with ≥ 5% mass per mode (stalls excl. / incl.) | 0.00 (1 mode) / 0.77 (2 modes) | sensitivity |
| P-c6 | directed kicks break error loops (HR > 1) | ln HR -0.31 ± 0.25 (105 rows) | failed |
| P-d1 | βJ₀ < 1 | βJ₀ = 0.09 (stalls excl.; 0.71 incl.) | supported |
| P-d2 | no valley bimodality (stalls excl.) | p = 1.00 (incl.: 0.00); stall minutes 0.054 | supported |
| P-d3 | no branch-memory excess | ACF30 0.66 vs null p95 0.29 | failed |

Period verdict rule: core predictions (P-a1/a2, P-a4, P-c1/c2/c3, P-d1, P-d2): all supported → supported; none → failed; otherwise mixed. Underpowered rows are n/a.

**NE17 split (sensitivity):** before_0414: TS1r β = -1.85, TS2 β_lnk = -1.32; from_0414: TS1r β = -1.39, TS2 β_lnk = -2.00

## Scorecard (period-specific axes)
- **C (adequacy):** kick effects vs. the day-swap null and the memoryless null within agent (rows P-a*, P-c*).
- **D (unfitted):** dwell-law shape and the swarm bimodality prediction from βJ₀ (P-d*).
- **G (ground truth):** the regime difference in what ends idling (H09) is the known structure tested by P-c1/P-c2.

## Notes
- 2026-10-03: one 213-min village-off gap (A3). Stall minutes (5.4%) drive βJ₀ 0.71 → 0.09 and the stall-included bimodality, as anticipated from synthetic data. NE17 split: aging on both sides (TS1r −1.85 / −1.39; TS2r −0.50 / −0.38).

## Round 1b (improved data, 2026-10-04)
*Replication layer (templated across periods). Predictions: the card's "Round 1b" predictions as they apply here. Numbers: `data/processed/H16-metastable-traps-kramers/r1b/G38/results.json`; tables built by `scheme/build.py --r1b`.*

| Statistic | Round 1 | Round 1b |
| --- | --- | --- |
| TS1r deep slope (inputs unchanged) | -1.71 | -1.71 |
| TS2r gate slope on ln k (inputs unchanged) | -0.44 | -0.44 |
| error-loop rows | 6741 (stderr non-empty) | 4418 (real failures) |
| error-loop aging β (boot CI), deep escapes | -0.41 [-0.59, +0.64], 218 | -0.07 [-0.31, +2.75], 77 |
| Jev blocked spells (p_blocked ≥ 0.5): β (Wald CI), spells | – | -0.17 [-0.68, +0.34], 414 |
| Jev loop spells (longest_run ≥ 5): β (Wald CI), spells | – | -0.77 [-1.17, -0.37], 722 |
| directed kick at the gate (TS2r OR, dose 1) | 2.90 | 2.92 (leading-@ nudge targets) |
| undirected kick ln HR vs day-swap null p95 (TS1) | +0.20 | +0.20 vs +0.12 |
| directed kick on real-failure loops, ln HR (SE) | -0.31 (stderr loops) | -0.53 (0.17) |
| N_tgt kicks | 120 (every named agent) | 110 (leading @) |
