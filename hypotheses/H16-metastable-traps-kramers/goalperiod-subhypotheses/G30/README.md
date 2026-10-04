# H16 × G30: Adopt a park and get it cleaned (2026-02-09 → 2026-02-13)

**Verdict:** mixed
**Verdict (1b):** mixed (unchanged under the round-1 rule; its core predictions did not change). Error loops on real failures: β +1.27 (stderr loops in round 1: -1.05); Jev blocked spells β +0.43; loop spells β +0.02
**Role:** exploratory (round 1, non-holdout)
**Period:** regime I · mode C · 11 agents · #general · 5 days. Splits or exclusions: see the main card's period table.

## Why this period
Regime I with the nudger switching on (first nudges 02-13, NE10). Shared objective (C): more directed chat than G27. Nudge effects rest on one day only.

## Prediction
*Written 2026-10-03, before running on this period.* The card's predictions as they apply to a regime-I period:
- **(a)** TS1r deep-window slope β (agent FE, ≥ 10 min) < −0.3 with CI below −0.3 (aging; P-a2). With kick covariates added,
  |β| shrinks toward 0 (P-a3: driven Kramers). TS3/TS4 loops: aging (P-a5/a6) if ≥ 15 deep escapes. TS2 not applicable.
- **(b)** ≥ 50% of agents have a double well in G(x) (P-b0). Markov-embedding closure holds: median |ln(k_obs/k_MSM2)| ≤ 0.3
  (P-b2, regime I). 1D closure misses by > 2× (P-b3, not diagnostic). Arrhenius slope of ln k_TS1r,deep on ΔG in
  [−1.2, −0.2] if ≥ 6 eligible agents (P-b1).
- **(c)** Undirected kicks: HR ≥ 1.5 and above the day-swap null p95 (P-c1); directed HR ≥ 1.5 (ordering low confidence).
  Dose law, if powered: additive or saturating preferred over Kramers (P-c4).
- **(d)** βJ₀ < 1 (expected 0–0.6); no valley bimodality beyond the null with joint silences excluded; no branch-memory
  excess (P-d1–d3).
- **Against:** a memoryless deep slope (|β| ≤ 0.3, CI inside the band) supports Kramers; undirected HR ≤ 1 contradicts
  message-triggered escape; βJ₀ < 1 with significant bimodality after stall exclusion falsifies the mean-field claim.
- Period-specific: nudges exist on 02-13 only; N_tgt effects are not scored.

## Result
Run 2026-10-03 with `analysis/run_period.py --period G30`; numbers in `data/processed/H16-metastable-traps-kramers/G30/results.json`; figure `figures/period.pdf`.

Data: 5 days, 11 agents; TS1 316 / TS1r 338 spells, TS2 14 gates, TS3 1906 and TS4 97 loop-turn rows; kicks {'A_und': 24247, 'A_men': 2325, 'H_und': 152, 'H_men': 13, 'N_tgt': 20, 'N_by': 112}.

| Prediction | Statement | Observed | Verdict |
| --- | --- | --- | --- |
| P-a2 | TS1r deep slope < −0.3 (aging) | β = 2.61; boot CI [1.73, 5.83]; Wald CI [0.46, 4.76] [Wald verdict: failed (timer-like)]; 24 deep escapes; pooled β 1.31 | failed (timer-like) |
| P-a5 | TS3 loop aging (k ≥ 3) | β = -1.05; boot CI [-1.30, 0.19]; Wald CI [-1.71, -0.40] [Wald verdict: supported]; 111 escapes | inconclusive |
| P-a6 | TS4 loop aging (k ≥ 3) | β = 2.37; boot CI [-0.31, 6.11]; Wald CI [-1.58, 6.32] [Wald verdict: inconclusive]; 18 escapes | inconclusive |
| P-b0 | ≥ 50% agents double well | – of 0 agents | n/a (not diagnostic: coordinate artifact) |
| P-b2 | MSM2 closure | n = 0 agents with ≥ 15 passages | n/a |
| P-b1 | Arrhenius slope | n = 0 eligible agents (< 6) | n/a |
| P-c1 | undirected HR ≥ 1.5, > null p95 | HR 0.66 (ln -0.42 ± 0.51); null p95 ln 0.12 | failed |
| P-c1b | directed HR ≥ 1.5 | HR 0.93 (ln -0.08 ± 0.30); null p95 ln 0.11 | failed |
| P-c4 | dose law undirected (TS1): not Kramers | best additive; κ = -0.04; escapes at dose ≥ 2: 258 | supported |
| A2 (post hoc) | exact-time kick model: directed / undirected ln HR vs null p95 | dir -0.22 ± 0.32 (null p95 0.11); und -0.45 ± 0.55 (null p95 -0.16) | sensitivity |
| A4 (post hoc) | valley bimodality vs within-day circular-shift null | p = 1.00 | sensitivity |
| A5 (post hoc) | valley with ≥ 5% mass per mode (stalls excl. / incl.) | 0.00 (1 mode) / 0.00 (1 modes) | sensitivity |
| P-c6 | directed kicks break error loops (HR > 1) | ln HR -0.08 ± 0.28 (88 rows) | failed |
| P-d1 | βJ₀ < 1 | βJ₀ = 0.23 (stalls excl.; 0.23 incl.) | supported |
| P-d2 | no valley bimodality (stalls excl.) | p = 1.00 (incl.: 1.00); stall minutes 0.000 | supported |
| P-d3 | no branch-memory excess | ACF30 0.06 vs null p95 0.06 | supported |

Period verdict rule: core predictions (P-a1/a2, P-a4, P-c1/c2/c3, P-d1, P-d2): all supported → supported; none → failed; otherwise mixed. Underpowered rows are n/a.

## Scorecard (period-specific axes)
- **C (adequacy):** kick effects vs. the day-swap null and the memoryless null within agent (rows P-a*, P-c*).
- **D (unfitted):** dwell-law shape and the swarm bimodality prediction from βJ₀ (P-d*).
- **G (ground truth):** the regime difference in what ends idling (H09) is the known structure tested by P-c1/P-c2.

## Notes
- 2026-10-03: the timer-like TS1r deep slope (+2.61) rests on 24 deep escapes in 5 days; treat as noise-limited.

## Round 1b (improved data, 2026-10-04)
*Replication layer (templated across periods). Predictions: the card's "Round 1b" predictions as they apply here. Numbers: `data/processed/H16-metastable-traps-kramers/r1b/G30/results.json`; tables built by `scheme/build.py --r1b`.*

| Statistic | Round 1 | Round 1b |
| --- | --- | --- |
| TS1r deep slope (inputs unchanged) | +2.61 | +2.61 |
| TS2r gate slope on ln k (inputs unchanged) | n/a | n/a |
| error-loop rows | 1906 (stderr non-empty) | 1002 (real failures) |
| error-loop aging β (boot CI), deep escapes | -1.05 [-1.30, +0.19], 111 | +1.27 [-0.39, +5.57], 25 |
| Jev blocked spells (p_blocked ≥ 0.5): β (Wald CI), spells | – | +0.43 [-1.18, +2.05], 155 |
| Jev loop spells (longest_run ≥ 5): β (Wald CI), spells | – | +0.02 [-0.58, +0.61], 250 |
| directed kick at the gate (TS2r OR, dose 1) | n/a | n/a (leading-@ nudge targets) |
| undirected kick ln HR vs day-swap null p95 (TS1) | -0.42 | -0.42 vs +0.21 |
| directed kick on real-failure loops, ln HR (SE) | -0.08 (stderr loops) | -0.06 (0.21) |
| N_tgt kicks | 20 (every named agent) | 12 (leading @) |
