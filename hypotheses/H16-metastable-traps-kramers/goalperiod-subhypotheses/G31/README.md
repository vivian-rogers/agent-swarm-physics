# H16 × G31: Pick your own goal (farewell to 3.7 Sonnet) (2026-02-16 → 2026-02-19 (02-20 excluded: NE11))

**Verdict:** mixed
**Role:** exploratory (round 1, non-holdout)
**Period:** regime I · mode F · 12 agents · #general · 4 days. Splits or exclusions: see the main card's period table.

## Why this period
Free period in regime I with the nudger on; the last non-holdout regime-I days before the 100-turn session cap (NE11) and before the held-out #32. Closest regime-I stand-in for the #32 confirmation.

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
- Period-specific: 4 days; nudger on; power for directed kicks low.

## Result
Run 2026-10-03 with `analysis/run_period.py --period G31`; numbers in `data/processed/H16-metastable-traps-kramers/G31/results.json`; figure `figures/period.pdf`.

Data: 4 days, 12 agents; TS1 317 / TS1r 336 spells, TS2 7 gates, TS3 2527 and TS4 65 loop-turn rows; kicks {'A_und': 22324, 'A_men': 2739, 'H_und': 101, 'H_men': 4, 'N_tgt': 40, 'N_by': 188}.

| Prediction | Statement | Observed | Verdict |
| --- | --- | --- | --- |
| P-a2 | TS1r deep slope < −0.3 | too few deep escapes | n/a |
| P-a5 | TS3 loop aging (k ≥ 3) | β = -0.68; boot CI [-1.25, 2.99]; Wald CI [-1.27, -0.09] [Wald verdict: inconclusive]; 127 escapes | inconclusive |
| P-a6 | TS4 loop aging | too few | n/a |
| P-b0 | ≥ 50% agents double well | – of 0 agents | n/a (not diagnostic: coordinate artifact) |
| P-b2 | MSM2 closure | n = 0 agents with ≥ 15 passages | n/a |
| P-b1 | Arrhenius slope | n = 0 eligible agents (< 6) | n/a |
| P-c1 | undirected HR ≥ 1.5, > null p95 | HR 0.92 (ln -0.09 ± 0.56); null p95 ln 0.07 | failed |
| P-c1b | directed HR ≥ 1.5 | HR 1.37 (ln 0.32 ± 0.28); null p95 ln 0.22 | failed |
| P-c4 | dose law undirected (TS1): not Kramers | best kramers; κ = -0.90; escapes at dose ≥ 2: 220 | failed |
| A2 (post hoc) | exact-time kick model: directed / undirected ln HR vs null p95 | dir 0.15 ± 0.29 (null p95 0.11); und 0.13 ± 0.64 (null p95 0.16) | sensitivity |
| A4 (post hoc) | valley bimodality vs within-day circular-shift null | p = 1.00 | sensitivity |
| A5 (post hoc) | valley with ≥ 5% mass per mode (stalls excl. / incl.) | 0.00 (1 mode) / 0.00 (1 modes) | sensitivity |
| P-c6 | directed kicks break error loops (HR > 1) | ln HR -0.14 ± 0.22 (152 rows) | failed |
| P-d1 | βJ₀ < 1 | βJ₀ = 0.09 (stalls excl.; 0.11 incl.) | supported |
| P-d2 | no valley bimodality (stalls excl.) | p = 1.00 (incl.: 1.00); stall minutes 0.000 | supported |
| P-d3 | no branch-memory excess | ACF30 0.03 vs null p95 0.12 | supported |

Period verdict rule: core predictions (P-a1/a2, P-a4, P-c1/c2/c3, P-d1, P-d2): all supported → supported; none → failed; otherwise mixed. Underpowered rows are n/a.

## Scorecard (period-specific axes)
- **C (adequacy):** kick effects vs. the day-swap null and the memoryless null within agent (rows P-a*, P-c*).
- **D (unfitted):** dwell-law shape and the swarm bimodality prediction from βJ₀ (P-d*).
- **G (ground truth):** the regime difference in what ends idling (H09) is the known structure tested by P-c1/P-c2.

## Notes
