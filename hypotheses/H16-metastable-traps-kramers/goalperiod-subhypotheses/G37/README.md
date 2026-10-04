# H16 × G37: Pick your own goal! (2026-03-30 → 2026-04-01)

**Verdict:** mixed
**Verdict (1b):** mixed (unchanged under the round-1 rule; its core predictions did not change). Error loops on real failures: β -0.53 (stderr loops in round 1: -0.39); Jev blocked spells β +1.10; loop spells β +0.91
**Role:** replication (exploratory (round 1, non-holdout))
**Period:** regime III · mode F · 13 agents · #best / #rest · 3 days. Splits or exclusions: see the main card's period table.

## Why this period
First regime-III goal (timer-gated PAUSE chains, H09). Only 3 days: low power; descriptive weight.

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
- Period-specific: 3 days; most per-period tests are expected to be underpowered (verdict likely mixed/descriptive).

## Result
Run 2026-10-03 with `analysis/run_period.py --period G37`; numbers in `data/processed/H16-metastable-traps-kramers/G37/results.json`; figure `figures/period.pdf`.

Data: 3 days, 12 agents; TS1 441 / TS1r 417 spells, TS2 258 gates, TS3 1251 and TS4 69 loop-turn rows; kicks {'A_und': 3593, 'A_men': 533, 'H_und': 20, 'H_men': 5, 'N_tgt': 24, 'N_by': 125}.

| Prediction | Statement | Observed | Verdict |
| --- | --- | --- | --- |
| P-a1 | TS1r deep slope < −0.3 (aging) | β = -1.56; boot CI [-1.64, -0.37]; Wald CI [-2.22, -0.90] [Wald verdict: supported]; 46 deep escapes; pooled β -1.97 | supported |
| P-a4 (TS2r, amended) | gate escape falls with k (agent FE) | β_lnk = -0.36; boot CI [-0.67, 0.23]; Wald CI [-0.78, 0.05] [Wald verdict: inconclusive]; 254 gates; pooled -0.59 | inconclusive |
| P-a4b (TS2r, amended) | re-pause keeps/lengthens declared duration | median ln(next/cur) = 0.00; longer 0.23, shorter 0.13 | supported |
| P-a4 | gate escape falls with k (agent FE), strict TS2 | β_lnk = -1.20; boot CI [-2.14, -0.38]; Wald CI [-2.32, -0.08]; 254 gates | supported |
| P-a4b | re-pause keeps/lengthens declared duration | median ln(next/cur) = 0.00; longer 0.07, shorter 0.10 | supported |
| P-a5 | TS3 loop aging (k ≥ 3) | β = -0.39; boot CI [-1.22, 0.79]; Wald CI [-2.02, 1.24] [Wald verdict: inconclusive]; 53 escapes | inconclusive |
| P-a6 | TS4 loop aging | too few | n/a |
| P-b0 | ≥ 50% agents double well | – of 0 agents | n/a (not diagnostic: coordinate artifact) |
| P-b2 | MSM2 closure | n = 0 agents with ≥ 15 passages | n/a |
| P-b1 | Arrhenius slope | n = 0 eligible agents (< 6) | n/a |
| P-c2 | undirected ≈ 1 (TS1) | HR 1.16 (ln 0.15 ± 0.22) | supported |
| P-c2b | directed HR ≥ 1.3, > null p95 (TS1) | HR 1.51 (ln 0.41 ± 0.38); null p95 ln 0.40 | supported |
| P-c5 | N_tgt 15-min window ln HR > 0 | ln HR 0.21 ± 0.57 (175 bins) | inconclusive |
| P-c4 | dose law undirected (TS1): not Kramers | best kramers; κ = 84.36; escapes at dose ≥ 2: 82 | failed |
| P-c3 (TS2r, amended) | directed kick during pause: gate OR ≥ 1.5 | OR(dose 1) 0.91 (ln -0.09 ± 0.75); kicked gates by dose [39, 10, 3] | failed |
| P-c3b (TS2r, amended) | undirected kick during pause: gate OR CI includes 1 | ln OR(dose 1) 0.85 ± 0.94 | supported |
| P-c3 | directed kick during pause: gate OR ≥ 1.5 | OR(dose 1) 12.72 (ln 2.54 ± 2.46); gates kicked [39, 10, 3] | supported |
| A2 (post hoc) | exact-time kick model: directed / undirected ln HR vs null p95 | dir 0.22 ± 0.41 (null p95 0.20); und 0.14 ± 0.22 (null p95 0.54) | sensitivity |
| A3 (post hoc) | outage-censored TS1r deep slope | 1 outages (513 min); β = -1.56 Wald CI [-2.22, -0.90] | sensitivity |
| A4 (post hoc) | valley bimodality vs within-day circular-shift null | p = 1.00 | sensitivity |
| A5 (post hoc) | valley with ≥ 5% mass per mode (stalls excl. / incl.) | 0.00 (1 mode) / 0.90 (2 modes) | sensitivity |
| P-d1 | βJ₀ < 1 | βJ₀ = 1.10 (stalls excl.; 1.34 incl.) | failed |
| P-d2 | no valley bimodality (stalls excl.) | p = 1.00 (incl.: 0.00); stall minutes 0.333 | supported |
| P-d3 | no branch-memory excess | ACF30 0.95 vs null p95 0.77 | failed |

Period verdict rule: core predictions (P-a1/a2, P-a4, P-c1/c2/c3, P-d1, P-d2): all supported → supported; none → failed; otherwise mixed. Underpowered rows are n/a.

## Scorecard (period-specific axes)
- **C (adequacy):** kick effects vs. the day-swap null and the memoryless null within agent (rows P-a*, P-c*).
- **D (unfitted):** dwell-law shape and the swarm bimodality prediction from βJ₀ (P-d*).
- **G (ground truth):** the regime difference in what ends idling (H09) is the known structure tested by P-c1/P-c2.

## Notes
- 2026-10-03 (post hoc): the 03-31 window spans 755 min with a 513-min village-off gap (all agents silent). It inflates βJ₀ (1.10 with K = 0 minutes excluded; 0.35 against the within-day circular-shift null, A4) and makes the pre-registered valley test fire with stalls included. TS1r slopes are unchanged by outage censoring (A3), because spells > 4 h were already censored.

## Round 1b (improved data, 2026-10-04)
*Replication layer (templated across periods). Predictions: the card's "Round 1b" predictions as they apply here. Numbers: `data/processed/H16-metastable-traps-kramers/r1b/G37/results.json`; tables built by `scheme/build.py --r1b`.*

| Statistic | Round 1 | Round 1b |
| --- | --- | --- |
| TS1r deep slope (inputs unchanged) | -1.56 | -1.56 |
| TS2r gate slope on ln k (inputs unchanged) | -0.36 | -0.36 |
| error-loop rows | 1251 (stderr non-empty) | 645 (real failures) |
| error-loop aging β (boot CI), deep escapes | -0.39 [-1.22, +0.79], 53 | -0.53 [-0.53, +4.00], 14 |
| Jev blocked spells (p_blocked ≥ 0.5): β (Wald CI), spells | – | +1.10 [-0.64, +2.84], 85 |
| Jev loop spells (longest_run ≥ 5): β (Wald CI), spells | – | +0.91 [+0.01, +1.81], 157 |
| directed kick at the gate (TS2r OR, dose 1) | 0.91 | 0.83 (leading-@ nudge targets) |
| undirected kick ln HR vs day-swap null p95 (TS1) | +0.15 | +0.15 vs +0.51 |
| directed kick on real-failure loops, ln HR (SE) | +0.04 (stderr loops) | -0.24 (0.53) |
| N_tgt kicks | 24 (every named agent) | 20 (leading @) |
