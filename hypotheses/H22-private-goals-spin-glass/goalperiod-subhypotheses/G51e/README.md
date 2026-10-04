# H22 × G51e: Each agent: Maximize your assigned goal! — unit 51e (2026-09-03 → 09-04)

**Verdict:** descriptive
**Verdict (1b):** descriptive (round 1: descriptive)
**Role:** replication (exploratory)
**Period:** regime III · mode I/K · 29 → 32 agents · one room · 2 days (NE33: Muse Spark 1.3, Gemini 3.8 Flash, GPT-6 Astra join; their roles start 09-04); day-thirds as pseudo-days.

## Why this period
The batch-join days just before the held-out tail. Descriptive only.

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

Descriptive only.

## Result
Data: `data/processed/H22-private-goals-spin-glass/G51/<unit>/results.json`; figure: `figures/H22_G51e.pdf`.

**Unit 51e** (2 days, day-thirds as pseudo-days; N eligible = 13; verdict: descriptive)

| Prediction | Observed (90% CI) | Null / reference | Verdict |
| --- | --- | --- | --- |
| P1 heterogeneous content couplings | ρ_split = 0.246; σ_J = 0.0476; N = 11 | per-agent day-permutation null: q95 ρ = 0.289, p = 0.106 | fail |
| P2 SK ratio κ < 1 | κ̂ = 5.23 [3.32, 14.18]; J̄ = 0.0751 | glass < 1 < ferro (uninformative if > 1: drive) | fail |
| P3 drive-robust balance τ₃(dc) < 0.25 | – [0.00, 0.00] | SK ≈ 0; factions ≈ 0.5 | indeterminate (CI spans both); uninterpretable without P1 |
| P3 (secondary) raw τ₃ | 0.684 [0.00, 0.68] | SK ≈ 0; ferro/drive → 1 | – |
| P3 (secondary) triangle frustration F | 0.333 (F_w 0.117; p_neg 0.200) | sign shuffle 0.403 [0.358, 0.455], p_low = 0.022 | fail (non-specific, Amendment 1) |
| (desc.) reliable-edge F | 0.311 on 61 triangles | random signs 0.334 | – |
| (desc.) ground-state frustration | 0.068 | sign shuffle 0.191, p_low = 0.010 | – (sign-shuffle null flags balance in most synthetic SK runs: not evidence) |
| (family check) after removing lab×lab block means | τ₃ -2.360, τ₃(dc) –, F 0.364 | F null 0.241, p_low 1.000 | – |
| P4 content T_SY (raw) | 0.0441 (mean 0.0857, n = 23; U mean 0.0416) | role permutation: SD 0.0215, p_less 0.990, p_greater 0.010 | – |
| P4 content T_SY (family adjusted) | 0.0466 (mean 0.0318, n = 23; U mean -0.0148) | role permutation: SD 0.0221, p_less 0.989, p_greater 0.012 | – |
| P4 content T_NC (raw) | 0.0008 (mean 0.0424, n = 3; U mean 0.0416) | role permutation: SD 0.0460, p_less 0.560, p_greater 0.440 | – |
| P4 content T_NC (family adjusted) | -0.0017 (mean -0.0166, n = 3; U mean -0.0148) | role permutation: SD 0.0464, p_less 0.517, p_greater 0.483 | – |
| (first run) T_SR on the complete-matrix agent set (family-adj.) | – (n = 0) | p_less –, p_greater – | – |
| (manipulation) static role field: SR cos(H_i,H_j) − U | – (n = 0) | role permutation p_greater – | – |
| (secondary) talk T_SR (family-adj.) | – (n = 0) | p_less –, p_greater – | – |
| (secondary) talk MF role blocks (H05 block_J) | J_in(SR) –, J_out 0.047 | – | – |
| (secondary) talk couplings | ρ_split 0.203 (p 0.100); κ̂ 1.55; τ₃ -1.447; τ₃(dc) 1.554 | pseudo-null | – |

## Scorecard (period-specific axes)
- **C** 1: content couplings beat the per-agent day-permutation null where P1 passes, but none of the H22-specific statistics (τ₃(dc), T_SR < 0, W) beat their nulls in the predicted direction.
- **D** 0: no glass signature (random-sign frustration with conflict-borne negative couplings; collective metastable states).
- **G** 1: known structure recovered: same-role pairs share a content field (static SR alignment, role permutation).
- **E** n/a within the unit.

## Notes
- Data: `data/processed/H22-private-goals-spin-glass/G51/51e/`. Figure: `figures/H22_G51e.pdf`.
- Card: `../../README.md` (Observables, Null, Prediction, Amendment 1).

## Round 1b (improved data, 2026-10-04)
*Re-run on the corrected inputs (card section "Round 1b"); round-1 numbers kept above.* DQ6 ground-truth roles (Opus 5's first role recovered), DQ5 statement vectors in two models (bge, gte), DQ5 `style_resid_period` vectors ("styp"), restatements removed ("dedup"), `activity_bins_fixed` for talk spins, and the DQ2 stance channel with the calibrated agent-field null. Data: `data/processed/H22-private-goals-spin-glass/r1b/`.

| Unit | Variant | heterogeneity ρ_split | τ₃(dc) | T_SR / pairs (p>) | T_OP | W (p) | talk ρ_split (p) |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 51e | round 1 | 0.25 (p 0.106) | nan | – / 0 (p> –) | – | – (p –) | 0.20 (p 0.100) |
| 51e | bge | 0.25 (p 0.106) | nan | – / 0 (p> –) | – | – (p –) | -0.01 (p 0.542) |
| 51e | gte | 0.25 (p 0.123) | -0.22 | – / 0 (p> –) | – | – (p –) | -0.01 (p 0.542) |
| 51e | bge styp | 0.23 (p 0.140) | nan | – / 0 (p> –) | – | – (p –) | -0.01 (p 0.542) |
| 51e | gte styp | 0.26 (p 0.086) | 0.32 | – / 0 (p> –) | – | – (p –) | -0.01 (p 0.542) |
| 51e | bge dedup | 0.26 (p 0.093) | nan | – / 0 (p> –) | – | – (p –) | -0.01 (p 0.542) |
| 51e | **stance (DQ2)** | dc split-half 0.26 (agent-field p 0.035) | –  | -0.246 / 1 (p> 0.780) | -0.217 | – | neg. pairs 22 vs 4.3 |

