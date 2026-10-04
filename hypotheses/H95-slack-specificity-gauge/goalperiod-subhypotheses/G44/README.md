# H95 × G44: #best fine-tunes a leader; #rest picks its own goals (2026-05-26 → 05-29)

**Verdict:** mixed (units: G44best mixed, G44rest supported)
**Role:** replication + native (exploratory)
**Period:** regime III · 4 + 10 committing agents · horizon 16 active h after the kickoff, settled window = its last 4 h · W_∅ start (every agent at ∅ at t = 0).

## Why this period
- Two room kickoffs on the same days: #best (named leader fine-tune) and #rest (own goals). Two replication units and native N1.

## Prediction
*Written 2026-10-04 ~20:25 UTC (card), with amendment A1 (synthetic, before any new real-data statistic), before running on this period.*
- Per-unit rule (card): supported if S ≤ 2 with x ≥ 0.5, or S ≥ 3 with x < 0.5; failed if S ≥ 3 with x ≥ 0.5, or S ≤ 2 with x < 0.3; mixed otherwise.
- The unit enters the across-kickoff test P1 (ρ(S, x) ≤ −0.5), whose power at n = 9 is 0.29 (A1).

## Result
*Run 2026-10-04 ~21:40 UTC (`analysis/run.py`; data `data/processed/H95-slack-specificity-gauge/G44/results*.json`; figure `../../figures/summary_obs.pdf`).* x = share of first-4-active-hour agent-work commits on repos that H54 flags as kickoff-named; S = ĀT_e/W (H75 estimator, agent bootstrap B = 200); S₀ = median S after permuting each agent's repo labels among its own commits.

| Unit | N | x (variants) | conc. c | S [95% CI] | T_e (h) | W | Ā (/agent/h) | Ā_ss | S₀ | S_text | synthetic band at x | rule |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| G44best | 4 | 0.69 (strict 0.00; day 1 0.69; agent-weighted 0.66) | 0.06 | 2.50 [1.00, 33.50] | 0.75 | 1.00 | 3.33 | 1.62 | 2.00 | -0.09 | outside [1.00, 1.75] | mixed |
| G44rest | 10 | 0.17 (strict 0.00; day 1 0.17; agent-weighted 0.08) | 0.21 | 14.50 [5.20, 22.01] | 4.25 | 1.00 | 3.41 | 1.60 | 9.50 | +0.42 | outside [2.67, 5.25] | supported |

Post-hoc design code (A2, labelled post hoc): G44best d = 1, G44rest d = 0 (1 = the goal assigns a concrete artifact).

## Scorecard (period-specific axes)
- C/D: the unit's (x, S) point is compared with the synthetic gauge band at its x (descriptive, A1).

## Native N1: two room kickoffs on the same days
*Prediction (card):* x_best − x_rest ≥ 0.3 and S_rest/S_best ≥ 2. Credence 0.55 (the S half was already known from H75).

- x: #best 0.69 vs #rest 0.17 (Δ +0.52).
- S: #best 2.50 vs #rest 14.50 (ratio ×5.8); S₀ 2.00 vs 9.50.
- **Verdict: supported** (4 agents in #best; the slack half replicates H75 by construction of the same estimator).
