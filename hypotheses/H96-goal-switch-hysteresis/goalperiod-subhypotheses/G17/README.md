# H96 × G17: old-state remanence after the #16 → #17 switch (2025-10-13 → 2025-10-17)

**Verdict:** failed
**Role:** replication
**Period:** regime I · transition #16 → #17 · pre day 2025-10-10 · old-state days 2025-10-07, 2025-10-08, 2025-10-09 · post days 2025-10-13, 2025-10-14, 2025-10-15 · 20 placebo old states.

## Why this period
The common estimator (card O1–O3, O5) at the transition #16 → #17: both periods non-holdout and in regime I. The row belongs to the new period. It is one point for the card-level order test (O4): its old-state order q and its inertia time τ_old.

## Prediction
*Written 2026-10-04 21:40 UTC, before running on this period (card predictions applied).*
- The old state is identified: M_pre's agent-bootstrap CI excludes 0.
- Quench (card P1, expected): day-1 remanence is a small fraction of the pre level, below the median persistence ratio of ordinary day boundaries (pseudo-switches) of regime I; τ_old < 8 active h (P3).
- HH123's lag reading for this transition: M_1's CI excludes 0 and R₁ ≥ the pseudo-switch median.
- Verdict rule (card): *supported* (lag) if M_pre > 0, M_1 > 0 and R₁ ≥ the pseudo median; *failed* (quench) if M_pre > 0 and either M_1's CI includes 0 or R₁'s CI lies below the pseudo median; *mixed* otherwise; *descriptive* if M_pre's CI includes 0.

## Result
*Run 2026-10-04 (`analysis/run.py`; non-holdout; bge primary, gte check).* 7 agents, 20 placebo old states, old-state order q = 0.313.

| Quantity | bge | gte | Null / reference |
| --- | --- | --- | --- |
| M_pre (old-state excess, pre day) | 0.235 [0.141, 0.375] | 0.240 [0.096, 0.414] | 0 |
| M_1 (day 1 after the switch) | 0.010 [-0.070, 0.080] | 0.017 [-0.068, 0.103] | 0 |
| R₁ = M_1 / M_pre | 0.04 [-0.38, 0.26] | 0.07 [-0.55, 0.30] | pseudo-switch median 0.85 |
| τ_old (active h) | 0.05 [0.05, 0.18] | 0.13 [0.05, 0.29] | quench ≪ 1 h |
| τ_sw switching time, A1 (active h; 500 = no decline) | 8.1 [2.8, 500.0] | 500.0 [6.3, 500.0] | – |
| old kickoff R₁ (O6) | -1.16 [-37.91, -0.01] | – | |
| new-kickoff depth A_K, day 1 | 0.309 [0.181, 0.438] | 0.330 [0.185, 0.478] | 0 |

**Verdict (card rule):** bge failed; gte failed. M_exc by bin (active h 0.2, 0.7, 1.5, 2.9, 5.8, 8.5): -0.008, -0.015, 0.033, 0.056, -0.064, 0.041.

## Scorecard (period-specific axes)
- **C:** placebo old states and pseudo-switches as nulls; **D:** R₁ and τ_old are unfitted relative to the pre level; **F:** synthetic recovery at this transition's counts (`synthetic/synthetic.json`).

## Notes
- Data: `data/processed/H96-goal-switch-hysteresis/results/transitions_{bge_small,gte_modernbert}_style_resid32.json` (key P = 17).
