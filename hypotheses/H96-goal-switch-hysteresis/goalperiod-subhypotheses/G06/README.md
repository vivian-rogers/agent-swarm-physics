# H96 × G06: old-state remanence after the #5 → #6 switch (2025-06-26 → 2025-07-15)

**Verdict:** failed
**Role:** replication
**Period:** regime I · transition #5 → #6 · pre day 2025-06-25 · old-state days 2025-06-20, 2025-06-23, 2025-06-24 · post days 2025-06-26, 2025-06-27, 2025-06-29 · 19 placebo old states.

## Why this period
The common estimator (card O1–O3, O5) at the transition #5 → #6: both periods non-holdout and in regime I. The row belongs to the new period. It is one point for the card-level order test (O4): its old-state order q and its inertia time τ_old.

## Prediction
*Written 2026-10-04 21:40 UTC, before running on this period (card predictions applied).*
- The old state is identified: M_pre's agent-bootstrap CI excludes 0.
- Quench (card P1, expected): day-1 remanence is a small fraction of the pre level, below the median persistence ratio of ordinary day boundaries (pseudo-switches) of regime I; τ_old < 8 active h (P3).
- HH123's lag reading for this transition: M_1's CI excludes 0 and R₁ ≥ the pseudo-switch median.
- Verdict rule (card): *supported* (lag) if M_pre > 0, M_1 > 0 and R₁ ≥ the pseudo median; *failed* (quench) if M_pre > 0 and either M_1's CI includes 0 or R₁'s CI lies below the pseudo median; *mixed* otherwise; *descriptive* if M_pre's CI includes 0.

## Result
*Run 2026-10-04 (`analysis/run.py`; non-holdout; bge primary, gte check).* 4 agents, 19 placebo old states, old-state order q = 0.334.

| Quantity | bge | gte | Null / reference |
| --- | --- | --- | --- |
| M_pre (old-state excess, pre day) | 0.263 [0.103, 0.357] | 0.185 [0.086, 0.329] | 0 |
| M_1 (day 1 after the switch) | -0.041 [-0.144, 0.102] | -0.236 [-0.311, -0.165] | 0 |
| R₁ = M_1 / M_pre | -0.16 [-0.75, 0.32] | -1.28 [-2.27, -0.89] | pseudo-switch median 0.85 |
| τ_old (active h) | 0.10 [0.06, 0.17] | 0.05 [0.05, 0.05] | quench ≪ 1 h |
| τ_sw switching time, A1 (active h; 500 = no decline) | – [500.0, 500.0] | – [–, –] | – |
| old kickoff R₁ (O6) | – [-14.76, -1.86] | – | |
| new-kickoff depth A_K, day 1 | 0.169 [0.105, 0.280] | 0.189 [0.135, 0.278] | 0 |

**Verdict (card rule):** bge failed; gte failed. M_exc by bin (active h 0.2, 0.7, 1.5, 3.0, 18.4): 0.028, -0.085, -0.072, -0.062, 0.230.

## Scorecard (period-specific axes)
- **C:** placebo old states and pseudo-switches as nulls; **D:** R₁ and τ_old are unfitted relative to the pre level; **F:** synthetic recovery at this transition's counts (`synthetic/synthetic.json`).

## Notes
- Data: `data/processed/H96-goal-switch-hysteresis/results/transitions_{bge_small,gte_modernbert}_style_resid32.json` (key P = 6).
