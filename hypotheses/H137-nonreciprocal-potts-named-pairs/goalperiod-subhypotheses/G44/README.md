# H137 × G44: Finetune your leader! (2026-05-26 → 2026-06-01)

**Verdict:** pending
**Role:** exploratory
**Period:** regime III · mode C · 17-18 agents · rooms [2, 3] · 4 non-reserved days. Units: 44a, 44b (`period_units`). H137 role: replication + native N3 (descriptive).

## Why this period
Native N3 (descriptive). The assigned #best room's hop graph is a tree (H129). Follow currents in #best should run toward the assigned repo whatever the naming; in #rest any asymmetry should follow naming.

Structural counts (2026-10-07, before any follow direction; `results/structure.parquet`): 44a: 12,343 calls, 731 project hops (call), 288 follow hops, 16/20/86 one-way/mutual/none pairs, 13 one-way pairs with a follow hop (103 rows) -> testable; 44b: 14,594 calls, 691 project hops (call), 277 follow hops, 25/12/98 one-way/mutual/none pairs, 21 one-way pairs with a follow hop (300 rows) -> testable.

## Prediction
*Written 2026-10-07, before running H137 on this period.*
- The card's P1 and P3 are pooled predictions; this period contributes rows to them. Per unit (testable units only): θ_name > 0 with CI > 0 (A1 estimator, with the hopper-propensity control), σ_mutual and σ_none inside their nulls (P2), read-minus-in-flight follow rate > 0 (P4).
- Expected here: θ_name small (|θ| < 0.2) with a CI that includes 0. Naming is mostly mutual within active pairs, and named reads are sparse next to the hop rate.
- What counts against H137 here: θ_name < 0 with CI < 0 (the named agent leads, the namer follows), or σ_one no larger than σ_none.
- The decision for every unit depends on S0 (pooled synthetic power at J = 1 ≥ 0.8). If S0 fails, this period's numbers are descriptive.
- **N3 (G44, descriptive):** in #best the follow current runs toward the assigned repo regardless of naming; in #rest any asymmetry follows naming. No verdict.

## Result
Not run yet.

## Scorecard (period-specific axes)
Not run yet.

## Notes
- 2026-10-07: folder created with the structural counts and the dated prediction, before any H137 outcome on this period.
