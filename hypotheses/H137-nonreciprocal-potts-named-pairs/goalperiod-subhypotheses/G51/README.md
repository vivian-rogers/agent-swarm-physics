# H137 × G51: Each agent: Maximize your assigned goal! (2026-07-06 → 2026-09-20)

**Verdict:** descriptive
**Role:** exploratory
**Period:** regime III · mode I/K · 21-32 agents · rooms [0, 15] · 45 non-reserved days. Units: 51a, 51b, 51c, 51d, 51e, 51f, 51g, 51h, 51i, 51j, 51k, 51l (`period_units`). H137 role: replication (51a-51l) + native N1 (pooled).

## Why this period
Native N1. The largest naming graph (21-32 agents, units 51a-51l). Direct comparison with H90's failed talk-channel pair test: if project follows show the naming direction that talk did not, the coupling acts on work.

Structural counts (2026-10-07, before any follow direction; `results/structure.parquet`): 51a: 69,317 calls, 2,712 project hops (call), 1,244 follow hops, 58/61/53 one-way/mutual/none pairs, 51 one-way pairs with a follow hop (748 rows) -> testable; 51b: 19,436 calls, 637 project hops (call), 212 follow hops, 36/20/171 one-way/mutual/none pairs, 14 one-way pairs with a follow hop (47 rows) -> testable; 51c: 125,749 calls, 6,073 project hops (call), 1,832 follow hops, 60/49/122 one-way/mutual/none pairs, 45 one-way pairs with a follow hop (928 rows) -> testable; 51d: 100,862 calls, 4,594 project hops (call), 1,571 follow hops, 77/59/138 one-way/mutual/none pairs, 52 one-way pairs with a follow hop (1045 rows) -> testable; 51e: 66,292 calls, 3,456 project hops (call), 1,216 follow hops, 59/62/143 one-way/mutual/none pairs, 49 one-way pairs with a follow hop (552 rows) -> testable; 51f: 93,694 calls, 5,102 project hops (call), 1,759 follow hops, 65/52/158 one-way/mutual/none pairs, 55 one-way pairs with a follow hop (1061 rows) -> testable; 51g: 260,133 calls, 14,207 project hops (call), 4,367 follow hops, 76/85/112 one-way/mutual/none pairs, 56 one-way pairs with a follow hop (1939 rows) -> testable; 51h: 77,613 calls, 5,128 project hops (call), 1,522 follow hops, 42/25/227 one-way/mutual/none pairs, 31 one-way pairs with a follow hop (943 rows) -> testable; 51i: 37,772 calls, 1,895 project hops (call), 813 follow hops, 32/24/270 one-way/mutual/none pairs, 26 one-way pairs with a follow hop (705 rows) -> testable; 51j: 39,700 calls, 1,996 project hops (call), 817 follow hops, 54/15/283 one-way/mutual/none pairs, 46 one-way pairs with a follow hop (818 rows) -> testable; 51k: 18,043 calls, 850 project hops (call), 339 follow hops, 37/19/353 one-way/mutual/none pairs, 28 one-way pairs with a follow hop (215 rows) -> testable; 51l: 19,596 calls, 1,040 project hops (call), 432 follow hops, 37/21/388 one-way/mutual/none pairs, 25 one-way pairs with a follow hop (312 rows) -> testable.

## Prediction
*Written 2026-10-07, before running H137 on this period.*
- The card's P1 and P3 are pooled predictions; this period contributes rows to them. Per unit (testable units only): θ_name > 0 with CI > 0 (A1 estimator, with the hopper-propensity control), σ_mutual and σ_none inside their nulls (P2), read-minus-in-flight follow rate > 0 (P4).
- Expected here: θ_name small (|θ| < 0.2) with a CI that includes 0. Naming is mostly mutual within active pairs, and named reads are sparse next to the hop rate.
- What counts against H137 here: θ_name < 0 with CI < 0 (the named agent leads, the namer follows), or σ_one no larger than σ_none.
- The decision for every unit depends on S0 (pooled synthetic power at J = 1 ≥ 0.8). If S0 fails, this period's numbers are descriptive.
- **N1 (G51 pooled over 51a-51l):** θ_name > 0 with CI > 0. Credence 0.15.

## Result
*Run 2026-10-07 (exploration data).*

All numbers are descriptive. S0 failed (pooled synthetic power at J = 1 is 0.18), so H137 is untestable at village counts and no per-period verdict is possible. A1 is the amended θ_name with the hopper-propensity control; the card's θ_name is biased negative in the no-following world (W0 −0.21 ± 0.09). N1b is the propensity-adjusted direction null (A2). Pair-bootstrap CIs; N2 within-stratum permutation p (500 draws per unit). Data: `data/processed/H137-nonreciprocal-potts-named-pairs/results/units.parquet`; estimates rows `h137_*` (role replication).

| Unit | θ_name A1 [95% CI] (N2 p) | θ_name card [95% CI] | mean A one-way (N1b p) | σ_mutual / σ_none N1b p | σ_one − σ_none | O4 read − in-flight (×10⁻³) |
| --- | --- | --- | --- | --- | --- | --- |
| 51a | -0.10 [-0.39, +0.18] (0.689) | -0.53 [-0.93, -0.16] | -0.52 (0.661) | 0.062 / 0.946 | +10.7 | +2.4 [-3.7, +8.6] |
| 51b | +0.52 [-0.84, +1.75] (0.385) | +0.90 [-0.01, +1.81] | +0.39 (0.344) | 0.013 / 0.312 | +1.9 | +4.8 [-1.2, +15.7] |
| 51c | -0.13 [-0.44, +0.13] (0.816) | +0.22 [-0.73, +0.89] | -1.09 (0.970) | 0.202 / 0.542 | +25.8 | +4.4 [-4.8, +13.1] |
| 51d | +0.12 [-0.10, +0.59] (0.289) | -1.10 [-1.84, -0.36] | -0.66 (0.035) | 0.133 / 0.263 | +5.3 | +6.1 [+0.3, +11.5] |
| 51e | -0.05 [-0.52, +0.25] (0.679) | -0.04 [-1.04, +0.63] | -0.54 (0.816) | 0.354 / 0.617 | +7.4 | +8.4 [-0.8, +19.1] |
| 51f | -0.30 [-0.70, +0.09] (0.842) | -0.84 [-1.35, -0.36] | -0.64 (0.995) | 0.001 / 0.009 | +8.5 | +12.0 [+5.6, +19.5] |
| 51g | -0.23 [-0.61, +0.10] (0.976) | -0.91 [-2.09, +0.01] | -0.98 (0.714) | 0.001 / 0.845 | +26.7 | +20.2 [+12.1, +28.5] |
| 51h | +0.03 [-0.49, +0.54] (0.758) | -0.80 [-1.61, -0.02] | -1.16 (0.995) | 0.043 / 0.878 | +28.9 | +7.9 [-2.8, +19.4] |
| 51i | -0.46 [-1.19, +0.05] (0.960) | -1.68 [-2.64, -1.01] | -1.74 (0.849) | 0.911 / 0.001 | +21.4 | +6.1 [-8.4, +20.8] |
| 51j | -0.03 [-0.66, +0.66] (0.635) | -1.52 [-2.29, -0.91] | -1.47 (0.404) | 0.003 / 0.025 | -2.6 | -2.2 [-10.4, +6.1] |
| 51k | +0.47 [-0.14, +1.27] (0.168) | -0.26 [-1.18, +0.59] | -0.24 (0.155) | 0.711 / 0.068 | +0.0 | +5.3 [-11.7, +24.6] |
| 51l | +0.16 [-0.59, +0.77] (0.499) | -0.62 [-1.94, +0.17] | -0.82 (0.735) | 0.220 / 0.302 | +3.9 | -2.5 [-20.2, +14.0] |

- θ_name (A1) CI above 0 in 0 of 12 testable units and below 0 in 0.
- **N1 native (51a–51l pooled):** θ_name A1 -0.07 [-0.21, +0.07] (N2 p 0.926; 478 one-way pairs, 9313 rows). The card's θ_name is -0.78 [-1.04, -0.54], the sign the propensity bias makes. The prediction (θ_name > 0, CI > 0) is not met, and the test has no power (S0). Like H90's talk-channel pair test, the project channel shows no naming direction.

## Scorecard (period-specific axes)
- C adequacy: 0 (no statistic is a valid, powered test; S0 failed).
- D unfitted predictions: 0.
- G ground truth: n/a.

## Notes
- 2026-10-07: folder created with the structural counts and the dated prediction, before any H137 outcome on this period.
- 2026-10-07: round-1 results filled in (descriptive).
