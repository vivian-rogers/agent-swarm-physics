# H13 × G39: Build your own interactive world! (2026-04-27 → 05-01)

**Verdict:** mixed
**Role:** exploratory
**Period:** regime III · mode I · 15 agents · two rooms, reshuffled 04-27 · 5 days.
**Units analysed:** 39

## Why this period
Individual-objective week: each agent builds its own world, so position differences come from priors rather than a shared task. Family vs room with a new room partition.

## Prediction
*Written 2026-10-03 23:50 UTC, before running on this period.* The card's P1–P8 (`../README.md`, Prediction) as they apply here:
- P1: T_field > 0 (p < 0.05). P2: retention ≥ 0.5.
- P5/P7-y1: talk b_lab n.s. H05 found no talk block structure in #39, so b_room may be weak too.
- P6: Δ_content n.s.
- P7-y2: b_lab > 0 (p < 0.05); b_room small. P7-y3: b_room ≥ b_lab.
- P8: 'genuinely' ratio ≥ 2; classification above chance.

## Result
Data: `data/processed/H13-family-fields/G39/results_u<unit>.json`; figure: `figures/H13_G39.pdf` (cos(H_i, H_j) heatmap ordered by lab, room in brackets; talk and content K×K mean-field matrices).

**Verdict rule:** see `analysis/period_results.py`. Units detecting a family field (a1 p < 0.05 or room-adjusted y2 b_lab p < 0.05): 39 of 39. The field never survives the pre-registered style rival (P2) in this period; no-family-coupling predictions (P5, P6) are violated in at least one unit (see table).

**Unit 39** (5 days, N = 12, families {'Anthropic': 6, 'OpenAI': 4})

| Prediction | Observed | Null | Verdict |
| --- | --- | --- | --- |
| P1 family field (a1) | T = 0.173 ± 0.388; p = 0.0400; R²_fam = 0.24 | perm null -0.001 ± 0.079 | pass |
| P2 survives style residualization (a2) | T = -0.125; p = 0.9936; retention -0.72 | lab permutation | fail |
| (post hoc) S-a′ within-agent style map | T = 0.062; p = 0.193 | lab permutation | descriptive |
| (post hoc) style features alone | T = 0.253; p = 0.028 | lab permutation | descriptive |
| P8 leave-one-out family classification (d1) | accuracy 0.90 (n = 10); p = 0.038 | chance 0.51 | pass |
| P8 'genuinely' (Anthropic vs others, per 1k words) | 0.11 vs 0.00 (ratio n/a); p = 0.172 | lab permutation | fail |
| P8 lexical profile T_lex | 0.139; p = 0.004 | lab permutation | pass |
| P5 talk K×K: Δ = J_in − J_out (b1) | -0.119 [-0.435, 0.104]; J_in -0.014, J_out 0.105; p = 0.767 | lab permutation; day bootstrap | holds (no family coupling) |
| P6 content co-movement K×K: Δ (b2) | 0.081 ± 0.078; p = 0.030; windows 31 | lab permutation | violated |
| P7 y1 talk: b_lab / b_room | -0.014 (p 0.839) / +0.047 (p 0.003); 66 pairs, 8 same-lab cross-room | node permutations | room > lab |
| P7 y2 content field: b_lab / b_room | +0.171 (p 0.043) / +0.037 (p 0.235); 66 pairs, 8 same-lab cross-room | node permutations | lab ≥ room |
| P7 y3 co-movement: b_lab / b_room | +0.109 (p 0.030) / +0.101 (p 0.022); 30 pairs, 1 same-lab cross-room | node permutations | lab ≥ room |
| P7 y4 lexical: b_lab / b_room | +0.136 (p 0.013) / -0.020 (p 0.668); 66 pairs, 8 same-lab cross-room | node permutations | lab ≥ room |
| (post hoc) y2 after S-a: b_lab / b_room | -0.126 (p 0.991) / +0.009 (p 0.377) | node permutations | descriptive |

Within-unit stationarity (first vs second half of days, family field cos): Anthropic 0.76, OpenAI 0.74

## Scorecard (period-specific axes)
- **C (adequacy):** family field beats the lab-permutation null in 39; it does not beat the style rival (S-a) in any unit. Score 1.
- **G (ground truth):** family identity recovered by leave-one-out classification in 39; rooms recovered as the dominant coupling grouping (39).
- **D, E:** not informed by this period alone (d2/d3 for G51 only).

## Notes
- Data: `data/processed/H13-family-fields/G39/`. Per-period figures: `figures/`.
