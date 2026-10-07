# H137 × G44: Finetune your leader! (2026-05-26 → 2026-06-01)

**Verdict:** descriptive
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
*Run 2026-10-07 (exploration data).*

All numbers are descriptive. S0 failed (pooled synthetic power at J = 1 is 0.18), so H137 is untestable at village counts and no per-period verdict is possible. A1 is the amended θ_name with the hopper-propensity control; the card's θ_name is biased negative in the no-following world (W0 −0.21 ± 0.09). N1b is the propensity-adjusted direction null (A2). Pair-bootstrap CIs; N2 within-stratum permutation p (500 draws per unit). Data: `data/processed/H137-nonreciprocal-potts-named-pairs/results/units.parquet`; estimates rows `h137_*` (role replication).

| Unit | θ_name A1 [95% CI] (N2 p) | θ_name card [95% CI] | mean A one-way (N1b p) | σ_mutual / σ_none N1b p | σ_one − σ_none | O4 read − in-flight (×10⁻³) |
| --- | --- | --- | --- | --- | --- | --- |
| 44a | +0.03 [-0.62, +0.87] (0.391) | +0.04 [-0.59, +0.95] | -0.02 (0.384) | 0.458 / 0.018 | -1.7 | +9.1 [-9.2, +24.5] |
| 44b | +0.18 [-0.18, +0.55] (0.299) | +0.20 [-0.37, +1.01] | +0.48 (0.161) | 0.376 / 0.374 | +0.3 | -1.0 [-23.1, +17.0] |

- θ_name (A1) CI above 0 in 0 of 2 testable units and below 0 in 0.
- **N3 native (descriptive):** #best θ_name A1 -0.72 [-2.30, +1.63] (9 one-way pairs); #rest +0.16 [-0.20, +0.55] (25 pairs). No cross-room follow hops. Neither room shows a naming direction.

## Scorecard (period-specific axes)
- C adequacy: 0 (no statistic is a valid, powered test; S0 failed).
- D unfitted predictions: 0.
- G ground truth: n/a.

## Notes
- 2026-10-07: folder created with the structural counts and the dated prediction, before any H137 outcome on this period.
- 2026-10-07: round-1 results filled in (descriptive).
