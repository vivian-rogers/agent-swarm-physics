# H13 × G44: Finetune your leader! (2026-05-26 → 05-29)

**Verdict:** failed
**Verdict (1b):** failed (round 1: failed; same in both embedding models)
**Verdict (r2):** descriptive (round-2 rules are pooled across units; see the card's Round 2)
**Role:** replication (exploratory)
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

## Round 1b (improved data, 2026-10-04)
*Re-run of the pre-registered statistics on the corrected inputs (card section "Round 1b"). Old numbers are kept above.* Inputs: DQ5 statement vectors (bge and gte-modernbert, regime-whitened, 32-d), H13's own style rival S-a and DQ5's shared `style_resid_period` vectors, DQ5 restatement flags, `activity_bins_fixed` for talk spins, and Jev v3 behavior states (HH267, card Amendment 2). Data: `data/processed/H13-family-fields/r1b/`.

| Unit | T_field round 1 (bge) | T_field gte | S-a own (bge / gte) | shared style_resid_period (bge / gte) | T bge, restatements removed | talk Δ old → fixed table | behavioral T_B |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 44 | 0.065 (p 0.185) | 0.049 (p 0.241) | 0.051 / 0.018 | 0.054 (p 0.219) / 0.020 (p 0.328) | 0.063 | -0.008 (p 0.501) → -0.011 (p 0.514) | 0.114 (p 0.057) |

- **Talk on the corrected table:** family homophily in talk timing (Δ > 0, p < 0.05) in no unit of this period.
- **Reading:** the content field is unchanged in both models and still vanishes under either style rival; the behavioral field is reported in the card (B1–B4).

<!-- r2:start -->
## Round 2 (2026-10-05): graded style rival, read-out family contrast, newcomers
*Pre-registered in the card (Round 2, 03:25 UTC), validated on synthetic skeletons, then run on non-reserved data. The round-2 verdicts are pooled across units; the numbers below are this period's contributions. Code: `analysis/r2_ladder.py`, `r2_readout.py`, `r2_encult.py`; data: `data/processed/H13-family-fields/r2/`.*

| Unit | T raw (bge / gte) | T W3: within-agent style + function words (bge / gte) | T S-a (pooled; style-only null −0.046) | read-out J same / cross lab (bge) | Δ_J^adj [95% CI] | talk Δβ [95% CI] |
| --- | --- | --- | --- | --- | --- | --- |
| 44 | 0.065 / 0.049 | 0.091 / 0.084 | 0.051 | 0.074 / -0.009 | 0.046 [-0.079, 0.163] | -0.0004 [-0.0114, 0.0043] |

* lab-permutation p < 0.05. Pooled (card): W3 keeps 32% (bge) / 47% (gte) of the raw field; the read-out contrast Δ_J^adj = 0.029 [0.010, 0.054] over 8 regime-III units (half of it is lab-level susceptibility and potency, post hoc); talk shows no family contrast.

**Newcomers joining in this period (R2-B; lab alignment a(d), bge raw, 5-statement means):**
- Claude Opus 4.8 (Anthropic): a(d) = -0.67, -0.74; room outsiderness r(d) = 0.06, 0.06
<!-- r2:end -->
