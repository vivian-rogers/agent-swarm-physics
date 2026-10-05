# H16 × G51: Private roles (long goal) (2026-07-06 → 2026-09-02 (non-holdout, pre-NE33))

**Verdict:** mixed
**Verdict (1b):** mixed (unchanged under the round-1 rule; its core predictions did not change). Error loops on real failures: β -0.57 (stderr loops in round 1: -0.72); Jev blocked spells β -0.39; loop spells β -0.46
**Role:** replication (exploratory (round 1, non-holdout))
**Period:** regime III · mode P (I/K) · 21–32 agents · 8-h days · ~40 days. Splits or exclusions: see the main card's period table.

## Why this period
The private-role era: 8-h days, largest roster, most nudges (773 automated messages). By far the most power for every test; plans hidden from others (NE26), so coupling should be weakest.

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
- Period-specific: 8-h days; highest power, so the per-period verdicts here carry the most weight; plans hidden (NE26) → βJ₀ expected among the lowest.

## Result
Run 2026-10-03 with `analysis/run_period.py --period G51`; numbers in `data/processed/H16-metastable-traps-kramers/G51/results.json`; figure `figures/period.pdf`.

Data: 43 days, 29 agents; TS1 27885 / TS1r 24885 spells, TS2 23740 gates, TS3 51075 and TS4 8316 loop-turn rows; kicks {'A_und': 828400, 'A_men': 38360, 'H_und': 1981, 'H_men': 92, 'N_tgt': 970, 'N_by': 16781}.

| Prediction | Statement | Observed | Verdict |
| --- | --- | --- | --- |
| P-a1 | TS1r deep slope < −0.3 (aging) | β = -0.77; boot CI [-0.87, -0.61]; Wald CI [-0.81, -0.73] [Wald verdict: supported]; 4321 deep escapes; pooled β -0.95 | supported |
| P-a4 (TS2r, amended) | gate escape falls with k (agent FE) | β_lnk = -0.38; boot CI [-0.43, -0.33]; Wald CI [-0.43, -0.34] [Wald verdict: supported]; 23538 gates; pooled -0.80 | supported |
| P-a4b (TS2r, amended) | re-pause keeps/lengthens declared duration | median ln(next/cur) = 0.00; longer 0.25, shorter 0.18 | supported |
| P-a4 | gate escape falls with k (agent FE), strict TS2 | β_lnk = -0.94; boot CI [-1.05, -0.82]; Wald CI [-1.00, -0.88]; 23538 gates | supported |
| P-a4b | re-pause keeps/lengthens declared duration | median ln(next/cur) = 0.00; longer 0.13, shorter 0.08 | supported |
| P-a5 | TS3 loop aging (k ≥ 3) | β = -0.72; boot CI [-0.89, -0.37]; Wald CI [-0.87, -0.58] [Wald verdict: supported]; 2253 escapes | supported |
| P-a6 | TS4 loop aging (k ≥ 3) | β = -0.29; boot CI [-0.78, 0.34]; Wald CI [-0.46, -0.11] [Wald verdict: inconclusive]; 1321 escapes | inconclusive |
| P-b0 | ≥ 50% agents double well | 0.79 of 28 agents | supported (not diagnostic: coordinate artifact) |
| P-b2 | MSM2 closure fails, obs slower | median |ln| = 0.00, median ln(obs/pred) = -0.00 (n = 18) | failed (not diagnostic: one-step passage, tautological) |
| P-b3 | 1D closure misses > 2× (not diagnostic) | median |ln| = 0.44 | failed (not diagnostic) |
| P-b1 | Arrhenius slope in [−1.2, −0.2] | slope -0.66 (n = 22, Spearman -0.89) | supported (weak: largely mechanical) |
| P-c2 | undirected ≈ 1 (TS1) | HR 1.48 (ln 0.39 ± 0.04) | failed |
| P-c2b | directed HR ≥ 1.3, > null p95 (TS1) | HR 1.20 (ln 0.18 ± 0.04); null p95 ln 0.09 | failed |
| P-c5 | N_tgt 15-min window ln HR > 0 | ln HR 0.36 ± 0.08 (13584 bins) | supported |
| P-c4 | dose law directed (TS1): not Kramers | best additive; κ = 1.55; escapes at dose ≥ 2: 468 | supported |
| P-c4 | dose law undirected (TS1): not Kramers | best saturating; κ = 1.07; escapes at dose ≥ 2: 17837 | supported |
| P-c3 (TS2r, amended) | directed kick during pause: gate OR ≥ 1.5 | OR(dose 1) 1.54 (ln 0.43 ± 0.10); kicked gates by dose [2739, 623, 402] | supported |
| P-c3b (TS2r, amended) | undirected kick during pause: gate OR CI includes 1 | ln OR(dose 1) 0.11 ± 0.10 | failed |
| P-c3 | directed kick during pause: gate OR ≥ 1.5 | OR(dose 1) 4.37 (ln 1.47 ± 0.14); gates kicked [2739, 623, 402] | supported |
| P-c4 | dose law directed (TS2): not Kramers | best saturating; κ = 1.32 | supported |
| A2 (post hoc) | exact-time kick model: directed / undirected ln HR vs null p95 | dir 0.19 ± 0.04 (null p95 0.09); und 0.39 ± 0.04 (null p95 0.24) | sensitivity |
| A3 (post hoc) | outage-censored TS1r deep slope | 7 outages (930 min); β = -0.65 Wald CI [-0.70, -0.61] | sensitivity |
| A4 (post hoc) | valley bimodality vs within-day circular-shift null | p = 1.00 | sensitivity |
| A5 (post hoc) | valley with ≥ 5% mass per mode (stalls excl. / incl.) | 0.00 (1 mode) / 0.00 (1 modes) | sensitivity |
| P-c6 | directed kicks break error loops (HR > 1) | ln HR -0.02 ± 0.07 (1255 rows) | failed |
| P-d1 | βJ₀ < 1 | βJ₀ = 0.41 (stalls excl.; 0.66 incl.) | supported |
| P-d2 | no valley bimodality (stalls excl.) | p = 1.00 (incl.: 0.00); stall minutes 0.027 | supported |
| P-d3 | no branch-memory excess | ACF30 0.53 vs null p95 0.23 | failed |

Period verdict rule: core predictions (P-a1/a2, P-a4, P-c1/c2/c3, P-d1, P-d2): all supported → supported; none → failed; otherwise mixed. Underpowered rows are n/a.

## Scorecard (period-specific axes)
- **C (adequacy):** kick effects vs. the day-swap null and the memoryless null within agent (rows P-a*, P-c*).
- **D (unfitted):** dwell-law shape and the swarm bimodality prediction from βJ₀ (P-d*).
- **G (ground truth):** the regime difference in what ends idling (H09) is the known structure tested by P-c1/P-c2.

## Notes
- 2026-10-03: 6 days with village-off gaps (7 outages, 930 min). A3 outage censoring changes the TS1r deep slope from −0.77 to −0.65. Branch memory (residual ACF at 30 min 0.53 vs null p95 0.23) without bimodality: slow collective persistence, not bistability.

## Round 1b (improved data, 2026-10-04)
*Replication layer (templated across periods). Predictions: the card's "Round 1b" predictions as they apply here. Numbers: `data/processed/H16-metastable-traps-kramers/r1b/G51/results.json`; tables built by `scheme/build.py --r1b`.*

| Statistic | Round 1 | Round 1b |
| --- | --- | --- |
| TS1r deep slope (inputs unchanged) | -0.77 | -0.77 |
| TS2r gate slope on ln k (inputs unchanged) | -0.38 | -0.38 |
| error-loop rows | 51075 (stderr non-empty) | 26872 (real failures) |
| error-loop aging β (boot CI), deep escapes | -0.72 [-0.89, -0.37], 2253 | -0.57 [-0.69, -0.06], 984 |
| Jev blocked spells (p_blocked ≥ 0.5): β (Wald CI), spells | – | -0.39 [-0.56, -0.22], 3417 |
| Jev loop spells (longest_run ≥ 5): β (Wald CI), spells | – | -0.46 [-0.63, -0.29], 3936 |
| directed kick at the gate (TS2r OR, dose 1) | 1.54 | 1.52 (leading-@ nudge targets) |
| undirected kick ln HR vs day-swap null p95 (TS1) | +0.39 | +0.39 vs +0.25 |
| directed kick on real-failure loops, ln HR (SE) | -0.02 (stderr loops) | -0.07 (0.05) |
| N_tgt kicks | 970 (every named agent) | 729 (leading @) |

## Round 2 (2026-10-05)
*Replication layer, exploratory, non-reserved days. Predictions: the card's "Round 2" section (written before any round-2 statistic). Numbers: `data/processed/H16-metastable-traps-kramers/r2/results_r2.json`.*

| Statistic | Round 2 |
| --- | --- |
| gate aging slope (sustained escape, ln trap age; 21361 gates) | -0.35 [-0.44, -0.23] |
| urn-predicted gate slope: U-tok / U-call / U-entry / U-rec | -0.02 / -0.36 / -0.03 / -0.03 |
| aging absorbed by ln(1 − f): ρ U-call (β_f) / U-tok | +0.47 [+0.33, +0.70] (β_f +1.05) / +0.47 |
| forced reset inside a trap (NE41), log OR (276 gates) | +2.68 [+2.31, +3.16] |
| directed read at the gate / undirected only / difference (log OR) | +0.69 / +0.24 / +0.45 [+0.32, +0.58] |
| dose: 1 vs 2+ directed items (log OR) | +0.63 vs +0.85 |
| TS1r deep slope, pooled (agent FE) | -0.77 [-0.87, -0.61], 4321 escapes |
| TS1r deep slope within agent × kind_start × last_kind cells | -0.64 [-0.71, -0.49] |
| TS1r deep slope, pause-start spells | -0.61 [-0.69, -0.49], 3136 escapes |
| TS1r deep slope, consolidation-latency spells removed | -0.71 [-0.82, -0.57] |
| mixing share 1 − β_within/β_pooled | +0.16 |
| pure-mixture null (agent × kind cells), mean [95%] | -0.20 [-0.24, -0.16]; observed below it (M-P2) |
| day-cell mixture null (post hoc P4) | -0.93 [-0.98, -0.89] |
| post hoc P1: forced-reset step, outcome shifted one call | +2.35 [+2.01, +2.74] |
| post hoc P5: escape after forced reset vs none, k = 1 / 2–4 / ≥ 5 | 0.93/0.91/0.58 vs 0.68/0.44/0.09 |
| per-agent TS1r slopes (R3-P3) | I² 0.92, 26 agents, range 0.00 to −1.83 |

**Reading.** The forced erasure lifts escape from 0.47 to 0.84 (R1-P3 holds; frailty-proof). The own-call urn predicts the gate exponent and absorbs about half of it (R1-P1b holds, R1-P2 fails), but not the TS1r exponent. A directed read works by address (R2-P1, R2-P2 hold). Pause-start spells age within kind and beat the pure-mixture null (M-P1, M-P2 hold); the day-cell null (post hoc) reproduces the TS1r slope. Verdict unchanged (mixed).
