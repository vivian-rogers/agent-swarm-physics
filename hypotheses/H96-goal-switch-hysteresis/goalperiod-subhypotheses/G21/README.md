# H96 × G21: old-state remanence after the #20 → #21 switch (2025-12-01 → 2025-12-05)

**Verdict:** failed
**Role:** replication
**Period:** regime I · transition #20 → #21 · pre day 2025-11-28 · old-state days 2025-11-25, 2025-11-26, 2025-11-27 · post days 2025-12-01, 2025-12-02, 2025-12-03 · 20 placebo old states.

## Why this period
The common estimator (card O1–O3, O5) at the transition #20 → #21: both periods non-holdout and in regime I. The row belongs to the new period. It is one point for the card-level order test (O4): its old-state order q and its inertia time τ_old.

## Prediction
*Written 2026-10-04 21:40 UTC, before running on this period (card predictions applied).*
- The old state is identified: M_pre's agent-bootstrap CI excludes 0.
- Quench (card P1, expected): day-1 remanence is a small fraction of the pre level, below the median persistence ratio of ordinary day boundaries (pseudo-switches) of regime I; τ_old < 8 active h (P3).
- HH123's lag reading for this transition: M_1's CI excludes 0 and R₁ ≥ the pseudo-switch median.
- Verdict rule (card): *supported* (lag) if M_pre > 0, M_1 > 0 and R₁ ≥ the pseudo median; *failed* (quench) if M_pre > 0 and either M_1's CI includes 0 or R₁'s CI lies below the pseudo median; *mixed* otherwise; *descriptive* if M_pre's CI includes 0.

## Result
*Run 2026-10-04 (`analysis/run.py`; non-holdout; bge primary, gte check).* 10 agents, 20 placebo old states, old-state order q = 0.427.

| Quantity | bge | gte | Null / reference |
| --- | --- | --- | --- |
| M_pre (old-state excess, pre day) | 0.033 [0.000, 0.077] | 0.241 [0.157, 0.316] | 0 |
| M_1 (day 1 after the switch) | -0.100 [-0.156, -0.054] | -0.023 [-0.082, 0.043] | 0 |
| R₁ = M_1 / M_pre | -3.08 [-12.67, -1.00] | -0.10 [-0.48, 0.16] | pseudo-switch median 0.85 |
| τ_old (active h) | 0.05 [0.05, 0.05] | 0.11 [0.05, 0.22] | quench ≪ 1 h |
| τ_sw switching time, A1 (active h; 500 = no decline) | – [–, –] | 7.4 [3.0, 500.0] | – |
| old kickoff R₁ (O6) | – [–, –] | – | |
| new-kickoff depth A_K, day 1 | 0.523 [0.452, 0.584] | 0.459 [0.404, 0.514] | 0 |

**Verdict (card rule):** bge failed; gte failed. M_exc by bin (active h 0.3, 0.8, 1.5, 3.1, 6.4, 10.4): -0.080, -0.124, -0.169, -0.048, 0.010, -0.173.

## Scorecard (period-specific axes)
- **C:** placebo old states and pseudo-switches as nulls; **D:** R₁ and τ_old are unfitted relative to the pre level; **F:** synthetic recovery at this transition's counts (`synthetic/synthetic.json`).

## Notes
- Data: `data/processed/H96-goal-switch-hysteresis/results/transitions_{bge_small,gte_modernbert}_style_resid32.json` (key P = 21).
