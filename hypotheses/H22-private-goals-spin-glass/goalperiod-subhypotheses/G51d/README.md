# H22 × G51d: Each agent: Maximize your assigned goal! — unit 51d (2026-08-25 → 09-02)

**Verdict:** inconclusive
**Verdict (1b):** inconclusive (round 1: inconclusive)
**Role:** replication (exploratory)
**Period:** regime III · mode I/K · 27 → 29 agents · one room · 7 days. GLM-5.3 Flash joins 08-28 (Press baron from 08-31), Fable 5.1 joins 09-01 (AI safety researcher).

## Why this period
After #focus closes, before the NE33 batch join. Moderate power (synthetic: heterogeneity detected in 30–92% of replicates depending on coupling strength; P5 power 0.64).

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

Counted, with lower power than 51b/51c.

## Result
Data: `data/processed/H22-private-goals-spin-glass/G51/<unit>/results.json`; figure: `figures/H22_G51d.pdf`.

**Unit 51d** (7 days; N eligible = 15; verdict: inconclusive)

| Prediction | Observed (90% CI) | Null / reference | Verdict |
| --- | --- | --- | --- |
| P1 heterogeneous content couplings | ρ_split = 0.116; σ_J = 0.0228; N = 12 | per-agent day-permutation null: q95 ρ = 0.217, p = 0.233 | fail |
| P2 SK ratio κ < 1 | κ̂ = 9.74 [4.98, 21.81]; J̄ = 0.0642 | glass < 1 < ferro (uninformative if > 1: drive) | fail |
| P3 drive-robust balance τ₃(dc) < 0.25 | -0.120 [-0.12, 0.21] | SK ≈ 0; factions ≈ 0.5 | pass; uninterpretable without P1 |
| P3 (secondary) raw τ₃ | 0.497 [0.00, 0.57] | SK ≈ 0; ferro/drive → 1 | – |
| P3 (secondary) triangle frustration F | 0.164 (F_w 0.044; p_neg 0.061) | sign shuffle 0.165 [0.145, 0.182], p_low = 0.566 | pass (non-specific, Amendment 1) |
| (desc.) reliable-edge F | 0.103 on 87 triangles | random signs 0.113 | – |
| (desc.) ground-state frustration | 0.012 | sign shuffle 0.065, p_low = 0.010 | – (sign-shuffle null flags balance in most synthetic SK runs: not evidence) |
| (family check) after removing lab×lab block means | τ₃ -0.014, τ₃(dc) -0.049, F 0.445 | F null 0.341, p_low 1.000 | – |
| P4 content T_SR (raw) | 0.0004 (mean 0.0539, n = 1; U mean 0.0535) | role permutation: SD 0.0565, p_less 0.546, p_greater 0.454 | – |
| P4 content T_SR (family adjusted) | -0.0024 (mean -0.0059, n = 1; U mean -0.0035) | role permutation: SD 0.0554, p_less 0.514, p_greater 0.486 | fail |
| P4 content T_OP (raw) | 0.0004 (mean 0.0540, n = 2; U mean 0.0535) | role permutation: SD 0.0454, p_less 0.534, p_greater 0.466 | – |
| P4 content T_OP (family adjusted) | 0.0081 (mean 0.0046, n = 2; U mean -0.0035) | role permutation: SD 0.0437, p_less 0.601, p_greater 0.400 | – |
| P4 content T_K (raw) | 0.0004 (mean 0.0539, n = 3; U mean 0.0535) | role permutation: SD 0.0365, p_less 0.523, p_greater 0.477 | – |
| P4 content T_K (family adjusted) | 0.0046 (mean 0.0011, n = 3; U mean -0.0035) | role permutation: SD 0.0356, p_less 0.579, p_greater 0.421 | – |
| P4 content T_SY (raw) | 0.0122 (mean 0.0658, n = 23; U mean 0.0535) | role permutation: SD 0.0153, p_less 0.813, p_greater 0.187 | – |
| P4 content T_SY (family adjusted) | 0.0149 (mean 0.0114, n = 23; U mean -0.0035) | role permutation: SD 0.0147, p_less 0.865, p_greater 0.135 | – |
| P4 content T_NC (raw) | -0.0044 (mean 0.0491, n = 5; U mean 0.0535) | role permutation: SD 0.0283, p_less 0.448, p_greater 0.552 | – |
| P4 content T_NC (family adjusted) | -0.0071 (mean -0.0106, n = 5; U mean -0.0035) | role permutation: SD 0.0284, p_less 0.409, p_greater 0.591 | – |
| (first run) T_SR on the complete-matrix agent set (family-adj.) | -0.0112 (n = 1) | p_less 0.453, p_greater 0.548 | – |
| (manipulation) static role field: SR cos(H_i,H_j) − U | 0.440 (n = 1) | role permutation p_greater 0.026 | – |
| (secondary) talk T_SR (family-adj.) | 0.0196 (n = 1) | p_less 0.752, p_greater 0.248 | – |
| (secondary) talk MF role blocks (H05 block_J) | J_in(SR) 0.205, J_out 0.047 | – | – |
| (secondary) talk couplings | ρ_split 0.115 (p 0.292); κ̂ 2.11; τ₃ –; τ₃(dc) – | pseudo-null | – |
| P5 overlap synchrony W, memory M | W = 0.69 (p = 0.789); M = 0.49; q_self 0.714, q(1) 0.628, q_∞ 0.545 (N = 15) | circular day-shift null (W = 1) | fail |

## Scorecard (period-specific axes)
- **C** 1: content couplings beat the per-agent day-permutation null where P1 passes, but none of the H22-specific statistics (τ₃(dc), T_SR < 0, W) beat their nulls in the predicted direction.
- **D** 0: no glass signature (random-sign frustration with conflict-borne negative couplings; collective metastable states).
- **G** 1: known structure recovered: same-role pairs share a content field (static SR alignment, role permutation).
- **E** n/a within the unit.

## Notes
- Data: `data/processed/H22-private-goals-spin-glass/G51/51d/`. Figure: `figures/H22_G51d.pdf`.
- Card: `../../README.md` (Observables, Null, Prediction, Amendment 1).

## Round 1b (improved data, 2026-10-04)
*Re-run on the corrected inputs (card section "Round 1b"); round-1 numbers kept above.* DQ6 ground-truth roles (Opus 5's first role recovered), DQ5 statement vectors in two models (bge, gte), DQ5 `style_resid_period` vectors ("styp"), restatements removed ("dedup"), `activity_bins_fixed` for talk spins, and the DQ2 stance channel with the calibrated agent-field null. Data: `data/processed/H22-private-goals-spin-glass/r1b/`.

| Unit | Variant | heterogeneity ρ_split | τ₃(dc) | T_SR / pairs (p>) | T_OP | W (p) | talk ρ_split (p) |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 51d | round 1 | 0.12 (p 0.233) | -0.12 | -0.002 / 1 (p> 0.486) | 0.008 | 0.69 (p 0.79) | 0.12 (p 0.292) |
| 51d | bge | 0.12 (p 0.233) | -0.12 | -0.002 / 1 (p> 0.486) | 0.008 | 0.68 (p 0.79) | 0.34 (p 0.003) |
| 51d | gte | 0.34 (p 0.020) | 1.55 | 0.002 / 1 (p> 0.400) | -0.004 | 0.79 (p 0.67) | 0.34 (p 0.003) |
| 51d | bge styp | 0.08 (p 0.309) | -0.32 | 0.016 / 1 (p> 0.296) | 0.004 | 0.56 (p 0.89) | 0.34 (p 0.003) |
| 51d | gte styp | 0.31 (p 0.040) | 1.39 | 0.013 / 1 (p> 0.365) | -0.006 | 1.01 (p 0.45) | 0.34 (p 0.003) |
| 51d | bge dedup | 0.11 (p 0.249) | -0.12 | -0.002 / 1 (p> 0.473) | 0.009 | 0.72 (p 0.76) | 0.34 (p 0.003) |
| 51d | **stance (DQ2)** | dc split-half 0.43 (agent-field p 0.005) | 0.05 [-0.02, 0.23] | 0.011 / 4 (p> 0.513) | 0.224 | – | neg. pairs 33 vs 6.7 |

