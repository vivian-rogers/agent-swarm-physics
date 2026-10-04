# H96 × G25: old-state remanence after the #24 → #25 switch (2025-12-29 → 2026-01-02)

**Verdict:** failed
**Role:** replication
**Period:** regime I · transition #24 → #25 · pre day 2025-12-26 · old-state days 2025-12-23, 2025-12-24, 2025-12-25 · post days 2025-12-29, 2025-12-30, 2025-12-31 · 20 placebo old states.

## Why this period
The common estimator (card O1–O3, O5) at the transition #24 → #25: both periods non-holdout and in regime I. The row belongs to the new period. It is one point for the card-level order test (O4): its old-state order q and its inertia time τ_old.

## Prediction
*Written 2026-10-04 21:40 UTC, before running on this period (card predictions applied).*
- The old state is identified: M_pre's agent-bootstrap CI excludes 0.
- Quench (card P1, expected): day-1 remanence is a small fraction of the pre level, below the median persistence ratio of ordinary day boundaries (pseudo-switches) of regime I; τ_old < 8 active h (P3).
- HH123's lag reading for this transition: M_1's CI excludes 0 and R₁ ≥ the pseudo-switch median.
- Verdict rule (card): *supported* (lag) if M_pre > 0, M_1 > 0 and R₁ ≥ the pseudo median; *failed* (quench) if M_pre > 0 and either M_1's CI includes 0 or R₁'s CI lies below the pseudo median; *mixed* otherwise; *descriptive* if M_pre's CI includes 0.

## Result
*Run 2026-10-04 (`analysis/run.py`; non-holdout; bge primary, gte check).* 10 agents, 20 placebo old states, old-state order q = 0.349.

| Quantity | bge | gte | Null / reference |
| --- | --- | --- | --- |
| M_pre (old-state excess, pre day) | 0.355 [0.282, 0.403] | 0.454 [0.347, 0.548] | 0 |
| M_1 (day 1 after the switch) | -0.048 [-0.110, 0.013] | -0.186 [-0.219, -0.159] | 0 |
| R₁ = M_1 / M_pre | -0.14 [-0.32, 0.03] | -0.41 [-0.53, -0.32] | pseudo-switch median 0.85 |
| τ_old (active h) | 0.07 [0.05, 0.12] | 0.05 [0.05, 0.07] | quench ≪ 1 h |
| τ_sw switching time, A1 (active h; 500 = no decline) | – [0.7, 415.8] | – [–, –] | – |
| old kickoff R₁ (O6) | -0.51 [-1.28, 0.03] | – | |
| new-kickoff depth A_K, day 1 | 0.202 [0.165, 0.231] | 0.391 [0.372, 0.410] | 0 |

**Verdict (card rule):** bge failed; gte failed. M_exc by bin (active h 0.2, 0.7, 1.5, 3.1, 6.1, 10.1): 0.018, -0.107, -0.043, -0.028, -0.143, -0.288.

## Scorecard (period-specific axes)
- **C:** placebo old states and pseudo-switches as nulls; **D:** R₁ and τ_old are unfitted relative to the pre level; **F:** synthetic recovery at this transition's counts (`synthetic/synthetic.json`).

## Notes
- Data: `data/processed/H96-goal-switch-hysteresis/results/transitions_{bge_small,gte_modernbert}_style_resid32.json` (key P = 25).
