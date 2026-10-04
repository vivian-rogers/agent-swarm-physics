# H96 × G20: old-state remanence after the #19 → #20 switch (2025-11-17 → 2025-11-28)

**Verdict:** failed
**Role:** replication
**Period:** regime I · transition #19 → #20 · pre day 2025-11-14 · old-state days 2025-11-11, 2025-11-12, 2025-11-13 · post days 2025-11-17, 2025-11-18, 2025-11-19 · 19 placebo old states.

## Why this period
The common estimator (card O1–O3, O5) at the transition #19 → #20: both periods non-holdout and in regime I. The row belongs to the new period. It is one point for the card-level order test (O4): its old-state order q and its inertia time τ_old.

## Prediction
*Written 2026-10-04 21:40 UTC, before running on this period (card predictions applied).*
- The old state is identified: M_pre's agent-bootstrap CI excludes 0.
- Quench (card P1, expected): day-1 remanence is a small fraction of the pre level, below the median persistence ratio of ordinary day boundaries (pseudo-switches) of regime I; τ_old < 8 active h (P3).
- HH123's lag reading for this transition: M_1's CI excludes 0 and R₁ ≥ the pseudo-switch median.
- Verdict rule (card): *supported* (lag) if M_pre > 0, M_1 > 0 and R₁ ≥ the pseudo median; *failed* (quench) if M_pre > 0 and either M_1's CI includes 0 or R₁'s CI lies below the pseudo median; *mixed* otherwise; *descriptive* if M_pre's CI includes 0.

## Result
*Run 2026-10-04 (`analysis/run.py`; non-holdout; bge primary, gte check).* 9 agents, 19 placebo old states, old-state order q = 0.388.

| Quantity | bge | gte | Null / reference |
| --- | --- | --- | --- |
| M_pre (old-state excess, pre day) | 0.356 [0.258, 0.423] | 0.424 [0.308, 0.542] | 0 |
| M_1 (day 1 after the switch) | 0.004 [-0.045, 0.053] | 0.190 [0.134, 0.238] | 0 |
| R₁ = M_1 / M_pre | 0.01 [-0.12, 0.16] | 0.45 [0.31, 0.61] | pseudo-switch median 0.85 |
| τ_old (active h) | 0.05 [0.05, 0.06] | 0.11 [0.05, 20.02] | quench ≪ 1 h |
| τ_sw switching time, A1 (active h; 500 = no decline) | 500.0 [4.3, 500.0] | 500.0 [500.0, 500.0] | – |
| old kickoff R₁ (O6) | 0.08 [-0.25, 1.65] | – | |
| new-kickoff depth A_K, day 1 | 0.278 [0.224, 0.332] | 0.314 [0.269, 0.357] | 0 |

**Verdict (card rule):** bge failed; gte failed. M_exc by bin (active h 0.2, 0.7, 1.5, 3.2, 6.1, 10.0): -0.075, 0.009, -0.028, 0.035, 0.116, 0.082.

## Scorecard (period-specific axes)
- **C:** placebo old states and pseudo-switches as nulls; **D:** R₁ and τ_old are unfitted relative to the pre level; **F:** synthetic recovery at this transition's counts (`synthetic/synthetic.json`).

## Notes
- Data: `data/processed/H96-goal-switch-hysteresis/results/transitions_{bge_small,gte_modernbert}_style_resid32.json` (key P = 20).
