# H30 × G37: Pick your own goal! (2026-03-30 → 2026-04-02)

**Verdict:** mixed — nudge 0.49 min (n 21); low power
**Role:** exploratory
**Period:** regime III · mode F · 13 agents at start · 3 active days.

## Why this period
First regime-III goal (3 days, 20 nudges).

## Prediction
*Written 2026-10-03, before running on this period.*

- P1: χ_act(N_tgt) point estimate > 0 (CI expected to include 0 at this dose).
- P2: χ_act(N_by) within ±0.15 min of 0 if estimable.
- No stability statistics (too few days or kicks); the daily series is descriptive.
- Against (weakly): a negative point estimate with CI excluding 0.

## Result
Days: 3; kicks by class: {'H_men': 2, 'N_tgt': 24, 'H_und': 11, 'N_by': 125}; content pairs with statements on both sides: 142.

| Prediction | Observed | Null / reference | Verdict |
| --- | --- | --- | --- |
| P1 χ_act(N_tgt), min per nudge (pre-registered model) | 0.49 [-3.23, 1.84] (n = 21); with day FE (A2) 1.35 [-1.76, 2.37]: first nudge in 30 min 1.54 [-5.18, 2.47], repeat 0.00 [CI unstable: too few days], outage-masked 1.35 [-1.76, 2.37], swarm lull – vs not 1.43 [-1.76, 2.52] | day-swap 0.58 [-0.93, 1.98] | supported (point > 0) |
| P2 χ_act(N_by) per bystander; χ_coll per nudge (pre-registered model) | 0.54 [0.36, 0.77]; χ_coll 3.63 [-1.28, 6.41] (5.8 bystanders/nudge); with day FE 0.51 [0.24, 0.71], χ_coll 4.36 [-0.44, 5.82]; day FE within swarm lulls – / outside 0.44 [0.18, 0.60] | day-swap -0.05 [-0.55, 0.46] | failed |

Daily gauge: `data/processed/H30-operator-susceptibility/G37/daily.parquet`; figure: `figures/daily_gauge.pdf`.

## Scorecard (period-specific axes)
- C: χ_act does not beat the day-swap / zero null at the period level.
- D: the bystander (N_by / H_und) response and the pre-window placebo are unfitted checks of the mapping (see rows P2, P11).
- F: estimator validated on synthetic swarms at this period's sampling class (card, Synthetic validation).

## Notes
- 2026-10-03: folder and prediction written before the run (card Amendment A1 applies).
- 2026-10-03: round-1 results filled in from `results.json`.
- 2026-10-03: round-1 results filled in from `results.json`.
- 2026-10-03: round-1 results filled in from `results.json`.
