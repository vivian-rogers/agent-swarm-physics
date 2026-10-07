# H137 × G20: Start a Substack and join the blogosphere (2025-11-17 → 2025-12-01)

**Verdict:** descriptive
**Role:** exploratory
**Period:** regime I · mode I · 8-10 agents · rooms [0] · 10 non-reserved days. Units: 20a, 20b, 20c, 20d (`period_units`). H137 role: replication.

## Why this period
Replication unit: it meets the structural precondition (>= 20 follow-hop rows in one-way pairs and >= 8 one-way pairs with a follow hop).

Structural counts (2026-10-07, before any follow direction; `results/structure.parquet`): 20a: 8,009 calls, 54 project hops (call), 23 follow hops, 17/11/0 one-way/mutual/none pairs, 12 one-way pairs with a follow hop (17 rows) -> below the precondition; 20b: 4,345 calls, 10 project hops (call), 3 follow hops, 23/1/3 one-way/mutual/none pairs, 3 one-way pairs with a follow hop (3 rows) -> below the precondition; 20c: 15,354 calls, 50 project hops (call), 12 follow hops, 25/8/2 one-way/mutual/none pairs, 5 one-way pairs with a follow hop (10 rows) -> below the precondition; 20d: 18,324 calls, 47 project hops (call), 18 follow hops, 27/18/0 one-way/mutual/none pairs, 18 one-way pairs with a follow hop (28 rows) -> testable.

## Prediction
*Written 2026-10-07, before running H137 on this period.*
- The card's P1 and P3 are pooled predictions; this period contributes rows to them. Per unit (testable units only): θ_name > 0 with CI > 0 (A1 estimator, with the hopper-propensity control), σ_mutual and σ_none inside their nulls (P2), read-minus-in-flight follow rate > 0 (P4).
- Expected here: θ_name small (|θ| < 0.2) with a CI that includes 0. Naming is mostly mutual within active pairs, and named reads are sparse next to the hop rate.
- What counts against H137 here: θ_name < 0 with CI < 0 (the named agent leads, the namer follows), or σ_one no larger than σ_none.
- The decision for every unit depends on S0 (pooled synthetic power at J = 1 ≥ 0.8). If S0 fails, this period's numbers are descriptive.

## Result
*Run 2026-10-07 (exploration data).*

All numbers are descriptive. S0 failed (pooled synthetic power at J = 1 is 0.18), so H137 is untestable at village counts and no per-period verdict is possible. A1 is the amended θ_name with the hopper-propensity control; the card's θ_name is biased negative in the no-following world (W0 −0.21 ± 0.09). N1b is the propensity-adjusted direction null (A2). Pair-bootstrap CIs; N2 within-stratum permutation p (500 draws per unit). Data: `data/processed/H137-nonreciprocal-potts-named-pairs/results/units.parquet`; estimates rows `h137_*` (role replication).

| Unit | θ_name A1 [95% CI] (N2 p) | θ_name card [95% CI] | mean A one-way (N1b p) | σ_mutual / σ_none N1b p | σ_one − σ_none | O4 read − in-flight (×10⁻³) |
| --- | --- | --- | --- | --- | --- | --- |
| 20d | +0.34 [-0.70, +2.50] (0.365) | +0.38 [-0.69, +2.00] | -0.07 (0.223) | 0.451 / – | – | -2.8 [-12.7, +4.3] |

- θ_name (A1) CI above 0 in 0 of 1 testable units and below 0 in 0.

## Scorecard (period-specific axes)
- C adequacy: 0 (no statistic is a valid, powered test; S0 failed).
- D unfitted predictions: 0.
- G ground truth: n/a.

## Notes
- 2026-10-07: folder created with the structural counts and the dated prediction, before any H137 outcome on this period.
- 2026-10-07: round-1 results filled in (descriptive).
