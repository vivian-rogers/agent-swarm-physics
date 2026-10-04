# H95 × G38: Choose a charity and raise money (two rooms) (2026-04-02 → 04-24)

**Verdict:** supported
**Role:** replication + native (exploratory)
**Period:** regime III · 12 committing agents · horizon 20 active h after the kickoff, settled window = its last 4 h · W_∅ start (every agent at ∅ at t = 0).

## Why this period
- An objective (raise money) with no named artifact, two rooms and per-agent goal overrides. Hosts native N2 (rooms).

## Prediction
*Written 2026-10-04 ~20:25 UTC (card), with amendment A1 (synthetic, before any new real-data statistic), before running on this period.*
- Per-unit rule (card): supported if S ≤ 2 with x ≥ 0.5, or S ≥ 3 with x < 0.5; failed if S ≥ 3 with x ≥ 0.5, or S ≤ 2 with x < 0.3; mixed otherwise.
- The unit enters the across-kickoff test P1 (ρ(S, x) ≤ −0.5), whose power at n = 9 is 0.29 (A1).

## Result
*Run 2026-10-04 ~21:40 UTC (`analysis/run.py`; data `data/processed/H95-slack-specificity-gauge/G38/results*.json`; figure `../../figures/summary_obs.pdf`).* x = share of first-4-active-hour agent-work commits on repos that H54 flags as kickoff-named; S = ĀT_e/W (H75 estimator, agent bootstrap B = 200); S₀ = median S after permuting each agent's repo labels among its own commits.

| Unit | N | x (variants) | conc. c | S [95% CI] | T_e (h) | W | Ā (/agent/h) | Ā_ss | S₀ | S_text | synthetic band at x | rule |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| G38 | 12 | 0.01 (strict 0.00; day 1 0.01; agent-weighted 0.01) | 0.26 | 4.82 [1.75, 25.10] | 4.00 | 0.92 | 1.10 | 0.40 | 5.12 | +0.05 | inside [2.67, 5.25] | supported |

W_pre variant (pre-kickoff allocation from the last 2 non-holdout days): S = 21.29, T_e = 12.75 h, W = 0.58.
Post-hoc design code (A2, labelled post hoc): G38 d = 0 (1 = the goal assigns a concrete artifact).

## Scorecard (period-specific axes)
- C/D: the unit's (x, S) point is compared with the synthetic gauge band at its x (descriptive, A1).

## Native N2: two rooms
*Prediction (card):* the room with the higher x has the lower S and T_e; |Δx| ≥ 0.2. Credence 0.35.

Rooms (committing agents, majority room in the first 4 active h): {'3': 8, '2': 4}.

| Unit | N | x (variants) | conc. c | S [95% CI] | T_e (h) | W | Ā (/agent/h) | Ā_ss | S₀ | S_text | synthetic band at x | rule |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| room 3 | 8 | 0.02 (strict 0.00; day 1 0.02; agent-weighted 0.01) | 0.41 | 4.88 [2.74, 8.25] | 10.25 | 1.00 | 0.48 | 0.34 | 5.25 | +0.05 | outside [nan, nan] | supported |
| room 2 | 4 | 0.00 (strict 0.00; day 1 0.00; agent-weighted 0.00) | 0.23 | 3.00 [1.50, 28.59] | 1.25 | 0.75 | 1.80 | 0.50 | 4.58 | +0.05 | outside [nan, nan] | supported |

- Δx = 0.02 (both rooms put < 3% of day-1 work on named repos); S 4.88 (higher-x room) vs 3.00; T_e 10.25 vs 1.25 h.
- **Verdict: failed** (no x contrast to test; the 4-agent #best room settles in 1.25 h, #rest in 10.25 h, as in G44).
