# H13 × G41: Perform novel research! (2026-05-11 → 05-15)

**Verdict:** mixed
**Verdict (1b):** mixed (round 1: mixed; same in both embedding models)
**Role:** replication (exploratory)
**Period:** regime III · mode I · 15 agents · two rooms · 5 days.
**Units analysed:** 41

## Why this period
The rooms converged on different research topics (#rest: multi-agent coordination; #best: AI-judge bias). A strong room field in content, crossed with family.

## Prediction
*Written 2026-10-03 23:50 UTC, before running on this period.* The card's P1–P8 (`../README.md`, Prediction) as they apply here:
- P1: T_field > 0 (p < 0.05). P2: retention ≥ 0.5.
- P5/P7-y1: talk b_lab n.s., b_room > b_lab (H05: talk block structure passes here).
- P6: Δ_content n.s.
- P7-y2: b_lab > 0 (p < 0.05) **despite** a large b_room (room topics).
- P7-y3: b_room > b_lab.
- P8: 'genuinely' ratio ≥ 2; classification above chance.

## Result
Data: `data/processed/H13-family-fields/G41/results_u<unit>.json`; figure: `figures/H13_G41.pdf` (cos(H_i, H_j) heatmap ordered by lab, room in brackets; talk and content K×K mean-field matrices).

**Verdict rule:** see `analysis/period_results.py`. Units detecting a family field (a1 p < 0.05 or room-adjusted y2 b_lab p < 0.05): 41 of 41. The field never survives the pre-registered style rival (P2) in this period; no-family-coupling predictions (P5, P6) hold in every unit.

**Unit 41** (5 days, N = 14, families {'Anthropic': 6, 'OpenAI': 4, 'Google': 2})

| Prediction | Observed | Null | Verdict |
| --- | --- | --- | --- |
| P1 family field (a1) | T = 0.278 ± 0.421; p = 0.0108; R²_fam = 0.35 | perm null 0.002 ± 0.088 | pass |
| P2 survives style residualization (a2) | T = -0.089; p = 0.9058; retention -0.32 | lab permutation | fail |
| (post hoc) S-a′ within-agent style map | T = 0.032; p = 0.298 | lab permutation | descriptive |
| (post hoc) style features alone | T = 0.483; p = 0.002 | lab permutation | descriptive |
| P8 leave-one-out family classification (d1) | accuracy 0.67 (n = 12); p = 0.058 | chance 0.32 | fail |
| P8 'genuinely' (Anthropic vs others, per 1k words) | 0.15 vs 0.17 (ratio 0.9); p = 0.547 | lab permutation | fail |
| P8 lexical profile T_lex | 0.108; p = 0.030 | lab permutation | pass |
| P5 talk K×K: Δ = J_in − J_out (b1) | 0.002 [-0.087, 0.053]; J_in 0.030, J_out 0.028; p = 0.407 | lab permutation; day bootstrap | holds (no family coupling) |
| P6 content co-movement K×K: Δ (b2) | 0.032 ± 0.132; p = 0.068; windows 40 | lab permutation | holds |
| P7 y1 talk: b_lab / b_room | +0.000 (p 0.476) / +0.016 (p 0.035); 91 pairs, 9 same-lab cross-room | node permutations | room > lab |
| P7 y2 content field: b_lab / b_room | +0.259 (p 0.003) / +0.471 (p 0.001); 91 pairs, 9 same-lab cross-room | node permutations | room > lab |
| P7 y3 co-movement: b_lab / b_room | +0.053 (p 0.051) / +0.268 (p 0.003); 86 pairs, 9 same-lab cross-room | node permutations | room > lab |
| P7 y4 lexical: b_lab / b_room | +0.104 (p 0.032) / +0.123 (p 0.009); 91 pairs, 9 same-lab cross-room | node permutations | room > lab |
| (post hoc) y2 after S-a: b_lab / b_room | -0.109 (p 0.965) / +0.480 (p 0.000) | node permutations | descriptive |

Within-unit stationarity (first vs second half of days, family field cos): Anthropic 0.39, OpenAI 0.70, Google 0.47

## Scorecard (period-specific axes)
- **C (adequacy):** family field beats the lab-permutation null in 41; it does not beat the style rival (S-a) in any unit. Score 1.
- **G (ground truth):** family identity recovered by leave-one-out classification in no unit; rooms recovered as the dominant coupling grouping (41).
- **D, E:** not informed by this period alone (d2/d3 for G51 only).

## Notes
- Data: `data/processed/H13-family-fields/G41/`. Per-period figures: `figures/`.

## Round 1b (improved data, 2026-10-04)
*Re-run of the pre-registered statistics on the corrected inputs (card section "Round 1b"). Old numbers are kept above.* Inputs: DQ5 statement vectors (bge and gte-modernbert, regime-whitened, 32-d), H13's own style rival S-a and DQ5's shared `style_resid_period` vectors, DQ5 restatement flags, `activity_bins_fixed` for talk spins, and Jev v3 behavior states (HH267, card Amendment 2). Data: `data/processed/H13-family-fields/r1b/`.

| Unit | T_field round 1 (bge) | T_field gte | S-a own (bge / gte) | shared style_resid_period (bge / gte) | T bge, restatements removed | talk Δ old → fixed table | behavioral T_B |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 41 | 0.278 (p 0.011) | 0.259 (p 0.019) | -0.089 / -0.086 | -0.084 (p 0.887) / -0.078 (p 0.826) | 0.254 | 0.002 (p 0.407) → 0.001 (p 0.431) | 0.097 (p 0.102) |

- **Talk on the corrected table:** family homophily in talk timing (Δ > 0, p < 0.05) in no unit of this period.
- **Reading:** the content field is unchanged in both models and still vanishes under either style rival; the behavioral field is reported in the card (B1–B4).
