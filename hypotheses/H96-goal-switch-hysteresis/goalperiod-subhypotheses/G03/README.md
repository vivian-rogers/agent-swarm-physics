# H96 × G03: old-state remanence after the #2 → #3 switch (2025-05-12 → 2025-05-14)

**Verdict:** failed
**Role:** replication
**Period:** regime I · transition #2 → #3 · pre day 2025-05-11 · old-state days 2025-05-10 · post days 2025-05-12, 2025-05-13, 2025-05-14 · 20 placebo old states.

## Why this period
The common estimator (card O1–O3, O5) at the transition #2 → #3: both periods non-holdout and in regime I. The row belongs to the new period. It is one point for the card-level order test (O4): its old-state order q and its inertia time τ_old.

## Prediction
*Written 2026-10-04 21:40 UTC, before running on this period (card predictions applied).*
- The old state is identified: M_pre's agent-bootstrap CI excludes 0.
- Quench (card P1, expected): day-1 remanence is a small fraction of the pre level, below the median persistence ratio of ordinary day boundaries (pseudo-switches) of regime I; τ_old < 8 active h (P3).
- HH123's lag reading for this transition: M_1's CI excludes 0 and R₁ ≥ the pseudo-switch median.
- Verdict rule (card): *supported* (lag) if M_pre > 0, M_1 > 0 and R₁ ≥ the pseudo median; *failed* (quench) if M_pre > 0 and either M_1's CI includes 0 or R₁'s CI lies below the pseudo median; *mixed* otherwise; *descriptive* if M_pre's CI includes 0.

## Result
*Run 2026-10-04 (`analysis/run.py`; non-holdout; bge primary, gte check).* 4 agents, 20 placebo old states, old-state order q = 0.484.

| Quantity | bge | gte | Null / reference |
| --- | --- | --- | --- |
| M_pre (old-state excess, pre day) | 0.370 [0.112, 0.582] | 0.611 [0.533, 0.767] | 0 |
| M_1 (day 1 after the switch) | -0.100 [-0.161, -0.051] | -0.144 [-0.234, -0.109] | 0 |
| R₁ = M_1 / M_pre | -0.27 [-1.13, -0.11] | -0.23 [-0.42, -0.14] | pseudo-switch median 0.85 |
| τ_old (active h) | 0.05 [0.05, 0.14] | 0.05 [0.05, 0.10] | quench ≪ 1 h |
| τ_sw switching time, A1 (active h; 500 = no decline) | – [0.8, 500.0] | – [–, –] | – |
| old kickoff R₁ (O6) | – [–, –] | – | |
| new-kickoff depth A_K, day 1 | -0.194 [-0.246, -0.130] | -0.029 [-0.080, 0.032] | 0 |

**Verdict (card rule):** bge failed; gte failed. M_exc by bin (active h 0.3, 0.7, 1.5, 3.0, 4.9): -0.085, -0.027, -0.124, 0.470, 0.081.

## Scorecard (period-specific axes)
- **C:** placebo old states and pseudo-switches as nulls; **D:** R₁ and τ_old are unfitted relative to the pre level; **F:** synthetic recovery at this transition's counts (`synthetic/synthetic.json`).

## Notes
- Data: `data/processed/H96-goal-switch-hysteresis/results/transitions_{bge_small,gte_modernbert}_style_resid32.json` (key P = 3).
