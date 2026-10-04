# H06 × G44: Finetune your leader! (#rest room: pick your own goal) (2026-05-26 → 2026-05-29)

**Verdict:** failed (P1; P2 failed; P3 failed; art failed; no model adequate (joint PPC p < 0.01 for all three))
**Role:** exploratory
**Period:** regime III · mode C for #best, free for #rest · #rest room only: 12 agents · 4 days × 4 h

## Why this period
#best fine-tuned a leader; #rest picked its own goals (all chose creative work and tested what survives consolidation). The #rest room is a free 'week' with a well-defined room.

## Prediction
*Written 2026-10-04, before running on this period.* The card's rules (`../../README.md`, Prediction, with the amendments made after the synthetic validation and before any real-data run) applied here:
- **P1 (primary, intention clusters `km24`):** NCD beats Hubbell and the conformist rival by ≥ 2 in synthetic log-likelihood, in ≥ 4/6 clusterings, and is adequate (no statistic with PPC p < 0.05/9). Failed if a rival beats NCD by ≥ 2 in ≥ 4/6 clusterings. "Supported" with μ̂_NCD ≥ μ_L/2 is downgraded to mixed (amendment 2).
- **P2:** β̂ below the Hubbell predictive median and inside NCD's 95% interval (rare projects recruit more per capita). Against: β̂ above Hubbell's 97.5% point (herding).
- **P3:** λ̄ inside NCD's 95% predictive interval and below Hubbell's 2.5% point when μ̂ < μ_L.
- **P4:** only if μ̂_NCD < μ_B: interior mode in P_n, ΔBIC > 0, infiltration inside NCD's interval.
- **P8:** λ̄ and copy-consistency above the day-shift independent-agents null (one-sided p < 0.05).

**Expectation for this period:** All #rest agents chose creative work: a shared theme, but separate artifacts, which looks like agent-bound projects plus a common field. Expect NCD not adequate and no decisive win (mixed); conformist if a shared creative project emerged.

## Result
*Run 2026-10-04 (exploratory round 1).* Data: `data/processed/H06-neutral-cooperative-dynamics/G44/round1_G44.json`. Figure: [`figures/pn_G44.pdf`](figures/pn_G44.pdf).

| Prediction | Observed | Null / rival | Verdict |
| --- | --- | --- | --- |
| P1 NCD beats both rivals (km24; ≥ 4/6 clusterings; adequate) | LLR_NH -1.4, LLR_NC -18.6; NCD ≥ 2 over both in 0/6 clusterings, a rival ≥ 2 over NCD in 4/6; best model per clustering {'ncd': 1, 'hubbell': 1, 'conformist': 4} | joint PPC p: NCD 0.002, Hubbell 0.002, conformist 0.002 | **failed** |
| P2 β̂ below Hubbell median, inside NCD 95% | β̂ 1.39 (26 recruitment events) | NCD -1.23 [-4.60, 1.63]; Hubbell -0.15 [-3.39, 2.91]; conformist 2.74 [-0.09, 6.06] | failed (no negative frequency dependence) |
| P3 λ̄ inside NCD 95% (below Hubbell 2.5%) | λ̄ 0.13; μ̂_NCD 0.204 (μ_B 0.016, μ_L 0.23); asymptotic λ* 0.25 | NCD 0.24 [0.19, 0.31]; Hubbell 0.25 [0.18, 0.37] | failed (lambda outside NCD 95%) |
| P4 signatures if μ̂ < μ_B | interior mode False; ΔBIC 5.3; infiltration 0.14 | NCD infiltration 0.21 [0.07, 0.41] | n/a (between mu_B and mu_L: no bimodality required) |
| P8 λ̄ and copy-consistency above independent agents | λ̄ 0.13, copy-consistency 0.33 | day-shift null means 0.11 (p 0.005), 0.26 (p 0.070) | failed |
| Mapping audit (O8) | copy-consistency 0.33; singleton fraction 0.86; λ̄ halves 0.11, 0.14 | NCD copy 0.98 [0.92, 1.00], singletons 0.53 [0.38, 0.65] | descriptive |
| Post hoc: statistics reproduced (PPC p ≥ 0.05, of 9) NCD / Hubbell / conformist | 3 / 2 / 2 | NCD misses: c, f, lam, xmax, single, rich | descriptive (post hoc) |
| P5 artifact labels (secondary) | LLR_NH -7.2, LLR_NC -6.0; λ̄ 0.19 (NCD 0.25 [0.20, 0.30], Hubbell 0.21 [0.17, 0.29]); β̂ 4.19 (NCD -1.41 [-4.15, 1.18], Hubbell -0.12 [-4.14, 3.36]); reproduced 5 / 4 / 3 | joint PPC NCD 0.002 | failed; P2 failed (herding: beta above Hubbell 97.5%); P3 failed (lambda outside NCD 95%) |

**All label sets** (λ and β cells: mean [95% predictive interval] of 400 fresh replicates at each model's profile fit):

| Label set | N | labelled/win | changes | μ̂_NCD (μ_B, μ_L) | λ̄ obs | λ NCD | λ Hubbell | λ conf. | β̂ obs | β NCD | β Hubbell | LLR_NH | LLR_NC | best | NCD adequate | copy-cons. |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| km8 | 12 | 10.9 | 146 | 0.204 (0.016, 0.23) | 0.10 | 0.24 [0.19, 0.31] | 0.20 [0.16, 0.27] | 0.52 [0.28, 0.73] | 3.82 | -1.35 [-4.11, 1.22] | -0.20 [-3.80, 3.06] | -3.3 | -32.8 | conformist | no | 0.19 |
| km24 (primary) | 12 | 10.9 | 92 | 0.204 (0.016, 0.23) | 0.13 | 0.24 [0.19, 0.31] | 0.25 [0.18, 0.37] | 0.53 [0.22, 0.84] | 1.39 | -1.23 [-4.60, 1.63] | -0.15 [-3.39, 2.91] | -1.4 | -18.6 | conformist | no | 0.33 |
| km64 | 12 | 10.9 | 72 | 0.204 (0.016, 0.23) | 0.17 | 0.24 [0.18, 0.31] | 0.53 [0.30, 0.90] | 0.67 [0.35, 0.89] | -4.44 | -1.40 [-5.26, 1.88] | 0.54 [-2.85, 4.48] | -2.0 | 6.1 | hubbell | no | 0.68 |
| wd8 | 12 | 10.9 | 131 | 0.204 (0.016, 0.23) | 0.10 | 0.24 [0.19, 0.31] | 0.20 [0.16, 0.27] | 0.53 [0.26, 0.77] | 1.97 | -1.42 [-4.68, 1.36] | 0.05 [-3.16, 2.98] | -10.0 | -21.7 | conformist | no | 0.19 |
| wd24 | 12 | 10.9 | 76 | 0.204 (0.016, 0.23) | 0.12 | 0.24 [0.18, 0.32] | 0.25 [0.16, 0.41] | 0.53 [0.20, 0.81] | 2.20 | -1.29 [-5.16, 1.55] | -0.20 [-4.13, 3.39] | -2.4 | -12.1 | conformist | no | 0.30 |
| wd64 | 12 | 10.9 | 33 | 0.081 (0.016, 0.23) | 0.18 | 0.33 [0.22, 0.48] | 0.46 [0.25, 0.83] | 0.66 [0.24, 0.94] | 0.00 | -1.30 [-6.06, 3.03] | 0.19 [-3.61, 4.03] | 0.3 | 3.6 | ncd | no | 0.78 |
| art | 12 | 9.8 | 108 | 0.204 (0.016, 0.23) | 0.19 | 0.25 [0.20, 0.30] | 0.21 [0.17, 0.29] | 0.36 [0.20, 0.58] | 4.19 | -1.41 [-4.15, 1.18] | -0.12 [-4.14, 3.36] | -7.2 | -6.0 | hubbell | no | 0.27 |
| art_nocarry | 12 | 7.8 | 96 | 0.278 (0.016, 0.23) | 0.23 | 0.25 [0.22, 0.30] | 0.24 [0.21, 0.31] | 0.54 [0.30, 0.73] | 5.36 | -1.22 [-4.42, 1.91] | -0.20 [-3.96, 2.97] | -2.2 | -3.7 | conformist | no | 0.25 |

## Scorecard (period-specific axes)
- **C (adequacy):** NCD joint PPC p = 0.002 (km24); not adequate.
- **D (unfitted / signature):** P2 failed (no negative frequency dependence); P3 failed (lambda outside NCD 95%); P4 n/a (between mu_B and mu_L: no bimodality required).
- **H (rivals):** best model by synthetic likelihood per clustering {'ncd': 1, 'hubbell': 1, 'conformist': 4}; artifact labels: failed.

## Notes
- 2026-10-04: folder created; predictions written before the real-data run.
- 2026-10-04: round 1 run; Result and Verdict filled by `analysis/period_folders.py`.
