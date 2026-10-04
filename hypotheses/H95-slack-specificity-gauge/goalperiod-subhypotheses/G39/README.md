# H95 × G39: Build your own interactive world (2026-04-27 → 05-01)

**Verdict:** failed
**Role:** replication (exploratory)
**Period:** regime III · 14 committing agents · horizon 20 active h after the kickoff, settled window = its last 4 h · W_∅ start (every agent at ∅ at t = 0).

## Why this period
- Each agent builds its own world: a target type named per agent (H75: instant freeze). The discriminating case for R2 (named but deconcentrated).

## Prediction
*Written 2026-10-04 ~20:25 UTC (card), with amendment A1 (synthetic, before any new real-data statistic), before running on this period.*
- Per-unit rule (card): supported if S ≤ 2 with x ≥ 0.5, or S ≥ 3 with x < 0.5; failed if S ≥ 3 with x ≥ 0.5, or S ≤ 2 with x < 0.3; mixed otherwise.
- The unit enters the across-kickoff test P1 (ρ(S, x) ≤ −0.5), whose power at n = 9 is 0.29 (A1).

## Result
*Run 2026-10-04 ~21:40 UTC (`analysis/run.py`; data `data/processed/H95-slack-specificity-gauge/G39/results*.json`; figure `../../figures/summary_obs.pdf`).* x = share of first-4-active-hour agent-work commits on repos that H54 flags as kickoff-named; S = ĀT_e/W (H75 estimator, agent bootstrap B = 200); S₀ = median S after permuting each agent's repo labels among its own commits.

| Unit | N | x (variants) | conc. c | S [95% CI] | T_e (h) | W | Ā (/agent/h) | Ā_ss | S₀ | S_text | synthetic band at x | rule |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| G39 | 14 | 0.00 (strict 0.00; day 1 0.00; agent-weighted 0.00) | 0.09 | 1.00 [1.00, 1.00] | 0.25 | 0.79 | 3.14 | 0.04 | 1.00 | -0.64 | outside [2.67, 5.13] | failed |

W_pre variant (pre-kickoff allocation from the last 2 non-holdout days): S = 1.00, T_e = 0.25 h, W = 0.79.
Post-hoc design code (A2, labelled post hoc): G39 d = 1 (1 = the goal assigns a concrete artifact).

## Scorecard (period-specific axes)
- A: x = 0 although the kickoff names the artifact type each agent builds: H54's flags link no G39 repo (its named artifacts are sites, not DQ4 repos). The pre-registered gauge cannot see per-agent targets.
- C/D: the unit's (x, S) point is compared with the synthetic gauge band at its x (descriptive, A1).
