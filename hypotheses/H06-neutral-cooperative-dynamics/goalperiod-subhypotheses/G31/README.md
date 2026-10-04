# H06 × G31: Pick your own goal (agents bid 3.7 Sonnet farewell) (2026-02-16 → 2026-02-20)

**Verdict:** failed (P1; P2 supported; P3 failed; art failed; no model adequate (joint PPC p < 0.01 for all three))
**Role:** exploratory
**Period:** regime I · mode F · 13 agents (Sonnet 4.6 joins, 3.7 Sonnet leaves) · 1 room · 5 days × 4 h (8 windows/day). Inside: 100-turn session cap (2026-02-20).

## Why this period
The best-sampled free week: 10 artifact-labelled agents per window and 1,291 intentions. The dataset summary says about nine agents converged on one task with competing PRs; H11 found herding waves onto successive shared repos (βJ_CW +4.9, z_N2 +14.3).

## Prediction
*Written 2026-10-04, before running on this period.* The card's rules (`../../README.md`, Prediction, with the amendments made after the synthetic validation and before any real-data run) applied here:
- **P1 (primary, intention clusters `km24`):** NCD beats Hubbell and the conformist rival by ≥ 2 in synthetic log-likelihood, in ≥ 4/6 clusterings, and is adequate (no statistic with PPC p < 0.05/9). Failed if a rival beats NCD by ≥ 2 in ≥ 4/6 clusterings. "Supported" with μ̂_NCD ≥ μ_L/2 is downgraded to mixed (amendment 2).
- **P2:** β̂ below the Hubbell predictive median and inside NCD's 95% interval (rare projects recruit more per capita). Against: β̂ above Hubbell's 97.5% point (herding).
- **P3:** λ̄ inside NCD's 95% predictive interval and below Hubbell's 2.5% point when μ̂ < μ_L.
- **P4:** only if μ̂_NCD < μ_B: interior mode in P_n, ΔBIC > 0, infiltration inside NCD's interval.
- **P8:** λ̄ and copy-consistency above the day-shift independent-agents null (one-sided p < 0.05).

**Expectation for this period:** **Artifact labels:** the conformist (herding) rival beats NCD (LLR_NC ≤ −2), P2 fails in the herding direction (β̂ > 0). **Intention clusters:** uncertain; if the convergence shows in stated goals too, the conformist rival wins there as well. NCD support here would contradict H11.

## Result
*Run 2026-10-04 (exploratory round 1).* Data: `data/processed/H06-neutral-cooperative-dynamics/G31/round1_G31.json`. Figure: [`figures/pn_G31.pdf`](figures/pn_G31.pdf).

| Prediction | Observed | Null / rival | Verdict |
| --- | --- | --- | --- |
| P1 NCD beats both rivals (km24; ≥ 4/6 clusterings; adequate) | LLR_NH 22.0, LLR_NC -34.9; NCD ≥ 2 over both in 0/6 clusterings, a rival ≥ 2 over NCD in 6/6; best model per clustering {'ncd': 0, 'hubbell': 2, 'conformist': 4} | joint PPC p: NCD 0.002, Hubbell 0.002, conformist 0.002 | **failed** |
| P2 β̂ below Hubbell median, inside NCD 95% | β̂ -0.78 (83 recruitment events) | NCD -1.24 [-3.26, 0.63]; Hubbell 0.08 [-1.53, 2.08]; conformist 3.24 [1.01, 6.06] | supported |
| P3 λ̄ inside NCD 95% (below Hubbell 2.5%) | λ̄ 0.15; μ̂_NCD 0.204 (μ_B 0.015, μ_L 0.22); asymptotic λ* 0.23 | NCD 0.23 [0.20, 0.26]; Hubbell 0.44 [0.32, 0.61] | failed (lambda outside NCD 95%) |
| P4 signatures if μ̂ < μ_B | interior mode False; ΔBIC 4.3; infiltration 0.20 | NCD infiltration 0.24 [0.17, 0.32] | n/a (between mu_B and mu_L: no bimodality required) |
| P8 λ̄ and copy-consistency above independent agents | λ̄ 0.15, copy-consistency 0.34 | day-shift null means 0.12 (p 0.005), 0.22 (p 0.005) | supported |
| Mapping audit (O8) | copy-consistency 0.34; singleton fraction 0.79; λ̄ halves 0.14, 0.17 | NCD copy 0.98 [0.95, 1.00], singletons 0.54 [0.48, 0.60] | descriptive |
| Post hoc: statistics reproduced (PPC p ≥ 0.05, of 9) NCD / Hubbell / conformist | 2 / 3 / 0 | NCD misses: c, f, lam, xmax, single, rich, dbic2 | descriptive (post hoc) |
| P5 artifact labels (secondary) | LLR_NH -15.7, LLR_NC -3.9; λ̄ 0.37 (NCD 0.35 [0.30, 0.40], Hubbell 0.60 [0.39, 0.83]); β̂ -1.73 (NCD -1.61 [-3.33, 0.12], Hubbell 0.39 [-1.72, 3.53]); reproduced 6 / 4 / 0 | joint PPC NCD 0.002 | failed; P2 supported; P3 supported |

**All label sets** (λ and β cells: mean [95% predictive interval] of 400 fresh replicates at each model's profile fit):

| Label set | N | labelled/win | changes | μ̂_NCD (μ_B, μ_L) | λ̄ obs | λ NCD | λ Hubbell | λ conf. | β̂ obs | β NCD | β Hubbell | LLR_NH | LLR_NC | best | NCD adequate | copy-cons. |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| km8 | 13 | 11.5 | 333 | 0.378 (0.015, 0.22) | 0.12 | 0.17 [0.15, 0.19] | 0.19 [0.17, 0.22] | 0.53 [0.37, 0.68] | 1.38 | -0.99 [-3.62, 1.90] | -0.03 [-2.80, 2.56] | 19.2 | -31.6 | conformist | no | 0.23 |
| km24 (primary) | 13 | 11.5 | 298 | 0.204 (0.015, 0.22) | 0.15 | 0.23 [0.20, 0.26] | 0.44 [0.32, 0.61] | 0.53 [0.32, 0.69] | -0.78 | -1.24 [-3.26, 0.63] | 0.08 [-1.53, 2.08] | 22.0 | -34.9 | conformist | no | 0.34 |
| km64 | 13 | 11.5 | 266 | 0.032 (0.015, 0.22) | 0.22 | 0.40 [0.33, 0.48] | 0.44 [0.31, 0.65] | 0.79 [0.61, 0.90] | 0.20 | -1.64 [-3.35, 0.23] | 0.09 [-1.89, 2.13] | -22.6 | 72.4 | hubbell | no | 0.56 |
| wd8 | 13 | 11.5 | 336 | 0.378 (0.015, 0.22) | 0.13 | 0.17 [0.15, 0.18] | 0.19 [0.17, 0.22] | 0.52 [0.36, 0.68] | 2.20 | -1.06 [-4.04, 1.63] | -0.07 [-2.88, 2.59] | 2.8 | -33.9 | conformist | no | 0.23 |
| wd24 | 13 | 11.5 | 311 | 0.150 (0.015, 0.22) | 0.16 | 0.26 [0.23, 0.30] | 0.37 [0.28, 0.48] | 0.52 [0.31, 0.70] | -1.64 | -1.38 [-3.04, 0.35] | 0.04 [-1.69, 1.66] | -30.7 | -47.8 | conformist | no | 0.31 |
| wd64 | 13 | 11.5 | 271 | 0.032 (0.015, 0.22) | 0.21 | 0.41 [0.34, 0.49] | 0.44 [0.32, 0.64] | 0.79 [0.59, 0.89] | -0.73 | -1.53 [-3.43, 0.53] | 0.11 [-1.52, 2.09] | -8.6 | 80.0 | hubbell | no | 0.57 |
| art | 13 | 11.4 | 204 | 0.059 (0.015, 0.22) | 0.37 | 0.35 [0.30, 0.40] | 0.60 [0.39, 0.83] | 0.68 [0.45, 0.83] | -1.73 | -1.61 [-3.33, 0.12] | 0.39 [-1.72, 3.53] | -15.7 | -3.9 | hubbell | no | 0.59 |
| art_nocarry | 13 | 10.1 | 192 | 0.032 (0.015, 0.22) | 0.39 | 0.41 [0.35, 0.48] | 0.59 [0.42, 0.79] | 0.69 [0.50, 0.82] | -2.01 | -1.68 [-3.71, 0.27] | 0.22 [-1.98, 3.47] | -19.3 | -4.0 | hubbell | no | 0.57 |

## Scorecard (period-specific axes)
- **C (adequacy):** NCD joint PPC p = 0.002 (km24); not adequate.
- **D (unfitted / signature):** P2 supported; P3 failed (lambda outside NCD 95%); P4 n/a (between mu_B and mu_L: no bimodality required).
- **H (rivals):** best model by synthetic likelihood per clustering {'ncd': 0, 'hubbell': 2, 'conformist': 4}; artifact labels: failed.

## Notes
- 2026-10-04: folder created; predictions written before the real-data run.
- 2026-10-04: round 1 run; Result and Verdict filled by `analysis/period_folders.py`.
