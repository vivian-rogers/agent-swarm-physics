# H22 × G51a: Each agent: Maximize your assigned goal! — unit 51a (2026-07-06 → 07-08)

**Verdict:** descriptive
**Verdict (1b):** descriptive (round 1: descriptive)
**Role:** replication (exploratory)
**Period:** regime III · mode I/K (private roles, NE26 starts) · 21 agents, 8 h/day (07-07 ran ≈ 17 h) · one room (#general) · 3 days; day-thirds used as pseudo-days (Amendment 1).

## Why this period
The first three days of private roles, before the GPT-5.6 batch join (NE32). Roles have just been handed out, so if conflict structures coupling at all, the signal should already be there; but 3 days give low power, so this unit is descriptive.

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

Short unit: low power (synthetic: comparable short units detect heterogeneity in ≤ 30% of replicates). No verdict counted.

## Result
Data: `data/processed/H22-private-goals-spin-glass/G51/<unit>/results.json`; figure: `figures/H22_G51a.pdf`.

**Unit 51a** (3 days, day-thirds as pseudo-days; N eligible = 13; verdict: descriptive)

| Prediction | Observed (90% CI) | Null / reference | Verdict |
| --- | --- | --- | --- |
| P1 heterogeneous content couplings | ρ_split = -0.049; σ_J = –; N = 12 | per-agent day-permutation null: q95 ρ = 0.235, p = 0.598 | fail |
| P2 SK ratio κ < 1 | κ̂ = – [2.09, 26.01]; J̄ = 0.0510 | glass < 1 < ferro (uninformative if > 1: drive) | fail |
| P3 drive-robust balance τ₃(dc) < 0.25 | 1.325 [-0.84, 11.28] | SK ≈ 0; factions ≈ 0.5 | indeterminate (CI spans both); uninterpretable without P1 |
| P3 (secondary) raw τ₃ | 0.748 [0.00, 0.94] | SK ≈ 0; ferro/drive → 1 | – |
| P3 (secondary) triangle frustration F | 0.327 (F_w 0.149; p_neg 0.182) | sign shuffle 0.380 [0.336, 0.418], p_low = 0.029 | fail (non-specific, Amendment 1) |
| (desc.) reliable-edge F | 0.055 on 55 triangles | random signs 0.142 | – |
| (desc.) ground-state frustration | 0.126 | sign shuffle 0.177, p_low = 0.030 | – (sign-shuffle null flags balance in most synthetic SK runs: not evidence) |
| (family check) after removing lab×lab block means | τ₃ 1.151, τ₃(dc) 1.075, F 0.500 | F null 0.455, p_low 0.923 | – |
| P4 content T_OP (raw) | -0.1361 (mean -0.0887, n = 2; U mean 0.0474) | role permutation: SD 0.0521, p_less 0.007, p_greater 0.993 | – |
| P4 content T_OP (family adjusted) | -0.1310 (mean -0.1324, n = 2; U mean -0.0014) | role permutation: SD 0.0513, p_less 0.008, p_greater 0.992 | – |
| P4 content T_K (raw) | -0.1361 (mean -0.0887, n = 2; U mean 0.0474) | role permutation: SD 0.0521, p_less 0.007, p_greater 0.993 | – |
| P4 content T_K (family adjusted) | -0.1310 (mean -0.1324, n = 2; U mean -0.0014) | role permutation: SD 0.0513, p_less 0.008, p_greater 0.992 | – |
| P4 content T_SY (raw) | 0.0162 (mean 0.0636, n = 21; U mean 0.0474) | role permutation: SD 0.0230, p_less 0.779, p_greater 0.221 | – |
| P4 content T_SY (family adjusted) | 0.0167 (mean 0.0154, n = 21; U mean -0.0014) | role permutation: SD 0.0221, p_less 0.778, p_greater 0.222 | – |
| P4 content T_NC (raw) | 0.0106 (mean 0.0579, n = 3; U mean 0.0474) | role permutation: SD 0.0436, p_less 0.624, p_greater 0.376 | – |
| P4 content T_NC (family adjusted) | 0.0051 (mean 0.0038, n = 3; U mean -0.0014) | role permutation: SD 0.0431, p_less 0.565, p_greater 0.435 | – |
| (first run) T_SR on the complete-matrix agent set (family-adj.) | – (n = 0) | p_less –, p_greater – | – |
| (manipulation) static role field: SR cos(H_i,H_j) − U | – (n = 0) | role permutation p_greater – | – |
| (secondary) talk T_SR (family-adj.) | – (n = 0) | p_less –, p_greater – | – |
| (secondary) talk MF role blocks (H05 block_J) | J_in(SR) –, J_out 0.052 | – | – |
| (secondary) talk couplings | ρ_split -0.122 (p 0.827); κ̂ –; τ₃ –; τ₃(dc) – | pseudo-null | – |

## Scorecard (period-specific axes)
- **C** 1: content couplings beat the per-agent day-permutation null where P1 passes, but none of the H22-specific statistics (τ₃(dc), T_SR < 0, W) beat their nulls in the predicted direction.
- **D** 0: no glass signature (random-sign frustration with conflict-borne negative couplings; collective metastable states).
- **G** 1: known structure recovered: same-role pairs share a content field (static SR alignment, role permutation).
- **E** n/a within the unit.

## Notes
- Data: `data/processed/H22-private-goals-spin-glass/G51/51a/`. Figure: `figures/H22_G51a.pdf`.
- Card: `../../README.md` (Observables, Null, Prediction, Amendment 1).

## Round 1b (improved data, 2026-10-04)
*Re-run on the corrected inputs (card section "Round 1b"); round-1 numbers kept above.* DQ6 ground-truth roles (Opus 5's first role recovered), DQ5 statement vectors in two models (bge, gte), DQ5 `style_resid_period` vectors ("styp"), restatements removed ("dedup"), `activity_bins_fixed` for talk spins, and the DQ2 stance channel with the calibrated agent-field null. Data: `data/processed/H22-private-goals-spin-glass/r1b/`.

| Unit | Variant | heterogeneity ρ_split | τ₃(dc) | T_SR / pairs (p>) | T_OP | W (p) | talk ρ_split (p) |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 51a | round 1 | -0.05 (p 0.598) | 1.33 | – / 0 (p> –) | -0.131 | – (p –) | -0.12 (p 0.827) |
| 51a | bge | -0.05 (p 0.598) | 1.33 | – / 0 (p> –) | -0.131 | – (p –) | 0.06 (p 0.365) |
| 51a | gte | 0.06 (p 0.429) | -0.90 | – / 0 (p> –) | -0.037 | – (p –) | 0.06 (p 0.365) |
| 51a | bge styp | -0.11 (p 0.711) | 3.59 | – / 0 (p> –) | -0.158 | – (p –) | 0.06 (p 0.365) |
| 51a | gte styp | -0.03 (p 0.628) | nan | – / 0 (p> –) | -0.055 | – (p –) | 0.06 (p 0.365) |
| 51a | bge dedup | -0.03 (p 0.542) | 1.10 | – / 0 (p> –) | -0.131 | – (p –) | 0.06 (p 0.365) |
| 51a | **stance (DQ2)** | dc split-half 0.09 (agent-field p 0.199) | -0.63 [-0.63, -0.63] | 0.146 / 3 (p> 0.299) | 0.078 | – | neg. pairs 19 vs 4.7 |

