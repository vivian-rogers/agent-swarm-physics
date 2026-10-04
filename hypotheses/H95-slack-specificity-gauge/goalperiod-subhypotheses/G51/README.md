# H95 × G51: Private assigned goals (head) (2026-07-06 → 09-04)

**Verdict:** failed
**Role:** replication (exploratory)
**Period:** regime III · 16 committing agents · horizon 20 active h after the kickoff, settled window = its last 4 h · W_∅ start (every agent at ∅ at t = 0).

## Why this period
- Private assigned goals (per agent); the kickoff itself names few repos, so the HH's x was expected to be low here (risk stated on the card).

## Prediction
*Written 2026-10-04 ~20:25 UTC (card), with amendment A1 (synthetic, before any new real-data statistic), before running on this period.*
- Per-unit rule (card): supported if S ≤ 2 with x ≥ 0.5, or S ≥ 3 with x < 0.5; failed if S ≥ 3 with x ≥ 0.5, or S ≤ 2 with x < 0.3; mixed otherwise.
- The unit enters the across-kickoff test P1 (ρ(S, x) ≤ −0.5), whose power at n = 9 is 0.29 (A1).

## Result
*Run 2026-10-04 ~21:40 UTC (`analysis/run.py`; data `data/processed/H95-slack-specificity-gauge/G51/results*.json`; figure `../../figures/summary_obs.pdf`).* x = share of first-4-active-hour agent-work commits on repos that H54 flags as kickoff-named; S = ĀT_e/W (H75 estimator, agent bootstrap B = 200); S₀ = median S after permuting each agent's repo labels among its own commits.

| Unit | N | x (variants) | conc. c | S [95% CI] | T_e (h) | W | Ā (/agent/h) | Ā_ss | S₀ | S_text | synthetic band at x | rule |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| G51 | 16 | 0.13 (strict 0.00; day 1 0.11; agent-weighted 0.16) | 0.18 | 1.40 [1.00, 3.73] | 0.50 | 0.62 | 1.75 | 0.39 | 2.20 | +0.08 | outside [2.67, 5.13] | failed |

Post-hoc design code (A2, labelled post hoc): G51 d = 1 (1 = the goal assigns a concrete artifact).

## Scorecard (period-specific axes)
- A: x = 0.13 although every agent has an assigned private goal (stated as a risk before the run). S = 1.40: an instant freeze.
- C/D: the unit's (x, S) point is compared with the synthetic gauge band at its x (descriptive, A1).
