# H13 × G38: Choose a charity and raise as much money as you can for it (2026-04-02 → 04-24)

**Verdict:** mixed
**Role:** exploratory
**Period:** regime III · mode C · 12–14 agents (Opus 4.7 joins 04-17, Kimi K2.6 04-22) · two rooms · 17 days. Split at NE17 (04-14, outreach approval) and NE18 (04-20, history search) into 38a (8 days), 38b (4), 38c (5), as in H01.
**Units analysed:** 38a, 38b, 38c

## Why this period
The longest two-room shared-objective period. Three sub-units give a within-period replication of the family field and of family vs room.

## Prediction
*Written 2026-10-03 23:50 UTC, before running on this period.* The card's P1–P8 (`../README.md`, Prediction) as they apply here:
- In each of 38a, 38b and 38c: P1 T_field > 0 (p < 0.05); P2 retention ≥ 0.5.
- P5/P7-y1: talk b_lab n.s., b_room > b_lab.
- P6: Δ_content n.s.
- P7-y2: b_lab > 0 (p < 0.05); b_room modest (one shared goal; room-specific kickoffs).
- P7-y3: b_room > b_lab.
- P8: 'genuinely' ratio ≥ 2; classification above chance.
- The family field direction should be stable across 38a/38b/38c (descriptive; part of a3).

## Result
Data: `data/processed/H13-family-fields/G38/results_u<unit>.json`; figure: `figures/H13_G38.pdf` (cos(H_i, H_j) heatmap ordered by lab, room in brackets; talk and content K×K mean-field matrices).

**Verdict rule:** see `analysis/period_results.py`. Units detecting a family field (a1 p < 0.05 or room-adjusted y2 b_lab p < 0.05): 38a, 38c of 38a, 38b, 38c. The field never survives the pre-registered style rival (P2) in this period; no-family-coupling predictions (P5, P6) hold in every unit.

**Unit 38a** (8 days, N = 11, families {'Anthropic': 5, 'OpenAI': 4})

| Prediction | Observed | Null | Verdict |
| --- | --- | --- | --- |
| P1 family field (a1) | T = 0.114 ± 0.309; p = 0.1786; R²_fam = 0.21 | perm null -0.001 ± 0.148 | fail |
| P2 survives style residualization (a2) | T = -0.015; p = 0.4301; retention -0.13 | lab permutation | fail |
| (post hoc) S-a′ within-agent style map | T = -0.008; p = 0.382 | lab permutation | descriptive |
| (post hoc) style features alone | T = 0.490; p = 0.007 | lab permutation | descriptive |
| P8 leave-one-out family classification (d1) | accuracy 0.78 (n = 9); p = 0.198 | chance 0.51 | fail |
| P8 'genuinely' (Anthropic vs others, per 1k words) | 0.36 vs 0.03 (ratio 13.2); p = 0.015 | lab permutation | pass |
| P8 lexical profile T_lex | 0.067; p = 0.128 | lab permutation | fail |
| P5 talk K×K: Δ = J_in − J_out (b1) | -0.035 [-0.155, 0.087]; J_in -0.013, J_out 0.022; p = 0.723 | lab permutation; day bootstrap | holds (no family coupling) |
| P6 content co-movement K×K: Δ (b2) | -0.060 ± 0.124; p = 0.575; windows 62 | lab permutation | holds |
| P7 y1 talk: b_lab / b_room | -0.003 (p 0.642) / +0.018 (p 0.016); 55 pairs, 9 same-lab cross-room | node permutations | room > lab |
| P7 y2 content field: b_lab / b_room | +0.181 (p 0.020) / +0.894 (p 0.003); 55 pairs, 9 same-lab cross-room | node permutations | room > lab |
| P7 y3 co-movement: b_lab / b_room | -0.009 (p 0.595) / +0.298 (p 0.005); 51 pairs, 8 same-lab cross-room | node permutations | room > lab |
| P7 y4 lexical: b_lab / b_room | +0.079 (p 0.086) / +0.160 (p 0.011); 55 pairs, 9 same-lab cross-room | node permutations | room > lab |
| (post hoc) y2 after S-a: b_lab / b_room | +0.033 (p 0.323) / +0.635 (p 0.003) | node permutations | descriptive |

Within-unit stationarity (first vs second half of days, family field cos): Anthropic 0.73, OpenAI 0.75

**Unit 38b** (4 days, N = 10, families {'Anthropic': 5, 'OpenAI': 3})

| Prediction | Observed | Null | Verdict |
| --- | --- | --- | --- |
| P1 family field (a1) | T = -0.027 ± 0.309; p = 0.4545; R²_fam = 0.15 | perm null 0.001 ± 0.166 | fail |
| P2 survives style residualization (a2) | T = -0.078; p = 0.7656; retention n/a | lab permutation | fail |
| (post hoc) S-a′ within-agent style map | T = -0.107; p = 0.752 | lab permutation | descriptive |
| (post hoc) style features alone | T = 0.368; p = 0.038 | lab permutation | descriptive |
| P8 leave-one-out family classification (d1) | accuracy 0.62 (n = 8); p = 0.525 | chance 0.52 | fail |
| P8 'genuinely' (Anthropic vs others, per 1k words) | 0.41 vs 0.03 (ratio 14.2); p = 0.120 | lab permutation | fail |
| P8 lexical profile T_lex | 0.051; p = 0.193 | lab permutation | fail |
| P5 talk K×K: Δ = J_in − J_out (b1) | -0.486 [-2.355, -0.104]; J_in -0.332, J_out 0.153; p = 0.985 | lab permutation; day bootstrap | holds (no family coupling) |
| P6 content co-movement K×K: Δ (b2) | -0.001 ± 0.101; p = 0.300; windows 31 | lab permutation | holds |
| P7 y1 talk: b_lab / b_room | -0.035 (p 0.973) / +0.007 (p 0.348); 43 pairs, 8 same-lab cross-room | node permutations | room > lab |
| P7 y2 content field: b_lab / b_room | +0.075 (p 0.195) / +0.887 (p 0.004); 45 pairs, 8 same-lab cross-room | node permutations | room > lab |
| P7 y3 co-movement: b_lab / b_room | +0.045 (p 0.171) / +0.177 (p 0.006); 28 pairs, 5 same-lab cross-room | node permutations | room > lab |
| P7 y4 lexical: b_lab / b_room | +0.091 (p 0.097) / +0.300 (p 0.006); 45 pairs, 8 same-lab cross-room | node permutations | room > lab |
| (post hoc) y2 after S-a: b_lab / b_room | -0.048 (p 0.654) / +0.260 (p 0.032) | node permutations | descriptive |

Within-unit stationarity (first vs second half of days, family field cos): Anthropic 0.31, OpenAI 0.85

**Unit 38c** (5 days, N = 12, families {'Anthropic': 5, 'OpenAI': 4})

| Prediction | Observed | Null | Verdict |
| --- | --- | --- | --- |
| P1 family field (a1) | T = 0.119 ± 0.490; p = 0.1564; R²_fam = 0.22 | perm null 0.001 ± 0.138 | fail |
| P2 survives style residualization (a2) | T = 0.011; p = 0.3751; retention 0.09 | lab permutation | fail |
| (post hoc) S-a′ within-agent style map | T = 0.026; p = 0.323 | lab permutation | descriptive |
| (post hoc) style features alone | T = 0.112; p = 0.215 | lab permutation | descriptive |
| P8 leave-one-out family classification (d1) | accuracy 0.67 (n = 9); p = 0.391 | chance 0.51 | fail |
| P8 'genuinely' (Anthropic vs others, per 1k words) | 0.32 vs 0.03 (ratio 10.0); p = 0.113 | lab permutation | fail |
| P8 lexical profile T_lex | 0.064; p = 0.072 | lab permutation | fail |
| P5 talk K×K: Δ = J_in − J_out (b1) | -0.041 [-0.250, 0.042]; J_in 0.018, J_out 0.058; p = 0.563 | lab permutation; day bootstrap | holds (no family coupling) |
| P6 content co-movement K×K: Δ (b2) | -0.047 ± 0.219; p = 0.614; windows 36 | lab permutation | holds |
| P7 y1 talk: b_lab / b_room | -0.001 (p 0.493) / -0.005 (p 0.562); 55 pairs, 9 same-lab cross-room | node permutations | lab ≥ room |
| P7 y2 content field: b_lab / b_room | +0.138 (p 0.024) / +0.862 (p 0.002); 66 pairs, 9 same-lab cross-room | node permutations | room > lab |
| P7 y3 co-movement: b_lab / b_room | +0.024 (p 0.259) / +0.138 (p 0.003); 34 pairs, 8 same-lab cross-room | node permutations | room > lab |
| P7 y4 lexical: b_lab / b_room | +0.092 (p 0.029) / +0.175 (p 0.002); 66 pairs, 9 same-lab cross-room | node permutations | room > lab |
| (post hoc) y2 after S-a: b_lab / b_room | +0.020 (p 0.354) / +0.400 (p 0.001) | node permutations | descriptive |

Within-unit stationarity (first vs second half of days, family field cos): Anthropic 0.68, OpenAI 0.69

## Scorecard (period-specific axes)
- **C (adequacy):** family field beats the lab-permutation null in 38a, 38c; it does not beat the style rival (S-a) in any unit. Score 1.
- **G (ground truth):** family identity recovered by leave-one-out classification in no unit; rooms recovered as the dominant coupling grouping (38a, 38b, 38c).
- **D, E:** not informed by this period alone (d2/d3 for G51 only).

## Notes
- Data: `data/processed/H13-family-fields/G38/`. Per-period figures: `figures/`.
- 2026-10-04: 2026-04-22 (38c) had only 9 talk-minutes in the whole village (a quiet or broken day); the talk table has 4 of 5 days for 38c.
- 2026-10-04: one Google agent fails eligibility (≥ 2 days with ≥ 3 chat statements) in 38a–c, so K = 2 (Anthropic, OpenAI). a1 is n.s. in all three sub-units, while the room-adjusted y2 b_lab is significant in 38a and 38c (the large room field, b_room ≈ 0.86–0.89, inflates the variance of T_field). Counting y2 b_lab as detection was decided after seeing the data (see the card's deviations); under an a1-only rule this period would be 'failed'.
