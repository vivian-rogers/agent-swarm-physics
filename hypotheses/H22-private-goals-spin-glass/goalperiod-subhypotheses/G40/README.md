# H22 × G40: shared-objective contrast (40; 2026-05-04 → 05-08)

**Verdict:** descriptive
**Verdict (1b):** descriptive (round 1: descriptive)
**Role:** replication (exploratory (contrast))
**Period:** regime III · mode C (connect worlds into one 3D universe) · 15 agents · #best, #rest plus #universe-coordination · 5 days (day-thirds as pseudo-days).

## Why this period
A strongly coordinated shared-objective week (interface standards): the most ferromagnetic candidate.

## Prediction
*Written 2026-10-04 00:43 UTC, before running H22 on this period.*
H22's expectation for a shared-objective week:
- the ferro / balanced side: raw τ₃ ≥ 0.25 or κ̂ > 1, or couplings at the noise floor;
- #51's raw τ₃ below this period's;
- the largest-room variant (one room, like #51) shows the same ordering.

Under Amendment 1 these units are near-powerless. Synthetic heterogeneity detection is ≤ 30% (38a) and ≤ 18% (#40, #44) even at strong couplings, so:
- P1 is expected to fail here;
- the contrast is then descriptive;
- τ₃ values without P1 are not interpreted.

Two rooms make the coupling matrix block-structured, a balanced (factional) structure that raises τ₃(dc). The largest-room variant is the fair comparison.

## Result
Data: `data/processed/H22-private-goals-spin-glass/G40/<unit>/results.json`; figure: `figures/H22_G40.pdf`.

**Unit 40** (5 days, day-thirds as pseudo-days; N eligible = 9; verdict: descriptive (ferro side, as H22 expects for a shared-objective week))

| Prediction | Observed (90% CI) | Null / reference | Verdict |
| --- | --- | --- | --- |
| P1 heterogeneous content couplings | ρ_split = 0.313; σ_J = 0.0577; N = 9 | per-agent day-permutation null: q95 ρ = 0.289, p = 0.050 | pass |
| P2 SK ratio κ < 1 | κ̂ = 6.89 [4.59, 19.46]; J̄ = 0.1325 | glass < 1 < ferro (uninformative if > 1: drive) | fail |
| P3 drive-robust balance τ₃(dc) < 0.25 | – [-34.37, 13.41] | SK ≈ 0; factions ≈ 0.5 | indeterminate (CI spans both) |
| P3 (secondary) raw τ₃ | 0.512 [-1.33, 0.97] | SK ≈ 0; ferro/drive → 1 | – |
| P3 (secondary) triangle frustration F | 0.143 (F_w 0.011; p_neg 0.056) | sign shuffle 0.157 [0.143, 0.167], p_low = 0.415 | pass (non-specific, Amendment 1) |
| (desc.) reliable-edge F | 0.073 on 55 triangles | random signs 0.091 | – |
| (desc.) ground-state frustration | 0.010 | sign shuffle 0.057, p_low = 0.040 | – (sign-shuffle null flags balance in most synthetic SK runs: not evidence) |
| (family check) after removing lab×lab block means | τ₃ –, τ₃(dc) –, F 0.357 | F null 0.419, p_low 0.119 | – |
| (secondary) talk couplings | ρ_split 0.126 (p 0.286); κ̂ 0.75; τ₃ 2.021; τ₃(dc) 2.880 | pseudo-null | – |
| P5 overlap synchrony W, memory M | W = 1.48 (p = 0.181); M = 0.83; q_self 0.648, q(1) 0.611, q_∞ 0.435 (N = 9) | circular day-shift null (W = 1) | descriptive |
| (post hoc) overlap with per-room day fields | W = 1.51 (p = 0.171); M = 0.83 | circular day-shift null | – |
| (room rival) largest room only (room 4) | N 9; ρ_split 0.313 (p 0.050); κ̂ 6.89; τ₃ 0.512; τ₃(dc) –; F 0.143 (null 0.158) | – | – |

## Scorecard (period-specific axes)
- **C** 1 where P1 passes (38a, #44): couplings beat the pseudo-null; low power elsewhere.
- **G** 1: the two-room structure shows up as a balanced (factional) block structure (τ₃(dc) ≈ 1 in 38a, #44); the overlap synchrony in #44 disappears once each room's day field is removed (post hoc).
- **D, E** n/a.

## Notes
- Data: `data/processed/H22-private-goals-spin-glass/G40/<unit>/`. Figure: `figures/H22_G40.pdf`.
- Card: `../../README.md` (Observables, Null, Prediction, Amendment 1).

## Round 1b (improved data, 2026-10-04)
*Re-run on the corrected inputs (card section "Round 1b"); round-1 numbers kept above.* DQ6 ground-truth roles (Opus 5's first role recovered), DQ5 statement vectors in two models (bge, gte), DQ5 `style_resid_period` vectors ("styp"), restatements removed ("dedup"), `activity_bins_fixed` for talk spins, and the DQ2 stance channel with the calibrated agent-field null. Data: `data/processed/H22-private-goals-spin-glass/r1b/`.

| Unit | Variant | heterogeneity ρ_split | τ₃(dc) | T_SR / pairs (p>) | T_OP | W (p) | talk ρ_split (p) |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 40 | round 1 | 0.31 (p 0.050) | nan | – / None (p> –) | – | 1.48 (p 0.18) | 0.13 (p 0.286) |
| 40 | bge | 0.31 (p 0.050) | nan | – / None (p> –) | – | 1.46 (p 0.19) | 0.21 (p 0.146) |
| 40 | gte | 0.33 (p 0.043) | nan | – / None (p> –) | – | 2.51 (p 0.02) | 0.21 (p 0.146) |
| 40 | bge styp | 0.32 (p 0.037) | 1.56 | – / None (p> –) | – | 0.34 (p 0.92) | 0.21 (p 0.146) |
| 40 | gte styp | 0.42 (p 0.010) | nan | – / None (p> –) | – | 1.09 (p 0.36) | 0.21 (p 0.146) |
| 40 | bge dedup | 0.26 (p 0.143) | 1.23 | – / None (p> –) | – | 2.11 (p 0.06) | 0.21 (p 0.143) |
| 40 | **stance (DQ2)** | dc split-half 0.20 (agent-field p 0.179) | -0.82 [-14858.19, 2.97] | – / None (p> –) | – | – | neg. pairs 8 vs 1.6 |

