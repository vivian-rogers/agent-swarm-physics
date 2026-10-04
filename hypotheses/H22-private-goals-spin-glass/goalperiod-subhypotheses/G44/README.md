# H22 × G44: shared-objective contrast (44; 2026-05-26 → 05-29)

**Verdict:** descriptive
**Role:** exploratory (contrast)
**Period:** regime III · mode C for #best only (fine-tune the leader); #rest chose its own creative goals · 16 → 18 agents · two rooms · 4 days (day-thirds as pseudo-days).

## Why this period
The card names #44 as a contrast. Caveat: only the four #best agents share the objective; the largest room (#rest) is a free-choice room, so its largest-room variant is not a shared-objective contrast.

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
Data: `data/processed/H22-private-goals-spin-glass/G44/<unit>/results.json`; figure: `figures/H22_G44.pdf`.

**Unit 44** (4 days, day-thirds as pseudo-days; N eligible = 11; verdict: descriptive (ferro side, as H22 expects for a shared-objective week))

| Prediction | Observed (90% CI) | Null / reference | Verdict |
| --- | --- | --- | --- |
| P1 heterogeneous content couplings | ρ_split = 0.586; σ_J = 0.1050; N = 9 | per-agent day-permutation null: q95 ρ = 0.369, p = 0.003 | pass |
| P2 SK ratio κ < 1 | κ̂ = 2.76 [1.68, 5.97]; J̄ = 0.0966 | glass < 1 < ferro (uninformative if > 1: drive) | fail |
| P3 drive-robust balance τ₃(dc) < 0.25 | 0.953 [-0.97, 3.01] | SK ≈ 0; factions ≈ 0.5 | indeterminate (CI spans both) |
| P3 (secondary) raw τ₃ | 0.466 [-0.16, 0.63] | SK ≈ 0; ferro/drive → 1 | – |
| P3 (secondary) triangle frustration F | 0.369 (F_w 0.055; p_neg 0.194) | sign shuffle 0.402 [0.345, 0.464], p_low = 0.293 | pass (non-specific, Amendment 1) |
| (desc.) reliable-edge F | 0.300 on 20 triangles | random signs 0.361 | – |
| (desc.) ground-state frustration | 0.070 | sign shuffle 0.163, p_low = 0.059 | – (sign-shuffle null flags balance in most synthetic SK runs: not evidence) |
| (family check) after removing lab×lab block means | τ₃ 0.372, τ₃(dc) 0.818, F 0.333 | F null 0.344, p_low 0.458 | – |
| (secondary) talk couplings | ρ_split 0.121 (p 0.223); κ̂ 1.69; τ₃ –; τ₃(dc) – | pseudo-null | – |
| P5 overlap synchrony W, memory M | W = 3.99 (p = 0.006); M = 0.73; q_self 0.560, q(1) 0.527, q_∞ 0.438 (N = 11) | circular day-shift null (W = 1) | descriptive |
| (post hoc) overlap with per-room day fields | W = 1.03 (p = 0.389); M = -0.62 | circular day-shift null | – |
| (room rival) largest room only (room 3) | N 7; ρ_split 0.255 (p 0.198); κ̂ 6.04; τ₃ 0.751; τ₃(dc) –; F 0.143 (null 0.143) | – | – |

## Scorecard (period-specific axes)
- **C** 1 where P1 passes (38a, #44): couplings beat the pseudo-null; low power elsewhere.
- **G** 1: the two-room structure shows up as a balanced (factional) block structure (τ₃(dc) ≈ 1 in 38a, #44); the overlap synchrony in #44 disappears once each room's day field is removed (post hoc).
- **D, E** n/a.

## Notes
- Data: `data/processed/H22-private-goals-spin-glass/G44/<unit>/`. Figure: `figures/H22_G44.pdf`.
- Card: `../../README.md` (Observables, Null, Prediction, Amendment 1).
