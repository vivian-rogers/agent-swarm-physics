# H96 × G04: old-state remanence after the #3 → #4 switch (2025-05-15 → 2025-06-18)

**Verdict:** failed
**Role:** replication
**Period:** regime I · transition #3 → #4 · pre day 2025-05-14 · old-state days 2025-05-12, 2025-05-13 · post days 2025-05-15, 2025-05-16, 2025-05-19 · 19 placebo old states.

## Why this period
The common estimator (card O1–O3, O5) at the transition #3 → #4: both periods non-holdout and in regime I. The row belongs to the new period. It is one point for the card-level order test (O4): its old-state order q and its inertia time τ_old.

## Prediction
*Written 2026-10-04 21:40 UTC, before running on this period (card predictions applied).*
- The old state is identified: M_pre's agent-bootstrap CI excludes 0.
- Quench (card P1, expected): day-1 remanence is a small fraction of the pre level, below the median persistence ratio of ordinary day boundaries (pseudo-switches) of regime I; τ_old < 8 active h (P3).
- HH123's lag reading for this transition: M_1's CI excludes 0 and R₁ ≥ the pseudo-switch median.
- Verdict rule (card): *supported* (lag) if M_pre > 0, M_1 > 0 and R₁ ≥ the pseudo median; *failed* (quench) if M_pre > 0 and either M_1's CI includes 0 or R₁'s CI lies below the pseudo median; *mixed* otherwise; *descriptive* if M_pre's CI includes 0.

## Result
*Run 2026-10-04 (`analysis/run.py`; non-holdout; bge primary, gte check).* 4 agents, 19 placebo old states, old-state order q = 0.688.

| Quantity | bge | gte | Null / reference |
| --- | --- | --- | --- |
| M_pre (old-state excess, pre day) | 0.397 [0.213, 0.578] | 0.447 [0.325, 0.580] | 0 |
| M_1 (day 1 after the switch) | 0.110 [-0.108, 0.344] | 0.121 [-0.005, 0.333] | 0 |
| R₁ = M_1 / M_pre | 0.28 [-0.50, 0.61] | 0.27 [-0.02, 0.61] | pseudo-switch median 0.85 |
| τ_old (active h) | 0.65 [0.27, 2.53] | 0.88 [0.25, 1.92] | quench ≪ 1 h |
| τ_sw switching time, A1 (active h; 500 = no decline) | 16.5 [1.3, 500.0] | 7.2 [2.7, 500.0] | – |
| old kickoff R₁ (O6) | – [0.45, 8.58] | – | |
| new-kickoff depth A_K, day 1 | 0.214 [-0.026, 0.454] | 0.155 [-0.113, 0.424] | 0 |

**Verdict (card rule):** bge failed; gte failed. M_exc by bin (active h 0.3, 0.7, 1.5, 3.0, 4.7): 0.272, 0.121, 0.020, 0.078, 0.166.

## Scorecard (period-specific axes)
- **C:** placebo old states and pseudo-switches as nulls; **D:** R₁ and τ_old are unfitted relative to the pre level; **F:** synthetic recovery at this transition's counts (`synthetic/synthetic.json`).

## Notes
- Data: `data/processed/H96-goal-switch-hysteresis/results/transitions_{bge_small,gte_modernbert}_style_resid32.json` (key P = 4).
