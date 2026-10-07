# H137 × G51: Each agent: Maximize your assigned goal! (2026-07-06 → 2026-09-20)

**Verdict:** pending
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
Not run yet.

## Scorecard (period-specific axes)
Not run yet.

## Notes
- 2026-10-07: folder created with the structural counts and the dated prediction, before any H137 outcome on this period.
