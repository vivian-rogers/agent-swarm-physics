# H96 × G41: old-state remanence after the #40 → #41 switch (2026-05-11 → 2026-05-15)

**Verdict:** failed
**Role:** replication
**Period:** regime III · transition #40 → #41 · pre day 2026-05-08 · old-state days 2026-05-05, 2026-05-06, 2026-05-07 · post days 2026-05-11, 2026-05-12, 2026-05-13 · 5 placebo old states.

## Why this period
The common estimator (card O1–O3, O5) at the transition #40 → #41: both periods non-holdout and in regime III. The row belongs to the new period. It is one point for the card-level order test (O4): its old-state order q and its inertia time τ_old.

## Prediction
*Written 2026-10-04 21:40 UTC, before running on this period (card predictions applied).*
- The old state is identified: M_pre's agent-bootstrap CI excludes 0.
- Quench (card P1, expected): day-1 remanence is a small fraction of the pre level, below the median persistence ratio of ordinary day boundaries (pseudo-switches) of regime III; τ_old < 8 active h (P3).
- HH123's lag reading for this transition: M_1's CI excludes 0 and R₁ ≥ the pseudo-switch median.
- Verdict rule (card): *supported* (lag) if M_pre > 0, M_1 > 0 and R₁ ≥ the pseudo median; *failed* (quench) if M_pre > 0 and either M_1's CI includes 0 or R₁'s CI lies below the pseudo median; *mixed* otherwise; *descriptive* if M_pre's CI includes 0.

## Result
*Run 2026-10-04 (`analysis/run.py`; non-holdout; bge primary, gte check).* 15 agents, 5 placebo old states, old-state order q = 0.424.

| Quantity | bge | gte | Null / reference |
| --- | --- | --- | --- |
| M_pre (old-state excess, pre day) | 0.544 [0.404, 0.658] | 0.529 [0.408, 0.640] | 0 |
| M_1 (day 1 after the switch) | -0.151 [-0.256, -0.044] | -0.153 [-0.244, -0.029] | 0 |
| R₁ = M_1 / M_pre | -0.28 [-0.53, -0.08] | -0.29 [-0.52, -0.05] | pseudo-switch median 0.89 |
| τ_old (active h) | 0.05 [0.05, 0.05] | 0.05 [0.05, 0.05] | quench ≪ 1 h |
| τ_sw switching time, A1 (active h; 500 = no decline) | – [4.4, 500.0] | – [2.5, 444.6] | – |
| old kickoff R₁ (O6) | 0.18 [-0.06, 0.51] | – | |
| new-kickoff depth A_K, day 1 | 0.197 [0.165, 0.236] | 0.257 [0.211, 0.299] | 0 |

**Verdict (card rule):** bge failed; gte failed. M_exc by bin (active h 0.2, 0.8, 1.5, 2.9, 5.9, 9.9): -0.239, -0.129, -0.096, -0.112, -0.106, -0.056.

## Scorecard (period-specific axes)
- **C:** placebo old states and pseudo-switches as nulls; **D:** R₁ and τ_old are unfitted relative to the pre level; **F:** synthetic recovery at this transition's counts (`synthetic/synthetic.json`).

## Notes
- Data: `data/processed/H96-goal-switch-hysteresis/results/transitions_{bge_small,gte_modernbert}_style_resid32.json` (key P = 41).
