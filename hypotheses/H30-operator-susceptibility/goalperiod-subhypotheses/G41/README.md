# H30 × G41: Perform novel research! (2026-05-11 → 2026-05-18)

**Verdict:** mixed — nudge 0.86 [0.51, 1.26] min (n 53); low power
**Role:** exploratory
**Period:** regime III · mode I · 15 agents at start · 5 active days.

## Why this period
Regime III, 5 days, 59 nudges (≈ 12/day) with tailored content.

## Prediction
*Written 2026-10-03, before running on this period.*

- P1: χ_act(N_tgt) > 0 (point; CI may include 0 with 5 days).
- P2: χ_act(N_by) within ±0.15 min of 0.
- P5: χ_con(N_tgt) may be > 0 (tailored nudges).

## Result
Days: 5; kicks by class: {'H_men': 6, 'N_tgt': 72, 'N_by': 346, 'H_und': 49}; content pairs with statements on both sides: 429.

| Prediction | Observed | Null / reference | Verdict |
| --- | --- | --- | --- |
| P1 χ_act(N_tgt), min per nudge (pre-registered model) | 0.86 [0.51, 1.26] (n = 53); with day FE (A2) 0.28 [-0.60, 1.22]: first nudge in 30 min 0.63 [-0.49, 1.55], repeat 0.47 [-0.87, 1.72], outage-masked 0.28 [-0.60, 1.22], swarm lull 0.01 [-3.45, 0.77] vs not 0.17 [-0.60, 1.51] | day-swap 0.25 [-0.75, 1.50] | supported (point > 0); CI excludes 0 |
| P2 χ_act(N_by) per bystander; χ_coll per nudge (pre-registered model) | 0.43 [-0.08, 0.77]; χ_coll 2.73 [0.36, 4.17] (4.5 bystanders/nudge); with day FE -0.31 [-0.69, -0.01], χ_coll -1.15 [-3.52, 0.99]; day FE within swarm lulls -0.74 [-2.14, -0.24] / outside -0.15 [-0.50, 0.09] | day-swap 0.08 [-0.36, 0.65] | failed |
| P5 χ_con(N_tgt), cosine | 0.008 [-0.018, 0.035] (n = 68; matched 0.002 [-0.022, 0.024]) | pseudo-true null -0.004 [-0.012, 0.004] | CI includes 0 |

Daily gauge: `data/processed/H30-operator-susceptibility/G41/daily.parquet`; figure: `figures/daily_gauge.pdf`.

## Scorecard (period-specific axes)
- C: χ_act does not beat the day-swap / zero null at the period level.
- D: the bystander (N_by / H_und) response and the pre-window placebo are unfitted checks of the mapping (see rows P2, P11).
- F: estimator validated on synthetic swarms at this period's sampling class (card, Synthetic validation).

## Notes
- 2026-10-03: folder and prediction written before the run (card Amendment A1 applies).
- 2026-10-03: round-1 results filled in from `results.json`.
- 2026-10-03: round-1 results filled in from `results.json`.
- 2026-10-03: round-1 results filled in from `results.json`.
