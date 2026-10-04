# H30 × G40: Connect your worlds into a 3D universe! (2026-05-04 → 2026-05-11)

**Verdict:** failed — nudge -1.15 min (n 9); low power
**Verdict (1b):** failed (r1 failed; fixed bins, receiving call)
**Role:** replication (exploratory)
**Period:** regime III · mode C · 15 agents at start · 5 active days.

## Why this period
Regime III, 5 days, 11 nudges; rooms merged (NE42).

## Prediction
*Written 2026-10-03, before running on this period.*

- P1: χ_act(N_tgt) point estimate > 0 (CI expected to include 0 at this dose).
- P2: χ_act(N_by) within ±0.15 min of 0 if estimable.
- No stability statistics (too few days or kicks); the daily series is descriptive.
- Against (weakly): a negative point estimate with CI excluding 0.

## Result
Days: 5; kicks by class: {'N_tgt': 11, 'N_by': 143}; content pairs with statements on both sides: 147.

| Prediction | Observed | Null / reference | Verdict |
| --- | --- | --- | --- |
| P1 χ_act(N_tgt), min per nudge (pre-registered model) | -1.15 [-2.72, 0.82] (n = 9); with day FE (A2) -0.87 [-2.26, 0.82]: first nudge in 30 min -0.97 [-2.44, 0.82], repeat -0.00 [CI unstable: too few days], outage-masked -0.87 [-2.26, 0.82], swarm lull -0.18 [CI unstable: too few days] vs not -1.46 [-3.45, 1.47] | day-swap -0.49 [-1.44, 0.37] | failed (point ≤ 0) |
| P2 χ_act(N_by) per bystander; χ_coll per nudge (pre-registered model) | -1.36 [-1.93, -0.88]; χ_coll -15.45 [-21.31, -9.93] (10.6 bystanders/nudge); with day FE -0.16 [-0.76, 0.44], χ_coll -2.44 [-8.65, 4.24]; day FE within swarm lulls -0.14 [-0.65, 35.59] / outside -0.58 [-0.92, -0.03] | day-swap 0.21 [-0.59, 0.81] | failed |

Daily gauge: `data/processed/H30-operator-susceptibility/G40/daily.parquet`; figure: `figures/daily_gauge.pdf`.

## Scorecard (period-specific axes)
- C: χ_act does not beat the day-swap / zero null at the period level.
- D: the bystander (N_by / H_und) response and the pre-window placebo are unfitted checks of the mapping (see rows P2, P11).
- F: estimator validated on synthetic swarms at this period's sampling class (card, Synthetic validation).

## Notes
- 2026-10-03: folder and prediction written before the run (card Amendment A1 applies).
- 2026-10-03: round-1 results filled in from `results.json`.
- 2026-10-03: round-1 results filled in from `results.json`.
- 2026-10-03: round-1 results filled in from `results.json`.

## Round 1b (improved data, 2026-10-04)
Fixed activity bins, leading-@ nudge target, kicks at the DQ1 receiving call, past-only kick adjustment with a day fixed effect, content also with gte-modernbert. Numbers in `data/processed/H30-operator-susceptibility/r1b/G40/results.json`; verdict rule unchanged.

| Statistic | Round 1 | Round 1b |
| --- | --- | --- |
| χ_act(N_tgt), level model (r1: no FE; 1b: day FE, past-only) | -1.15 [-2.72, 0.82] (n 9) | -1.12 [-3.33, 1.84] (n 9) |
| χ_act(N_tgt) with day FE / without | -0.87 [-2.26, 0.82] | -1.18 [-3.41, 1.79] (no FE) |
| first / repeat nudge | -0.97 [-2.44, 0.82] / -0.00 [-0.00, -0.00] | -1.13 [-3.34, 1.83] / – |
| bystander χ_act(N_by) | -1.36 [-1.93, -0.88] | -0.57 [-1.27, 0.10] |

Round-1b prediction rows: P1 failed (point ≤ 0); P2 failed.
