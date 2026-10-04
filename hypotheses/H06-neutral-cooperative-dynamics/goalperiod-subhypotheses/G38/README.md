# H06 × G38: Choose a charity and raise as much money as you can for it (2026-04-02 → 2026-04-24)

**Verdict:** mixed (P6 contrast)
**Verdict (1b):** mixed (P6; km24 all inadequate; work: Hubbell adequate, NCD not)
**Role:** exploratory (contrast)
**Period:** regime III · mode C · 12–14 agents · #best/#rest rooms (pooled; the rooms got different instructions) · 17 days × 4 h

## Why this period
Long shared-objective contrast in regime III (H11: herding, βJ_CW +4.3, but a small within-day excess). Pooling the two rooms adds two fields.

## Prediction
*Written 2026-10-04, before running on this period.* The card's rules (`../../README.md`, Prediction, with the amendments made after the synthetic validation and before any real-data run) applied here:
- **P6 (contrast):** LLR_NC ≤ −2 (the conformist rival beats NCD) on intention `km24`, and λ̄ above NCD's 97.5% predictive point. Verdict: supported if both hold, failed if NCD beats the conformist rival by ≥ 2, mixed otherwise. P1–P4 are also reported for comparison.

**Expectation for this period:** **P6:** conformist beats NCD; λ̄ above NCD's 97.5% point. Two rooms with different instructions may instead make projects room-bound (mixed).

## Result
*Run 2026-10-04 (exploratory round 1).* Data: `data/processed/H06-neutral-cooperative-dynamics/G38/round1_G38.json`. Figure: [`figures/pn_G38.pdf`](figures/pn_G38.pdf).

| Prediction | Observed | Null / rival | Verdict |
| --- | --- | --- | --- |
| P6 conformist beats NCD and λ̄ above NCD 97.5% (km24) | LLR_NC -151.4 (≤ −2); λ̄ 0.09 vs NCD 97.5% point 0.21 (not above) | joint PPC p: ncd 0.002, hubbell 0.002, conformist 0.002 | **mixed** |
| For comparison: P1 rule | failed (best per clustering {'ncd': 0, 'hubbell': 0, 'conformist': 6}); P2 mixed; P3 failed (lambda outside NCD 95%) | reproduced NCD / Hubbell / conformist 0 / 1 / 0 | descriptive |
| Independent-agents null | λ̄ 0.09 vs 0.09 (p 0.254); copy-consistency 0.15 vs 0.06 (p 0.005) | | descriptive |
| Artifact labels | LLR_NH 9.0, LLR_NC 20.8; λ̄ 0.32 (NCD 97.5% 0.34); β̂ -3.04 | reproduced 7 / 4 / 5 | mixed |

**All label sets:**

| Label set | N | labelled/win | changes | μ̂_NCD (μ_B, μ_L) | λ̄ obs | λ NCD | λ Hubbell | λ conf. | β̂ obs | β NCD | β Hubbell | LLR_NH | LLR_NC | best | NCD adequate | copy-cons. |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| km8 | 14 | 11.7 | 906 | 0.150 (0.014, 0.21) | 0.09 | 0.25 [0.22, 0.27] | 0.23 [0.20, 0.26] | 0.52 [0.40, 0.62] | -2.11 | -1.43 [-2.49, -0.37] | 0.01 [-1.28, 1.05] | -116.7 | -196.3 | conformist | no | 0.06 |
| km24 (primary) | 14 | 11.7 | 724 | 0.278 (0.014, 0.21) | 0.09 | 0.19 [0.17, 0.21] | 0.42 [0.33, 0.53] | 0.52 [0.35, 0.65] | -5.80 | -1.24 [-2.88, 0.32] | 0.04 [-1.02, 0.97] | -44.6 | -151.4 | conformist | no | 0.15 |
| km64 | 14 | 11.7 | 545 | 0.204 (0.014, 0.21) | 0.10 | 0.22 [0.19, 0.24] | 0.42 [0.30, 0.59] | 0.53 [0.34, 0.70] | -1.60 | -1.33 [-2.74, -0.01] | -0.02 [-1.22, 1.44] | -151.7 | -156.3 | conformist | no | 0.23 |
| wd8 | 14 | 11.7 | 818 | 0.378 (0.014, 0.21) | 0.09 | 0.16 [0.15, 0.17] | 0.23 [0.20, 0.26] | 0.52 [0.36, 0.66] | -3.82 | -1.19 [-3.09, 0.35] | -0.01 [-1.22, 1.00] | 19.5 | -105.8 | conformist | no | 0.07 |
| wd24 | 14 | 11.7 | 624 | 0.278 (0.014, 0.21) | 0.09 | 0.19 [0.17, 0.21] | 0.42 [0.31, 0.56] | 0.53 [0.37, 0.67] | -3.80 | -1.27 [-2.96, 0.12] | 0.00 [-1.22, 1.28] | -119.3 | -148.6 | conformist | no | 0.13 |
| wd64 | 14 | 11.7 | 467 | 0.204 (0.014, 0.21) | 0.10 | 0.22 [0.19, 0.25] | 0.64 [0.44, 0.90] | 0.52 [0.31, 0.69] | -1.53 | -1.38 [-2.88, 0.09] | 0.23 [-1.62, 2.65] | -73.6 | -132.5 | conformist | no | 0.24 |
| art | 14 | 9.8 | 212 | 0.110 (0.014, 0.21) | 0.32 | 0.29 [0.25, 0.34] | 0.42 [0.30, 0.58] | 0.52 [0.28, 0.72] | -3.04 | -1.48 [-3.06, 0.13] | 0.05 [-1.56, 1.69] | 9.0 | 20.8 | ncd | no | 0.61 |

## Scorecard (period-specific axes)
- **D:** P6 mixed.
- **H:** best per clustering {'ncd': 0, 'hubbell': 0, 'conformist': 6}; reproduced statistics NCD / Hubbell / conformist 0 / 1 / 0 (post hoc).

## Notes
- 2026-10-04: folder created; predictions written before the real-data run.
- 2026-10-04: round 1 run; Result and Verdict filled by `analysis/period_folders.py`.

## Round 1b (2026-10-04)
*Corrected inputs: intention clusters on gte-modernbert `style_resid_period` (`gte_sr`), shared `project_states`, DQ4 work labels. Data: `data/processed/H06-neutral-cooperative-dynamics/r1b/` (`light_r1b.json`, `fit_*`/`round1b_*` JSON).*
- `gte_sr` km24: LLR_NH −140.3, LLR_NC −144.0 (round 1 LLR_NC −151), joint PPC 0.002 for all three; singletons 0.93 (0.94), λ̄ 0.094 vs NCD 0.41 [0.35, 0.48]; copy-consistency 0.14 (null 0.07). P6 stays mixed (conformist ≫ NCD, λ̄ below NCD).
- **Work labels:** testable (52 changes); joint PPC NCD 0.007, Hubbell 0.047, conformist 0.002; λ̄ 0.46 vs NCD 0.41 [0.35, 0.48]; singletons 0.52; β̂ −4.7.
