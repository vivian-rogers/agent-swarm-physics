# H06 × G25: Create a digital museum of 2025 (2025-12-29 → 2026-01-02)

**Verdict:** mixed (P6 contrast)
**Verdict (1b):** failed (P6: conformist no longer beats NCD)
**Role:** replication (exploratory (contrast))
**Period:** regime I · mode C · 10 agents · 1 room · 5 days × 4 h

## Why this period
Shared-objective contrast with divisible subtasks (H11: herding, βJ_CW +4.1).

## Prediction
*Written 2026-10-04, before running on this period.* The card's rules (`../../README.md`, Prediction, with the amendments made after the synthetic validation and before any real-data run) applied here:
- **P6 (contrast):** LLR_NC ≤ −2 (the conformist rival beats NCD) on intention `km24`, and λ̄ above NCD's 97.5% predictive point. Verdict: supported if both hold, failed if NCD beats the conformist rival by ≥ 2, mixed otherwise. P1–P4 are also reported for comparison.

**Expectation for this period:** **P6:** conformist beats NCD; λ̄ above NCD's 97.5% point.

## Result
*Run 2026-10-04 (exploratory round 1).* Data: `data/processed/H06-neutral-cooperative-dynamics/G25/round1_G25.json`. Figure: [`figures/pn_G25.pdf`](figures/pn_G25.pdf).

| Prediction | Observed | Null / rival | Verdict |
| --- | --- | --- | --- |
| P6 conformist beats NCD and λ̄ above NCD 97.5% (km24) | LLR_NC -30.2 (≤ −2); λ̄ 0.20 vs NCD 97.5% point 0.51 (not above) | joint PPC p: ncd 0.003, hubbell 0.002, conformist 0.002 | **mixed** |
| For comparison: P1 rule | failed (best per clustering {'ncd': 0, 'hubbell': 3, 'conformist': 3}); P2 supported; P3 failed (lambda outside NCD 95%) | reproduced NCD / Hubbell / conformist 3 / 1 / 0 | descriptive |
| Independent-agents null | λ̄ 0.20 vs 0.16 (p 0.005); copy-consistency 0.45 vs 0.35 (p 0.010) | | descriptive |
| Artifact labels | LLR_NH -4.3, LLR_NC -0.7; λ̄ 0.49 (NCD 97.5% 0.56); β̂ 1.98 | reproduced 8 / 9 / 8 | failed |

**All label sets:**

| Label set | N | labelled/win | changes | μ̂_NCD (μ_B, μ_L) | λ̄ obs | λ NCD | λ Hubbell | λ conf. | β̂ obs | β NCD | β Hubbell | LLR_NH | LLR_NC | best | NCD adequate | copy-cons. |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| km8 | 10 | 9.5 | 240 | 0.150 (0.017, 0.25) | 0.17 | 0.30 [0.26, 0.35] | 0.23 [0.19, 0.29] | 0.55 [0.34, 0.74] | -0.17 | -1.38 [-3.28, 0.57] | 0.00 [-2.52, 2.51] | 1.6 | -6.2 | conformist | no | 0.31 |
| km24 (primary) | 10 | 9.5 | 214 | 0.044 (0.017, 0.25) | 0.20 | 0.43 [0.36, 0.51] | 0.51 [0.35, 0.72] | 0.67 [0.43, 0.82] | -0.52 | -1.54 [-3.57, 0.73] | 0.16 [-1.87, 3.03] | -52.9 | -30.2 | hubbell | no | 0.45 |
| km64 | 10 | 9.5 | 173 | 0.044 (0.017, 0.25) | 0.35 | 0.43 [0.36, 0.53] | 0.66 [0.46, 0.89] | 0.68 [0.48, 0.84] | -1.60 | -1.52 [-3.54, 0.95] | 0.45 [-2.53, 4.32] | -15.5 | 21.7 | hubbell | no | 0.62 |
| wd8 | 10 | 9.5 | 228 | 0.278 (0.017, 0.25) | 0.15 | 0.23 [0.20, 0.27] | 0.50 [0.36, 0.70] | 0.54 [0.35, 0.75] | 0.83 | -1.21 [-3.61, 1.23] | 0.10 [-1.97, 2.81] | 2.4 | -32.7 | conformist | no | 0.26 |
| wd24 | 10 | 9.5 | 203 | 0.044 (0.017, 0.25) | 0.21 | 0.43 [0.36, 0.52] | 0.51 [0.36, 0.72] | 0.67 [0.44, 0.85] | 1.78 | -1.47 [-3.63, 0.85] | 0.19 [-1.85, 2.92] | -29.3 | -31.9 | conformist | no | 0.38 |
| wd64 | 10 | 9.5 | 171 | 0.081 (0.017, 0.25) | 0.31 | 0.37 [0.32, 0.43] | 0.66 [0.44, 0.90] | 0.68 [0.46, 0.83] | -0.41 | -1.44 [-3.20, 0.34] | 0.58 [-2.00, 4.38] | -12.8 | 12.6 | hubbell | no | 0.67 |
| art | 10 | 6.2 | 45 | 0.059 (0.017, 0.25) | 0.49 | 0.46 [0.38, 0.56] | 0.43 [0.33, 0.60] | 0.71 [0.48, 0.88] | 1.98 | -1.48 [-4.50, 1.94] | 0.14 [-3.05, 4.28] | -4.3 | -0.7 | hubbell | no | 0.90 |

## Scorecard (period-specific axes)
- **D:** P6 mixed.
- **H:** best per clustering {'ncd': 0, 'hubbell': 3, 'conformist': 3}; reproduced statistics NCD / Hubbell / conformist 3 / 1 / 0 (post hoc).

## Notes
- 2026-10-04: folder created; predictions written before the real-data run.
- 2026-10-04: round 1 run; Result and Verdict filled by `analysis/period_folders.py`.

## Round 1b (2026-10-04)
*Corrected inputs: intention clusters on gte-modernbert `style_resid_period` (`gte_sr`), shared `project_states`, DQ4 work labels. Data: `data/processed/H06-neutral-cooperative-dynamics/r1b/` (`light_r1b.json`, `fit_*`/`round1b_*` JSON).*
- `gte_sr` km24 only: LLR_NH +5.7, LLR_NC +0.9 (round 1 LLR_NC −30); joint PPC 0.002 for all; singletons 0.70 (0.74); λ̄ 0.24 vs NCD 0.33 [0.28, 0.39].
