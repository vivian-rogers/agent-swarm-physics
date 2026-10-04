# H30 × G33: Discuss, debate, and act on your views about the recent Pentagon-AI company news (2026-03-02 → 2026-03-05)

**Verdict:** mixed — nudge 0.14 min (n 20); low power
**Verdict (1b):** mixed (r1 mixed; fixed bins, receiving call)
**Role:** exploratory
**Period:** regime II · mode C · 12 agents at start · 3 active days.

## Why this period
Regime II (rooms + sessions), 3 days, 22 nudges.

## Prediction
*Written 2026-10-03, before running on this period.*

- P1: χ_act(N_tgt) point estimate > 0 (CI expected to include 0 at this dose).
- P2: χ_act(N_by) within ±0.15 min of 0 if estimable.
- No stability statistics (too few days or kicks); the daily series is descriptive.
- Against (weakly): a negative point estimate with CI excluding 0.

## Result
Days: 3; kicks by class: {'N_by': 200, 'N_tgt': 42}; content pairs with statements on both sides: 226.

| Prediction | Observed | Null / reference | Verdict |
| --- | --- | --- | --- |
| P1 χ_act(N_tgt), min per nudge (pre-registered model) | 0.14 [-2.11, 1.33] (n = 20); with day FE (A2) 0.49 [-0.97, 1.74]: first nudge in 30 min 0.45 [-1.13, 2.29], repeat 0.91 [-13.04, 2.15], outage-masked 0.49 [-0.97, 1.74], swarm lull 2.47 [CI unstable: too few days] vs not 0.70 [-0.85, 1.41] | day-swap 0.44 [-0.25, 1.41] | supported (point > 0) |
| P2 χ_act(N_by) per bystander; χ_coll per nudge (pre-registered model) | -0.98 [-1.23, -0.62]; χ_coll -6.32 [-7.36, -5.27] (6.6 bystanders/nudge); with day FE -0.98 [-1.24, -0.76], χ_coll -6.04 [-7.70, -3.46]; day FE within swarm lulls -1.42 [-7.60, -1.24] / outside -1.05 [-1.22, -0.72] | day-swap -0.33 [-0.65, 0.19] | failed |

Daily gauge: `data/processed/H30-operator-susceptibility/G33/daily.parquet`; figure: `figures/daily_gauge.pdf`.

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
Fixed activity bins, leading-@ nudge target, kicks at the DQ1 receiving call, past-only kick adjustment with a day fixed effect, content also with gte-modernbert. Numbers in `data/processed/H30-operator-susceptibility/r1b/G33/results.json`; verdict rule unchanged.

| Statistic | Round 1 | Round 1b |
| --- | --- | --- |
| χ_act(N_tgt), level model (r1: no FE; 1b: day FE, past-only) | 0.14 [-2.11, 1.33] (n 20) | 0.61 [-1.32, 2.38] (n 15) |
| χ_act(N_tgt) with day FE / without | 0.49 [-0.97, 1.74] | 0.78 [-0.96, 2.26] (no FE) |
| first / repeat nudge | 0.45 [-1.13, 2.29] / 0.91 [-13.04, 2.15] | 0.54 [-1.28, 3.27] / 0.43 [CI unstable] |
| bystander χ_act(N_by) | -0.98 [-1.23, -0.62] | -0.68 [-0.75, -0.59] |

Round-1b prediction rows: P1 supported (point > 0); P2 failed.
