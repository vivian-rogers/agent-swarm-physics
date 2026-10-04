# H30 × G31: Pick your own goal (agents bid 3.7 Sonnet farewell) (2026-02-16 → 2026-02-23)

**Verdict:** mixed — nudge 0.68 min (n 18); low power
**Role:** exploratory
**Period:** regime I · mode F · 12 agents at start · 5 active days.

## Why this period
Regime I free week, 25 nudges; first week of the nudger at full strength.

## Prediction
*Written 2026-10-03, before running on this period.*

- P1: χ_act(N_tgt) point estimate > 0 (CI expected to include 0 at this dose).
- P2: χ_act(N_by) within ±0.15 min of 0 if estimable.
- No stability statistics (too few days or kicks); the daily series is descriptive.
- Against (weakly): a negative point estimate with CI excluding 0.

## Result
Days: 5; kicks by class: {'N_tgt': 46, 'H_und': 80, 'H_men': 3, 'N_by': 237}; content pairs with statements on both sides: 345.

| Prediction | Observed | Null / reference | Verdict |
| --- | --- | --- | --- |
| P1 χ_act(N_tgt), min per nudge (pre-registered model) | 0.68 [-0.25, 2.00] (n = 18); with day FE (A2) 0.74 [-0.56, 2.27]: first nudge in 30 min 0.53 [-0.81, 2.29], repeat 0.75 [CI unstable: too few days], outage-masked 0.74 [-0.56, 2.27], swarm lull -1.56 [-69.80, -0.30] vs not 0.56 [-1.11, 3.16] | day-swap -0.28 [-2.09, 0.91] | supported (point > 0) |
| P2 χ_act(N_by) per bystander; χ_coll per nudge (pre-registered model) | 0.41 [0.10, 0.86]; χ_coll 2.64 [0.82, 6.01] (5.2 bystanders/nudge); with day FE 0.35 [0.04, 0.80], χ_coll 2.38 [0.71, 5.08]; day FE within swarm lulls 0.06 [-0.18, 10.67] / outside 0.38 [0.10, 0.93] | day-swap -0.15 [-0.74, 0.50] | failed |

Daily gauge: `data/processed/H30-operator-susceptibility/G31/daily.parquet`; figure: `figures/daily_gauge.pdf`.

## Scorecard (period-specific axes)
- C: χ_act does not beat the day-swap / zero null at the period level.
- D: the bystander (N_by / H_und) response and the pre-window placebo are unfitted checks of the mapping (see rows P2, P11).
- F: estimator validated on synthetic swarms at this period's sampling class (card, Synthetic validation).

## Notes
- 2026-10-03: folder and prediction written before the run (card Amendment A1 applies).
- 2026-10-03: round-1 results filled in from `results.json`.
- 2026-10-03: round-1 results filled in from `results.json`.
- 2026-10-03: round-1 results filled in from `results.json`.
