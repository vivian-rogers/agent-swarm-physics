# H96 × G37: old-state remanence after the #36 → #37 switch (2026-03-30 → 2026-04-01)

**Verdict:** failed
**Role:** replication
**Period:** regime III · transition #36 → #37 · pre day 2026-03-27 · old-state days 2026-03-24, 2026-03-25, 2026-03-26 · post days 2026-03-30, 2026-03-31, 2026-04-01 · 6 placebo old states.

## Why this period
The common estimator (card O1–O3, O5) at the transition #36 → #37: both periods non-holdout and in regime III. The row belongs to the new period. It is one point for the card-level order test (O4): its old-state order q and its inertia time τ_old.

## Prediction
*Written 2026-10-04 21:40 UTC, before running on this period (card predictions applied).*
- The old state is identified: M_pre's agent-bootstrap CI excludes 0.
- Quench (card P1, expected): day-1 remanence is a small fraction of the pre level, below the median persistence ratio of ordinary day boundaries (pseudo-switches) of regime III; τ_old < 8 active h (P3).
- HH123's lag reading for this transition: M_1's CI excludes 0 and R₁ ≥ the pseudo-switch median.
- Verdict rule (card): *supported* (lag) if M_pre > 0, M_1 > 0 and R₁ ≥ the pseudo median; *failed* (quench) if M_pre > 0 and either M_1's CI includes 0 or R₁'s CI lies below the pseudo median; *mixed* otherwise; *descriptive* if M_pre's CI includes 0.

## Result
*Run 2026-10-04 (`analysis/run.py`; non-holdout; bge primary, gte check).* 12 agents, 6 placebo old states, old-state order q = 0.457.

| Quantity | bge | gte | Null / reference |
| --- | --- | --- | --- |
| M_pre (old-state excess, pre day) | 0.421 [0.357, 0.501] | 0.426 [0.355, 0.510] | 0 |
| M_1 (day 1 after the switch) | 0.116 [0.010, 0.220] | 0.001 [-0.074, 0.092] | 0 |
| R₁ = M_1 / M_pre | 0.28 [0.02, 0.60] | 0.00 [-0.16, 0.25] | pseudo-switch median 0.89 |
| τ_old (active h) | 0.28 [0.11, 20.93] | 0.05 [0.05, 0.45] | quench ≪ 1 h |
| τ_sw switching time, A1 (active h; 500 = no decline) | 38.1 [8.1, 500.0] | 500.0 [7.1, 500.0] | – |
| old kickoff R₁ (O6) | 0.25 [-0.02, 0.54] | – | |
| new-kickoff depth A_K, day 1 | 0.053 [-0.032, 0.123] | 0.211 [0.129, 0.287] | 0 |

**Verdict (card rule):** bge failed; gte failed. M_exc by bin (active h 0.3, 0.7, 1.5, 3.0, 4.0, 14.3, 18.6): 0.151, 0.063, 0.041, 0.058, 0.067, 0.174.

## Scorecard (period-specific axes)
- **C:** placebo old states and pseudo-switches as nulls; **D:** R₁ and τ_old are unfitted relative to the pre level; **F:** synthetic recovery at this transition's counts (`synthetic/synthetic.json`).

## Notes
- Data: `data/processed/H96-goal-switch-hysteresis/results/transitions_{bge_small,gte_modernbert}_style_resid32.json` (key P = 37).
