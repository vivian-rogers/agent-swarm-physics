# H96 × G19: old-state remanence after the #18 → #19 switch (2025-11-03 → 2025-11-14)

**Verdict:** supported
**Role:** replication
**Period:** regime I · transition #18 → #19 · pre day 2025-10-31 · old-state days 2025-10-28, 2025-10-29, 2025-10-30 · post days 2025-11-03, 2025-11-04, 2025-11-05 · 19 placebo old states.

## Why this period
The common estimator (card O1–O3, O5) at the transition #18 → #19: both periods non-holdout and in regime I. The row belongs to the new period. It is one point for the card-level order test (O4): its old-state order q and its inertia time τ_old.

## Prediction
*Written 2026-10-04 21:40 UTC, before running on this period (card predictions applied).*
- The old state is identified: M_pre's agent-bootstrap CI excludes 0.
- Quench (card P1, expected): day-1 remanence is a small fraction of the pre level, below the median persistence ratio of ordinary day boundaries (pseudo-switches) of regime I; τ_old < 8 active h (P3).
- HH123's lag reading for this transition: M_1's CI excludes 0 and R₁ ≥ the pseudo-switch median.
- Verdict rule (card): *supported* (lag) if M_pre > 0, M_1 > 0 and R₁ ≥ the pseudo median; *failed* (quench) if M_pre > 0 and either M_1's CI includes 0 or R₁'s CI lies below the pseudo median; *mixed* otherwise; *descriptive* if M_pre's CI includes 0.

## Result
*Run 2026-10-04 (`analysis/run.py`; non-holdout; bge primary, gte check).* 7 agents, 19 placebo old states, old-state order q = 0.475.

| Quantity | bge | gte | Null / reference |
| --- | --- | --- | --- |
| M_pre (old-state excess, pre day) | 0.381 [0.312, 0.437] | 0.277 [0.209, 0.367] | 0 |
| M_1 (day 1 after the switch) | 0.340 [0.254, 0.429] | 0.204 [0.165, 0.241] | 0 |
| R₁ = M_1 / M_pre | 0.89 [0.69, 1.20] | 0.74 [0.50, 1.07] | pseudo-switch median 0.85 |
| τ_old (active h) | 14.63 [5.23, 84.82] | 6.99 [0.05, 37.28] | quench ≪ 1 h |
| τ_sw switching time, A1 (active h; 500 = no decline) | 500.0 [8.5, 500.0] | 352.7 [6.1, 500.0] | – |
| old kickoff R₁ (O6) | – [-1.31, 19.81] | – | |
| new-kickoff depth A_K, day 1 | 0.224 [0.160, 0.274] | 0.167 [0.078, 0.243] | 0 |

**Verdict (card rule):** bge supported; gte mixed. M_exc by bin (active h 0.2, 0.8, 1.4, 3.1, 5.8, 10.0): 0.015, 0.306, 0.289, 0.300, 0.098, 0.355.

## Scorecard (period-specific axes)
- **C:** placebo old states and pseudo-switches as nulls; **D:** R₁ and τ_old are unfitted relative to the pre level; **F:** synthetic recovery at this transition's counts (`synthetic/synthetic.json`).

## Notes
- Data: `data/processed/H96-goal-switch-hysteresis/results/transitions_{bge_small,gte_modernbert}_style_resid32.json` (key P = 19).
