# H137 × G30: Adopt a park and get it cleaned! (2026-02-09 → 2026-02-16)

**Verdict:** descriptive
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
*Run 2026-10-07 (exploration data).*

All numbers are descriptive. S0 failed (pooled synthetic power at J = 1 is 0.18), so H137 is untestable at village counts and no per-period verdict is possible. A1 is the amended θ_name with the hopper-propensity control; the card's θ_name is biased negative in the no-following world (W0 −0.21 ± 0.09). N1b is the propensity-adjusted direction null (A2). Pair-bootstrap CIs; N2 within-stratum permutation p (500 draws per unit). Data: `data/processed/H137-nonreciprocal-potts-named-pairs/results/units.parquet`; estimates rows `h137_*` (role replication).

| Unit | θ_name A1 [95% CI] (N2 p) | θ_name card [95% CI] | mean A one-way (N1b p) | σ_mutual / σ_none N1b p | σ_one − σ_none | O4 read − in-flight (×10⁻³) |
| --- | --- | --- | --- | --- | --- | --- |
| 30a | -0.78 [-1.32, -0.23] (1.000) | -0.41 [-1.24, +0.71] | +0.00 (0.990) | 0.803 / 0.958 | +1.0 | -25.5 [-118.9, +42.3] |
| 30b | -0.01 [-0.17, +0.16] (0.457) | -0.45 [-0.68, -0.13] | +0.01 (0.860) | 0.939 / 0.361 | +9.8 | -12.4 [-35.8, +9.3] |

- θ_name (A1) CI above 0 in 0 of 2 testable units and below 0 in 1.

## Scorecard (period-specific axes)
- C adequacy: 0 (no statistic is a valid, powered test; S0 failed).
- D unfitted predictions: 0.
- G ground truth: n/a.

## Notes
- 2026-10-07: folder created with the structural counts and the dated prediction, before any H137 outcome on this period.
- 2026-10-07: round-1 results filled in (descriptive).
