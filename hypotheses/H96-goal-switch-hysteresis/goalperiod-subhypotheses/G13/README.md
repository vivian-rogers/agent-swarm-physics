# H96 × G13: old-state remanence after the #12 → #13 switch (2025-09-08 → 2025-09-19)

**Verdict:** descriptive
**Role:** replication
**Period:** regime I · transition #12 → #13 · pre day 2025-09-05 · old-state days 2025-09-02, 2025-09-03, 2025-09-04 · post days 2025-09-08, 2025-09-09, 2025-09-10 · 20 placebo old states.

## Why this period
The common estimator (card O1–O3, O5) at the transition #12 → #13: both periods non-holdout and in regime I. The row belongs to the new period. It is one point for the card-level order test (O4): its old-state order q and its inertia time τ_old.

## Prediction
*Written 2026-10-04 21:40 UTC, before running on this period (card predictions applied).*
- The old state is identified: M_pre's agent-bootstrap CI excludes 0.
- Quench (card P1, expected): day-1 remanence is a small fraction of the pre level, below the median persistence ratio of ordinary day boundaries (pseudo-switches) of regime I; τ_old < 8 active h (P3).
- HH123's lag reading for this transition: M_1's CI excludes 0 and R₁ ≥ the pseudo-switch median.
- Verdict rule (card): *supported* (lag) if M_pre > 0, M_1 > 0 and R₁ ≥ the pseudo median; *failed* (quench) if M_pre > 0 and either M_1's CI includes 0 or R₁'s CI lies below the pseudo median; *mixed* otherwise; *descriptive* if M_pre's CI includes 0.

## Result
*Run 2026-10-04 (`analysis/run.py`; non-holdout; bge primary, gte check).* 7 agents, 20 placebo old states, old-state order q = 0.455.

| Quantity | bge | gte | Null / reference |
| --- | --- | --- | --- |
| M_pre (old-state excess, pre day) | 0.041 [-0.028, 0.098] | 0.109 [0.042, 0.191] | 0 |
| M_1 (day 1 after the switch) | 0.188 [0.120, 0.314] | 0.198 [0.081, 0.309] | 0 |
| R₁ = M_1 / M_pre | 4.64 [1.41, 43.25] | 1.81 [0.84, 4.95] | pseudo-switch median 0.85 |
| τ_old (active h) | 500.00 [7.07, 500.00] | 10.35 [1.94, 500.00] | quench ≪ 1 h |
| τ_sw switching time, A1 (active h; 500 = no decline) | 7.4 [1.9, 500.0] | 3.4 [2.0, 500.0] | – |
| old kickoff R₁ (O6) | – [0.59, 147.86] | – | |
| new-kickoff depth A_K, day 1 | 0.141 [0.064, 0.225] | 0.259 [0.196, 0.335] | 0 |

**Verdict (card rule):** bge descriptive; gte supported. M_exc by bin (active h 0.2, 0.8, 1.4, 3.0, 6.0, 8.5): 0.171, 0.131, 0.185, 0.133, 0.091, 0.049.

## Scorecard (period-specific axes)
- **C:** placebo old states and pseudo-switches as nulls; **D:** R₁ and τ_old are unfitted relative to the pre level; **F:** synthetic recovery at this transition's counts (`synthetic/synthetic.json`).

## Notes
- Data: `data/processed/H96-goal-switch-hysteresis/results/transitions_{bge_small,gte_modernbert}_style_resid32.json` (key P = 13).
