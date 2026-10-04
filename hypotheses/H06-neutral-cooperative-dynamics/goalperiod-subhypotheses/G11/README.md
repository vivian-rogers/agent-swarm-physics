# H06 × G11: Pursue whatever you'd like to (2025-08-25 → 2025-08-29)

**Verdict:** failed (P1; P2 failed; P3 failed; art n/a; no model adequate (joint PPC p < 0.01 for all three))
**Role:** exploratory
**Period:** regime I · mode F · 7 agents · 1 room (#general) · 5 days × ≈ 3 h (6 windows/day)

## Why this period
The first free week after the batch join of NE27 (N 4 → 7). goal-periods.md ranks model 06 first here (self-chosen meta-projects, e.g. documenting platform instabilities). Smallest N of the free weeks: synthetic power at N = 7 is lower (see the card's calibration notes).

## Prediction
*Written 2026-10-04, before running on this period.* The card's rules (`../../README.md`, Prediction, with the amendments made after the synthetic validation and before any real-data run) applied here:
- **P1 (primary, intention clusters `km24`):** NCD beats Hubbell and the conformist rival by ≥ 2 in synthetic log-likelihood, in ≥ 4/6 clusterings, and is adequate (no statistic with PPC p < 0.05/9). Failed if a rival beats NCD by ≥ 2 in ≥ 4/6 clusterings. "Supported" with μ̂_NCD ≥ μ_L/2 is downgraded to mixed (amendment 2).
- **P2:** β̂ below the Hubbell predictive median and inside NCD's 95% interval (rare projects recruit more per capita). Against: β̂ above Hubbell's 97.5% point (herding).
- **P3:** λ̄ inside NCD's 95% predictive interval and below Hubbell's 2.5% point when μ̂ < μ_L.
- **P4:** only if μ̂_NCD < μ_B: interior mode in P_n, ΔBIC > 0, infiltration inside NCD's interval.
- **P8:** λ̄ and copy-consistency above the day-shift independent-agents null (one-sided p < 0.05).

**Expectation for this period:** Artifact labels are too sparse here (H11: 0.7 labelled agents per window), so only intention clusters are tested. With N = 7 and 5 short days, I expect at best a mixed verdict. My prior leans to agent-bound projects (each agent its own meta-project), which none of the copying models contain: expect NCD not adequate, P8 weak.

## Result
*Run 2026-10-04 (exploratory round 1).* Data: `data/processed/H06-neutral-cooperative-dynamics/G11/round1_G11.json`. Figure: [`figures/pn_G11.pdf`](figures/pn_G11.pdf).

| Prediction | Observed | Null / rival | Verdict |
| --- | --- | --- | --- |
| P1 NCD beats both rivals (km24; ≥ 4/6 clusterings; adequate) | LLR_NH -3.9, LLR_NC -7.0; NCD ≥ 2 over both in 0/6 clusterings, a rival ≥ 2 over NCD in 4/6; best model per clustering {'ncd': 0, 'hubbell': 2, 'conformist': 4} | joint PPC p: NCD 0.003, Hubbell 0.003, conformist 0.003 | **failed** |
| P2 β̂ below Hubbell median, inside NCD 95% | β̂ 4.03 (10 recruitment events) | NCD -1.18 [-5.37, 3.93]; Hubbell 0.20 [-3.40, 4.47]; conformist 2.34 [-2.19, 5.88] | failed (no negative frequency dependence) |
| P3 λ̄ inside NCD 95% (below Hubbell 2.5%) | λ̄ 0.21; μ̂_NCD 0.204 (μ_B 0.020, μ_L 0.30); asymptotic λ* 0.37 | NCD 0.34 [0.25, 0.48]; Hubbell 0.45 [0.30, 0.68] | failed (lambda outside NCD 95%) |
| P4 signatures if μ̂ < μ_B | interior mode False; ΔBIC 1.0; infiltration 0.75 | NCD infiltration 0.43 [0.18, 0.75] | n/a (between mu_B and mu_L: no bimodality required) |
| P8 λ̄ and copy-consistency above independent agents | λ̄ 0.21, copy-consistency 0.23 | day-shift null means 0.18 (p 0.005), 0.21 (p 0.269) | failed |
| Mapping audit (O8) | copy-consistency 0.23; singleton fraction 0.91; λ̄ halves 0.17, 0.28 | NCD copy 0.99 [0.92, 1.00], singletons 0.53 [0.34, 0.69] | descriptive |
| Post hoc: statistics reproduced (PPC p ≥ 0.05, of 9) NCD / Hubbell / conformist | 3 / 3 / 1 | NCD misses: c, lam, xmax, single, rich | descriptive (post hoc) |
| P5 artifact labels | 1.1 labelled slots per window | needs ≥ 3 | n/a (insufficient labels) |

**All label sets** (λ and β cells: mean [95% predictive interval] of 400 fresh replicates at each model's profile fit):

| Label set | N | labelled/win | changes | μ̂_NCD (μ_B, μ_L) | λ̄ obs | λ NCD | λ Hubbell | λ conf. | β̂ obs | β NCD | β Hubbell | LLR_NH | LLR_NC | best | NCD adequate | copy-cons. |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| km8 | 7 | 6.8 | 91 | 0.150 (0.020, 0.30) | 0.19 | 0.37 [0.31, 0.45] | 0.38 [0.29, 0.52] | 0.44 [0.30, 0.60] | 4.16 | -1.22 [-4.06, 2.03] | 0.24 [-3.13, 3.50] | -28.2 | -36.4 | conformist | no | 0.07 |
| km24 (primary) | 7 | 6.8 | 54 | 0.204 (0.020, 0.30) | 0.21 | 0.34 [0.25, 0.48] | 0.45 [0.30, 0.68] | 0.57 [0.29, 0.84] | 4.03 | -1.18 [-5.37, 3.93] | 0.20 [-3.40, 4.47] | -3.9 | -7.0 | conformist | no | 0.23 |
| km64 | 7 | 6.8 | 34 | 0.081 (0.020, 0.30) | 0.30 | 0.45 [0.32, 0.65] | 0.52 [0.33, 0.80] | 0.69 [0.35, 0.92] | -0.10 | -1.08 [-5.19, 3.69] | 0.12 [-3.99, 4.10] | -0.1 | 1.7 | hubbell | no | 0.74 |
| wd8 | 7 | 6.8 | 76 | 0.278 (0.020, 0.30) | 0.19 | 0.30 [0.24, 0.40] | 0.31 [0.23, 0.40] | 0.58 [0.34, 0.81] | 3.44 | -0.88 [-5.19, 3.15] | -0.05 [-4.74, 4.49] | -7.3 | -13.8 | conformist | no | 0.10 |
| wd24 | 7 | 6.8 | 50 | 0.204 (0.020, 0.30) | 0.20 | 0.33 [0.25, 0.44] | 0.45 [0.30, 0.69] | 0.57 [0.27, 0.83] | 5.36 | -1.11 [-5.36, 3.08] | 0.13 [-3.83, 4.19] | -8.3 | -14.9 | conformist | no | 0.27 |
| wd64 | 7 | 6.8 | 26 | 0.081 (0.020, 0.30) | 0.32 | 0.45 [0.31, 0.64] | 0.44 [0.28, 0.73] | 0.70 [0.39, 0.92] | 1.28 | -1.16 [-5.40, 3.26] | 0.10 [-3.94, 4.44] | -1.0 | 4.3 | hubbell | yes | 0.60 |
| art | 7 | 1.1 | – | n/a (insufficient labels) | | | | | | | | | | | | |
| art_nocarry | 7 | 0.7 | – | n/a (insufficient labels) | | | | | | | | | | | | |

## Scorecard (period-specific axes)
- **C (adequacy):** NCD joint PPC p = 0.003 (km24); not adequate.
- **D (unfitted / signature):** P2 failed (no negative frequency dependence); P3 failed (lambda outside NCD 95%); P4 n/a (between mu_B and mu_L: no bimodality required).
- **H (rivals):** best model by synthetic likelihood per clustering {'ncd': 0, 'hubbell': 2, 'conformist': 4}; artifact labels: n/a (insufficient labels).

## Notes
- 2026-10-04: folder created; predictions written before the real-data run.
- 2026-10-04: round 1 run; Result and Verdict filled by `analysis/period_folders.py`.
