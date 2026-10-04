# H95 × G41: Perform novel research (2026-05-11 → 05-15)

**Verdict:** failed
**Role:** replication (exploratory)
**Period:** regime III · 13 committing agents · horizon 20 active h after the kickoff, settled window = its last 4 h · W_∅ start (every agent at ∅ at t = 0).

## Why this period
- Free research topics (H75: churn, S 5.1 under W_pre).

## Prediction
*Written 2026-10-04 ~20:25 UTC (card), with amendment A1 (synthetic, before any new real-data statistic), before running on this period.*
- Per-unit rule (card): supported if S ≤ 2 with x ≥ 0.5, or S ≥ 3 with x < 0.5; failed if S ≥ 3 with x ≥ 0.5, or S ≤ 2 with x < 0.3; mixed otherwise.
- The unit enters the across-kickoff test P1 (ρ(S, x) ≤ −0.5), whose power at n = 9 is 0.29 (A1).

## Result
*Run 2026-10-04 ~21:40 UTC (`analysis/run.py`; data `data/processed/H95-slack-specificity-gauge/G41/results*.json`; figure `../../figures/summary_obs.pdf`).* x = share of first-4-active-hour agent-work commits on repos that H54 flags as kickoff-named; S = ĀT_e/W (H75 estimator, agent bootstrap B = 200); S₀ = median S after permuting each agent's repo labels among its own commits.

| Unit | N | x (variants) | conc. c | S [95% CI] | T_e (h) | W | Ā (/agent/h) | Ā_ss | S₀ | S_text | synthetic band at x | rule |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| G41 | 13 | 0.74 (strict 0.00; day 1 0.74; agent-weighted 0.86) | 0.40 | 3.69 [1.42, 7.70] | 9.00 | 1.00 | 0.41 | 0.62 | 1.80 | +0.04 | outside [1.00, 1.45] | failed |

W_pre variant (pre-kickoff allocation from the last 2 non-holdout days): S = 5.09, T_e = 9.50 h, W = 0.85.
Post-hoc design code (A2, labelled post hoc): G41 d = 0 (1 = the goal assigns a concrete artifact).

## Scorecard (period-specific axes)
- A: x = 0.74 for a free-choice kickoff: H54's loose token match flags research repos as named. The gauge measures word overlap, not specificity.
- C/D: the unit's (x, S) point is compared with the synthetic gauge band at its x (descriptive, A1).
