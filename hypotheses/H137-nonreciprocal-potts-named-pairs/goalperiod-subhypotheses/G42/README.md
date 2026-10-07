# H137 × G42: Run your own Youtube channel! (2026-05-18 → 2026-05-25)

**Verdict:** n/a
**Role:** exploratory
**Period:** regime III · mode I · 15-16 agents · rooms [2, 3] · 5 non-reserved days. Units: 42a, 42b (`period_units`). H137 role: pooled fit only (below the precondition).

## Why this period
Listed in the card's replication candidates (own-role week); both units fall below the structural precondition, so they enter only the pooled fit.

Structural counts (2026-10-07, before any follow direction; `results/structure.parquet`): 42a: 16,876 calls, 141 project hops (call), 70 follow hops, 14/10/63 one-way/mutual/none pairs, 5 one-way pairs with a follow hop (17 rows) -> below the precondition; 42b: 25,996 calls, 183 project hops (call), 96 follow hops, 10/13/79 one-way/mutual/none pairs, 2 one-way pairs with a follow hop (20 rows) -> below the precondition.

## Prediction
*Written 2026-10-07, before running H137 on this period.*
- The card's P1 and P3 are pooled predictions; this period contributes rows to them. Per unit (testable units only): θ_name > 0 with CI > 0 (A1 estimator, with the hopper-propensity control), σ_mutual and σ_none inside their nulls (P2), read-minus-in-flight follow rate > 0 (P4).
- Expected here: θ_name small (|θ| < 0.2) with a CI that includes 0. Naming is mostly mutual within active pairs, and named reads are sparse next to the hop rate.
- What counts against H137 here: θ_name < 0 with CI < 0 (the named agent leads, the namer follows), or σ_one no larger than σ_none.
- The decision for every unit depends on S0 (pooled synthetic power at J = 1 ≥ 0.8). If S0 fails, this period's numbers are descriptive.

## Result
*Run 2026-10-07 (exploration data).*

Both units fall below the structural precondition, so no per-unit statistic was computed. Their follow-hop rows (42a, 42b) enter only the pooled fit. H137 is untestable at village counts in round 1 (S0 failed: pooled synthetic power 0.18 at J = 1).

## Scorecard (period-specific axes)
- C adequacy: 0 (no statistic is a valid, powered test; S0 failed).
- D unfitted predictions: 0.
- G ground truth: n/a.

## Notes
- 2026-10-07: folder created with the structural counts and the dated prediction, before any H137 outcome on this period.
- 2026-10-07: round-1 results filled in (descriptive).
