# H96 × G18: old-state remanence after the #17 → #18 switch (2025-10-20 → 2025-10-31)

**Verdict:** failed
**Role:** replication
**Period:** regime I · transition #17 → #18 · pre day 2025-10-17 · old-state days 2025-10-14, 2025-10-15, 2025-10-16 · post days 2025-10-20, 2025-10-21, 2025-10-22 · 19 placebo old states.

## Why this period
The common estimator (card O1–O3, O5) at the transition #17 → #18: both periods non-holdout and in regime I. The row belongs to the new period. It is one point for the card-level order test (O4): its old-state order q and its inertia time τ_old.

## Prediction
*Written 2026-10-04 21:40 UTC, before running on this period (card predictions applied).*
- The old state is identified: M_pre's agent-bootstrap CI excludes 0.
- Quench (card P1, expected): day-1 remanence is a small fraction of the pre level, below the median persistence ratio of ordinary day boundaries (pseudo-switches) of regime I; τ_old < 8 active h (P3).
- HH123's lag reading for this transition: M_1's CI excludes 0 and R₁ ≥ the pseudo-switch median.
- Verdict rule (card): *supported* (lag) if M_pre > 0, M_1 > 0 and R₁ ≥ the pseudo median; *failed* (quench) if M_pre > 0 and either M_1's CI includes 0 or R₁'s CI lies below the pseudo median; *mixed* otherwise; *descriptive* if M_pre's CI includes 0.

## Result
*Run 2026-10-04 (`analysis/run.py`; non-holdout; bge primary, gte check).* 8 agents, 19 placebo old states, old-state order q = 0.377.

| Quantity | bge | gte | Null / reference |
| --- | --- | --- | --- |
| M_pre (old-state excess, pre day) | 0.667 [0.585, 0.749] | 0.649 [0.592, 0.735] | 0 |
| M_1 (day 1 after the switch) | -0.054 [-0.130, 0.063] | -0.032 [-0.119, 0.032] | 0 |
| R₁ = M_1 / M_pre | -0.08 [-0.21, 0.09] | -0.05 [-0.19, 0.05] | pseudo-switch median 0.85 |
| τ_old (active h) | 0.05 [0.05, 0.05] | 0.05 [0.05, 0.07] | quench ≪ 1 h |
| τ_sw switching time, A1 (active h; 500 = no decline) | 500.0 [7.4, 500.0] | – [5.7, 500.0] | – |
| old kickoff R₁ (O6) | -0.18 [-0.46, 0.02] | – | |
| new-kickoff depth A_K, day 1 | 0.284 [0.236, 0.326] | 0.409 [0.360, 0.464] | 0 |

**Verdict (card rule):** bge failed; gte failed. M_exc by bin (active h 0.2, 0.7, 1.5, 3.1, 6.1, 9.0): -0.070, -0.082, 0.034, -0.008, 0.266, 0.315.

## Scorecard (period-specific axes)
- **C:** placebo old states and pseudo-switches as nulls; **D:** R₁ and τ_old are unfitted relative to the pre level; **F:** synthetic recovery at this transition's counts (`synthetic/synthetic.json`).

## Notes
- Data: `data/processed/H96-goal-switch-hysteresis/results/transitions_{bge_small,gte_modernbert}_style_resid32.json` (key P = 18).
