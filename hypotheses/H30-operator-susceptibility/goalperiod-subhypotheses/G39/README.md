# H30 × G39: Build your own interactive world! (2026-04-27 → 2026-05-04)

**Verdict:** failed — nudge -1.87 min (n 7); low power
**Verdict (1b):** mixed (r1 failed; fixed bins, receiving call)
**Role:** exploratory
**Period:** regime III · mode I · 15 agents at start · 5 active days.

## Why this period
Regime III, 5 days, 7 nudges and 13 human messages: low power.

## Prediction
*Written 2026-10-03, before running on this period.*

- P1: χ_act(N_tgt) point estimate > 0 (CI expected to include 0 at this dose).
- P2: χ_act(N_by) within ±0.15 min of 0 if estimable.
- No stability statistics (too few days or kicks); the daily series is descriptive.
- Against (weakly): a negative point estimate with CI excluding 0.

## Result
Days: 5; kicks by class: {'H_und': 59, 'N_tgt': 8, 'N_by': 64, 'H_men': 2}; content pairs with statements on both sides: 110.

| Prediction | Observed | Null / reference | Verdict |
| --- | --- | --- | --- |
| P1 χ_act(N_tgt), min per nudge (pre-registered model) | -1.87 [-60.37, -1.26] (n = 7); with day FE (A2) -2.20 [-29.73, 2.31]: first nudge in 30 min -2.09 [-29.75, 2.29], repeat -2.62 [CI unstable: too few days], outage-masked -2.20 [-29.73, 2.31], swarm lull 1.76 [-0.40, 44.77] vs not -2.83 [-71.87, 0.38] | day-swap -1.41 [-4.23, 0.95] | failed (point ≤ 0) |
| P2 χ_act(N_by) per bystander; χ_coll per nudge (pre-registered model) | 0.17 [-3.48, 0.89]; χ_coll -0.54 [CI unstable: too few days] (7.9 bystanders/nudge); with day FE -0.50 [-1.90, -0.05], χ_coll -6.13 [-54.58, -2.26]; day FE within swarm lulls 0.27 [-6.93, 11.63] / outside -0.54 [-16.22, 0.04] | day-swap 0.05 [-0.32, 0.64] | failed |

Daily gauge: `data/processed/H30-operator-susceptibility/G39/daily.parquet`; figure: `figures/daily_gauge.pdf`.

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
Fixed activity bins, leading-@ nudge target, kicks at the DQ1 receiving call, past-only kick adjustment with a day fixed effect, content also with gte-modernbert. Numbers in `data/processed/H30-operator-susceptibility/r1b/G39/results.json`; verdict rule unchanged.

| Statistic | Round 1 | Round 1b |
| --- | --- | --- |
| χ_act(N_tgt), level model (r1: no FE; 1b: day FE, past-only) | -1.87 [CI unstable] (n 7) | 0.31 [-0.40, 1.87] (n 6) |
| χ_act(N_tgt) with day FE / without | -2.20 [-29.73, 2.31] | 0.65 [0.08, 2.93] (no FE) |
| first / repeat nudge | -2.09 [-29.75, 2.29] / -2.62 [CI unstable] | 0.33 [-0.82, 1.87] / 0.25 [0.25, 0.25] |
| bystander χ_act(N_by) | 0.17 [-3.48, 0.89] | -0.41 [-2.64, 0.42] |
| χ_con(H_und) bge (gte) | -0.009 [-0.009, -0.009] | -0.013 [-0.013, -0.013] (-0.005 [-0.005, -0.005]) |
| χ_act(H_und) | -0.03 [-1.04, 21.90] | -0.48 [-4.70, 1.58] |

Round-1b prediction rows: P1 supported (point > 0); P2 failed.
