# H137 × G18: Reduce global poverty as much as you can (2025-10-20 → 2025-11-03)

**Verdict:** pending
**Role:** exploratory
**Period:** regime I · mode C · 7-8 agents · rooms [0] · 10 non-reserved days. Units: 18a, 18b, 18c (`period_units`). H137 role: replication.

## Why this period
Replication unit: it meets the structural precondition (>= 20 follow-hop rows in one-way pairs and >= 8 one-way pairs with a follow hop).

Structural counts (2026-10-07, before any follow direction; `results/structure.parquet`): 18a: 4,187 calls, 17 project hops (call), 7 follow hops, 16/4/0 one-way/mutual/none pairs, 10 one-way pairs with a follow hop (12 rows) -> below the precondition; 18b: 17,163 calls, 243 project hops (call), 131 follow hops, 20/8/0 one-way/mutual/none pairs, 20 one-way pairs with a follow hop (199 rows) -> testable; 18c: 10,599 calls, 52 project hops (call), 19 follow hops, 15/6/0 one-way/mutual/none pairs, 8 one-way pairs with a follow hop (13 rows) -> below the precondition.

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
