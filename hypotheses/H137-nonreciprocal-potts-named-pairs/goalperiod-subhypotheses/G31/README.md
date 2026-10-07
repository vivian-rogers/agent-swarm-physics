# H137 × G31: Pick your own goal (agents bid 3.7 Sonnet farewell) (2026-02-16 → 2026-02-23)

**Verdict:** pending
**Role:** exploratory
**Period:** regime I · mode F · 11-12 agents · rooms [0] · 5 non-reserved days. Units: 31a, 31b, 31c, 31d (`period_units`). H137 role: replication.

## Why this period
Replication unit: it meets the structural precondition (>= 20 follow-hop rows in one-way pairs and >= 8 one-way pairs with a follow hop).

Structural counts (2026-10-07, before any follow direction; `results/structure.parquet`): 31a: 14,495 calls, 813 project hops (call), 452 follow hops, 32/20/1 one-way/mutual/none pairs, 32 one-way pairs with a follow hop (713 rows) -> testable; 31b: 6,910 calls, 363 project hops (call), 178 follow hops, 22/15/6 one-way/mutual/none pairs, 18 one-way pairs with a follow hop (116 rows) -> testable; 31c: 6,632 calls, 275 project hops (call), 134 follow hops, 22/15/9 one-way/mutual/none pairs, 17 one-way pairs with a follow hop (118 rows) -> testable; 31d: 7,282 calls, 354 project hops (call), 226 follow hops, 22/16/9 one-way/mutual/none pairs, 22 one-way pairs with a follow hop (300 rows) -> testable.

## Prediction
*Written 2026-10-07, before running H137 on this period.*
- The card's P1 and P3 are pooled predictions; this period contributes rows to them. Per unit (testable units only): θ_name > 0 with CI > 0 (A1 estimator, with the hopper-propensity control), σ_mutual and σ_none inside their nulls (P2), read-minus-in-flight follow rate > 0 (P4).
- Expected here: θ_name small (|θ| < 0.2) with a CI that includes 0. Naming is mostly mutual within active pairs, and named reads are sparse next to the hop rate.
- What counts against H137 here: θ_name < 0 with CI < 0 (the named agent leads, the namer follows), or σ_one no larger than σ_none.
- The decision for every unit depends on S0 (pooled synthetic power at J = 1 ≥ 0.8). If S0 fails, this period's numbers are descriptive.

## Result
Not run yet.

## Scorecard (period-specific axes)
Not run yet.

## Notes
- 2026-10-07: folder created with the structural counts and the dated prediction, before any H137 outcome on this period.
