# H13 × G36: Interact with other AI agents outside the Village! (2026-03-24 → 03-27 (36b; 03-23, regime II, dropped))

**Verdict:** mixed
**Verdict (1b):** mixed (round 1: mixed; same in both embedding models)
**Verdict (r2):** descriptive (round-2 rules are pooled across units; see the card's Round 2)
**Role:** replication (exploratory)
**Period:** regime III (first days after perma-computer-use, NE14) · mode C · 13 agents · two rooms · 4 days. Split: 03-23 (one regime II day) is dropped because the whitening basis is per regime.
**Units analysed:** 36b

## Why this period
Two-room shared-objective week right after the regime boundary: family vs room, and the first regime III unit for the invariance check.

## Prediction
*Written 2026-10-03 23:50 UTC, before running on this period.* The card's P1–P8 (`../README.md`, Prediction) as they apply here:
- P1: T_field > 0 (p < 0.05). P2: retention ≥ 0.5.
- P5/P7-y1: talk b_lab n.s., b_room ≥ b_lab. H05 found no talk block structure in #36, so b_room may be weak.
- P6: Δ_content n.s.
- P7-y2: b_lab > 0 (p < 0.05); b_room small (shared task, no room-specific goal).
- P7-y3: b_room > b_lab.
- P8: 'genuinely' ratio ≥ 2; T_lex > 0; classification above chance.

## Result
Data: `data/processed/H13-family-fields/G36/results_u<unit>.json`; figure: `figures/H13_G36.pdf` (cos(H_i, H_j) heatmap ordered by lab, room in brackets; talk and content K×K mean-field matrices).

**Verdict rule:** see `analysis/period_results.py`. Units detecting a family field (a1 p < 0.05 or room-adjusted y2 b_lab p < 0.05): 36b of 36b. The field never survives the pre-registered style rival (P2) in this period; no-family-coupling predictions (P5, P6) hold in every unit.

**Unit 36b** (4 days, N = 12, families {'Anthropic': 6, 'OpenAI': 3, 'Google': 2})

| Prediction | Observed | Null | Verdict |
| --- | --- | --- | --- |
| P1 family field (a1) | T = 0.379 ± 0.304; p = 0.0052; R²_fam = 0.43 | perm null 0.002 ± 0.099 | pass |
| P2 survives style residualization (a2) | T = 0.012; p = 0.4055; retention 0.03 | lab permutation | fail |
| (post hoc) S-a′ within-agent style map | T = 0.070; p = 0.145 | lab permutation | descriptive |
| (post hoc) style features alone | T = 0.403; p = 0.016 | lab permutation | descriptive |
| P8 leave-one-out family classification (d1) | accuracy 0.82 (n = 11); p = 0.007 | chance 0.33 | pass |
| P8 'genuinely' (Anthropic vs others, per 1k words) | 0.11 vs 0.10 (ratio 1.1); p = 0.509 | lab permutation | fail |
| P8 lexical profile T_lex | 0.138; p = 0.006 | lab permutation | pass |
| P5 talk K×K: Δ = J_in − J_out (b1) | 0.049 [-0.670, 0.425]; J_in 0.078, J_out 0.028; p = 0.277 | lab permutation; day bootstrap | holds (no family coupling) |
| P6 content co-movement K×K: Δ (b2) | -0.027 ± 0.089; p = 0.616; windows 31 | lab permutation | holds |
| P7 y1 talk: b_lab / b_room | +0.002 (p 0.437) / -0.006 (p 0.613); 45 pairs, 7 same-lab cross-room | node permutations | lab ≥ room |
| P7 y2 content field: b_lab / b_room | +0.430 (p 0.005) / +0.194 (p 0.043); 55 pairs, 12 same-lab cross-room | node permutations | lab ≥ room |
| P7 y3 co-movement: b_lab / b_room | +0.003 (p 0.437) / +0.194 (p 0.002); 51 pairs, 12 same-lab cross-room | node permutations | room > lab |
| P7 y4 lexical: b_lab / b_room | +0.178 (p 0.003) / +0.113 (p 0.008); 55 pairs, 12 same-lab cross-room | node permutations | lab ≥ room |
| (post hoc) y2 after S-a: b_lab / b_room | +0.016 (p 0.378) / +0.123 (p 0.043) | node permutations | descriptive |

Within-unit stationarity (first vs second half of days, family field cos): Anthropic 0.82, OpenAI 0.74, Google 0.57

## Scorecard (period-specific axes)
- **C (adequacy):** family field beats the lab-permutation null in 36b; it does not beat the style rival (S-a) in any unit. Score 1.
- **G (ground truth):** family identity recovered by leave-one-out classification in 36b; rooms recovered as the dominant coupling grouping (36b).
- **D, E:** not informed by this period alone (d2/d3 for G51 only).

## Notes
- Data: `data/processed/H13-family-fields/G36/`. Per-period figures: `figures/`.
- 2026-10-04: 03-23 (the one regime II day of #36) dropped because the whitening basis is per regime; unit 36b = 03-24 → 03-27.

## Round 1b (improved data, 2026-10-04)
*Re-run of the pre-registered statistics on the corrected inputs (card section "Round 1b"). Old numbers are kept above.* Inputs: DQ5 statement vectors (bge and gte-modernbert, regime-whitened, 32-d), H13's own style rival S-a and DQ5's shared `style_resid_period` vectors, DQ5 restatement flags, `activity_bins_fixed` for talk spins, and Jev v3 behavior states (HH267, card Amendment 2). Data: `data/processed/H13-family-fields/r1b/`.

| Unit | T_field round 1 (bge) | T_field gte | S-a own (bge / gte) | shared style_resid_period (bge / gte) | T bge, restatements removed | talk Δ old → fixed table | behavioral T_B |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 36b | 0.379 (p 0.005) | 0.358 (p 0.006) | 0.012 / -0.045 | 0.033 (p 0.292) / -0.007 (p 0.542) | 0.380 | 0.049 (p 0.277) → -0.009 (p 0.522) | 0.169 (p 0.050) |

- **Talk on the corrected table:** family homophily in talk timing (Δ > 0, p < 0.05) in no unit of this period.
- **Reading:** the content field is unchanged in both models and still vanishes under either style rival; the behavioral field is reported in the card (B1–B4).

<!-- r2:start -->
## Round 2 (2026-10-05): graded style rival, read-out family contrast, newcomers
*Pre-registered in the card (Round 2, 03:25 UTC), validated on synthetic skeletons, then run on non-reserved data. The round-2 verdicts are pooled across units; the numbers below are this period's contributions. Code: `analysis/r2_ladder.py`, `r2_readout.py`, `r2_encult.py`; data: `data/processed/H13-family-fields/r2/`.*

| Unit | T raw (bge / gte) | T W3: within-agent style + function words (bge / gte) | T S-a (pooled; style-only null −0.046) | read-out J same / cross lab (bge) | Δ_J^adj [95% CI] | talk Δβ [95% CI] |
| --- | --- | --- | --- | --- | --- | --- |
| 36b | 0.379* / 0.358* | 0.110 / 0.125 | 0.012 | not eligible (< 200 hop-0 rows) | – | -0.0018 [-0.0138, 0.0099] |

* lab-permutation p < 0.05. Pooled (card): W3 keeps 32% (bge) / 47% (gte) of the raw field; the read-out contrast Δ_J^adj = 0.029 [0.010, 0.054] over 8 regime-III units (half of it is lab-level susceptibility and potency, post hoc); talk shows no family contrast.
<!-- r2:end -->
