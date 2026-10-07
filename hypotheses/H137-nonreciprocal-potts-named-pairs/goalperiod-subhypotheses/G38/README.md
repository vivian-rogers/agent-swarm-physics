# H137 × G38: Choose a charity and raise as much money as you can for it (2026-04-02 → 2026-04-27)

**Verdict:** pending
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
Not run yet.

## Scorecard (period-specific axes)
Not run yet.

## Notes
- 2026-10-07: folder created with the structural counts and the dated prediction, before any H137 outcome on this period.
