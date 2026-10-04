# H13 × G40: Connect your worlds into a 3D universe! (2026-05-04 → 05-08)

**Verdict:** mixed
**Role:** exploratory
**Period:** regime III · mode C · 15 agents · one room (#universe-coordination) except GPT-5, alone in #rest · 5 days.
**Units analysed:** 40

## Why this period
The cleanest regime III **one-room** unit before #51: family coupling (b1, b2) without the room confound. GPT-5 is excluded from b1/b2 (it sits alone in another room) but kept in (a) and (d). No (c).

## Prediction
*Written 2026-10-03 23:50 UTC, before running on this period.* The card's P1–P8 (`../README.md`, Prediction) as they apply here:
- P1: T_field > 0 (p < 0.05). P2: retention ≥ 0.5.
- P5: Δ_talk = J_in − J_out n.s. (p ≥ 0.05); enrichment J_in/J_out < 1.3.
- P6: Δ_content n.s.
- P8: 'genuinely' ratio ≥ 2; T_lex > 0; classification above chance.
- Counts against P5/P6: Δ_talk or Δ_content > 0 at p < 0.05.

## Result
Data: `data/processed/H13-family-fields/G40/results_u<unit>.json`; figure: `figures/H13_G40.pdf` (cos(H_i, H_j) heatmap ordered by lab, room in brackets; talk and content K×K mean-field matrices).

**Verdict rule:** see `analysis/period_results.py`. Units detecting a family field (a1 p < 0.05 or room-adjusted y2 b_lab p < 0.05): 40 of 40. The field never survives the pre-registered style rival (P2) in this period; no-family-coupling predictions (P5, P6) hold in every unit.

**Unit 40** (5 days, N = 13, families {'Anthropic': 6, 'OpenAI': 3, 'Google': 2})

| Prediction | Observed | Null | Verdict |
| --- | --- | --- | --- |
| P1 family field (a1) | T = 0.318 ± 0.434; p = 0.0070; R²_fam = 0.48 | perm null 0.000 ± 0.095 | pass |
| P2 survives style residualization (a2) | T = -0.048; p = 0.7435; retention -0.15 | lab permutation | fail |
| (post hoc) S-a′ within-agent style map | T = 0.178; p = 0.043 | lab permutation | descriptive |
| (post hoc) style features alone | T = 0.394; p = 0.002 | lab permutation | descriptive |
| P8 leave-one-out family classification (d1) | accuracy 0.91 (n = 11); p = 0.003 | chance 0.32 | pass |
| P8 'genuinely' (Anthropic vs others, per 1k words) | 0.00 vs 0.02 (ratio 0.0); p = 1.000 | lab permutation | fail |
| P8 lexical profile T_lex | 0.141; p = 0.005 | lab permutation | pass |
| P5 talk K×K: Δ = J_in − J_out (b1) | 0.040 [-0.090, 0.226]; J_in 0.047, J_out 0.007; p = 0.209 | lab permutation; day bootstrap | holds (no family coupling) |
| P6 content co-movement K×K: Δ (b2) | 0.017 ± 0.109; p = 0.146; windows 40 | lab permutation | holds |

Within-unit stationarity (first vs second half of days, family field cos): Anthropic 0.90, OpenAI 0.89, Google 0.43

## Scorecard (period-specific axes)
- **C (adequacy):** family field beats the lab-permutation null in 40; it does not beat the style rival (S-a) in any unit. Score 1.
- **G (ground truth):** family identity recovered by leave-one-out classification in 40; rooms recovered as the dominant coupling grouping (one-room period: n/a).
- **D, E:** not informed by this period alone (d2/d3 for G51 only).

## Notes
- Data: `data/processed/H13-family-fields/G40/`. Per-period figures: `figures/`.
- 2026-10-04: GPT-5 (alone in #rest) excluded from the K×K fits (b1, b2), kept in (a) and (d), as pre-specified.
