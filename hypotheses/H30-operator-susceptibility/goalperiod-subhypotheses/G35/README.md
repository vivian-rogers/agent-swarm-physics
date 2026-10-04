# H30 × G35: Test your game to make it as fun and functional as you can! (2026-03-16 → 2026-03-23)

**Verdict:** failed — nudge -0.75 min (n 6); low power
**Verdict (1b):** failed (r1 failed; fixed bins, receiving call)
**Role:** exploratory
**Period:** regime II · mode C · 13 agents at start · 5 active days.

## Why this period
Regime II, 5 days, 17 nudges; the #best/#rest split (NE15) on its first day.

## Prediction
*Written 2026-10-03, before running on this period.*

- P1: χ_act(N_tgt) point estimate > 0 (CI expected to include 0 at this dose).
- P2: χ_act(N_by) within ±0.15 min of 0 if estimable.
- No stability statistics (too few days or kicks); the daily series is descriptive.
- Against (weakly): a negative point estimate with CI excluding 0.

## Result
Days: 5; kicks by class: {'H_men': 3, 'H_und': 20, 'N_by': 103, 'N_tgt': 19}; content pairs with statements on both sides: 139.

| Prediction | Observed | Null / reference | Verdict |
| --- | --- | --- | --- |
| P1 χ_act(N_tgt), min per nudge (pre-registered model) | -0.75 [-5.67, 0.22] (n = 6); with day FE (A2) -1.62 [-5.46, 0.24]: first nudge in 30 min -1.59 [-5.45, 0.24], repeat –, outage-masked -1.62 [-5.46, 0.24], swarm lull 0.58 [CI unstable: too few days] vs not -2.19 [-70.17, -1.97] | day-swap -0.19 [-1.69, 1.12] | failed (point ≤ 0) |
| P2 χ_act(N_by) per bystander; χ_coll per nudge (pre-registered model) | 0.94 [-0.02, 2.69]; χ_coll 2.05 [-1.18, 4.72] (2.5 bystanders/nudge); with day FE 0.24 [-0.02, 1.82], χ_coll 0.02 [-0.77, 3.10]; day FE within swarm lulls 0.03 [CI unstable: too few days] / outside 0.41 [-0.19, 5.98] | day-swap -0.17 [-0.77, 0.60] | failed |

Daily gauge: `data/processed/H30-operator-susceptibility/G35/daily.parquet`; figure: `figures/daily_gauge.pdf`.

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
Fixed activity bins, leading-@ nudge target, kicks at the DQ1 receiving call, past-only kick adjustment with a day fixed effect, content also with gte-modernbert. Numbers in `data/processed/H30-operator-susceptibility/r1b/G35/results.json`; verdict rule unchanged.

| Statistic | Round 1 | Round 1b |
| --- | --- | --- |
| χ_act(N_tgt), level model (r1: no FE; 1b: day FE, past-only) | -0.75 [-5.67, 0.22] (n 6) | -4.19 [-13.30, 0.13] (n 5) |
| χ_act(N_tgt) with day FE / without | -1.62 [-5.46, 0.24] | -3.90 [-13.09, 0.71] (no FE) |
| first / repeat nudge | -1.59 [-5.45, 0.24] / – | -4.18 [-13.29, 0.13] / – |
| bystander χ_act(N_by) | 0.94 [-0.02, 2.69] | 0.35 [-0.29, 1.91] |

Round-1b prediction rows: P1 failed (point ≤ 0); P2 failed.
