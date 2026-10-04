# H16 × G27: Hack the OWASP Juice Shop (competition) (2026-01-12 → 2026-01-23)

**Verdict:** mixed
**Verdict (1b):** mixed (unchanged under the round-1 rule; its core predictions did not change). Error loops on real failures: β -0.19 (stderr loops in round 1: -0.69); Jev blocked spells β -1.24; loop spells β +0.25
**Role (1b):** native (long debugging traps, N3, below) in addition to the replication
**Role:** exploratory (round 1, non-holdout)
**Period:** regime I · mode K · 10 agents · #general only · 10 days. Splits or exclusions: see the main card's period table.

## Why this period
Longest clean regime-I period before the nudger (NE10). Message-triggered escape (H09) can be tested without nudges; competition mode (K) gives individual work with bursty room chat. N_tgt is untestable here.

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
- Period-specific: no nudges (N_tgt/c5 untestable); 7 human messages only, so human kicks are underpowered.

## Result
Run 2026-10-03 with `analysis/run_period.py --period G27`; numbers in `data/processed/H16-metastable-traps-kramers/G27/results.json`; figure `figures/period.pdf`.

Data: 10 days, 10 agents; TS1 1092 / TS1r 999 spells, TS2 50 gates, TS3 3658 and TS4 1190 loop-turn rows; kicks {'A_und': 30266, 'A_men': 3421, 'H_und': 68, 'H_men': 2, 'N_tgt': 0, 'N_by': 0}.

| Prediction | Statement | Observed | Verdict |
| --- | --- | --- | --- |
| P-a2 | TS1r deep slope < −0.3 (aging) | β = -0.66; boot CI [-0.85, 0.74]; Wald CI [-1.43, 0.11] [Wald verdict: inconclusive]; 52 deep escapes; pooled β -1.53 | inconclusive |
| P-a3 | |β| shrinks with kick covariates (TS1 deep) | -0.16 → -0.52 | failed |
| P-a5 | TS3 loop aging (k ≥ 3) | β = -0.69; boot CI [-0.93, 0.40]; Wald CI [-1.11, -0.26] [Wald verdict: inconclusive]; 186 escapes | inconclusive |
| P-a6 | TS4 loop aging (k ≥ 3) | β = -0.66; boot CI [-0.85, 0.06]; Wald CI [-1.02, -0.30] [Wald verdict: inconclusive]; 210 escapes | inconclusive |
| P-b0 | ≥ 50% agents double well | 0.10 of 10 agents | failed (not diagnostic: coordinate artifact) |
| P-b2 | MSM2 closure | n = 0 agents with ≥ 15 passages | n/a |
| P-b1 | Arrhenius slope | n = 0 eligible agents (< 6) | n/a |
| P-c1 | undirected HR ≥ 1.5, > null p95 | HR 1.12 (ln 0.11 ± 0.19); null p95 ln 0.17 | failed |
| P-c1b | directed HR ≥ 1.5 | HR 1.14 (ln 0.13 ± 0.16); null p95 ln 0.11 | failed |
| P-c4 | dose law directed (TS1): not Kramers | best additive; κ = 1.42; escapes at dose ≥ 2: 63 | supported |
| P-c4 | dose law undirected (TS1): not Kramers | best additive; κ = 0.57; escapes at dose ≥ 2: 726 | supported |
| A2 (post hoc) | exact-time kick model: directed / undirected ln HR vs null p95 | dir 0.08 ± 0.16 (null p95 0.08); und 0.14 ± 0.20 (null p95 0.19) | sensitivity |
| A4 (post hoc) | valley bimodality vs within-day circular-shift null | p = 1.00 | sensitivity |
| A5 (post hoc) | valley with ≥ 5% mass per mode (stalls excl. / incl.) | 0.00 (1 mode) / 0.00 (1 modes) | sensitivity |
| P-c6 | directed kicks break error loops (HR > 1) | ln HR -0.54 ± 0.23 (165 rows) | failed |
| P-d1 | βJ₀ < 1 | βJ₀ = 0.26 (stalls excl.; 0.25 incl.) | supported |
| P-d2 | no valley bimodality (stalls excl.) | p = 1.00 (incl.: 1.00); stall minutes 0.000 | supported |
| P-d3 | no branch-memory excess | ACF30 0.21 vs null p95 0.14 | failed |

Period verdict rule: core predictions (P-a1/a2, P-a4, P-c1/c2/c3, P-d1, P-d2): all supported → supported; none → failed; otherwise mixed. Underpowered rows are n/a.

## Scorecard (period-specific axes)
- **C (adequacy):** kick effects vs. the day-swap null and the memoryless null within agent (rows P-a*, P-c*).
- **D (unfitted):** dwell-law shape and the swarm bimodality prediction from βJ₀ (P-d*).
- **G (ground truth):** the regime difference in what ends idling (H09) is the known structure tested by P-c1/P-c2.

## Notes
- 2026-10-03: no nudges (N_tgt untestable); kicks are almost all agent room messages (A_und 3,692 kicked bins).

## Round 1b (improved data, 2026-10-04)
*Replication layer (templated across periods). Predictions: the card's "Round 1b" predictions as they apply here. Numbers: `data/processed/H16-metastable-traps-kramers/r1b/G27/results.json`; tables built by `scheme/build.py --r1b`.*

| Statistic | Round 1 | Round 1b |
| --- | --- | --- |
| TS1r deep slope (inputs unchanged) | -0.66 | -0.66 |
| TS2r gate slope on ln k (inputs unchanged) | n/a | n/a |
| error-loop rows | 3658 (stderr non-empty) | 2577 (real failures) |
| error-loop aging β (boot CI), deep escapes | -0.69 [-0.93, +0.40], 186 | -0.19 [-0.93, +3.34], 57 |
| Jev blocked spells (p_blocked ≥ 0.5): β (Wald CI), spells | – | -1.24 [-1.93, -0.54], 335 |
| Jev loop spells (longest_run ≥ 5): β (Wald CI), spells | – | +0.25 [-0.82, +1.31], 293 |
| directed kick at the gate (TS2r OR, dose 1) | n/a | n/a (leading-@ nudge targets) |
| undirected kick ln HR vs day-swap null p95 (TS1) | +0.11 | +0.11 vs +0.18 |
| directed kick on real-failure loops, ln HR (SE) | -0.54 (stderr loops) | -0.51 (0.13) |
| N_tgt kicks | 0 (every named agent) | 0 (leading @) |

## Native test (round 1b): long debugging traps in #27
*Prediction written 2026-10-04 before running (card, "Round 1b", N3).* #27 (Juice Shop competition, 10 days, regime I, ~55k model calls of long debugging) is where traps should be deepest. At least one of TS3r (real-failure loops) or TS5 (Jev blocked spells) ages (β < −0.3, Wald CI below 0); credence 0.5. Directed messages do not break TS3r loops (P-c6r); credence 0.7.

*Result (`analysis/native_r1b.py`, `r1b/native_r1b.json`):* TS5 blocked spells **age**, β −1.24 (Wald [−1.93, −0.54]; boot [−2.10, +0.09]; 335 spells); TS3r is flat, β −0.19 (Wald [−0.98, 0.59]); TS6 loop spells flat (+0.25). Directed messages go with *fewer* loop breaks (ln HR −0.51 ± 0.13), undirected too (−0.38 ± 0.06). **Holds** on both statements: being blocked in a long debugging week deepens with time, and messages do not get agents out.
