# H95 × G42: Run your own YouTube channel (2026-05-18 → 05-22)

**Verdict:** supported
**Role:** replication (exploratory)
**Period:** regime III · 14 committing agents · horizon 20 active h after the kickoff, settled window = its last 4 h · W_∅ start (every agent at ∅ at t = 0).

## Why this period
- Each agent runs its own channel: an assigned artifact type per agent; new to H75's set.

## Prediction
*Written 2026-10-04 ~20:25 UTC (card), with amendment A1 (synthetic, before any new real-data statistic), before running on this period.*
- Per-unit rule (card): supported if S ≤ 2 with x ≥ 0.5, or S ≥ 3 with x < 0.5; failed if S ≥ 3 with x ≥ 0.5, or S ≤ 2 with x < 0.3; mixed otherwise.
- The unit enters the across-kickoff test P1 (ρ(S, x) ≤ −0.5), whose power at n = 9 is 0.29 (A1).

## Result
*Run 2026-10-04 ~21:40 UTC (`analysis/run.py`; data `data/processed/H95-slack-specificity-gauge/G42/results*.json`; figure `../../figures/summary_obs.pdf`).* x = share of first-4-active-hour agent-work commits on repos that H54 flags as kickoff-named; S = ĀT_e/W (H75 estimator, agent bootstrap B = 200); S₀ = median S after permuting each agent's repo labels among its own commits.

| Unit | N | x (variants) | conc. c | S [95% CI] | T_e (h) | W | Ā (/agent/h) | Ā_ss | S₀ | S_text | synthetic band at x | rule |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| G42 | 14 | 0.79 (strict 0.00; day 1 0.79; agent-weighted 0.67) | 0.31 | 1.22 [1.00, 2.56] | 0.50 | 0.64 | 1.57 | 0.00 | 1.00 | -0.33 | inside [1.00, 1.29] | supported |

W_pre variant (pre-kickoff allocation from the last 2 non-holdout days): S = 1.11, T_e = 0.50 h, W = 0.64.
Post-hoc design code (A2, labelled post hoc): G42 d = 1 (1 = the goal assigns a concrete artifact).

## Scorecard (period-specific axes)
- C/D: the unit's (x, S) point is compared with the synthetic gauge band at its x (descriptive, A1).
