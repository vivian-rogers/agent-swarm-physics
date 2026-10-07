# H137 × G38: Choose a charity and raise as much money as you can for it (2026-04-02 → 2026-04-27)

**Verdict:** descriptive
**Role:** exploratory
**Period:** regime III · mode C · 12-14 agents · rooms [2, 3] · 17 non-reserved days. Units: 38a, 38b, 38c, 38d, 38e (`period_units`). H137 role: replication (38a, 38e) + native N2.

## Why this period
Native N2. Two rooms (#best, #rest) route reading. One-way named pairs in the same room should carry the asymmetry; cross-room one-way pairs (rarely read) should not. The longest shared-goal week (17 days; units 38a-38e).

Structural counts (2026-10-07, before any follow direction; `results/structure.parquet`): 38a: 56,955 calls, 1,744 project hops (call), 833 follow hops, 19/8/33 one-way/mutual/none pairs, 19 one-way pairs with a follow hop (1009 rows) -> testable; 38b: 19,007 calls, 189 project hops (call), 98 follow hops, 8/5/47 one-way/mutual/none pairs, 6 one-way pairs with a follow hop (117 rows) -> below the precondition; 38c: 6,996 calls, 45 project hops (call), 21 follow hops, 9/6/57 one-way/mutual/none pairs, 5 one-way pairs with a follow hop (24 rows) -> below the precondition; 38d: 12,592 calls, 51 project hops (call), 16 follow hops, 9/7/57 one-way/mutual/none pairs, 6 one-way pairs with a follow hop (19 rows) -> below the precondition; 38e: 21,705 calls, 190 project hops (call), 85 follow hops, 17/2/54 one-way/mutual/none pairs, 9 one-way pairs with a follow hop (95 rows) -> testable.

## Prediction
*Written 2026-10-07, before running H137 on this period.*
- The card's P1 and P3 are pooled predictions; this period contributes rows to them. Per unit (testable units only): θ_name > 0 with CI > 0 (A1 estimator, with the hopper-propensity control), σ_mutual and σ_none inside their nulls (P2), read-minus-in-flight follow rate > 0 (P4).
- Expected here: θ_name small (|θ| < 0.2) with a CI that includes 0. Naming is mostly mutual within active pairs, and named reads are sparse next to the hop rate.
- What counts against H137 here: θ_name < 0 with CI < 0 (the named agent leads, the namer follows), or σ_one no larger than σ_none.
- The decision for every unit depends on S0 (pooled synthetic power at J = 1 ≥ 0.8). If S0 fails, this period's numbers are descriptive.
- **N2 (G38 rooms):** θ_name > 0 in same-room one-way pairs, θ_name ≈ 0 in cross-room pairs. Credence 0.2.

## Result
*Run 2026-10-07 (exploration data).*

All numbers are descriptive. S0 failed (pooled synthetic power at J = 1 is 0.18), so H137 is untestable at village counts and no per-period verdict is possible. A1 is the amended θ_name with the hopper-propensity control; the card's θ_name is biased negative in the no-following world (W0 −0.21 ± 0.09). N1b is the propensity-adjusted direction null (A2). Pair-bootstrap CIs; N2 within-stratum permutation p (500 draws per unit). Data: `data/processed/H137-nonreciprocal-potts-named-pairs/results/units.parquet`; estimates rows `h137_*` (role replication).

| Unit | θ_name A1 [95% CI] (N2 p) | θ_name card [95% CI] | mean A one-way (N1b p) | σ_mutual / σ_none N1b p | σ_one − σ_none | O4 read − in-flight (×10⁻³) |
| --- | --- | --- | --- | --- | --- | --- |
| 38a | +0.18 [-0.57, +0.63] (0.483) | +0.07 [-1.09, +1.03] | -0.75 (0.786) | 0.342 / 0.143 | +21.5 | +8.9 [-3.6, +22.5] |
| 38e | -1.13 [-2.81, -0.05] (0.940) | -0.52 [-1.40, +1.16] | -0.41 (0.928) | 0.764 / 0.244 | +1.4 | +35.7 [+0.0, +149.1] |

- θ_name (A1) CI above 0 in 0 of 2 testable units and below 0 in 1.
- **N2 native (rooms):** same-room one-way pairs θ_name A1 +0.15 [-0.20, +0.40] (N2 p 0.486; 44 pairs). Cross-room: 1 one-way pair with 27 follow rows, not estimable. Agents almost never follow across rooms, so the room contrast cannot be formed. Same-room effect: none detected (CI includes 0).

## Scorecard (period-specific axes)
- C adequacy: 0 (no statistic is a valid, powered test; S0 failed).
- D unfitted predictions: 0.
- G ground truth: n/a.

## Notes
- 2026-10-07: folder created with the structural counts and the dated prediction, before any H137 outcome on this period.
- 2026-10-07: round-1 results filled in (descriptive).
