# H06 × G16: Choose your own goal! (2025-10-06 → 2025-10-10)

**Verdict:** mixed (P1; P2 failed; P3 supported; art n/a; no model adequate (joint PPC p < 0.01 for all three))
**Verdict (1b):** failed (km24 only; all models inadequate)
**Role:** exploratory
**Period:** regime I · mode F · 7 agents · 1 room (#general) · 5 days × ≈ 3 h (6 windows/day)

## Why this period
Free week with operator rules (no more spreadsheets; stop reporting self-caused bugs). Ranked first for model 06 in goal-periods.md. Same small N as #11.

## Prediction
*Written 2026-10-04, before running on this period.* The card's rules (`../../README.md`, Prediction, with the amendments made after the synthetic validation and before any real-data run) applied here:
- **P1 (primary, intention clusters `km24`):** NCD beats Hubbell and the conformist rival by ≥ 2 in synthetic log-likelihood, in ≥ 4/6 clusterings, and is adequate (no statistic with PPC p < 0.05/9). Failed if a rival beats NCD by ≥ 2 in ≥ 4/6 clusterings. "Supported" with μ̂_NCD ≥ μ_L/2 is downgraded to mixed (amendment 2).
- **P2:** β̂ below the Hubbell predictive median and inside NCD's 95% interval (rare projects recruit more per capita). Against: β̂ above Hubbell's 97.5% point (herding).
- **P3:** λ̄ inside NCD's 95% predictive interval and below Hubbell's 2.5% point when μ̂ < μ_L.
- **P4:** only if μ̂_NCD < μ_B: interior mode in P_n, ΔBIC > 0, infiltration inside NCD's interval.
- **P8:** λ̄ and copy-consistency above the day-shift independent-agents null (one-sided p < 0.05).

**Expectation for this period:** Artifact labels too sparse (H11: 1.2 per window); intention clusters only. Expect mixed (low power at N = 7).

## Result
*Run 2026-10-04 (exploratory round 1).* Data: `data/processed/H06-neutral-cooperative-dynamics/G16/round1_G16.json`. Figure: [`figures/pn_G16.pdf`](figures/pn_G16.pdf).

| Prediction | Observed | Null / rival | Verdict |
| --- | --- | --- | --- |
| P1 NCD beats both rivals (km24; ≥ 4/6 clusterings; adequate) | LLR_NH -0.8, LLR_NC -8.8; NCD ≥ 2 over both in 0/6 clusterings, a rival ≥ 2 over NCD in 3/6; best model per clustering {'ncd': 1, 'hubbell': 1, 'conformist': 4} | joint PPC p: NCD 0.002, Hubbell 0.003, conformist 0.003 | **mixed** |
| P2 β̂ below Hubbell median, inside NCD 95% | β̂ 5.01 (19 recruitment events) | NCD -0.96 [-5.77, 3.56]; Hubbell 0.32 [-4.21, 4.18]; conformist 2.25 [-1.86, 5.97] | failed (herding: beta above Hubbell 97.5%) |
| P3 λ̄ inside NCD 95% (below Hubbell 2.5%) | λ̄ 0.21; μ̂_NCD 0.378 (μ_B 0.020, μ_L 0.30); asymptotic λ* 0.26 | NCD 0.26 [0.20, 0.34]; Hubbell 0.61 [0.37, 0.91] | supported |
| P4 signatures if μ̂ < μ_B | interior mode False; ΔBIC -0.5; infiltration 0.62 | NCD infiltration 0.34 [0.16, 0.56] | n/a (high mu) |
| P8 λ̄ and copy-consistency above independent agents | λ̄ 0.21, copy-consistency 0.53 | day-shift null means 0.18 (p 0.010), 0.38 (p 0.030) | supported |
| Mapping audit (O8) | copy-consistency 0.53; singleton fraction 0.86; λ̄ halves 0.24, 0.16 | NCD copy 1.00 [0.94, 1.00], singletons 0.68 [0.53, 0.82] | descriptive |
| Post hoc: statistics reproduced (PPC p ≥ 0.05, of 9) NCD / Hubbell / conformist | 1 / 3 / 1 | NCD misses: c, f, dbic2 | descriptive (post hoc) |
| P5 artifact labels | 2.2 labelled slots per window | needs ≥ 3 | n/a (insufficient labels) |

**All label sets** (λ and β cells: mean [95% predictive interval] of 400 fresh replicates at each model's profile fit):

| Label set | N | labelled/win | changes | μ̂_NCD (μ_B, μ_L) | λ̄ obs | λ NCD | λ Hubbell | λ conf. | β̂ obs | β NCD | β Hubbell | LLR_NH | LLR_NC | best | NCD adequate | copy-cons. |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| km8 | 7 | 6.9 | 79 | 0.278 (0.020, 0.30) | 0.16 | 0.30 [0.24, 0.37] | 0.38 [0.29, 0.52] | 0.45 [0.29, 0.66] | 0.38 | -1.16 [-4.92, 2.38] | 0.10 [-3.15, 3.29] | 5.6 | -5.7 | conformist | no | 0.20 |
| km24 (primary) | 7 | 6.9 | 44 | 0.378 (0.020, 0.30) | 0.21 | 0.26 [0.20, 0.34] | 0.61 [0.37, 0.91] | 0.59 [0.30, 0.86] | 5.01 | -0.96 [-5.77, 3.56] | 0.32 [-4.21, 4.18] | -0.8 | -8.8 | conformist | no | 0.53 |
| km64 | 7 | 6.9 | 30 | 0.110 (0.020, 0.30) | 0.33 | 0.41 [0.29, 0.59] | 0.54 [0.32, 0.84] | 0.69 [0.37, 0.93] | 1.52 | -1.13 [-5.32, 3.26] | 0.18 [-3.98, 4.26] | -0.8 | 1.7 | hubbell | no | 0.82 |
| wd8 | 7 | 6.9 | 61 | 0.378 (0.020, 0.30) | 0.16 | 0.26 [0.21, 0.33] | 0.31 [0.24, 0.45] | 0.25 [0.18, 0.40] | 1.21 | -1.22 [-5.32, 3.77] | -0.08 [-4.23, 3.91] | 0.9 | -3.3 | conformist | no | 0.28 |
| wd24 | 7 | 6.9 | 38 | 0.278 (0.020, 0.30) | 0.20 | 0.30 [0.23, 0.42] | 0.38 [0.23, 0.64] | 0.58 [0.27, 0.86] | 2.08 | -0.96 [-5.42, 3.82] | 0.09 [-4.67, 4.97] | 3.4 | -0.6 | conformist | no | 0.63 |
| wd64 | 7 | 6.9 | 26 | 0.110 (0.020, 0.30) | 0.32 | 0.41 [0.30, 0.59] | 0.53 [0.30, 0.88] | 0.57 [0.25, 0.89] | 1.58 | -0.85 [-5.34, 4.29] | 0.13 [-4.41, 4.74] | 1.7 | 4.5 | ncd | yes | 0.88 |
| art | 7 | 2.2 | – | n/a (insufficient labels) | | | | | | | | | | | | |
| art_nocarry | 7 | 1.2 | – | n/a (insufficient labels) | | | | | | | | | | | | |

## Scorecard (period-specific axes)
- **C (adequacy):** NCD joint PPC p = 0.002 (km24); not adequate.
- **D (unfitted / signature):** P2 failed (herding: beta above Hubbell 97.5%); P3 supported; P4 n/a (high mu).
- **H (rivals):** best model by synthetic likelihood per clustering {'ncd': 1, 'hubbell': 1, 'conformist': 4}; artifact labels: n/a (insufficient labels).

## Notes
- 2026-10-04: folder created; predictions written before the real-data run.
- 2026-10-04: round 1 run; Result and Verdict filled by `analysis/period_folders.py`.

## Round 1b (2026-10-04)
*Corrected inputs: intention clusters on gte-modernbert `style_resid_period` (`gte_sr`), shared `project_states`, DQ4 work labels. Data: `data/processed/H06-neutral-cooperative-dynamics/r1b/` (`light_r1b.json`, `fit_*`/`round1b_*` JSON).*
- km24 fit only (compute). `gte_sr` km24: LLR_NH −6.3, LLR_NC −9.4, joint PPC 0.003 for all; singletons 0.81 (round 1 0.86); λ̄ 0.22 vs NCD 0.41; β̂ +1.76 (herding side). The ladder was not re-run, so the 4/6 clustering clause is unchecked.
