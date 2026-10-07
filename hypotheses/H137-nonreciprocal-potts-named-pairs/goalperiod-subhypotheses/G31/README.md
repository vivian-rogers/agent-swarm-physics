# H137 × G31: Pick your own goal (agents bid 3.7 Sonnet farewell) (2026-02-16 → 2026-02-23)

**Verdict:** descriptive
**Role:** exploratory
**Period:** regime I · mode F · 11-12 agents · rooms [0] · 5 non-reserved days. Units: 31a, 31b, 31c, 31d (`period_units`). H137 role: replication.

## Why this period
Replication unit: it meets the structural precondition (>= 20 follow-hop rows in one-way pairs and >= 8 one-way pairs with a follow hop).

Structural counts (2026-10-07, before any follow direction; `results/structure.parquet`): 31a: 14,495 calls, 813 project hops (call), 452 follow hops, 32/20/1 one-way/mutual/none pairs, 32 one-way pairs with a follow hop (713 rows) -> testable; 31b: 6,910 calls, 363 project hops (call), 178 follow hops, 22/15/6 one-way/mutual/none pairs, 18 one-way pairs with a follow hop (116 rows) -> testable; 31c: 6,632 calls, 275 project hops (call), 134 follow hops, 22/15/9 one-way/mutual/none pairs, 17 one-way pairs with a follow hop (118 rows) -> testable; 31d: 7,282 calls, 354 project hops (call), 226 follow hops, 22/16/9 one-way/mutual/none pairs, 22 one-way pairs with a follow hop (300 rows) -> testable.

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
| 31a | -0.14 [-0.42, +0.06] (0.840) | -0.58 [-0.92, -0.28] | -0.46 (0.909) | 0.167 / 0.097 | -6.1 | +1.2 [-13.4, +14.0] |
| 31b | -0.12 [-0.97, +0.78] (0.565) | +0.05 [-0.59, +0.71] | -0.00 (0.743) | 0.115 / 0.251 | +1.5 | +5.3 [+0.0, +11.0] |
| 31c | +0.12 [-0.51, +1.35] (0.437) | +0.36 [-0.44, +1.47] | +0.03 (0.267) | 0.693 / 0.811 | -7.5 | +5.2 [-8.4, +17.6] |
| 31d | -0.03 [-0.41, +0.24] (0.675) | -0.36 [-0.87, +0.09] | -0.16 (0.400) | 0.972 / 0.537 | +0.4 | -8.0 [-46.0, +17.3] |

- θ_name (A1) CI above 0 in 0 of 4 testable units and below 0 in 0.

## Scorecard (period-specific axes)
- C adequacy: 0 (no statistic is a valid, powered test; S0 failed).
- D unfitted predictions: 0.
- G ground truth: n/a.

## Notes
- 2026-10-07: folder created with the structural counts and the dated prediction, before any H137 outcome on this period.
- 2026-10-07: round-1 results filled in (descriptive).
