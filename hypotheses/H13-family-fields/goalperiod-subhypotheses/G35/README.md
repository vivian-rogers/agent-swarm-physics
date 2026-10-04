# H13 × G35: Test your game to make it as fun and functional as you can! (2026-03-16 → 03-20)

**Verdict:** mixed
**Verdict (1b):** mixed (round 1: mixed; same in both embedding models; native: mixed)
**Role:** exploratory (round 1); native (round 1b: room × lab crossed, behavior channel)
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

## Native test (round 1b): room × lab crossed in the behavior channel
*Written 2026-10-04 07:13 UTC, before computing any behavioral statistic on #35.* Design facts seen: round 1's content results above (field lab ≥ room; co-movement room > lab), and the room × lab cross-tab (#best holds one agent from each of OpenAI, Anthropic and Google).

- **Why native.** #35 is the one period where the operator split the village into two rooms with lab crossed by design and both rooms doing the *same kind of task* (evolving forks of one RPG). So a room field in behavior should be small, and family and room separate cleanly. If families live in behavior (HH267), lab should organize behavior across rooms while style-free words carry no family term.
- **Observable.** H_i^B (card Amendment 2) over the 5 days; pair outcome y_B = cos(H_i^B, H_j^B). Pair OLS y = c + b_lab·same_lab + b_room·same_room (H13's `famroom`, node permutations 2,000 each). Same for style-residualized content (shared `style_resid_period`, bge and gte) as the word-channel comparison.
- **Prediction.** Behavior: b_lab > 0 at p < 0.05 and b_lab > b_room (credence 0.45: 45 pairs, 6 same-lab cross-room pairs). Style-residualized content: b_lab n.s. (credence 0.7), b_room > 0 (credence 0.6).
- **Counts against HH267:** behavioral b_lab ≤ 0 or n.s. while round 1's raw content b_lab stays significant.

**Native result** (run after the prediction; `analysis/r1b_behavior.py`, `r1b/behavior.json` → `native_G35`; 12 agents with behavior fields, 36 pairs, 5 same-lab cross-room pairs):

| Prediction | Observed | Verdict |
| --- | --- | --- |
| Behavior: b_lab > 0 at p < 0.05 and b_lab > b_room | b_lab = +0.125 (node-permutation p 0.21), b_room = −0.046 (p 0.57); behavioral T_B = 0.125 (p 0.11), leave-one-out 0.55 (p 0.17) | **fail** (direction as predicted, not significant) |
| Style-free words: b_lab n.s. | +0.024 (p 0.35) bge; +0.055 (p 0.26) gte | pass |
| Style-free words: b_room > 0 | +0.214 (p 0.018) bge; +0.235 (p 0.009) gte | pass |

**Native verdict: mixed.** Once style is removed, words in #35 follow rooms (the forks) and carry no family term; behavior leans the other way (family, not room) but is not significant with 5 same-lab cross-room pairs. Across all ten two-room units the behavioral family term is clearer: random-effects b_lab = 0.14 [0.06, 0.22] vs b_room = 0.03 [−0.05, 0.11] (lab > room in 7/10; card, Round 1b).

## Scorecard (period-specific axes)
- **C (adequacy):** family field beats the lab-permutation null in 35; it does not beat the style rival (S-a) in any unit. Score 1.
- **G (ground truth):** family identity recovered by leave-one-out classification in 35; rooms recovered as the dominant coupling grouping (35).
- **D, E:** not informed by this period alone (d2/d3 for G51 only).

## Notes
- Data: `data/processed/H13-family-fields/G35/`. Per-period figures: `figures/`.

## Round 1b (improved data, 2026-10-04)
*Re-run of the pre-registered statistics on the corrected inputs (card section "Round 1b"). Old numbers are kept above.* Inputs: DQ5 statement vectors (bge and gte-modernbert, regime-whitened, 32-d), H13's own style rival S-a and DQ5's shared `style_resid_period` vectors, DQ5 restatement flags, `activity_bins_fixed` for talk spins, and Jev v3 behavior states (HH267, card Amendment 2). Data: `data/processed/H13-family-fields/r1b/`.

| Unit | T_field round 1 (bge) | T_field gte | S-a own (bge / gte) | shared style_resid_period (bge / gte) | T bge, restatements removed | talk Δ old → fixed table | behavioral T_B |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 35 | 0.323 (p 0.000) | 0.347 (p 0.001) | 0.058 / 0.061 | 0.058 (p 0.158) / 0.061 (p 0.154) | 0.327 | 0.029 (p 0.240) → 0.023 (p 0.184) | 0.125 (p 0.108) |

- **Talk on the corrected table:** family homophily in talk timing (Δ > 0, p < 0.05) in no unit of this period.
- **Reading:** the content field is unchanged in both models and still vanishes under either style rival; the behavioral field is reported in the card (B1–B4).
