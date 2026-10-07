# H137 × G26: Elect a village leader. They choose this week’s goal! (2026-01-05 → 2026-01-12)

**Verdict:** descriptive
**Role:** exploratory
**Period:** regime I · mode C · 10 agents · rooms [0] · 5 non-reserved days. Units: 26 (`period_units`). H137 role: replication.

## Why this period
Replication unit: it meets the structural precondition (>= 20 follow-hop rows in one-way pairs and >= 8 one-way pairs with a follow hop).

Structural counts (2026-10-07, before any follow direction; `results/structure.parquet`): 26: 16,011 calls, 173 project hops (call), 83 follow hops, 20/25/0 one-way/mutual/none pairs, 16 one-way pairs with a follow hop (76 rows) -> testable.

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
| 26 | +0.65 [-0.49, +1.52] (0.070) | +0.79 [-0.08, +1.54] | +0.29 (0.112) | 0.303 / – | – | +3.1 [-6.4, +11.6] |

- θ_name (A1) CI above 0 in 0 of 1 testable units and below 0 in 0.

## Scorecard (period-specific axes)
- C adequacy: 0 (no statistic is a valid, powered test; S0 failed).
- D unfitted predictions: 0.
- G ground truth: n/a.

## Notes
- 2026-10-07: folder created with the structural counts and the dated prediction, before any H137 outcome on this period.
- 2026-10-07: round-1 results filled in (descriptive).
