# H22 × G51c: Each agent: Maximize your assigned goal! — unit 51c (2026-08-05 → 08-24)

**Verdict:** inconclusive
**Verdict (1b):** inconclusive (round 1: inconclusive)
**Verdict (1c):** inconclusive (unchanged) (round 1c, stance v2.1)
**Role:** replication (exploratory)
**Period:** regime III · mode I/K · 27 agents · #general plus #focus (Gemini 2.5 Pro and Opus 4.8 moved there, 08-05 → 08-24); those two are excluded from couplings (variant keeps them) · 14 days.

## Why this period
Second long stretch; the #focus split removes two agents from the room. Same predictions as 51b.

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

Counted. Variant with the #focus agents included reported alongside.

## Result
Data: `data/processed/H22-private-goals-spin-glass/G51/<unit>/results.json`; figure: `figures/H22_G51c.pdf`.

**Unit 51c** (14 days; N eligible = 19; verdict: inconclusive)

| Prediction | Observed (90% CI) | Null / reference | Verdict |
| --- | --- | --- | --- |
| P1 heterogeneous content couplings | ρ_split = 0.460; σ_J = 0.0493; N = 13 | per-agent day-permutation null: q95 ρ = 0.224, p = 0.003 | pass |
| P2 SK ratio κ < 1 | κ̂ = 3.94 [2.86, 6.15]; J̄ = 0.0539 | glass < 1 < ferro (uninformative if > 1: drive) | fail |
| P3 drive-robust balance τ₃(dc) < 0.25 | -0.126 [-2.11, 2.46] | SK ≈ 0; factions ≈ 0.5 | indeterminate (CI spans both) |
| P3 (secondary) raw τ₃ | 0.597 [0.33, 0.93] | SK ≈ 0; ferro/drive → 1 | – |
| P3 (secondary) triangle frustration F | 0.297 (F_w 0.071; p_neg 0.141) | sign shuffle 0.322 [0.290, 0.346], p_low = 0.131 | pass (non-specific, Amendment 1) |
| (desc.) reliable-edge F | 0.114 on 70 triangles | random signs 0.207 | – |
| (desc.) ground-state frustration | 0.052 | sign shuffle 0.131, p_low = 0.010 | – (sign-shuffle null flags balance in most synthetic SK runs: not evidence) |
| (family check) after removing lab×lab block means | τ₃ -0.075, τ₃(dc) -0.313, F 0.336 | F null 0.363, p_low 0.154 | – |
| P4 content T_SR (raw) | 0.0367 (mean 0.0960, n = 4; U mean 0.0593) | role permutation: SD 0.0403, p_less 0.814, p_greater 0.186 | – |
| P4 content T_SR (family adjusted) | 0.0361 (mean 0.0339, n = 4; U mean -0.0022) | role permutation: SD 0.0396, p_less 0.826, p_greater 0.175 | fail |
| P4 content T_OP (raw) | -0.0086 (mean 0.0507, n = 2; U mean 0.0593) | role permutation: SD 0.0567, p_less 0.483, p_greater 0.517 | – |
| P4 content T_OP (family adjusted) | -0.0137 (mean -0.0159, n = 2; U mean -0.0022) | role permutation: SD 0.0568, p_less 0.448, p_greater 0.552 | – |
| P4 content T_K (raw) | 0.0216 (mean 0.0809, n = 6; U mean 0.0593) | role permutation: SD 0.0318, p_less 0.746, p_greater 0.254 | – |
| P4 content T_K (family adjusted) | 0.0195 (mean 0.0173, n = 6; U mean -0.0022) | role permutation: SD 0.0321, p_less 0.734, p_greater 0.267 | – |
| P4 content T_SY (raw) | 0.0156 (mean 0.0749, n = 14; U mean 0.0593) | role permutation: SD 0.0319, p_less 0.721, p_greater 0.280 | – |
| P4 content T_SY (family adjusted) | 0.0144 (mean 0.0121, n = 14; U mean -0.0022) | role permutation: SD 0.0321, p_less 0.707, p_greater 0.294 | – |
| P4 content T_NC (raw) | -0.0061 (mean 0.0532, n = 11; U mean 0.0593) | role permutation: SD 0.0272, p_less 0.455, p_greater 0.545 | – |
| P4 content T_NC (family adjusted) | -0.0022 (mean -0.0044, n = 11; U mean -0.0022) | role permutation: SD 0.0275, p_less 0.510, p_greater 0.490 | – |
| (first run) T_SR on the complete-matrix agent set (family-adj.) | 0.0133 (n = 1) | p_less 0.672, p_greater 0.328 | – |
| (manipulation) static role field: SR cos(H_i,H_j) − U | 0.258 (n = 4) | role permutation p_greater 0.010 | – |
| (secondary) talk T_SR (family-adj.) | 0.0128 (n = 4) | p_less 0.835, p_greater 0.165 | – |
| (secondary) talk MF role blocks (H05 block_J) | J_in(SR) 0.165, J_out 0.074 | – | – |
| (secondary) talk couplings | ρ_split 0.129 (p 0.090); κ̂ 2.58; τ₃ 0.590; τ₃(dc) 0.751 | pseudo-null | – |
| P5 overlap synchrony W, memory M | W = 1.15 (p = 0.243); M = 0.75; q_self 0.625, q(1) 0.573, q_∞ 0.413 (N = 19) | circular day-shift null (W = 1) | fail |
| (variant) #focus agents kept | N 15; ρ_split 0.561 (p 0.010); κ̂ 3.40; τ₃(dc) 0.291 | – | – |

## Scorecard (period-specific axes)
- **C** 1: content couplings beat the per-agent day-permutation null where P1 passes, but none of the H22-specific statistics (τ₃(dc), T_SR < 0, W) beat their nulls in the predicted direction.
- **D** 0: no glass signature (random-sign frustration with conflict-borne negative couplings; collective metastable states).
- **G** 1: known structure recovered: same-role pairs share a content field (static SR alignment, role permutation).
- **E** n/a within the unit.

## Notes
- Data: `data/processed/H22-private-goals-spin-glass/G51/51c/`. Figure: `figures/H22_G51c.pdf`.
- Card: `../../README.md` (Observables, Null, Prediction, Amendment 1).

## Round 1b (improved data, 2026-10-04)
*Re-run on the corrected inputs (card section "Round 1b"); round-1 numbers kept above.* DQ6 ground-truth roles (Opus 5's first role recovered), DQ5 statement vectors in two models (bge, gte), DQ5 `style_resid_period` vectors ("styp"), restatements removed ("dedup"), `activity_bins_fixed` for talk spins, and the DQ2 stance channel with the calibrated agent-field null. Data: `data/processed/H22-private-goals-spin-glass/r1b/`.

| Unit | Variant | heterogeneity ρ_split | τ₃(dc) | T_SR / pairs (p>) | T_OP | W (p) | talk ρ_split (p) |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 51c | round 1 | 0.46 (p 0.003) | -0.13 | 0.036 / 4 (p> 0.175) | -0.014 | 1.15 (p 0.24) | 0.13 (p 0.090) |
| 51c | bge | 0.46 (p 0.003) | -0.13 | 0.036 / 4 (p> 0.175) | -0.014 | 1.16 (p 0.23) | 0.14 (p 0.047) |
| 51c | gte | 0.42 (p 0.003) | 0.57 | 0.052 / 4 (p> 0.104) | -0.030 | 1.61 (p 0.02) | 0.14 (p 0.047) |
| 51c | bge styp | 0.42 (p 0.003) | -0.15 | 0.034 / 4 (p> 0.182) | -0.025 | 1.09 (p 0.31) | 0.14 (p 0.047) |
| 51c | gte styp | 0.36 (p 0.003) | 0.47 | 0.047 / 4 (p> 0.125) | -0.043 | 1.59 (p 0.02) | 0.14 (p 0.047) |
| 51c | bge dedup | 0.48 (p 0.003) | 0.33 | 0.018 / 4 (p> 0.300) | 0.009 | 1.10 (p 0.31) | 0.10 (p 0.103) |
| 51c | **stance (DQ2)** | dc split-half 0.39 (agent-field p 0.005) | 0.23 [0.06, 0.36] | 0.127 / 5 (p> 0.232) | -0.343 | – | neg. pairs 54 vs 6.7 |

## Round 1c (stance v2.1, 2026-10-04)
*Pre-registered in the card (Round 1c, 22:10 UTC). Data: `data/processed/H22-private-goals-spin-glass/r1c/`.*

T^D_SR +1.47 pp (3 flags in 113 rival replies; NG p 0.06; corrected +2.4 pp), not significant. Γ +0.11 [−0.10, +0.32] (bge), +0.10 (gte); placebo percentile 0.80 / 0.75. τ₃(dc) of v2 soft stance 0.18 [−0.14, 0.34] (meets the P3 rule).
