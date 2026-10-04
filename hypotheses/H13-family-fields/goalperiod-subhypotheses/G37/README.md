# H13 × G37: Pick your own goal! (2026-03-30 → 04-01)

**Verdict:** failed
**Verdict (1b):** failed (round 1: failed; same in both embedding models)
**Role:** exploratory
**Period:** regime III · mode F (free) · 10 eligible agents (Anthropic 5, OpenAI 3, Google 1, DeepSeek 1) · two rooms · 3 days.
**Units analysed:** 37

## Why this period
A free week: with no imposed goal, a family's prior should show most clearly. Expected the largest T_field of the regime III units, descriptively. K = 2 multi-member labs (Google has one agent).

## Prediction
*Written 2026-10-03 23:50 UTC, before running on this period.* The card's P1–P8 (`../README.md`, Prediction) as they apply here:
- P1: T_field > 0 (p < 0.05), expected among the largest of all units.
- P2: retention ≥ 0.5.
- P5/P7-y1: talk b_lab n.s.
- P6: Δ_content n.s.
- P7-y2: b_lab > 0; b_room small (no room-specific goal). P7-y3: b_room > b_lab.
- P8: 'genuinely' ratio ≥ 2; classification above chance (only 2 classes, so chance = 0.5 among multi-member labs).
- Low power: 3 days and 10 agents. A null here counts against P1 only through the count rule.

## Result
Data: `data/processed/H13-family-fields/G37/results_u<unit>.json`; figure: `figures/H13_G37.pdf` (cos(H_i, H_j) heatmap ordered by lab, room in brackets; talk and content K×K mean-field matrices).

**Verdict rule:** see `analysis/period_results.py`. Units detecting a family field (a1 p < 0.05 or room-adjusted y2 b_lab p < 0.05): none of 37. The field never survives the pre-registered style rival (P2) in this period; no-family-coupling predictions (P5, P6) hold in every unit.

**Unit 37** (3 days, N = 10, families {'Anthropic': 5, 'OpenAI': 3})

| Prediction | Observed | Null | Verdict |
| --- | --- | --- | --- |
| P1 family field (a1) | T = -0.078 ± 0.157; p = 0.7838; R²_fam = 0.10 | perm null -0.000 ± 0.099 | fail |
| P2 survives style residualization (a2) | T = 0.029; p = 0.3097; retention n/a | lab permutation | fail |
| (post hoc) S-a′ within-agent style map | T = 0.024; p = 0.334 | lab permutation | descriptive |
| (post hoc) style features alone | T = 0.262; p = 0.044 | lab permutation | descriptive |
| P8 leave-one-out family classification (d1) | accuracy 0.25 (n = 8); p = 0.903 | chance 0.52 | fail |
| P8 'genuinely' (Anthropic vs others, per 1k words) | 0.81 vs 0.15 (ratio 5.3); p = 0.028 | lab permutation | pass |
| P8 lexical profile T_lex | 0.106; p = 0.059 | lab permutation | fail |
| P5 talk K×K: Δ = J_in − J_out (b1) | -0.029 [-0.034, 0.209]; J_in 0.110, J_out 0.140; p = 0.407 | lab permutation; day bootstrap | holds (no family coupling) |
| P6 content co-movement K×K: Δ (b2) | -0.655 ± 453958.718; p = 0.746; windows 20 | lab permutation | holds |
| P7 y1 talk: b_lab / b_room | +0.003 (p 0.452) / +0.089 (p 0.023); 42 pairs, 5 same-lab cross-room | node permutations | room > lab |
| P7 y2 content field: b_lab / b_room | -0.080 (p 0.836) / +0.349 (p 0.008); 45 pairs, 6 same-lab cross-room | node permutations | room > lab |
| P7 y3 co-movement: b_lab / b_room | +0.024 (p 0.312) / +0.299 (p 0.011); 24 pairs, 3 same-lab cross-room | node permutations | room > lab |
| P7 y4 lexical: b_lab / b_room | +0.106 (p 0.068) / +0.046 (p 0.213); 45 pairs, 6 same-lab cross-room | node permutations | lab ≥ room |
| (post hoc) y2 after S-a: b_lab / b_room | +0.029 (p 0.326) / +0.043 (p 0.235) | node permutations | descriptive |

## Scorecard (period-specific axes)
- **C:** 0 (no family field beyond the permutation null).
- **G (ground truth):** family identity recovered by leave-one-out classification in no unit; rooms recovered as the dominant coupling grouping (37).
- **D, E:** not informed by this period alone (d2/d3 for G51 only).

## Notes
- Data: `data/processed/H13-family-fields/G37/`. Per-period figures: `figures/`.
- 2026-10-04: K = 2 (Google has one eligible agent); 3 days, 10 agents: the lowest-power unit (synthetic F1 power 0.24 at a 10% family share). Content Δ = −0.66 comes from a near-singular mean-field inversion: 20 windows, loop gain 1.36, and a leave-one-agent-out jackknife SE that explodes. It is not interpretable, and the RE summary gives it ~0 weight. The raw within − across pair contrast is −0.045 (p = 0.71).

## Round 1b (improved data, 2026-10-04)
*Re-run of the pre-registered statistics on the corrected inputs (card section "Round 1b"). Old numbers are kept above.* Inputs: DQ5 statement vectors (bge and gte-modernbert, regime-whitened, 32-d), H13's own style rival S-a and DQ5's shared `style_resid_period` vectors, DQ5 restatement flags, `activity_bins_fixed` for talk spins, and Jev v3 behavior states (HH267, card Amendment 2). Data: `data/processed/H13-family-fields/r1b/`.

| Unit | T_field round 1 (bge) | T_field gte | S-a own (bge / gte) | shared style_resid_period (bge / gte) | T bge, restatements removed | talk Δ old → fixed table | behavioral T_B |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 37 | -0.078 (p 0.784) | -0.044 (p 0.568) | 0.029 / 0.048 | 0.031 (p 0.300) / 0.056 (p 0.231) | -0.078 | -0.029 (p 0.407) → 0.053 (p 0.200) | 0.089 (p 0.141) |

- **Talk on the corrected table:** family homophily in talk timing (Δ > 0, p < 0.05) in no unit of this period.
- **Reading:** the content field is unchanged in both models and still vanishes under either style rival; the behavioral field is reported in the card (B1–B4).
