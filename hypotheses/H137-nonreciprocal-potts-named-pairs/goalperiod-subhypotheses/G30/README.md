# H137 × G30: Adopt a park and get it cleaned! (2026-02-09 → 2026-02-16)

**Verdict:** pending
**Role:** exploratory
**Period:** regime I · mode C · 11 agents · rooms [0] · 5 non-reserved days. Units: 30a, 30b (`period_units`). H137 role: replication.

## Why this period
Replication unit: it meets the structural precondition (>= 20 follow-hop rows in one-way pairs and >= 8 one-way pairs with a follow hop).

Structural counts (2026-10-07, before any follow direction; `results/structure.parquet`): 30a: 6,672 calls, 100 project hops (call), 87 follow hops, 27/9/6 one-way/mutual/none pairs, 27 one-way pairs with a follow hop (238 rows) -> testable; 30b: 25,514 calls, 849 project hops (call), 730 follow hops, 35/17/1 one-way/mutual/none pairs, 35 one-way pairs with a follow hop (2082 rows) -> testable.

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
