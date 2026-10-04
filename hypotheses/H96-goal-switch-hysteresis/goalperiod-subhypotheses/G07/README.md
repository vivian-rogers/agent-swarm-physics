# H96 × G07: old-state remanence after the #6 → #7 switch (2025-07-16 → 2025-07-17)

**Verdict:** supported
**Role:** replication
**Period:** regime I · transition #6 → #7 · pre day 2025-07-15 · old-state days 2025-07-10, 2025-07-11, 2025-07-14 · post days 2025-07-16, 2025-07-17 · 19 placebo old states.

## Why this period
The common estimator (card O1–O3, O5) at the transition #6 → #7: both periods non-holdout and in regime I. The row belongs to the new period. It is one point for the card-level order test (O4): its old-state order q and its inertia time τ_old.

## Prediction
*Written 2026-10-04 21:40 UTC, before running on this period (card predictions applied).*
- The old state is identified: M_pre's agent-bootstrap CI excludes 0.
- Quench (card P1, expected): day-1 remanence is a small fraction of the pre level, below the median persistence ratio of ordinary day boundaries (pseudo-switches) of regime I; τ_old < 8 active h (P3).
- HH123's lag reading for this transition: M_1's CI excludes 0 and R₁ ≥ the pseudo-switch median.
- Verdict rule (card): *supported* (lag) if M_pre > 0, M_1 > 0 and R₁ ≥ the pseudo median; *failed* (quench) if M_pre > 0 and either M_1's CI includes 0 or R₁'s CI lies below the pseudo median; *mixed* otherwise; *descriptive* if M_pre's CI includes 0.

## Result
*Run 2026-10-04 (`analysis/run.py`; non-holdout; bge primary, gte check).* 4 agents, 19 placebo old states, old-state order q = 0.494.

| Quantity | bge | gte | Null / reference |
| --- | --- | --- | --- |
| M_pre (old-state excess, pre day) | 0.465 [0.393, 0.562] | 0.524 [0.296, 0.728] | 0 |
| M_1 (day 1 after the switch) | 0.442 [0.378, 0.490] | 0.482 [0.453, 0.525] | 0 |
| R₁ = M_1 / M_pre | 0.95 [0.77, 1.29] | 0.92 [0.69, 1.55] | pseudo-switch median 0.85 |
| τ_old (active h) | 10.35 [5.06, 102.90] | 20.68 [4.61, 500.00] | quench ≪ 1 h |
| τ_sw switching time, A1 (active h; 500 = no decline) | 6.7 [1.8, 500.0] | 138.4 [21.4, 500.0] | – |
| old kickoff R₁ (O6) | – [–, –] | – | |
| new-kickoff depth A_K, day 1 | 0.437 [0.317, 0.517] | 0.367 [0.329, 0.412] | 0 |

**Verdict (card rule):** bge supported; gte supported. M_exc by bin (active h 0.3, 0.7, 1.5, 3.0): 0.293, 0.124, 0.501, 0.396.

## Scorecard (period-specific axes)
- **C:** placebo old states and pseudo-switches as nulls; **D:** R₁ and τ_old are unfitted relative to the pre level; **F:** synthetic recovery at this transition's counts (`synthetic/synthetic.json`).

## Notes
- Data: `data/processed/H96-goal-switch-hysteresis/results/transitions_{bge_small,gte_modernbert}_style_resid32.json` (key P = 7).
