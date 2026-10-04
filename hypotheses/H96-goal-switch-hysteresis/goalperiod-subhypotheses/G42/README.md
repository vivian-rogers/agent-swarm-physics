# H96 × G42: old-state remanence after the #41 → #42 switch (2026-05-18 → 2026-05-22)

**Verdict:** failed
**Role:** replication
**Period:** regime III · transition #41 → #42 · pre day 2026-05-15 · old-state days 2026-05-12, 2026-05-13, 2026-05-14 · post days 2026-05-18, 2026-05-19, 2026-05-20 · 6 placebo old states.

## Why this period
The common estimator (card O1–O3, O5) at the transition #41 → #42: both periods non-holdout and in regime III. The row belongs to the new period. It is one point for the card-level order test (O4): its old-state order q and its inertia time τ_old.

## Prediction
*Written 2026-10-04 21:40 UTC, before running on this period (card predictions applied).*
- The old state is identified: M_pre's agent-bootstrap CI excludes 0.
- Quench (card P1, expected): day-1 remanence is a small fraction of the pre level, below the median persistence ratio of ordinary day boundaries (pseudo-switches) of regime III; τ_old < 8 active h (P3).
- HH123's lag reading for this transition: M_1's CI excludes 0 and R₁ ≥ the pseudo-switch median.
- Verdict rule (card): *supported* (lag) if M_pre > 0, M_1 > 0 and R₁ ≥ the pseudo median; *failed* (quench) if M_pre > 0 and either M_1's CI includes 0 or R₁'s CI lies below the pseudo median; *mixed* otherwise; *descriptive* if M_pre's CI includes 0.

## Result
*Run 2026-10-04 (`analysis/run.py`; non-holdout; bge primary, gte check).* 16 agents, 6 placebo old states, old-state order q = 0.249.

| Quantity | bge | gte | Null / reference |
| --- | --- | --- | --- |
| M_pre (old-state excess, pre day) | 0.265 [0.168, 0.348] | 0.212 [0.110, 0.307] | 0 |
| M_1 (day 1 after the switch) | 0.128 [0.057, 0.179] | 0.060 [-0.004, 0.108] | 0 |
| R₁ = M_1 / M_pre | 0.48 [0.26, 0.72] | 0.28 [-0.02, 0.48] | pseudo-switch median 0.89 |
| τ_old (active h) | 4.72 [0.11, 21.66] | 0.40 [0.15, 2.60] | quench ≪ 1 h |
| τ_sw switching time, A1 (active h; 500 = no decline) | 91.0 [15.3, 500.0] | 138.6 [6.8, 500.0] | – |
| old kickoff R₁ (O6) | 0.21 [-0.29, 0.97] | – | |
| new-kickoff depth A_K, day 1 | 0.439 [0.377, 0.496] | 0.452 [0.374, 0.517] | 0 |

**Verdict (card rule):** bge failed; gte failed. M_exc by bin (active h 0.2, 0.7, 1.5, 3.0, 6.1, 10.0): 0.107, 0.091, 0.087, 0.123, 0.103, 0.171.

## Scorecard (period-specific axes)
- **C:** placebo old states and pseudo-switches as nulls; **D:** R₁ and τ_old are unfitted relative to the pre level; **F:** synthetic recovery at this transition's counts (`synthetic/synthetic.json`).

## Notes
- Data: `data/processed/H96-goal-switch-hysteresis/results/transitions_{bge_small,gte_modernbert}_style_resid32.json` (key P = 42).
