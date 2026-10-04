# H13 × G42: Run your own Youtube channel! (2026-05-18 → 05-22)

**Verdict:** mixed
**Verdict (1b):** mixed (round 1: mixed; same in both embedding models)
**Role:** exploratory
**Period:** regime III · mode I · 15–16 agents (Gemini 3.5 Flash joins 05-20) · two rooms · 5 days.
**Units analysed:** 42

## Why this period
Individual-objective two-room week. Google has 3 agents here, the most of any pre-#51 unit.

## Prediction
*Written 2026-10-03 23:50 UTC, before running on this period.* The card's P1–P8 (`../README.md`, Prediction) as they apply here:
- P1: T_field > 0 (p < 0.05). P2: retention ≥ 0.5.
- P5/P7-y1: talk b_lab n.s.
- P6: Δ_content n.s.
- P7-y2: b_lab > 0 (p < 0.05). P7-y3: b_room ≥ b_lab.
- P8: 'genuinely' ratio ≥ 2; classification above chance.

## Result
Data: `data/processed/H13-family-fields/G42/results_u<unit>.json`; figure: `figures/H13_G42.pdf` (cos(H_i, H_j) heatmap ordered by lab, room in brackets; talk and content K×K mean-field matrices).

**Verdict rule:** see `analysis/period_results.py`. Units detecting a family field (a1 p < 0.05 or room-adjusted y2 b_lab p < 0.05): 42 of 42. The field never survives the pre-registered style rival (P2) in this period; no-family-coupling predictions (P5, P6) hold in every unit.

**Unit 42** (5 days, N = 14, families {'Anthropic': 6, 'OpenAI': 4, 'Google': 2})

| Prediction | Observed | Null | Verdict |
| --- | --- | --- | --- |
| P1 family field (a1) | T = 0.220 ± 0.384; p = 0.0088; R²_fam = 0.36 | perm null -0.001 ± 0.074 | pass |
| P2 survives style residualization (a2) | T = 0.064; p = 0.1794; retention 0.29 | lab permutation | fail |
| (post hoc) S-a′ within-agent style map | T = 0.215; p = 0.022 | lab permutation | descriptive |
| (post hoc) style features alone | T = 0.279; p = 0.007 | lab permutation | descriptive |
| P8 leave-one-out family classification (d1) | accuracy 0.83 (n = 12); p = 0.001 | chance 0.33 | pass |
| P8 'genuinely' (Anthropic vs others, per 1k words) | 0.79 vs 0.14 (ratio 5.5); p = 0.003 | lab permutation | pass |
| P8 lexical profile T_lex | 0.130; p = 0.003 | lab permutation | pass |
| P5 talk K×K: Δ = J_in − J_out (b1) | -0.307 [-0.368, 0.166]; J_in -0.045, J_out 0.262; p = 0.904 | lab permutation; day bootstrap | holds (no family coupling) |
| P6 content co-movement K×K: Δ (b2) | -0.033 ± 0.131; p = 0.500; windows 40 | lab permutation | holds |
| P7 y1 talk: b_lab / b_room | -0.010 (p 0.740) / +0.007 (p 0.269); 90 pairs, 8 same-lab cross-room | node permutations | room > lab |
| P7 y2 content field: b_lab / b_room | +0.163 (p 0.017) / +0.326 (p 0.000); 91 pairs, 8 same-lab cross-room | node permutations | room > lab |
| P7 y3 co-movement: b_lab / b_room | -0.035 (p 0.830) / +0.066 (p 0.026); 63 pairs, 6 same-lab cross-room | node permutations | room > lab |
| P7 y4 lexical: b_lab / b_room | +0.099 (p 0.017) / +0.081 (p 0.019); 91 pairs, 8 same-lab cross-room | node permutations | lab ≥ room |
| (post hoc) y2 after S-a: b_lab / b_room | -0.000 (p 0.479) / +0.371 (p 0.000) | node permutations | descriptive |

Within-unit stationarity (first vs second half of days, family field cos): Anthropic 0.58, OpenAI 0.80, Google 0.68

## Scorecard (period-specific axes)
- **C (adequacy):** family field beats the lab-permutation null in 42; it does not beat the style rival (S-a) in any unit. Score 1.
- **G (ground truth):** family identity recovered by leave-one-out classification in 42; rooms recovered as the dominant coupling grouping (42).
- **D, E:** not informed by this period alone (d2/d3 for G51 only).

## Notes
- Data: `data/processed/H13-family-fields/G42/`. Per-period figures: `figures/`.

## Round 1b (improved data, 2026-10-04)
*Re-run of the pre-registered statistics on the corrected inputs (card section "Round 1b"). Old numbers are kept above.* Inputs: DQ5 statement vectors (bge and gte-modernbert, regime-whitened, 32-d), H13's own style rival S-a and DQ5's shared `style_resid_period` vectors, DQ5 restatement flags, `activity_bins_fixed` for talk spins, and Jev v3 behavior states (HH267, card Amendment 2). Data: `data/processed/H13-family-fields/r1b/`.

| Unit | T_field round 1 (bge) | T_field gte | S-a own (bge / gte) | shared style_resid_period (bge / gte) | T bge, restatements removed | talk Δ old → fixed table | behavioral T_B |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 42 | 0.220 (p 0.009) | 0.189 (p 0.037) | 0.064 / 0.029 | 0.066 (p 0.177) / 0.035 (p 0.283) | 0.224 | -0.307 (p 0.904) → -0.056 (p 0.772) | 0.091 (p 0.113) |

- **Talk on the corrected table:** family homophily in talk timing (Δ > 0, p < 0.05) in no unit of this period.
- **Reading:** the content field is unchanged in both models and still vanishes under either style rival; the behavioral field is reported in the card (B1–B4).
