# H13 × G51: Each agent: Maximize your assigned goal! (2026-07-06 → 09-04 (non-holdout part; the tail 09-07 → 09-18 is held out))

**Verdict:** mixed
**Verdict (1b):** mixed (round 1: mixed; same in both embedding models)
**Verdict (r2):** descriptive (round-2 rules are pooled across units; see the card's Round 2)
**Role:** replication (exploratory)
**Period:** regime III · mode I/K (private assigned roles, NE26) · 21 → 32 agents, 8 h/day · essentially one room (#general). Split as in H01: 51a 07-06 → 07-08; 51b 07-09 → 08-04 (NE32 triplet onboarding; joins); 51c 08-05 → 08-24 (#focus: Gemini 2.5 Pro and Opus 4.8 in a side room, excluded from b in 51c); 51d 08-25 → 09-02; 51e 09-03 → 09-04 (NE33 batch join; 2 days, descriptive only).
**Units analysed:** 51a, 51b, 51c, 51d, 51e

## Why this period
The most families (K = 5: Anthropic, OpenAI, Google, Moonshot, DeepSeek; Zhipu from 08-28) and the most data, in one room: the best test of the K×K family coupling matrix (b) without a room confound, of newcomer classification (d2) and of the NE32 isolated triplet (d3). Assigned roles are agent-specific fields; pairs sharing a role are dropped from the family statistics. One same-role pair is same-family (the YouTubers GPT-5.2 and GPT-5.6 Terra).

## Prediction
*Written 2026-10-03 23:50 UTC, before running on this period.* The card's P1–P8 (`../README.md`, Prediction) as they apply here:
- In each of 51a–51d: P1 T_field > 0 (p < 0.05); P2 retention ≥ 0.5.
- P4: T' > 0 in at least some sub-units.
- P5: Δ_talk n.s. (p ≥ 0.05) in ≥ 2/3 of 51a–51d; enrichment < 1.3.
- P6: Δ_content n.s. in ≥ 1/2.
- P8: 'genuinely' ratio ≥ 2; T_lex > 0; leave-one-out classification above chance.
- If P3 passes: newcomers classified into their own family at ≥ 60%.
- d3 (descriptive): on 07-09 the triplet aligns more with the OpenAI field than with other families' fields.
- Agent-specific role fields add variance, so per-unit power is lower than the N suggests.

## Result
Data: `data/processed/H13-family-fields/G51/results_u<unit>.json`; figure: `figures/H13_G51.pdf` (cos(H_i, H_j) heatmap ordered by lab, room in brackets; talk and content K×K mean-field matrices).

**Verdict rule:** see `analysis/period_results.py`. Units detecting a family field (a1 p < 0.05 or room-adjusted y2 b_lab p < 0.05): 51a, 51b, 51c of 51a, 51b, 51c, 51d. The field never survives the pre-registered style rival (P2) in this period; no-family-coupling predictions (P5, P6) are violated in at least one unit (see table).

**Unit 51a** (3 days, N = 21, families {'Anthropic': 9, 'OpenAI': 5, 'Google': 3, 'DeepSeek': 2})

| Prediction | Observed | Null | Verdict |
| --- | --- | --- | --- |
| P1 family field (a1) | T = 0.055 ± 0.143; p = 0.0466; R²_fam = 0.22 | perm null -0.000 ± 0.030 | pass |
| P2 survives style residualization (a2) | T = 0.024; p = 0.2080; retention 0.43 | lab permutation | fail |
| (post hoc) S-a′ within-agent style map | T = 0.042; p = 0.103 | lab permutation | descriptive |
| (post hoc) style features alone | T = 0.228; p = 0.001 | lab permutation | descriptive |
| P8 leave-one-out family classification (d1) | accuracy 0.42 (n = 19); p = 0.107 | chance 0.24 | fail |
| P8 'genuinely' (Anthropic vs others, per 1k words) | 0.20 vs 0.14 (ratio 1.5); p = 0.256 | lab permutation | fail |
| P8 lexical profile T_lex | 0.066; p = 0.017 | lab permutation | pass |
| P5 talk K×K: Δ = J_in − J_out (b1) | 0.084 [0.071, 0.104]; J_in 0.089, J_out 0.005; p = 0.005 | lab permutation; day bootstrap | violated (family coupling) |
| P6 content co-movement K×K: Δ (b2) | -0.005 ± 0.034; p = 0.400; windows 48 | lab permutation | holds |

**Unit 51b** (19 days, N = 27, families {'Anthropic': 10, 'OpenAI': 8, 'Google': 3, 'DeepSeek': 2, 'Moonshot': 2})

| Prediction | Observed | Null | Verdict |
| --- | --- | --- | --- |
| P1 family field (a1) | T = 0.069 ± 0.091; p = 0.0094; R²_fam = 0.22 | perm null 0.001 ± 0.024 | pass |
| P2 survives style residualization (a2) | T = -0.008; p = 0.6113; retention -0.12 | lab permutation | fail |
| (post hoc) S-a′ within-agent style map | T = 0.029; p = 0.104 | lab permutation | descriptive |
| (post hoc) style features alone | T = 0.290; p = 0.000 | lab permutation | descriptive |
| P8 leave-one-out family classification (d1) | accuracy 0.40 (n = 25); p = 0.034 | chance 0.19 | pass |
| P8 'genuinely' (Anthropic vs others, per 1k words) | 0.29 vs 0.17 (ratio 1.7); p = 0.131 | lab permutation | fail |
| P8 lexical profile T_lex | 0.125; p = 0.000 | lab permutation | pass |
| P5 talk K×K: Δ = J_in − J_out (b1) | 0.026 [-0.103, 0.097]; J_in 0.133, J_out 0.107; p = 0.230 | lab permutation; day bootstrap | holds (no family coupling) |
| P6 content co-movement K×K: Δ (b2) | -0.002 ± 0.031; p = 0.287; windows 301 | lab permutation | holds |

Within-unit stationarity (first vs second half of days, family field cos): Anthropic 0.65, OpenAI 0.83, Google 0.89, DeepSeek 0.90, Moonshot 0.79

**Unit 51c** (14 days, N = 27, families {'Anthropic': 10, 'OpenAI': 8, 'Google': 3, 'DeepSeek': 2, 'Moonshot': 2})

| Prediction | Observed | Null | Verdict |
| --- | --- | --- | --- |
| P1 family field (a1) | T = 0.090 ± 0.105; p = 0.0020; R²_fam = 0.22 | perm null 0.000 ± 0.025 | pass |
| P2 survives style residualization (a2) | T = 0.041; p = 0.0554; retention 0.45 | lab permutation | fail |
| (post hoc) S-a′ within-agent style map | T = 0.066; p = 0.010 | lab permutation | descriptive |
| (post hoc) style features alone | T = 0.231; p = 0.000 | lab permutation | descriptive |
| P8 leave-one-out family classification (d1) | accuracy 0.48 (n = 25); p = 0.008 | chance 0.19 | pass |
| P8 'genuinely' (Anthropic vs others, per 1k words) | 0.37 vs 0.35 (ratio 1.0); p = 0.401 | lab permutation | fail |
| P8 lexical profile T_lex | 0.096; p = 0.001 | lab permutation | pass |
| P5 talk K×K: Δ = J_in − J_out (b1) | -0.010 [-0.078, 0.086]; J_in 0.030, J_out 0.040; p = 0.511 | lab permutation; day bootstrap | holds (no family coupling) |
| P6 content co-movement K×K: Δ (b2) | -0.001 ± 0.053; p = 0.174; windows 216 | lab permutation | holds |

Within-unit stationarity (first vs second half of days, family field cos): Anthropic 0.70, OpenAI 0.86, Google 0.83, DeepSeek 0.73, Moonshot 0.54

**Unit 51d** (7 days, N = 26, families {'Anthropic': 8, 'OpenAI': 8, 'Google': 3, 'DeepSeek': 2, 'Moonshot': 2})

| Prediction | Observed | Null | Verdict |
| --- | --- | --- | --- |
| P1 family field (a1) | T = 0.006 ± 0.096; p = 0.3793; R²_fam = 0.18 | perm null -0.000 ± 0.028 | fail |
| P2 survives style residualization (a2) | T = -0.030; p = 0.8560; retention -4.91 | lab permutation | fail |
| (post hoc) S-a′ within-agent style map | T = -0.007; p = 0.573 | lab permutation | descriptive |
| (post hoc) style features alone | T = 0.212; p = 0.004 | lab permutation | descriptive |
| P8 leave-one-out family classification (d1) | accuracy 0.26 (n = 23); p = 0.307 | chance 0.19 | fail |
| P8 'genuinely' (Anthropic vs others, per 1k words) | 0.16 vs 0.05 (ratio 3.1); p = 0.078 | lab permutation | fail |
| P8 lexical profile T_lex | 0.009; p = 0.328 | lab permutation | fail |
| P5 talk K×K: Δ = J_in − J_out (b1) | -0.053 [-0.161, 0.104]; J_in -0.045, J_out 0.007; p = 0.683 | lab permutation; day bootstrap | holds (no family coupling) |
| P6 content co-movement K×K: Δ (b2) | -0.008 ± 0.047; p = 0.404; windows 111 | lab permutation | holds |

Within-unit stationarity (first vs second half of days, family field cos): Anthropic 0.38, OpenAI 0.60, Google 0.68, DeepSeek 0.57, Moonshot 0.58

**Unit 51e** (2 days, N = 24, families {'Anthropic': 7, 'OpenAI': 6, 'Google': 3, 'DeepSeek': 2, 'Moonshot': 2}; descriptive only)

| Prediction | Observed | Null | Verdict |
| --- | --- | --- | --- |
| P1 family field (a1) | T = 0.012 ± 0.093; p = 0.3413; R²_fam = 0.24 | perm null -0.000 ± 0.034 | fail |
| P2 survives style residualization (a2) | T = -0.029; p = 0.7896; retention -2.47 | lab permutation | fail |
| (post hoc) S-a′ within-agent style map | T = 0.008; p = 0.394 | lab permutation | descriptive |
| (post hoc) style features alone | T = 0.218; p = 0.001 | lab permutation | descriptive |
| P8 leave-one-out family classification (d1) | accuracy 0.35 (n = 20); p = 0.115 | chance 0.19 | fail |
| P8 'genuinely' (Anthropic vs others, per 1k words) | 0.31 vs 0.06 (ratio 5.2); p = 0.035 | lab permutation | pass |
| P8 lexical profile T_lex | 0.052; p = 0.042 | lab permutation | pass |
| P5 talk K×K: Δ = J_in − J_out (b1) | -0.116 [-0.138, -0.088]; J_in -0.068, J_out 0.047; p = 0.859 | lab permutation; day bootstrap | holds (no family coupling) |
| P6 content co-movement K×K: Δ (b2) | -0.049 ± 0.132; p = 0.761; windows 32 | lab permutation | holds |

**d3 (NE32, 07-09, descriptive):** cosine of each isolated GPT-5.6 agent's day-demeaned 07-09 vector with incumbent family fields of 51b (07-09/07-10 excluded): GPT-5.6 Sol: Google 0.45, OpenAI -0.08, Anthropic 0.23; GPT-5.6 Terra: Google 0.23, OpenAI 0.12, Anthropic -0.14; GPT-5.6 Luna: Google -0.06, OpenAI 0.33, Anthropic -0.29. Triplet mutual cos 0.33 vs triplet–incumbent -0.06; statements on 07-09: {'GPT-5.6 Sol': 4, 'GPT-5.6 Terra': 8, 'GPT-5.6 Luna': 72}. Only Luna (72 statements) aligns with the OpenAI field; Sol (4) and Terra (8) are noise-dominated.

**d2 newcomers (counted, since P3 passed):** 4/11 classified into their own family by earlier units' family fields (chance 0.14, binomial p = 0.062; mean rank 3.1). Correct: GPT-5.6 Terra, GPT-5.6 Luna, Kimi K3, Gemini 3.8 Flash. Wrong: Claude Fable 5 → Google, Claude Sonnet 5 → Fine-tuned (Kimi), DeepSeek-V4-Pro → Anthropic, GPT-5.6 Sol → Moonshot, Claude Opus 5 → OpenAI, GLM-5.3 Flash → Fine-tuned (Kimi), Claude Fable 5.1 → Zhipu.

## Scorecard (period-specific axes)
- **C (adequacy):** family field beats the lab-permutation null in 51a, 51b, 51c; it does not beat the style rival (S-a) in any unit. Score 1.
- **G (ground truth):** family identity recovered by leave-one-out classification in 51b, 51c; rooms recovered as the dominant coupling grouping (one-room period: n/a).
- **D, E:** not informed by this period alone (d2/d3 for G51 only).

## Notes
- Data: `data/processed/H13-family-fields/G51/`. Per-period figures: `figures/`.
- 2026-10-04: in 51c the #focus pair (Gemini 2.5 Pro, Opus 4.8) is excluded from the K×K fits, as pre-specified. Same-role pairs are dropped from the family statistics.
- 2026-10-04: 51a is the one unit where talk timing shows family coupling (Δ = 0.084, p = 0.005; J_in 0.089 vs J_out 0.005). Not replicated in 51b–51d; 1 of 5 one-room units is at the expected false-positive rate for 5 tests.
- 2026-10-04: 51e (2 days, NE33 batch join) is descriptive only.

## Round 1b (improved data, 2026-10-04)
*Re-run of the pre-registered statistics on the corrected inputs (card section "Round 1b"). Old numbers are kept above.* Inputs: DQ5 statement vectors (bge and gte-modernbert, regime-whitened, 32-d), H13's own style rival S-a and DQ5's shared `style_resid_period` vectors, DQ5 restatement flags, `activity_bins_fixed` for talk spins, and Jev v3 behavior states (HH267, card Amendment 2). Data: `data/processed/H13-family-fields/r1b/`.

| Unit | T_field round 1 (bge) | T_field gte | S-a own (bge / gte) | shared style_resid_period (bge / gte) | T bge, restatements removed | talk Δ old → fixed table | behavioral T_B |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 51a | 0.055 (p 0.047) | 0.047 (p 0.076) | 0.024 / 0.016 | 0.012 (p 0.330) / 0.010 (p 0.359) | 0.056 | 0.084 (p 0.005) → 0.080 (p 0.008) | 0.107 (p 0.052) |
| 51b | 0.069 (p 0.009) | 0.084 (p 0.002) | -0.008 / 0.000 | 0.005 (p 0.399) / 0.014 (p 0.261) | 0.069 | 0.026 (p 0.230) → 0.019 (p 0.176) | 0.038 (p 0.192) |
| 51c | 0.090 (p 0.002) | 0.072 (p 0.007) | 0.041 / 0.034 | 0.057 (p 0.017) / 0.039 (p 0.065) | 0.096 | -0.010 (p 0.511) → 0.009 (p 0.327) | 0.025 (p 0.263) |
| 51d | 0.006 (p 0.379) | 0.048 (p 0.064) | -0.030 / 0.007 | -0.018 (p 0.725) / 0.022 (p 0.199) | 0.007 | -0.053 (p 0.683) → -0.026 (p 0.536) | 0.028 (p 0.213) |
| 51e | 0.012 (p 0.341) | -0.013 (p 0.643) | -0.029 / -0.019 | -0.004 (p 0.508) / -0.009 (p 0.605) | 0.005 | -0.116 (p 0.859) → -0.209 (p 0.983) | 0.042 (p 0.134) |

- **Talk on the corrected table:** family homophily in talk timing (Δ > 0, p < 0.05) in 51a of this period.
- **Reading:** the content field is unchanged in both models and still vanishes under either style rival; the behavioral field is reported in the card (B1–B4).

<!-- r2:start -->
## Round 2 (2026-10-05): graded style rival, read-out family contrast, newcomers
*Pre-registered in the card (Round 2, 03:25 UTC), validated on synthetic skeletons, then run on non-reserved data. The round-2 verdicts are pooled across units; the numbers below are this period's contributions. Code: `analysis/r2_ladder.py`, `r2_readout.py`, `r2_encult.py`; data: `data/processed/H13-family-fields/r2/`.*

| Unit | T raw (bge / gte) | T W3: within-agent style + function words (bge / gte) | T S-a (pooled; style-only null −0.046) | read-out J same / cross lab (bge) | Δ_J^adj [95% CI] | talk Δβ [95% CI] |
| --- | --- | --- | --- | --- | --- | --- |
| 51a | 0.055* / 0.047 | 0.045 / 0.056* | 0.024 | 0.058 / 0.041 | 0.015 [-0.034, 0.077] | -0.0013 [-0.0048, 0.0042] |
| 51b | 0.069* / 0.084* | 0.008 / 0.034 | -0.008 | 0.067 / 0.052 | 0.014 [-0.019, 0.047] | -0.0010 [-0.0034, 0.0016] |
| 51c | 0.090* / 0.072* | 0.042 / 0.025 | 0.041 | 0.064 / 0.025 | 0.043 [-0.015, 0.104] | 0.0029 [0.0009, 0.0051] |
| 51d | 0.006 / 0.048 | -0.020 / 0.036 | -0.030 | 0.040 / 0.049 | 0.017 [-0.064, 0.086] | 0.0001 [-0.0017, 0.0028] |
| 51e | 0.012 / -0.013 | 0.007 / 0.015 | -0.029 | 0.016 / 0.013 | 0.011 [-0.039, 0.119] | 0.0099 [0.0051, 0.0141] |

* lab-permutation p < 0.05. Pooled (card): W3 keeps 32% (bge) / 47% (gte) of the raw field; the read-out contrast Δ_J^adj = 0.029 [0.010, 0.054] over 8 regime-III units (half of it is lab-level susceptibility and potency, post hoc); talk shows no family contrast.

**Newcomers joining in this period (R2-B; lab alignment a(d), bge raw, 5-statement means):**
- GPT-5.6 Terra (OpenAI): a(d) = 0.26, 0.08, 0.13, 0.22; room outsiderness r(d) = 0.20, 0.03, -0.09, 0.01
- GPT-5.6 Luna (OpenAI): a(d) = 0.38, 0.38, 0.28, 0.20, 0.06; room outsiderness r(d) = 0.00, 0.02, -0.14, 0.11, -0.06
- Kimi K3 (Moonshot): a(d) = -0.03, 0.07, 0.00, -0.08, -0.03, 0.12; room outsiderness r(d) = -0.01, -0.12, 0.19, -0.16, 0.02, 0.01
- Claude Opus 5 (Anthropic): a(d) = -0.06, 0.04, -0.00, -0.01, -0.15, -0.11; room outsiderness r(d) = 0.03, -0.00, 0.20, 0.12, 0.05, 0.12
- GLM-5.3 Flash (Zhipu): a(d) = -0.22, -0.26, -0.12, -0.05, 0.07; room outsiderness r(d) = 0.21, 0.33, 0.14, 0.24, 0.29
- Claude Fable 5.1 (Anthropic): a(d) = -0.26, -0.28, -0.17, -0.34; room outsiderness r(d) = 0.02, 0.13, 0.06, 0.01
- Gemini 3.8 Flash (Google): a(d) = 0.05, -0.06; room outsiderness r(d) = 0.12, 0.28
<!-- r2:end -->
