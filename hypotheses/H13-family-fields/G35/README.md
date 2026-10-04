# H13 × G35: Test your game to make it as fun and functional as you can! (2026-03-16 → 03-20)

**Verdict:** mixed
**Role:** exploratory
**Period:** regime II · mode C · 13 agents · two rooms (#best: GPT-5.4, Opus 4.6, Gemini 3.1 Pro; #rest: the other 10) · 5 days.
**Units analysed:** 35

## Why this period
First two-room period: lab and room are crossed by design (#best holds one agent per big lab). The rooms evolved separate forks of one RPG (NE15), so a strong room field is expected in content. Regime II basis, so it is outside the invariance check (a3), a4 and d2.

## Prediction
*Written 2026-10-03 23:50 UTC, before running on this period.* The card's P1–P8 (`../README.md`, Prediction) as they apply here:
- P1: T_field > 0, lab-permutation p < 0.05.
- P2: survives style residualization with retention ≥ 0.5.
- P5/P7-y1 (talk): room dominates: b_room > b_lab, b_lab n.s. H05 found within-room talk coupling > cross-room here, so b_room should be > 0.
- P6: Δ_content not significant.
- P7-y2 (content field): b_lab > 0 at p < 0.05 (family persists across rooms), with a large b_room (separate forks).
- P7-y3 (content co-movement): b_room > b_lab.
- P8: Anthropic 'genuinely' rate ≥ 2× others; T_lex > 0; leave-one-out classification above chance.
- Counts against: b_lab (y2) ≤ 0 or n.s.; b_lab (y1) > b_room.

## Result
Data: `data/processed/H13-family-fields/G35/results_u<unit>.json`; figure: `figures/H13_G35.pdf` (cos(H_i, H_j) heatmap ordered by lab, room in brackets; talk and content K×K mean-field matrices).

**Verdict rule:** see `analysis/period_results.py`. Units detecting a family field (a1 p < 0.05 or room-adjusted y2 b_lab p < 0.05): 35 of 35. The field never survives the pre-registered style rival (P2) in this period; no-family-coupling predictions (P5, P6) hold in every unit.

**Unit 35** (5 days, N = 13, families {'Anthropic': 6, 'OpenAI': 4, 'Google': 2})

| Prediction | Observed | Null | Verdict |
| --- | --- | --- | --- |
| P1 family field (a1) | T = 0.323 ± 0.229; p = 0.0004; R²_fam = 0.36 | perm null 0.000 ± 0.063 | pass |
| P2 survives style residualization (a2) | T = 0.058; p = 0.1566; retention 0.18 | lab permutation | fail |
| (post hoc) S-a′ within-agent style map | T = 0.235; p = 0.001 | lab permutation | descriptive |
| (post hoc) style features alone | T = 0.264; p = 0.000 | lab permutation | descriptive |
| P8 leave-one-out family classification (d1) | accuracy 0.92 (n = 12); p = 0.000 | chance 0.34 | pass |
| P8 'genuinely' (Anthropic vs others, per 1k words) | 0.02 vs 0.04 (ratio 0.4); p = 0.800 | lab permutation | fail |
| P8 lexical profile T_lex | 0.337; p = 0.000 | lab permutation | pass |
| P5 talk K×K: Δ = J_in − J_out (b1) | 0.029 [-0.056, 0.130]; J_in 0.062, J_out 0.033; p = 0.240 | lab permutation; day bootstrap | holds (no family coupling) |
| P6 content co-movement K×K: Δ (b2) | -0.028 ± 0.151; p = 0.487; windows 40 | lab permutation | holds |
| P7 y1 talk: b_lab / b_room | -0.007 (p 0.680) / +0.024 (p 0.018); 36 pairs, 5 same-lab cross-room | node permutations | room > lab |
| P7 y2 content field: b_lab / b_room | +0.311 (p 0.000) / +0.245 (p 0.009); 45 pairs, 6 same-lab cross-room | node permutations | lab ≥ room |
| P7 y3 co-movement: b_lab / b_room | -0.004 (p 0.469) / +0.309 (p 0.006); 36 pairs, 5 same-lab cross-room | node permutations | room > lab |
| P7 y4 lexical: b_lab / b_room | +0.336 (p 0.002) / +0.046 (p 0.156); 45 pairs, 6 same-lab cross-room | node permutations | lab ≥ room |
| (post hoc) y2 after S-a: b_lab / b_room | +0.066 (p 0.145) / +0.167 (p 0.008) | node permutations | descriptive |

Within-unit stationarity (first vs second half of days, family field cos): Anthropic 0.74, OpenAI 0.85, Google 0.54

## Scorecard (period-specific axes)
- **C (adequacy):** family field beats the lab-permutation null in 35; it does not beat the style rival (S-a) in any unit. Score 1.
- **G (ground truth):** family identity recovered by leave-one-out classification in 35; rooms recovered as the dominant coupling grouping (35).
- **D, E:** not informed by this period alone (d2/d3 for G51 only).

## Notes
- Data: `data/processed/H13-family-fields/G35/`. Per-period figures: `figures/`.
