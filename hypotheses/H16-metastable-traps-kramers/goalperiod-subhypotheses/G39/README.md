# H16 × G39: Build your own interactive world (2026-04-27 → 2026-05-01)

**Verdict:** mixed
**Role:** exploratory (round 1, non-holdout)
**Period:** regime III · mode I · 15 agents · reshuffled rooms · 5 days. Splits or exclusions: see the main card's period table.

## Why this period
Individual objectives (I): traps should be individual, swarm coupling weak; a clean regime-III replicate.

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
Run 2026-10-03 with `analysis/run_period.py --period G39`; numbers in `data/processed/H16-metastable-traps-kramers/G39/results.json`; figure `figures/period.pdf`.

Data: 5 days, 15 agents; TS1 944 / TS1r 937 spells, TS2 66 gates, TS3 3195 and TS4 227 loop-turn rows; kicks {'A_und': 7332, 'A_men': 436, 'H_und': 100, 'H_men': 5, 'N_tgt': 8, 'N_by': 69}.

| Prediction | Statement | Observed | Verdict |
| --- | --- | --- | --- |
| P-a1 | TS1r deep slope < −0.3 (aging) | β = -1.97; boot CI [-3.91, 1.40]; Wald CI [-2.80, -1.13] [Wald verdict: supported]; 26 deep escapes; pooled β -2.43 | inconclusive |
| P-a4 | gate escape falls with k, strict TS2 | n/a: fewer than 10 re-pauses: chains do not exist under this definition (0 re-pauses) | n/a (no strict chains) |
| P-a5 | TS3 loop aging (k ≥ 3) | β = 0.20; boot CI [-0.13, 1.62]; Wald CI [-0.61, 1.02] [Wald verdict: inconclusive]; 71 escapes | inconclusive |
| P-a6 | TS4 loop aging (k ≥ 3) | β = -0.56; boot CI [-0.68, 0.29]; Wald CI [-1.73, 0.62] [Wald verdict: inconclusive]; 26 escapes | inconclusive |
| P-b0 | ≥ 50% agents double well | – of 0 agents | n/a (not diagnostic: coordinate artifact) |
| P-b2 | MSM2 closure | n = 0 agents with ≥ 15 passages | n/a |
| P-b1 | Arrhenius slope | n = 0 eligible agents (< 6) | n/a |
| P-c2 | undirected ≈ 1 (TS1) | HR 1.22 (ln 0.20 ± 0.15) | supported |
| P-c2b | directed HR ≥ 1.3, > null p95 (TS1) | HR 1.11 (ln 0.10 ± 0.33); null p95 ln 0.21 | failed |
| P-c5 | N_tgt 15-min window ln HR > 0 | ln HR 0.23 ± 1.00 (21 bins) | inconclusive |
| P-c4 | dose law undirected (TS1): not Kramers | best saturating; κ = 1.79; escapes at dose ≥ 2: 178 | supported |
| A2 (post hoc) | exact-time kick model: directed / undirected ln HR vs null p95 | dir -0.04 ± 0.35 (null p95 0.12); und 0.12 ± 0.16 (null p95 0.15) | sensitivity |
| A4 (post hoc) | valley bimodality vs within-day circular-shift null | p = 1.00 | sensitivity |
| A5 (post hoc) | valley with ≥ 5% mass per mode (stalls excl. / incl.) | 0.00 (1 mode) / 0.00 (1 modes) | sensitivity |
| P-c6 | directed kicks break error loops (HR > 1) | ln HR -0.43 ± 0.37 (50 rows) | failed |
| P-d1 | βJ₀ < 1 | βJ₀ = 0.15 (stalls excl.; 0.15 incl.) | supported |
| P-d2 | no valley bimodality (stalls excl.) | p = 1.00 (incl.: 1.00); stall minutes 0.000 | supported |
| P-d3 | no branch-memory excess | ACF30 0.19 vs null p95 0.21 | supported |

Period verdict rule: core predictions (P-a1/a2, P-a4, P-c1/c2/c3, P-d1, P-d2): all supported → supported; none → failed; otherwise mixed. Underpowered rows are n/a.

## Scorecard (period-specific axes)
- **C (adequacy):** kick effects vs. the day-swap null and the memoryless null within agent (rows P-a*, P-c*).
- **D (unfitted):** dwell-law shape and the swarm bimodality prediction from βJ₀ (P-d*).
- **G (ground truth):** the regime difference in what ends idling (H09) is the known structure tested by P-c1/P-c2.

## Notes
