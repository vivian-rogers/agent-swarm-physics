# H30 × G51: Each agent: Maximize your assigned goal! (2026-07-06 → 2026-09-20)

**Verdict:** mixed — nudge 0.59 [0.24, 0.93] min (n 875); content 0.025*, named 0.063
**Verdict (1b):** mixed (r1 mixed; fixed bins, receiving call)
**Role:** replication (exploratory)
**Period:** regime III · mode I/K · 21 agents at start · 55 active days (non-holdout part only: 07-06 → 09-04; the #51 tail is held out).

## Why this period
Regime III, 8 h days, up to 32 agents, 729 nudges over the 45 non-holdout days (≈ 16/day, nearly pure template): the main daily series. #51 tail (09-07 → 09-21) is held out.

## Prediction
*Written 2026-10-03, before running on this period.*

- P1: χ_act(N_tgt) > 0 with CI excluding 0, 0.8–2.5 min.
- P2: χ_act(N_by) within ±0.15 min of 0; χ_coll per nudge within a factor 1.5 of χ_act(N_tgt).
- P5: χ_con(N_tgt) within ±0.02 with CI including 0 (template nudges; bias bound −0.02).
- P6: permutation test does not reject a constant daily χ_act(N_tgt); permutation-calibrated R₁ < 0.3; lag-1 autocorrelation of the daily series not distinguishable from 0; ≥ 5-day windows needed.
- P7: per-kick slope on goal day has a CI including 0 (no aging; HH116 fails).
- P8: activity response early in the context cycle (turns 0–13) ≥ 1.3 × late (28+), and the per-kick slope on turns since reset < 0 (credence ~40%).
- P10: no lab's χ_act(N_tgt) differs from the pooled value after Holm correction.
- P11: pre-window placebo within ±0.5 min; day-swap null band includes 0; pseudo-true content null centered on 0.
- Against P6 (for HH116): permutation p < 0.05 with R₁ ≥ 0.5 and positive lag-1 autocorrelation.

## Result
Days: 45; kicks by class: {'H_und': 1957, 'N_tgt': 970, 'H_men': 95, 'N_by': 16781}; content pairs with statements on both sides: 15866.

| Prediction | Observed | Null / reference | Verdict |
| --- | --- | --- | --- |
| P1 χ_act(N_tgt), min per nudge (pre-registered model) | 0.59 [0.24, 0.93] (n = 875); with day FE (A2) 1.04 [0.77, 1.33]: first nudge in 30 min 1.36 [0.98, 1.75], repeat 0.26 [-0.13, 0.63], outage-masked 0.90 [0.63, 1.21], swarm lull 0.18 [-0.07, 0.50] vs not 0.84 [0.52, 1.18] | day-swap 0.03 [-0.25, 0.19] | sign supported, size outside 0.8–2.5 |
| P2 χ_act(N_by) per bystander; χ_coll per nudge (pre-registered model) | 0.13 [-0.11, 0.38]; χ_coll 3.38 [-1.64, 8.71] (20.9 bystanders/nudge); with day FE 0.43 [0.34, 0.52], χ_coll 10.14 [8.30, 12.28]; day FE within swarm lulls -0.03 [-0.08, 0.03] / outside 0.06 [-0.00, 0.14] | day-swap 0.04 [-0.01, 0.10] | supported |
| P5 χ_con(N_tgt), cosine | 0.003 [0.000, 0.005] (n = 713; matched -0.001 [-0.005, 0.002]) | pseudo-true null -0.001 [-0.003, 0.002] | failed |
| P6 daily χ_act(N_tgt) stability | perm p (msg) 0.082, within-agent 0.120; R₁(perm, msg) 0.28, within-agent 0.17; lag-1 -0.09 (p 0.677); 34 days, median 25 kicks/day; Q p 0.086; outage-masked: p 0.064, R₁ 0.38; no day FE (pre-registered): p 0.002, R₁ 0.62; agent-day FE: p 0.010, R₁ 0.50 | constant χ | supported |
| P6 daily χ_con(H_und) stability | perm p (msg) 0.086 (kick-level 0.002); R₁(perm, msg) 0.00; lag-1 -0.42; 20 days, median 48 pairs/day | constant χ | supported (R₁ < 0.5) |
| P6 daily χ_con(H_men) stability | perm p (msg) 0.186 (kick-level 0.116); R₁(perm, msg) 0.23; lag-1 -0.20; 9 days, median 5 pairs/day | constant χ | supported (R₁ < 0.5) |
| P6 daily χ_con(N_tgt) stability | perm p (msg) 0.685 (kick-level 0.747); R₁(perm, msg) 0.00; lag-1 -0.30; 34 days, median 22 pairs/day | constant χ | supported (R₁ < 0.5) |
| P7 aging: d r / d goal-day (activity, N_tgt) | -0.019 [-0.049, 0.012] min/day | 0 | supported (no aging) |
| P8 context fill (activity, N_tgt; controls matched on their own fill phase, A2) | early (turns 0–13) 0.94 [0.67, 1.22] n 685; mid 1.38 [0.56, 2.27]; late (28+) 1.00 [-0.58, 2.53] n 45; early − late -0.06 [-1.65, 1.56]; pre-registered per-kick slope 0.026 [-0.022, 0.074] min/turn | 0; ratio 1 | failed (late ≥ early) |
| P10 family (lab) differences in χ_act(N_tgt) | Google 0.13 [-1.48, 1.34] (n 41); Anthropic 1.56 [0.69, 2.42] (n 90); DeepSeek 0.78 [-0.30, 1.86] (n 93); OpenAI 1.04 [0.72, 1.35] (n 629) | pooled | supported |
| P11 nulls | pre-window placebo 0.11 (day FE 0.31); day-swap 0.03 [-0.25, 0.19]; pseudo-true content null -0.001 [-0.003, 0.002] | 0 | supported |

Daily gauge: `data/processed/H30-operator-susceptibility/G51/daily.parquet`; figure: `figures/daily_gauge.pdf`.

## Scorecard (period-specific axes)
- C: χ_act beats the day-swap / zero null at the period level.
- D: the bystander (N_by / H_und) response and the pre-window placebo are unfitted checks of the mapping (see rows P2, P11).
- F: estimator validated on synthetic swarms at this period's sampling class (card, Synthetic validation).

## Notes
- 2026-10-03: folder and prediction written before the run (card Amendment A1 applies).
- 2026-10-03: round-1 results filled in from `results.json`.
- 2026-10-03: round-1 results filled in from `results.json`.
- 2026-10-03: round-1 results filled in from `results.json`.

## Round 1b (improved data, 2026-10-04)
Fixed activity bins, leading-@ nudge target, kicks at the DQ1 receiving call, past-only kick adjustment with a day fixed effect, content also with gte-modernbert. Numbers in `data/processed/H30-operator-susceptibility/r1b/G51/results.json`; verdict rule unchanged.

| Statistic | Round 1 | Round 1b |
| --- | --- | --- |
| χ_act(N_tgt), level model (r1: no FE; 1b: day FE, past-only) | 0.59 [0.24, 0.93] (n 875) | 0.98 [0.63, 1.37] (n 658) |
| χ_act(N_tgt) with day FE / without | 1.04 [0.77, 1.33] | 1.07 [0.73, 1.47] (no FE) |
| first / repeat nudge | 1.36 [0.98, 1.75] / 0.26 [-0.13, 0.63] | 1.21 [0.80, 1.66] / 0.44 [-0.19, 1.10] |
| bystander χ_act(N_by) | 0.13 [-0.11, 0.38] | -0.01 [-0.09, 0.08] |
| χ_con(H_und) bge (gte) | 0.025 [0.014, 0.033] | 0.024 [0.014, 0.033] (0.019 [0.010, 0.026]) |
| χ_con(H_men) bge (gte) | 0.063 [0.043, 0.101] | 0.047 [0.031, 0.071] (0.047 [0.031, 0.079]) |
| χ_act(H_und) | 0.26 [-0.96, 1.58] | 0.15 [-0.05, 0.33] |

Round-1b prediction rows: P1 supported; P2 supported; P5 supported; P6 failed; P6 supported (R₁ < 0.5); P6 supported (R₁ < 0.5); P6 supported (R₁ < 0.5); P7 supported (no aging); P8 failed (late ≥ early); P10 supported; P11 supported.
