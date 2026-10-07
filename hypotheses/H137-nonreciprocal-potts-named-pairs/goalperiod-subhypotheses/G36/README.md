# H137 × G36: Interact with other AI agents outside the Village! (2026-03-23 → 2026-03-30)

**Verdict:** pending
**Role:** exploratory
**Period:** regime II · mode C · 12 agents · rooms [2, 3] · 5 non-reserved days. Units: 36a, 36b, 36c (`period_units`). H137 role: replication.

## Why this period
Replication unit: it meets the structural precondition (>= 20 follow-hop rows in one-way pairs and >= 8 one-way pairs with a follow hop).

Structural counts (2026-10-07, before any follow direction; `results/structure.parquet`): 36a: 7,090 calls, 527 project hops (call), 257 follow hops, 12/14/22 one-way/mutual/none pairs, 12 one-way pairs with a follow hop (151 rows) -> testable; 36b: 13,487 calls, 962 project hops (call), 551 follow hops, 19/10/18 one-way/mutual/none pairs, 19 one-way pairs with a follow hop (626 rows) -> testable; 36c: 14,714 calls, 1,336 project hops (call), 830 follow hops, 18/16/18 one-way/mutual/none pairs, 18 one-way pairs with a follow hop (778 rows) -> testable.

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
