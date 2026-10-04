# H30 × G38: Choose a charity and raise as much money as you can for it (2026-04-02 → 2026-04-27)

**Verdict:** mixed — nudge -0.08 [-0.98, 0.82] min (n 82); content 0.020
**Role:** exploratory
**Period:** regime III · mode C · 12 agents at start · 17 active days.

## Why this period
Regime III, 17 days, 110 nudges with tailored content: the second-longest nudge series; NE17 (04-14) and NE18 (04-20) inside.

## Prediction
*Written 2026-10-03, before running on this period.*

- P1: χ_act(N_tgt) > 0 with CI excluding 0, 0.8–2.5 min.
- P2: χ_act(N_by) within ±0.15 min of 0; χ_coll within a factor 1.5 of χ_act(N_tgt).
- P5: χ_con(N_tgt) may be > 0 (tailored nudges); no threshold. Bias bound −0.02 (A1).
- P6: permutation test does not reject a constant daily χ_act(N_tgt); R₁ < 0.3.
- P7: per-kick slope of the activity response on goal day has a CI including 0.
- P8 (low power): the per-kick slope on turns since reset is negative.
- P11: pre-window placebo for N_tgt within ±0.5 min; day-swap null band includes 0.

## Result
Days: 17; kicks by class: {'H_und': 104, 'N_by': 652, 'H_men': 8, 'N_tgt': 120}; content pairs with statements on both sides: 802.

| Prediction | Observed | Null / reference | Verdict |
| --- | --- | --- | --- |
| P1 χ_act(N_tgt), min per nudge (pre-registered model) | -0.08 [-0.98, 0.82] (n = 82); with day FE (A2) 0.38 [-0.46, 1.35]: first nudge in 30 min 0.72 [-0.36, 1.95], repeat -0.05 [-0.73, 0.44], outage-masked 0.42 [-0.44, 1.41], swarm lull 0.80 [-0.62, 2.78] vs not 0.10 [-0.82, 0.91] | day-swap 0.29 [-0.46, 0.94] | not supported (CI includes 0) |
| P2 χ_act(N_by) per bystander; χ_coll per nudge (pre-registered model) | -0.54 [-1.01, -0.01]; χ_coll -2.41 [-4.87, 0.11] (4.4 bystanders/nudge); with day FE -0.16 [-0.41, 0.12], χ_coll -0.42 [-1.63, 1.05]; day FE within swarm lulls 0.10 [-0.63, 0.63] / outside -0.26 [-0.60, 0.12] | day-swap -0.12 [-0.47, 0.30] | failed |
| P5 χ_con(N_tgt), cosine | 0.000 [-0.005, 0.007] (n = 112; matched -0.005 [-0.012, 0.004]) | pseudo-true null 0.004 [-0.004, 0.012] | CI includes 0 |
| P6 daily χ_act(N_tgt) stability | perm p (msg) 0.158, within-agent 0.184; R₁(perm, msg) 0.40, within-agent 0.30; lag-1 0.05 (p 0.281); 12 days, median 6 kicks/day; Q p 0.027; outage-masked: p 0.092, R₁ 0.47; no day FE (pre-registered): p 0.449, R₁ 0.06; agent-day FE: p 0.663, R₁ 0.00 | constant χ | failed |
| P6 daily χ_con(H_und) stability | perm p (msg) 0.168 (kick-level 0.050); R₁(perm, msg) 0.48; lag-1 -0.34; 8 days, median 12 pairs/day | constant χ | supported (R₁ < 0.5) |
| P6 daily χ_con(N_tgt) stability | perm p (msg) 0.086 (kick-level 0.337); R₁(perm, msg) 0.47; lag-1 0.05; 15 days, median 7 pairs/day | constant χ | supported (R₁ < 0.5) |
| P7 aging: d r / d goal-day (activity, N_tgt) | 0.016 [-0.171, 0.203] min/day | 0 | supported (no aging) |
| P8 context fill (activity, N_tgt; controls matched on their own fill phase, A2) | early (turns 0–13) 1.21 [-0.24, 3.27] n 31; mid 0.24 [-0.94, 1.53]; late (28+) -0.15 [-1.65, 0.93] n 15; early − late 1.36 [-0.59, 4.21]; pre-registered per-kick slope -0.045 [-0.099, 0.009] min/turn | 0; ratio 1 | direction only (early > late, CI includes 0) |
| P11 nulls | pre-window placebo -0.59 (day FE -0.38); day-swap 0.29 [-0.46, 0.94]; pseudo-true content null 0.004 [-0.004, 0.012] | 0 | failed |

Daily gauge: `data/processed/H30-operator-susceptibility/G38/daily.parquet`; figure: `figures/daily_gauge.pdf`.

## Scorecard (period-specific axes)
- C: χ_act does not beat the day-swap / zero null at the period level.
- D: the bystander (N_by / H_und) response and the pre-window placebo are unfitted checks of the mapping (see rows P2, P11).
- F: estimator validated on synthetic swarms at this period's sampling class (card, Synthetic validation).

## Notes
- 2026-10-03: folder and prediction written before the run (card Amendment A1 applies).
- 2026-10-03: round-1 results filled in from `results.json`.
- 2026-10-03: round-1 results filled in from `results.json`.
- 2026-10-03: round-1 results filled in from `results.json`.
