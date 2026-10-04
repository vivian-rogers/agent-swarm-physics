# H30 × G42: Run your own Youtube channel! (2026-05-18 → 2026-05-25)

**Verdict:** mixed — nudge 0.57 min (n 18); low power
**Verdict (1b):** failed (r1 mixed; fixed bins, receiving call)
**Role:** exploratory
**Period:** regime III · mode I · 15 agents at start · 5 active days.

## Why this period
Regime III, 5 days, 25 nudges.

## Prediction
*Written 2026-10-03, before running on this period.*

- P1: χ_act(N_tgt) point estimate > 0 (CI expected to include 0 at this dose).
- P2: χ_act(N_by) within ±0.15 min of 0 if estimable.
- No stability statistics (too few days or kicks); the daily series is descriptive.
- Against (weakly): a negative point estimate with CI excluding 0.

## Result
Days: 5; kicks by class: {'N_by': 198, 'H_men': 3, 'H_und': 41, 'N_tgt': 28}; content pairs with statements on both sides: 247.

| Prediction | Observed | Null / reference | Verdict |
| --- | --- | --- | --- |
| P1 χ_act(N_tgt), min per nudge (pre-registered model) | 0.57 [-1.76, 2.12] (n = 18); with day FE (A2) -0.45 [-2.96, 1.21]: first nudge in 30 min -0.75 [-4.71, 1.36], repeat 0.14 [-3.04, 3.75], outage-masked -0.45 [-2.96, 1.21], swarm lull 0.67 [CI unstable: too few days] vs not 0.08 [-2.46, 1.81] | day-swap -0.19 [-1.31, 0.99] | supported (point > 0) |
| P2 χ_act(N_by) per bystander; χ_coll per nudge (pre-registered model) | 0.36 [0.03, 0.72]; χ_coll 2.47 [1.45, 3.51] (5.8 bystanders/nudge); with day FE 0.05 [-0.29, 0.46], χ_coll -0.02 [-1.37, 1.03]; day FE within swarm lulls -0.09 [CI unstable: too few days] / outside 0.17 [-0.19, 0.57] | day-swap -0.05 [-0.44, 0.31] | failed |

Daily gauge: `data/processed/H30-operator-susceptibility/G42/daily.parquet`; figure: `figures/daily_gauge.pdf`.

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
Fixed activity bins, leading-@ nudge target, kicks at the DQ1 receiving call, past-only kick adjustment with a day fixed effect, content also with gte-modernbert. Numbers in `data/processed/H30-operator-susceptibility/r1b/G42/results.json`; verdict rule unchanged.

| Statistic | Round 1 | Round 1b |
| --- | --- | --- |
| χ_act(N_tgt), level model (r1: no FE; 1b: day FE, past-only) | 0.57 [-1.76, 2.12] (n 18) | -0.55 [-2.29, 1.74] (n 15) |
| χ_act(N_tgt) with day FE / without | -0.45 [-2.96, 1.21] | -0.73 [-2.54, 1.35] (no FE) |
| first / repeat nudge | -0.75 [-4.71, 1.36] / 0.14 [-3.04, 3.75] | -0.54 [-2.68, 3.02] / -0.15 [-2.65, 2.52] |
| bystander χ_act(N_by) | 0.36 [0.03, 0.72] | 0.16 [-0.29, 0.45] |
| χ_act(H_und) | -2.16 [-25.14, 22.82] | -0.62 [-7.48, 8.01] |

Round-1b prediction rows: P1 failed (point ≤ 0); P2 failed.
