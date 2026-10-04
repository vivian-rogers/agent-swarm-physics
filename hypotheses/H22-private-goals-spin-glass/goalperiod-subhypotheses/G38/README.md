# H22 × G38: shared-objective contrast (38a / 38b / 38c; 2026-04-02 → 04-24)

**Verdict:** descriptive
**Role:** exploratory (contrast)
**Period:** regime III · mode C (charity fundraiser, operator-specified) · 12 → 14 agents · two rooms (#best, #rest) · 17 days, split at 04-14 (NE17 outreach approval) and 04-20 (NE18 history search): 38a 8 days (counted, low power), 38b 4 days, 38c 5 days (day-thirds as pseudo-days).

## Why this period
The longest shared-objective period in regime III, with the same scaffold era as #51. The contrast for 'shared goal = ferromagnet'.

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
Data: `data/processed/H22-private-goals-spin-glass/G38/<unit>/results.json`; figure: `figures/H22_G38.pdf`.

**Unit 38a** (8 days; N eligible = 9; verdict: descriptive (ferro side, as H22 expects for a shared-objective week))

| Prediction | Observed (90% CI) | Null / reference | Verdict |
| --- | --- | --- | --- |
| P1 heterogeneous content couplings | ρ_split = 0.564; σ_J = 0.0921; N = 8 | per-agent day-permutation null: q95 ρ = 0.494, p = 0.023 | pass |
| P2 SK ratio κ < 1 | κ̂ = 2.99 [1.88, 6.84]; J̄ = 0.0972 | glass < 1 < ferro (uninformative if > 1: drive) | fail |
| P3 drive-robust balance τ₃(dc) < 0.25 | 1.026 [-0.29, 1.54] | SK ≈ 0; factions ≈ 0.5 | indeterminate (CI spans both) |
| P3 (secondary) raw τ₃ | 0.460 [0.00, 0.56] | SK ≈ 0; ferro/drive → 1 | – |
| P3 (secondary) triangle frustration F | 0.250 (F_w 0.037; p_neg 0.107) | sign shuffle 0.275 [0.214, 0.321], p_low = 0.331 | pass (non-specific, Amendment 1) |
| (desc.) reliable-edge F | 0.238 on 21 triangles | random signs 0.244 | – |
| (desc.) ground-state frustration | 0.032 | sign shuffle 0.101, p_low = 0.059 | – (sign-shuffle null flags balance in most synthetic SK runs: not evidence) |
| (family check) after removing lab×lab block means | τ₃ 0.746, τ₃(dc) 0.899, F 0.000 | F null 0.394, p_low 0.000 | – |
| (secondary) talk couplings | ρ_split -0.202 (p 0.877); κ̂ –; τ₃ –; τ₃(dc) – | pseudo-null | – |
| P5 overlap synchrony W, memory M | W = 3.14 (p = 0.001); M = 0.78; q_self 0.689, q(1) 0.625, q_∞ 0.398 (N = 9) | circular day-shift null (W = 1) | pass |
| (post hoc) overlap with per-room day fields | W = 1.98 (p = 0.018); M = 1.17 | circular day-shift null | – |
| (room rival) largest room only (room 3) | N 5; ρ_split 0.395 (p 0.139); κ̂ 6.46; τ₃ 0.489; τ₃(dc) 1.016; F 0.000 (null 0.000) | – | – |

**Unit 38b** (4 days, day-thirds as pseudo-days; N eligible = 6; verdict: descriptive (noise floor))

| Prediction | Observed (90% CI) | Null / reference | Verdict |
| --- | --- | --- | --- |
| P1 heterogeneous content couplings | ρ_split = 0.238; σ_J = 0.0617; N = 6 | per-agent day-permutation null: q95 ρ = 0.586, p = 0.276 | fail |
| P2 SK ratio κ < 1 | κ̂ = 1.90 [0.63, 4.14]; J̄ = 0.0479 | glass < 1 < ferro (uninformative if > 1: drive) | fail |
| P3 drive-robust balance τ₃(dc) < 0.25 | 0.073 [-5.71, 0.68] | SK ≈ 0; factions ≈ 0.5 | indeterminate (CI spans both); uninterpretable without P1 |
| P3 (secondary) raw τ₃ | -0.481 [-6.96, 0.07] | SK ≈ 0; ferro/drive → 1 | – |
| P3 (secondary) triangle frustration F | 0.400 (F_w 0.111; p_neg 0.333) | sign shuffle 0.516 [0.400, 0.700], p_low = 0.255 | pass (non-specific, Amendment 1) |
| (desc.) reliable-edge F | 0.600 on 5 triangles | random signs 0.481 | – |
| (desc.) ground-state frustration | 0.049 | sign shuffle 0.137, p_low = 0.050 | – (sign-shuffle null flags balance in most synthetic SK runs: not evidence) |
| (family check) after removing lab×lab block means | τ₃ -0.167, τ₃(dc) -0.097, F 0.200 | F null 0.098, p_low 0.985 | – |
| (secondary) talk couplings | ρ_split -0.166 (p 0.641); κ̂ –; τ₃ –; τ₃(dc) – | pseudo-null | – |
| P5 overlap synchrony W, memory M | W = 0.72 (p = 0.591); M = 0.78; q_self 0.822, q(1) 0.805, q_∞ 0.744 (N = 6) | circular day-shift null (W = 1) | descriptive |
| (post hoc) overlap with per-room day fields | W = 0.21 (p = 0.926); M = 7.33 | circular day-shift null | – |

**Unit 38c** (5 days, day-thirds as pseudo-days; N eligible = 6; verdict: descriptive (noise floor))

| Prediction | Observed (90% CI) | Null / reference | Verdict |
| --- | --- | --- | --- |
| P1 heterogeneous content couplings | ρ_split = -0.577; σ_J = –; N = 5 | per-agent day-permutation null: q95 ρ = 0.605, p = 0.937 | fail |
| P2 SK ratio κ < 1 | κ̂ = – [0.47, 7.80]; J̄ = 0.0489 | glass < 1 < ferro (uninformative if > 1: drive) | fail |
| P3 drive-robust balance τ₃(dc) < 0.25 | – [-49.48, 67.66] | SK ≈ 0; factions ≈ 0.5 | indeterminate (CI spans both); uninterpretable without P1 |
| P3 (secondary) raw τ₃ | – [-2.92, 75.14] | SK ≈ 0; ferro/drive → 1 | – |
| P3 (secondary) triangle frustration F | 0.500 (F_w 0.320; p_neg 0.300) | sign shuffle 0.539 [0.300, 0.700], p_low = 0.651 | pass (non-specific, Amendment 1) |
| (desc.) reliable-edge F | 0.333 on 3 triangles | random signs 0.318 | – |
| (desc.) ground-state frustration | 0.126 | sign shuffle 0.191, p_low = 0.178 | – (sign-shuffle null flags balance in most synthetic SK runs: not evidence) |
| (family check) after removing lab×lab block means | τ₃ –, τ₃(dc) –, F 0.400 | F null 0.238, p_low 0.946 | – |
| (secondary) talk couplings | ρ_split -0.225 (p 0.757); κ̂ –; τ₃ –; τ₃(dc) – | pseudo-null | – |
| P5 overlap synchrony W, memory M | W = 0.68 (p = 0.651); M = 0.83; q_self 0.732, q(1) 0.693, q_∞ 0.504 (N = 6) | circular day-shift null (W = 1) | descriptive |
| (post hoc) overlap with per-room day fields | W = 1.00 (p = 0.455); M = 3.51 | circular day-shift null | – |
| (room rival) largest room only (room 3) | N 4; ρ_split 0.138 (p 0.376); κ̂ 4.53; τ₃ 70.782; τ₃(dc) –; F 0.500 (null 0.500) | – | – |

## Scorecard (period-specific axes)
- **C** 1 where P1 passes (38a, #44): couplings beat the pseudo-null; low power elsewhere.
- **G** 1: the two-room structure shows up as a balanced (factional) block structure (τ₃(dc) ≈ 1 in 38a, #44); the overlap synchrony in #44 disappears once each room's day field is removed (post hoc).
- **D, E** n/a.

## Notes
- Data: `data/processed/H22-private-goals-spin-glass/G38/<unit>/`. Figure: `figures/H22_G38.pdf`.
- Card: `../../README.md` (Observables, Null, Prediction, Amendment 1).
