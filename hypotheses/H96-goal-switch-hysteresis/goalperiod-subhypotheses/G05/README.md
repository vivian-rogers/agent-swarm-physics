# H96 × G05: old-state remanence after the #4 → #5 switch (2025-06-19 → 2025-06-25)

**Verdict:** mixed
**Role:** replication
**Period:** regime I · transition #4 → #5 · pre day 2025-06-18 · old-state days 2025-06-13, 2025-06-16, 2025-06-17 · post days 2025-06-19, 2025-06-20, 2025-06-23 · 19 placebo old states.

## Why this period
The common estimator (card O1–O3, O5) at the transition #4 → #5: both periods non-holdout and in regime I. The row belongs to the new period. It is one point for the card-level order test (O4): its old-state order q and its inertia time τ_old.

## Prediction
*Written 2026-10-04 21:40 UTC, before running on this period (card predictions applied).*
- The old state is identified: M_pre's agent-bootstrap CI excludes 0.
- Quench (card P1, expected): day-1 remanence is a small fraction of the pre level, below the median persistence ratio of ordinary day boundaries (pseudo-switches) of regime I; τ_old < 8 active h (P3).
- HH123's lag reading for this transition: M_1's CI excludes 0 and R₁ ≥ the pseudo-switch median.
- Verdict rule (card): *supported* (lag) if M_pre > 0, M_1 > 0 and R₁ ≥ the pseudo median; *failed* (quench) if M_pre > 0 and either M_1's CI includes 0 or R₁'s CI lies below the pseudo median; *mixed* otherwise; *descriptive* if M_pre's CI includes 0.

## Result
*Run 2026-10-04 (`analysis/run.py`; non-holdout; bge primary, gte check).* 4 agents, 19 placebo old states, old-state order q = 0.504.

| Quantity | bge | gte | Null / reference |
| --- | --- | --- | --- |
| M_pre (old-state excess, pre day) | 0.520 [0.470, 0.621] | 0.629 [0.491, 0.756] | 0 |
| M_1 (day 1 after the switch) | 0.366 [0.239, 0.466] | 0.451 [0.328, 0.547] | 0 |
| R₁ = M_1 / M_pre | 0.70 [0.43, 0.91] | 0.72 [0.54, 0.86] | pseudo-switch median 0.85 |
| τ_old (active h) | 1.75 [0.45, 3.08] | 1.79 [1.24, 2.31] | quench ≪ 1 h |
| τ_sw switching time, A1 (active h; 500 = no decline) | 2.4 [1.5, 18.3] | 1.7 [0.7, 42.0] | – |
| old kickoff R₁ (O6) | 0.38 [-7.38, 2.85] | – | |
| new-kickoff depth A_K, day 1 | 0.200 [0.133, 0.258] | 0.250 [0.187, 0.296] | 0 |

**Verdict (card rule):** bge mixed; gte failed. M_exc by bin (active h 0.2, 0.8, 1.5, 3.0, 5.0): 0.246, 0.260, 0.381, -0.006, 0.143.

## Scorecard (period-specific axes)
- **C:** placebo old states and pseudo-switches as nulls; **D:** R₁ and τ_old are unfitted relative to the pre level; **F:** synthetic recovery at this transition's counts (`synthetic/synthetic.json`).

## Notes
- Data: `data/processed/H96-goal-switch-hysteresis/results/transitions_{bge_small,gte_modernbert}_style_resid32.json` (key P = 5).
