# H06 × G30: Adopt a park and get it cleaned! (2026-02-09 → 2026-02-13)

**Verdict:** mixed (P6 contrast)
**Verdict (1b):** mixed (P6); work labels: NCD and Hubbell adequate, no core
**Role:** exploratory (contrast)
**Period:** regime I · mode C · 12 agents · 1 room · 5 days × 4 h

## Why this period
Shared-objective contrast immediately before free week #31, same roster and hours: the cleanest mode contrast available (H11: herding, βJ_CW +2.0).

## Prediction
*Written 2026-10-04, before running on this period.* The card's rules (`../../README.md`, Prediction, with the amendments made after the synthetic validation and before any real-data run) applied here:
- **P6 (contrast):** LLR_NC ≤ −2 (the conformist rival beats NCD) on intention `km24`, and λ̄ above NCD's 97.5% predictive point. Verdict: supported if both hold, failed if NCD beats the conformist rival by ≥ 2, mixed otherwise. P1–P4 are also reported for comparison.

**Expectation for this period:** **P6:** conformist beats NCD; λ̄ above NCD's 97.5% point.

## Result
*Run 2026-10-04 (exploratory round 1).* Data: `data/processed/H06-neutral-cooperative-dynamics/G30/round1_G30.json`. Figure: [`figures/pn_G30.pdf`](figures/pn_G30.pdf).

| Prediction | Observed | Null / rival | Verdict |
| --- | --- | --- | --- |
| P6 conformist beats NCD and λ̄ above NCD 97.5% (km24) | LLR_NC -66.3 (≤ −2); λ̄ 0.14 vs NCD 97.5% point 0.31 (not above) | joint PPC p: ncd 0.002, hubbell 0.002, conformist 0.002 | **mixed** |
| For comparison: P1 rule | failed (best per clustering {'ncd': 0, 'hubbell': 2, 'conformist': 4}); P2 supported; P3 failed (lambda outside NCD 95%) | reproduced NCD / Hubbell / conformist 2 / 4 / 0 | descriptive |
| Independent-agents null | λ̄ 0.14 vs 0.11 (p 0.005); copy-consistency 0.36 vs 0.22 (p 0.005) | | descriptive |
| Artifact labels | LLR_NH -22.5, LLR_NC 24.5; λ̄ 0.61 (NCD 97.5% 0.59); β̂ 2.27 | reproduced 6 / 6 / 2 | failed |

**All label sets:**

| Label set | N | labelled/win | changes | μ̂_NCD (μ_B, μ_L) | λ̄ obs | λ NCD | λ Hubbell | λ conf. | β̂ obs | β NCD | β Hubbell | LLR_NH | LLR_NC | best | NCD adequate | copy-cons. |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| km8 | 12 | 12.0 | 381 | 0.278 (0.016, 0.23) | 0.12 | 0.20 [0.18, 0.22] | 0.19 [0.17, 0.23] | 0.34 [0.22, 0.50] | -1.35 | -1.21 [-3.28, 0.83] | -0.11 [-2.68, 2.22] | -22.8 | -74.8 | conformist | no | 0.22 |
| km24 (primary) | 12 | 12.0 | 363 | 0.150 (0.016, 0.23) | 0.14 | 0.26 [0.23, 0.31] | 0.45 [0.31, 0.63] | 0.68 [0.49, 0.81] | -1.57 | -1.43 [-3.29, 0.39] | 0.00 [-1.73, 2.03] | 21.2 | -66.3 | conformist | no | 0.36 |
| km64 | 12 | 12.0 | 331 | 0.024 (0.016, 0.23) | 0.19 | 0.44 [0.38, 0.51] | 0.60 [0.43, 0.79] | 0.78 [0.59, 0.89] | -2.05 | -1.58 [-3.55, 0.20] | 0.25 [-1.69, 3.40] | -60.9 | 84.3 | hubbell | no | 0.53 |
| wd8 | 12 | 12.0 | 376 | 0.278 (0.016, 0.23) | 0.12 | 0.20 [0.18, 0.23] | 0.19 [0.17, 0.23] | 0.34 [0.22, 0.48] | -6.17 | -1.16 [-3.68, 1.16] | 0.01 [-2.55, 2.33] | -18.4 | -39.5 | conformist | no | 0.26 |
| wd24 | 12 | 12.0 | 353 | 0.150 (0.016, 0.23) | 0.15 | 0.26 [0.23, 0.30] | 0.31 [0.25, 0.39] | 0.66 [0.47, 0.81] | -5.96 | -1.41 [-3.05, 0.27] | -0.03 [-1.91, 1.62] | -3.5 | -55.1 | conformist | no | 0.37 |
| wd64 | 12 | 12.0 | 329 | 0.081 (0.016, 0.23) | 0.19 | 0.32 [0.28, 0.38] | 0.61 [0.45, 0.79] | 0.78 [0.64, 0.88] | -4.67 | -1.55 [-3.12, 0.13] | 0.26 [-1.71, 2.92] | -5.1 | 82.5 | hubbell | no | 0.55 |
| art | 12 | 11.9 | 151 | 0.007 (0.016, 0.23) | 0.61 | 0.51 [0.46, 0.59] | 0.80 [0.61, 0.96] | 0.85 [0.75, 0.93] | 2.27 | -1.50 [-4.05, 2.38] | 0.55 [-2.50, 4.21] | -22.5 | 24.5 | hubbell | no | 0.85 |

## Scorecard (period-specific axes)
- **D:** P6 mixed.
- **H:** best per clustering {'ncd': 0, 'hubbell': 2, 'conformist': 4}; reproduced statistics NCD / Hubbell / conformist 2 / 4 / 0 (post hoc).

## Notes
- 2026-10-04: folder created; predictions written before the real-data run.
- 2026-10-04: round 1 run; Result and Verdict filled by `analysis/period_folders.py`.

## Round 1b (2026-10-04)
*Corrected inputs: intention clusters on gte-modernbert `style_resid_period` (`gte_sr`), shared `project_states`, DQ4 work labels. Data: `data/processed/H06-neutral-cooperative-dynamics/r1b/` (`light_r1b.json`, `fit_*`/`round1b_*` JSON).*
- `gte_sr` km24: LLR_NH −4.2, LLR_NC −44.2, all inadequate; singletons 0.74.
- **Work labels:** one dominant shared repo; joint PPC NCD 0.24, Hubbell 0.51, conformist 0.008; μ̂_NCD 0.007 (below μ_B 0.016); λ̄ 0.65 vs NCD 0.55 [0.44, 0.66]; singletons 0.23 vs 0.19; copy-consistency 0.88. The exchangeable models *can* fit when work sits on a shared repo, so the round-1 rejections are not a pipeline artifact. But there is no NCD signature: no interior mode in P_n (P4 failed although μ̂ < μ_B), β̂ = 0 (P2 failed), λ̄ inside both NCD's and Hubbell's ranges (P3 mixed), and Hubbell fits at least as well (LLR_NH +0.5).
