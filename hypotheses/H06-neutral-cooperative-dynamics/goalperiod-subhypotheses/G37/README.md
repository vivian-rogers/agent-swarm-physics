# H06 × G37: Pick your own goal! (2026-03-30 → 2026-04-01)

**Verdict:** failed (P1; P2 failed; P3 failed; art mixed; no model adequate (joint PPC p < 0.01 for all three))
**Verdict (1b):** failed (km24 only; all models inadequate)
**Role:** exploratory
**Period:** regime III · mode F · 13 agents · #best/#rest rooms (pooled: one free goal for both) · 3 days × 4 h (8 windows/day)

## Why this period
First free goal in regime III (audit accumulated frameworks and habits). H11: herding (βJ_CW +3.7, z_N2 +6.9). Only 3 days.

## Prediction
*Written 2026-10-04, before running on this period.* The card's rules (`../../README.md`, Prediction, with the amendments made after the synthetic validation and before any real-data run) applied here:
- **P1 (primary, intention clusters `km24`):** NCD beats Hubbell and the conformist rival by ≥ 2 in synthetic log-likelihood, in ≥ 4/6 clusterings, and is adequate (no statistic with PPC p < 0.05/9). Failed if a rival beats NCD by ≥ 2 in ≥ 4/6 clusterings. "Supported" with μ̂_NCD ≥ μ_L/2 is downgraded to mixed (amendment 2).
- **P2:** β̂ below the Hubbell predictive median and inside NCD's 95% interval (rare projects recruit more per capita). Against: β̂ above Hubbell's 97.5% point (herding).
- **P3:** λ̄ inside NCD's 95% predictive interval and below Hubbell's 2.5% point when μ̂ < μ_L.
- **P4:** only if μ̂_NCD < μ_B: interior mode in P_n, ΔBIC > 0, infiltration inside NCD's interval.
- **P8:** λ̄ and copy-consistency above the day-shift independent-agents null (one-sided p < 0.05).

**Expectation for this period:** Same as #31: conformist beats NCD on artifact labels; intention clusters uncertain. Pooling two rooms breaks well-mixing, which by itself lowers apparent herding. Short period: residence times are heavily truncated (P4 weak).

## Result
*Run 2026-10-04 (exploratory round 1).* Data: `data/processed/H06-neutral-cooperative-dynamics/G37/round1_G37.json`. Figure: [`figures/pn_G37.pdf`](figures/pn_G37.pdf).

| Prediction | Observed | Null / rival | Verdict |
| --- | --- | --- | --- |
| P1 NCD beats both rivals (km24; ≥ 4/6 clusterings; adequate) | LLR_NH -3.0, LLR_NC -16.3; NCD ≥ 2 over both in 1/6 clusterings, a rival ≥ 2 over NCD in 5/6; best model per clustering {'ncd': 1, 'hubbell': 1, 'conformist': 4} | joint PPC p: NCD 0.002, Hubbell 0.002, conformist 0.002 | **failed** |
| P2 β̂ below Hubbell median, inside NCD 95% | β̂ 1.07 (30 recruitment events) | NCD -1.41 [-4.61, 1.34]; Hubbell 0.02 [-2.40, 2.99]; conformist 2.71 [0.19, 6.44] | failed (no negative frequency dependence) |
| P3 λ̄ inside NCD 95% (below Hubbell 2.5%) | λ̄ 0.14; μ̂_NCD 0.150 (μ_B 0.016, μ_L 0.23); asymptotic λ* 0.29 | NCD 0.26 [0.20, 0.35]; Hubbell 0.38 [0.25, 0.58] | failed (lambda outside NCD 95%) |
| P4 signatures if μ̂ < μ_B | interior mode False; ΔBIC 28.6; infiltration 0.31 | NCD infiltration 0.29 [0.15, 0.50] | n/a (between mu_B and mu_L: no bimodality required) |
| P8 λ̄ and copy-consistency above independent agents | λ̄ 0.14, copy-consistency 0.37 | day-shift null means 0.21 (p 1.000), 0.23 (p 0.010) | failed |
| Mapping audit (O8) | copy-consistency 0.37; singleton fraction 0.83; λ̄ halves 0.15, 0.14 | NCD copy 1.00 [0.97, 1.00], singletons 0.45 [0.32, 0.57] | descriptive |
| Post hoc: statistics reproduced (PPC p ≥ 0.05, of 9) NCD / Hubbell / conformist | 3 / 3 / 2 | NCD misses: c, lam, xmax, single, rich | descriptive (post hoc) |
| P5 artifact labels (secondary) | LLR_NH 2.3, LLR_NC 9.2; λ̄ 0.22 (NCD 0.24 [0.20, 0.31], Hubbell 0.26 [0.19, 0.37]); β̂ -0.70 (NCD -1.33 [-4.57, 1.64], Hubbell -0.09 [-3.15, 2.90]); reproduced 7 / 8 / 7 | joint PPC NCD 0.062 | mixed (NCD best but mu near mu_L); P2 supported; P3 mixed (inside NCD and Hubbell intervals) |

**All label sets** (λ and β cells: mean [95% predictive interval] of 400 fresh replicates at each model's profile fit):

| Label set | N | labelled/win | changes | μ̂_NCD (μ_B, μ_L) | λ̄ obs | λ NCD | λ Hubbell | λ conf. | β̂ obs | β NCD | β Hubbell | LLR_NH | LLR_NC | best | NCD adequate | copy-cons. |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| km8 | 12 | 7.2 | 141 | 0.278 (0.016, 0.23) | 0.10 | 0.20 [0.16, 0.25] | 0.19 [0.16, 0.26] | 0.53 [0.29, 0.76] | -0.30 | -1.16 [-4.33, 1.79] | -0.17 [-3.58, 3.04] | 1.4 | -11.4 | conformist | no | 0.22 |
| km24 (primary) | 12 | 7.2 | 94 | 0.150 (0.016, 0.23) | 0.14 | 0.26 [0.20, 0.35] | 0.38 [0.25, 0.58] | 0.54 [0.27, 0.79] | 1.07 | -1.41 [-4.61, 1.34] | 0.02 [-2.40, 2.99] | -3.0 | -16.3 | conformist | no | 0.37 |
| km64 | 12 | 7.2 | 47 | 0.032 (0.016, 0.23) | 0.20 | 0.41 [0.30, 0.54] | 0.39 [0.24, 0.66] | 0.52 [0.19, 0.81] | 1.25 | -1.23 [-4.46, 2.37] | 0.29 [-2.90, 4.62] | -6.2 | 25.4 | hubbell | no | 0.75 |
| wd8 | 12 | 7.2 | 117 | 0.378 (0.016, 0.23) | 0.10 | 0.17 [0.14, 0.21] | 0.20 [0.15, 0.27] | 0.34 [0.18, 0.56] | 2.17 | -1.29 [-4.88, 2.17] | -0.21 [-3.60, 3.17] | -0.9 | -16.9 | conformist | no | 0.29 |
| wd24 | 12 | 7.2 | 74 | 0.204 (0.016, 0.23) | 0.13 | 0.23 [0.18, 0.32] | 0.32 [0.21, 0.50] | 0.34 [0.15, 0.62] | 3.25 | -1.43 [-5.10, 1.99] | 0.15 [-2.68, 3.41] | -2.5 | -3.2 | conformist | no | 0.48 |
| wd64 | 12 | 7.2 | 31 | 0.059 (0.016, 0.23) | 0.21 | 0.36 [0.25, 0.52] | 0.47 [0.27, 0.83] | 0.86 [0.61, 0.99] | 0.95 | -1.17 [-4.77, 2.61] | 0.30 [-3.47, 4.73] | 2.4 | 41.5 | ncd | no | 0.78 |
| art | 12 | 6.5 | 82 | 0.204 (0.016, 0.23) | 0.22 | 0.24 [0.20, 0.31] | 0.26 [0.19, 0.37] | 0.34 [0.17, 0.61] | -0.70 | -1.33 [-4.57, 1.64] | -0.09 [-3.15, 2.90] | 2.3 | 9.2 | ncd | yes | 0.77 |
| art_nocarry | 12 | 4.6 | 68 | 0.204 (0.016, 0.23) | 0.28 | 0.27 [0.22, 0.32] | 0.34 [0.26, 0.46] | 0.37 [0.21, 0.61] | -0.96 | -1.24 [-4.86, 2.39] | 0.06 [-3.44, 4.14] | 1.8 | 9.9 | ncd | yes | 0.71 |

## Scorecard (period-specific axes)
- **C (adequacy):** NCD joint PPC p = 0.002 (km24); not adequate.
- **D (unfitted / signature):** P2 failed (no negative frequency dependence); P3 failed (lambda outside NCD 95%); P4 n/a (between mu_B and mu_L: no bimodality required).
- **H (rivals):** best model by synthetic likelihood per clustering {'ncd': 1, 'hubbell': 1, 'conformist': 4}; artifact labels: mixed (NCD best but mu near mu_L).

## Notes
- 2026-10-04: folder created; predictions written before the real-data run.
- 2026-10-04: round 1 run; Result and Verdict filled by `analysis/period_folders.py`.

## Round 1b (2026-10-04)
*Corrected inputs: intention clusters on gte-modernbert `style_resid_period` (`gte_sr`), shared `project_states`, DQ4 work labels. Data: `data/processed/H06-neutral-cooperative-dynamics/r1b/` (`light_r1b.json`, `fit_*`/`round1b_*` JSON).*
- `gte_sr` km24: LLR_NH −24.9, LLR_NC −30.5, joint PPC 0.002 for all; singletons 0.72 (round 1 0.83); λ̄ 0.141 vs NCD 0.20 [0.16, 0.25] and *below* the day-shift null (0.21). Work labels: 3.8 per window but only 5 non-novel switches (not testable).
