# H30 × G30: Adopt a park and get it cleaned! (2026-02-09 → 2026-02-16)

**Verdict:** mixed — nudge -1.64 min (n 11); content 0.036*; low power
**Role:** exploratory
**Period:** regime I · mode C · 12 agents at start · 5 active days.

## Why this period
Regime I; the nudger switches on 2026-02-13 (NE10) inside this period (12 nudges): the first nudges.

## Prediction
*Written 2026-10-03, before running on this period.*

- P1: χ_act(N_tgt) point estimate > 0 (CI expected to include 0 at this dose).
- P2: χ_act(N_by) within ±0.15 min of 0 if estimable.
- No stability statistics (too few days or kicks); the daily series is descriptive.
- Against (weakly): a negative point estimate with CI excluding 0.

## Result
Days: 5; kicks by class: {'N_by': 112, 'H_men': 8, 'H_und': 135, 'N_tgt': 20}; content pairs with statements on both sides: 272.

| Prediction | Observed | Null / reference | Verdict |
| --- | --- | --- | --- |
| P1 χ_act(N_tgt), min per nudge (pre-registered model) | -1.64 [CI unstable: too few days] (n = 11); with day FE (A2) -2.03 [-67.69, 44.89]: first nudge in 30 min -2.11 [-67.63, 44.98], repeat -1.57 [CI unstable: too few days], outage-masked -2.03 [-67.69, 44.89], swarm lull – vs not -2.20 [-53.20, 36.25] | day-swap 0.61 [-1.01, 2.01] | failed (point ≤ 0) |
| P2 χ_act(N_by) per bystander; χ_coll per nudge (pre-registered model) | 0.56 [CI unstable: too few days]; χ_coll 2.64 [CI unstable: too few days] (7.3 bystanders/nudge); with day FE 0.14 [-2.01, 15.12], χ_coll -0.83 [CI unstable: too few days]; day FE within swarm lulls – / outside -0.04 [-2.21, 12.37] | day-swap -0.28 [-0.70, 0.30] | failed |
| P6 daily χ_con(H_und) stability | perm p (msg) 0.647 (kick-level 0.192); R₁(perm, msg) 0.00; lag-1 –; 4 days, median 21 pairs/day | constant χ | supported (R₁ < 0.5) |

Daily gauge: `data/processed/H30-operator-susceptibility/G30/daily.parquet`; figure: `figures/daily_gauge.pdf`.

## Scorecard (period-specific axes)
- C: χ_act does not beat the day-swap / zero null at the period level.
- D: the bystander (N_by / H_und) response and the pre-window placebo are unfitted checks of the mapping (see rows P2, P11).
- F: estimator validated on synthetic swarms at this period's sampling class (card, Synthetic validation).

## Notes
- 2026-10-03: folder and prediction written before the run (card Amendment A1 applies).
- 2026-10-03: round-1 results filled in from `results.json`.
- 2026-10-03: round-1 results filled in from `results.json`.
- 2026-10-03: round-1 results filled in from `results.json`.
