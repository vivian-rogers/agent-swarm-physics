# H22 × G51b: Each agent: Maximize your assigned goal! — unit 51b (2026-07-09 → 08-04)

**Verdict:** failed
**Verdict (1b):** failed (round 1: failed; rival homophily in every content variant)
**Role:** replication (exploratory)
**Period:** regime III · mode I/K · 24 → 27 agents · one room (#general; GPT-5.6 triplet isolated on 07-09, Grok 4.5 onboarding room 07-10, side room 07-24) · 19 days. Single joins inside (Grok 4.5 07-10, Kimi K3 07-17, Opus 5 07-24) handled by the population rule; NE38 (Opus 5's role restart, 07-29) inside.

## Why this period
The longest stationary stretch of the private-role era, in one room: the best-powered test of coupling signs and frustration (synthetic power for heterogeneity ≈ 1 at s ≥ 0.06; P5 power 0.88).

## Prediction
*Written 2026-10-04 00:43 UTC, before running H22 on this unit (after Amendment 1, which was based on synthetic data only).*
The card's P1–P5 under Amendment 1, applied to this unit:
- **P1:** content-coupling heterogeneity is real (ρ_split > per-agent day-permutation null, p < 0.05).
- **P2:** κ̂ < 1. Expected to fail because of common drive; uninformative if it fails.
- **P3 (primary):** τ₃(dc) < 0.25 with the 90% CI upper bound < 0.5, i.e. random-sign rather than factional heterogeneity. Secondary: triangle F not below the sign-shuffle null.
- **P4:** same-role rivals couple negatively: family-adjusted T_SR < 0, role-permutation p_less < 0.05, and mean J^c(SR) < 0. Also T_SY > 0. The homophily rival predicts T_SR > 0.
- **P5:** W > 1 (p < 0.05) and M > 0.2: collective metastable states.
- **Talk (secondary):** T_SR(J^t) < 0. Expected: talk heterogeneity at the noise floor (H02).
- **What counts against H22:** P1 passes but τ₃(dc) ≥ 0.25 (factions); T_SR ≥ 0 (and > 0 significantly = homophily); W ≈ 1.
- **My expectation:** P1 passes; P3 passes or is ambiguous (random-sign heterogeneity is the generic outcome; synthetic: SK and heterogeneous ferro both give τ₃(dc) ≈ 0, so a P3 pass alone is weak evidence); P4 fails or goes the homophily way; P5 fails (W ≈ 1).

Counted toward the hypothesis verdict.

## Result
Data: `data/processed/H22-private-goals-spin-glass/G51/<unit>/results.json`; figure: `figures/H22_G51b.pdf`.

**Unit 51b** (19 days; N eligible = 22; verdict: failed)

| Prediction | Observed (90% CI) | Null / reference | Verdict |
| --- | --- | --- | --- |
| P1 heterogeneous content couplings | ρ_split = 0.462; σ_J = 0.0423; N = 17 | per-agent day-permutation null: q95 ρ = 0.188, p = 0.003 | pass |
| P2 SK ratio κ < 1 | κ̂ = 5.16 [4.51, 8.19]; J̄ = 0.0529 | glass < 1 < ferro (uninformative if > 1: drive) | fail |
| P3 drive-robust balance τ₃(dc) < 0.25 | 0.223 [-0.21, 1.04] | SK ≈ 0; factions ≈ 0.5 | indeterminate (CI spans both) |
| P3 (secondary) raw τ₃ | 0.565 [0.47, 0.74] | SK ≈ 0; ferro/drive → 1 | – |
| P3 (secondary) triangle frustration F | 0.247 (F_w 0.079; p_neg 0.103) | sign shuffle 0.253 [0.235, 0.268], p_low = 0.295 | pass (non-specific, Amendment 1) |
| (desc.) reliable-edge F | 0.178 on 332 triangles | random signs 0.192 | – |
| (desc.) ground-state frustration | 0.039 | sign shuffle 0.106, p_low = 0.010 | – (sign-shuffle null flags balance in most synthetic SK runs: not evidence) |
| (family check) after removing lab×lab block means | τ₃ 0.246, τ₃(dc) 0.318, F 0.431 | F null 0.458, p_low 0.081 | – |
| P4 content T_SR (raw) | 0.0656 (mean 0.1181, n = 3; U mean 0.0525) | role permutation: SD 0.0267, p_less 0.990, p_greater 0.010 | – |
| P4 content T_SR (family adjusted) | 0.0656 (mean 0.0642, n = 3; U mean -0.0015) | role permutation: SD 0.0270, p_less 0.987, p_greater 0.013 | rival (homophily) |
| P4 content T_OP (raw) | -0.0477 (mean 0.0048, n = 2; U mean 0.0525) | role permutation: SD 0.0455, p_less 0.123, p_greater 0.878 | – |
| P4 content T_OP (family adjusted) | -0.0477 (mean -0.0492, n = 2; U mean -0.0015) | role permutation: SD 0.0454, p_less 0.113, p_greater 0.887 | – |
| P4 content T_K (raw) | 0.0203 (mean 0.0728, n = 5; U mean 0.0525) | role permutation: SD 0.0228, p_less 0.818, p_greater 0.182 | – |
| P4 content T_K (family adjusted) | 0.0203 (mean 0.0188, n = 5; U mean -0.0015) | role permutation: SD 0.0229, p_less 0.813, p_greater 0.187 | – |
| P4 content T_SY (raw) | 0.0035 (mean 0.0560, n = 38; U mean 0.0525) | role permutation: SD 0.0161, p_less 0.607, p_greater 0.393 | – |
| P4 content T_SY (family adjusted) | 0.0035 (mean 0.0020, n = 38; U mean -0.0015) | role permutation: SD 0.0161, p_less 0.608, p_greater 0.392 | – |
| P4 content T_NC (raw) | 0.0055 (mean 0.0581, n = 10; U mean 0.0525) | role permutation: SD 0.0209, p_less 0.640, p_greater 0.360 | – |
| P4 content T_NC (family adjusted) | 0.0055 (mean 0.0041, n = 10; U mean -0.0015) | role permutation: SD 0.0208, p_less 0.634, p_greater 0.366 | – |
| (first run) T_SR on the complete-matrix agent set (family-adj.) | 0.0668 (n = 3) | p_less 0.976, p_greater 0.024 | – |
| (manipulation) static role field: SR cos(H_i,H_j) − U | 0.403 (n = 5) | role permutation p_greater 0.000 | – |
| (secondary) talk T_SR (family-adj.) | 0.0024 (n = 5) | p_less 0.642, p_greater 0.358 | – |
| (secondary) talk MF role blocks (H05 block_J) | J_in(SR) -0.038, J_out 0.061 | – | – |
| (secondary) talk couplings | ρ_split 0.089 (p 0.100); κ̂ 6.57; τ₃ 0.113; τ₃(dc) -0.520 | pseudo-null | – |
| P5 overlap synchrony W, memory M | W = 1.16 (p = 0.213); M = 0.74; q_self 0.639, q(1) 0.590, q_∞ 0.454 (N = 22) | circular day-shift null (W = 1) | fail |

## Scorecard (period-specific axes)
- **C** 1: content couplings beat the per-agent day-permutation null where P1 passes, but none of the H22-specific statistics (τ₃(dc), T_SR < 0, W) beat their nulls in the predicted direction.
- **D** 0: no glass signature (random-sign frustration with conflict-borne negative couplings; collective metastable states).
- **G** 1: known structure recovered: same-role pairs share a content field (static SR alignment, role permutation).
- **E** n/a within the unit.

## Notes
- Data: `data/processed/H22-private-goals-spin-glass/G51/51b/`. Figure: `figures/H22_G51b.pdf`.
- Card: `../../README.md` (Observables, Null, Prediction, Amendment 1).

## Round 1b (improved data, 2026-10-04)
*Re-run on the corrected inputs (card section "Round 1b"); round-1 numbers kept above.* DQ6 ground-truth roles (Opus 5's first role recovered), DQ5 statement vectors in two models (bge, gte), DQ5 `style_resid_period` vectors ("styp"), restatements removed ("dedup"), `activity_bins_fixed` for talk spins, and the DQ2 stance channel with the calibrated agent-field null. Data: `data/processed/H22-private-goals-spin-glass/r1b/`.

| Unit | Variant | heterogeneity ρ_split | τ₃(dc) | T_SR / pairs (p>) | T_OP | W (p) | talk ρ_split (p) |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 51b | round 1 | 0.46 (p 0.003) | 0.22 | 0.066 / 3 (p> 0.013) | -0.048 | 1.16 (p 0.21) | 0.09 (p 0.100) |
| 51b | bge | 0.46 (p 0.003) | 0.22 | 0.066 / 3 (p> 0.013) | -0.048 | 1.16 (p 0.21) | 0.45 (p 0.003) |
| 51b | gte | 0.46 (p 0.003) | 0.36 | 0.046 / 3 (p> 0.054) | 0.005 | 1.14 (p 0.24) | 0.45 (p 0.003) |
| 51b | bge styp | 0.47 (p 0.003) | 0.31 | 0.069 / 3 (p> 0.013) | -0.038 | 0.99 (p 0.48) | 0.45 (p 0.003) |
| 51b | gte styp | 0.46 (p 0.003) | 0.37 | 0.048 / 3 (p> 0.045) | 0.012 | 1.08 (p 0.31) | 0.45 (p 0.003) |
| 51b | bge dedup | 0.47 (p 0.003) | 0.26 | 0.063 / 3 (p> 0.020) | -0.064 | 1.17 (p 0.20) | 0.45 (p 0.003) |
| 51b | **stance (DQ2)** | dc split-half 0.43 (agent-field p 0.005) | 0.25 [0.08, 0.38] | 0.086 / 5 (p> 0.330) | 0.109 | – | neg. pairs 70 vs 8.1 |

