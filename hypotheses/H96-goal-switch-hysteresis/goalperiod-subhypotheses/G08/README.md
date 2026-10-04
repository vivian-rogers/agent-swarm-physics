# H96 × G08: old-state remanence after the #7 → #8 switch (2025-07-18 → 2025-08-12)

**Verdict:** failed
**Role:** replication
**Period:** regime I · transition #7 → #8 · pre day 2025-07-17 · old-state days 2025-07-16 · post days 2025-07-18, 2025-07-21, 2025-07-22 · 20 placebo old states.

## Why this period
The common estimator (card O1–O3, O5) at the transition #7 → #8: both periods non-holdout and in regime I. The row belongs to the new period. It is one point for the card-level order test (O4): its old-state order q and its inertia time τ_old.

## Prediction
*Written 2026-10-04 21:40 UTC, before running on this period (card predictions applied).*
- The old state is identified: M_pre's agent-bootstrap CI excludes 0.
- Quench (card P1, expected): day-1 remanence is a small fraction of the pre level, below the median persistence ratio of ordinary day boundaries (pseudo-switches) of regime I; τ_old < 8 active h (P3).
- HH123's lag reading for this transition: M_1's CI excludes 0 and R₁ ≥ the pseudo-switch median.
- Verdict rule (card): *supported* (lag) if M_pre > 0, M_1 > 0 and R₁ ≥ the pseudo median; *failed* (quench) if M_pre > 0 and either M_1's CI includes 0 or R₁'s CI lies below the pseudo median; *mixed* otherwise; *descriptive* if M_pre's CI includes 0.

## Result
*Run 2026-10-04 (`analysis/run.py`; non-holdout; bge primary, gte check).* 4 agents, 20 placebo old states, old-state order q = 0.636.

| Quantity | bge | gte | Null / reference |
| --- | --- | --- | --- |
| M_pre (old-state excess, pre day) | 0.674 [0.553, 0.798] | 0.782 [0.714, 0.850] | 0 |
| M_1 (day 1 after the switch) | -0.189 [-0.252, -0.167] | -0.108 [-0.212, -0.028] | 0 |
| R₁ = M_1 / M_pre | -0.28 [-0.45, -0.24] | -0.14 [-0.29, -0.03] | pseudo-switch median 0.85 |
| τ_old (active h) | 0.05 [0.05, 0.05] | 0.05 [0.05, 0.05] | quench ≪ 1 h |
| τ_sw switching time, A1 (active h; 500 = no decline) | – [–, –] | – [–, –] | – |
| old kickoff R₁ (O6) | -0.39 [-0.69, -0.19] | – | |
| new-kickoff depth A_K, day 1 | 0.318 [0.235, 0.368] | 0.361 [0.327, 0.387] | 0 |

**Verdict (card rule):** bge failed; gte failed. M_exc by bin (active h 0.2, 0.7, 1.6, 3.0, 6.1, 8.6): -0.119, -0.073, -0.074, -0.359, -0.289, -0.102.

## Scorecard (period-specific axes)
- **C:** placebo old states and pseudo-switches as nulls; **D:** R₁ and τ_old are unfitted relative to the pre level; **F:** synthetic recovery at this transition's counts (`synthetic/synthetic.json`).

## Notes
- Data: `data/processed/H96-goal-switch-hysteresis/results/transitions_{bge_small,gte_modernbert}_style_resid32.json` (key P = 8).
