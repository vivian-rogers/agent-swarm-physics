# H137 × G19: Create a popular daily puzzle game like Wordle (2025-11-03 → 2025-11-17)

**Verdict:** pending
**Role:** exploratory
**Period:** regime I · mode C · 7-8 agents · rooms [0] · 10 non-reserved days. Units: 19a, 19b (`period_units`). H137 role: replication.

## Why this period
Replication unit: it meets the structural precondition (>= 20 follow-hop rows in one-way pairs and >= 8 one-way pairs with a follow hop).

Structural counts (2026-10-07, before any follow direction; `results/structure.parquet`): 19a: 30,063 calls, 271 project hops (call), 175 follow hops, 14/7/0 one-way/mutual/none pairs, 14 one-way pairs with a follow hop (281 rows) -> testable; 19b: 3,278 calls, 17 project hops (call), 8 follow hops, 23/5/0 one-way/mutual/none pairs, 19 one-way pairs with a follow hop (38 rows) -> testable.

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
