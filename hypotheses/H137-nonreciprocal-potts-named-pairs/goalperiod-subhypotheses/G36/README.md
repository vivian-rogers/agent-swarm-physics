# H137 × G36: Interact with other AI agents outside the Village! (2026-03-23 → 2026-03-30)

**Verdict:** descriptive
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
*Run 2026-10-07 (exploration data).*

All numbers are descriptive. S0 failed (pooled synthetic power at J = 1 is 0.18), so H137 is untestable at village counts and no per-period verdict is possible. A1 is the amended θ_name with the hopper-propensity control; the card's θ_name is biased negative in the no-following world (W0 −0.21 ± 0.09). N1b is the propensity-adjusted direction null (A2). Pair-bootstrap CIs; N2 within-stratum permutation p (500 draws per unit). Data: `data/processed/H137-nonreciprocal-potts-named-pairs/results/units.parquet`; estimates rows `h137_*` (role replication).

| Unit | θ_name A1 [95% CI] (N2 p) | θ_name card [95% CI] | mean A one-way (N1b p) | σ_mutual / σ_none N1b p | σ_one − σ_none | O4 read − in-flight (×10⁻³) |
| --- | --- | --- | --- | --- | --- | --- |
| 36a | +0.19 [-0.38, +0.69] (0.230) | +0.30 [-0.38, +0.92] | +0.13 (0.314) | 0.197 / 0.555 | +1.3 | -30.5 [-72.3, +7.9] |
| 36b | +0.27 [-0.03, +0.51] (0.098) | +0.57 [+0.06, +0.93] | +0.48 (0.023) | 0.373 / 0.635 | +3.2 | +32.7 [-14.8, +83.2] |
| 36c | +0.13 [-0.20, +0.44] (0.531) | -0.08 [-0.57, +0.42] | +0.36 (0.452) | 0.068 / 0.840 | +5.1 | +24.2 [-0.8, +55.9] |

- θ_name (A1) CI above 0 in 0 of 3 testable units and below 0 in 0.

## Scorecard (period-specific axes)
- C adequacy: 0 (no statistic is a valid, powered test; S0 failed).
- D unfitted predictions: 0.
- G ground truth: n/a.

## Notes
- 2026-10-07: folder created with the structural counts and the dated prediction, before any H137 outcome on this period.
- 2026-10-07: round-1 results filled in (descriptive).
