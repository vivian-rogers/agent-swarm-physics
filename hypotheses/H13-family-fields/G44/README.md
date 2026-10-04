# H13 × G44: Finetune your leader! (2026-05-26 → 05-29)

**Verdict:** failed
**Role:** exploratory
**Period:** regime III · mode D/C · 16–18 agents (Opus 4.8 and the temporary Fine-tuned Leader join) · two rooms with different tasks (#best fine-tunes a Kimi leader; #rest picks creative work) · 4 days. The fine-tuned leader is its own lab label ('Fine-tuned (Kimi)').
**Units analysed:** 44

## Why this period
The strongest room-specific task split in the data: a hard test of whether family identity survives a large room field (P7-y2).

## Prediction
*Written 2026-10-03 23:50 UTC, before running on this period.* The card's P1–P8 (`../README.md`, Prediction) as they apply here:
- P1: T_field > 0 (p < 0.05). P2: retention ≥ 0.5.
- P5/P7-y1: talk b_lab n.s., b_room > b_lab.
- P6: Δ_content n.s.
- P7-y2: b_lab > 0 (p < 0.05) with the largest b_room of all units.
- P7-y3: b_room > b_lab.
- P8: 'genuinely' ratio ≥ 2; classification above chance.

## Result
Data: `data/processed/H13-family-fields/G44/results_u<unit>.json`; figure: `figures/H13_G44.pdf` (cos(H_i, H_j) heatmap ordered by lab, room in brackets; talk and content K×K mean-field matrices).

**Verdict rule:** see `analysis/period_results.py`. Units detecting a family field (a1 p < 0.05 or room-adjusted y2 b_lab p < 0.05): none of 44. The field never survives the pre-registered style rival (P2) in this period; no-family-coupling predictions (P5, P6) hold in every unit.

**Unit 44** (4 days, N = 16, families {'Anthropic': 7, 'OpenAI': 4, 'Google': 2})

| Prediction | Observed | Null | Verdict |
| --- | --- | --- | --- |
| P1 family field (a1) | T = 0.065 ± 0.426; p = 0.1850; R²_fam = 0.19 | perm null 0.000 ± 0.091 | fail |
| P2 survives style residualization (a2) | T = 0.051; p = 0.2252; retention 0.79 | lab permutation | fail |
| (post hoc) S-a′ within-agent style map | T = 0.091; p = 0.142 | lab permutation | descriptive |
| (post hoc) style features alone | T = 0.169; p = 0.038 | lab permutation | descriptive |
| P8 leave-one-out family classification (d1) | accuracy 0.62 (n = 13); p = 0.085 | chance 0.32 | fail |
| P8 'genuinely' (Anthropic vs others, per 1k words) | 0.24 vs 0.16 (ratio 1.5); p = 0.313 | lab permutation | fail |
| P8 lexical profile T_lex | 0.051; p = 0.105 | lab permutation | fail |
| P5 talk K×K: Δ = J_in − J_out (b1) | -0.008 [-0.081, 0.179]; J_in 0.001, J_out 0.009; p = 0.501 | lab permutation; day bootstrap | holds (no family coupling) |
| P6 content co-movement K×K: Δ (b2) | -0.028 ± 0.127; p = 0.343; windows 32 | lab permutation | holds |
| P7 y1 talk: b_lab / b_room | +0.003 (p 0.387) / +0.006 (p 0.225); 120 pairs, 14 same-lab cross-room | node permutations | room > lab |
| P7 y2 content field: b_lab / b_room | +0.065 (p 0.166) / +0.715 (p 0.000); 120 pairs, 14 same-lab cross-room | node permutations | room > lab |
| P7 y3 co-movement: b_lab / b_room | +0.005 (p 0.423) / +0.264 (p 0.000); 88 pairs, 12 same-lab cross-room | node permutations | room > lab |
| P7 y4 lexical: b_lab / b_room | +0.051 (p 0.079) / +0.129 (p 0.003); 120 pairs, 14 same-lab cross-room | node permutations | room > lab |
| (post hoc) y2 after S-a: b_lab / b_room | +0.051 (p 0.210) / +0.657 (p 0.001) | node permutations | descriptive |

Within-unit stationarity (first vs second half of days, family field cos): Anthropic 0.84, OpenAI 0.82, Google 0.69

## Scorecard (period-specific axes)
- **C:** 0 (no family field beyond the permutation null).
- **G (ground truth):** family identity recovered by leave-one-out classification in no unit; rooms recovered as the dominant coupling grouping (44).
- **D, E:** not informed by this period alone (d2/d3 for G51 only).

## Notes
- Data: `data/processed/H13-family-fields/G44/`. Per-period figures: `figures/`.
- 2026-10-04: the 'Fine-tuned (Kimi)' agent is its own lab label (a singleton).
