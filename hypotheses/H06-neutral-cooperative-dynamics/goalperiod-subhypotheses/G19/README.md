# H06 × G19: Create a popular daily puzzle game like Wordle (2025-11-03 → 2025-11-14)

**Verdict:** mixed (P6 contrast)
**Verdict (1b):** mixed (P6 unchanged; all models inadequate)
**Role:** exploratory (contrast)
**Period:** regime I · mode C (shared objective) · 8 agents · 1 room · 10 days × 4 h

## Why this period
Shared-objective contrast with a clear consensus (H11: the build repo held ≈ 0.6 share from the start, βJ_CW +2.8).

## Prediction
*Written 2026-10-04, before running on this period.* The card's rules (`../../README.md`, Prediction, with the amendments made after the synthetic validation and before any real-data run) applied here:
- **P6 (contrast):** LLR_NC ≤ −2 (the conformist rival beats NCD) on intention `km24`, and λ̄ above NCD's 97.5% predictive point. Verdict: supported if both hold, failed if NCD beats the conformist rival by ≥ 2, mixed otherwise. P1–P4 are also reported for comparison.

**Expectation for this period:** **P6:** the conformist rival beats NCD (LLR_NC ≤ −2) on intention clusters, and λ̄ is above NCD's 97.5% point (a goal field concentrates effort).

## Result
*Run 2026-10-04 (exploratory round 1).* Data: `data/processed/H06-neutral-cooperative-dynamics/G19/round1_G19.json`. Figure: [`figures/pn_G19.pdf`](figures/pn_G19.pdf).

| Prediction | Observed | Null / rival | Verdict |
| --- | --- | --- | --- |
| P6 conformist beats NCD and λ̄ above NCD 97.5% (km24) | LLR_NC -29.4 (≤ −2); λ̄ 0.25 vs NCD 97.5% point 0.48 (not above) | joint PPC p: ncd 0.002, hubbell 0.002, conformist 0.002 | **mixed** |
| For comparison: P1 rule | failed (best per clustering {'ncd': 0, 'hubbell': 4, 'conformist': 2}); P2 failed (no negative frequency dependence); P3 failed (lambda outside NCD 95%) | reproduced NCD / Hubbell / conformist 0 / 1 / 1 | descriptive |
| Independent-agents null | λ̄ 0.25 vs 0.18 (p 0.005); copy-consistency 0.34 vs 0.17 (p 0.005) | | descriptive |
| Artifact labels | LLR_NH -19.6, LLR_NC -15.3; λ̄ 0.64 (NCD 97.5% 0.62); β̂ -2.03 | reproduced 3 / 8 / 6 | failed |

**All label sets:**

| Label set | N | labelled/win | changes | μ̂_NCD (μ_B, μ_L) | λ̄ obs | λ NCD | λ Hubbell | λ conf. | β̂ obs | β NCD | β Hubbell | LLR_NH | LLR_NC | best | NCD adequate | copy-cons. |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| km8 | 8 | 6.7 | 322 | 0.204 (0.019, 0.28) | 0.22 | 0.33 [0.30, 0.37] | 0.43 [0.36, 0.51] | 0.57 [0.45, 0.68] | -1.32 | -1.29 [-3.23, 0.90] | -0.01 [-1.94, 2.08] | -14.9 | -39.0 | conformist | no | 0.22 |
| km24 (primary) | 8 | 6.7 | 278 | 0.081 (0.019, 0.28) | 0.25 | 0.43 [0.39, 0.48] | 0.58 [0.48, 0.71] | 0.70 [0.57, 0.82] | 1.47 | -1.48 [-3.17, 0.27] | 0.11 [-2.12, 2.94] | -42.0 | -29.4 | hubbell | no | 0.34 |
| km64 | 8 | 6.7 | 248 | 0.024 (0.019, 0.28) | 0.30 | 0.54 [0.48, 0.64] | 0.59 [0.46, 0.74] | 0.69 [0.54, 0.82] | -0.84 | -1.40 [-3.55, 1.64] | 0.18 [-1.67, 3.01] | -76.9 | -33.9 | hubbell | no | 0.50 |
| wd8 | 8 | 6.7 | 315 | 0.204 (0.019, 0.28) | 0.22 | 0.33 [0.29, 0.37] | 0.43 [0.36, 0.50] | 0.57 [0.46, 0.68] | 0.55 | -1.30 [-3.38, 0.81] | 0.09 [-1.93, 1.90] | -5.6 | -35.3 | conformist | no | 0.20 |
| wd24 | 8 | 6.7 | 273 | 0.081 (0.019, 0.28) | 0.28 | 0.43 [0.39, 0.49] | 0.57 [0.47, 0.71] | 0.69 [0.55, 0.81] | 3.06 | -1.38 [-2.89, 0.20] | 0.19 [-2.06, 3.21] | -65.8 | -51.2 | hubbell | no | 0.36 |
| wd64 | 8 | 6.7 | 237 | 0.059 (0.019, 0.28) | 0.33 | 0.46 [0.40, 0.53] | 0.58 [0.46, 0.71] | 0.70 [0.56, 0.81] | -0.54 | -1.45 [-3.33, 0.51] | 0.17 [-1.86, 3.04] | -17.8 | 24.8 | hubbell | no | 0.51 |
| art | 8 | 5.8 | 123 | 0.032 (0.019, 0.28) | 0.64 | 0.54 [0.48, 0.62] | 0.59 [0.50, 0.70] | 0.70 [0.59, 0.80] | -2.03 | -1.48 [-3.86, 0.87] | 0.16 [-2.08, 3.45] | -19.6 | -15.3 | hubbell | no | 0.82 |

## Scorecard (period-specific axes)
- **D:** P6 mixed.
- **H:** best per clustering {'ncd': 0, 'hubbell': 4, 'conformist': 2}; reproduced statistics NCD / Hubbell / conformist 0 / 1 / 1 (post hoc).

## Notes
- 2026-10-04: folder created; predictions written before the real-data run.
- 2026-10-04: round 1 run; Result and Verdict filled by `analysis/period_folders.py`.

## Round 1b (2026-10-04)
*Corrected inputs: intention clusters on gte-modernbert `style_resid_period` (`gte_sr`), shared `project_states`, DQ4 work labels. Data: `data/processed/H06-neutral-cooperative-dynamics/r1b/` (`light_r1b.json`, `fit_*`/`round1b_*` JSON).*
- `gte_sr` km24 only: LLR_NH −53.0, LLR_NC −30.8; joint PPC 0.002 for all; singletons 0.76 (0.77); λ̄ 0.27 vs NCD 0.46. Work labels: none (regime I).
