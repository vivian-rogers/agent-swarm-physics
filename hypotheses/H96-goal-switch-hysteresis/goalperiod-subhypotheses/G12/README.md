# H96 × G12: old-state remanence after the #11 → #12 switch (2025-09-01 → 2025-09-05)

**Verdict:** mixed
**Role:** replication
**Period:** regime I · transition #11 → #12 · pre day 2025-08-29 · old-state days 2025-08-26, 2025-08-27, 2025-08-28 · post days 2025-09-01, 2025-09-02, 2025-09-03 · 19 placebo old states.

## Why this period
The common estimator (card O1–O3, O5) at the transition #11 → #12: both periods non-holdout and in regime I. The row belongs to the new period. It is one point for the card-level order test (O4): its old-state order q and its inertia time τ_old.

## Prediction
*Written 2026-10-04 21:40 UTC, before running on this period (card predictions applied).*
- The old state is identified: M_pre's agent-bootstrap CI excludes 0.
- Quench (card P1, expected): day-1 remanence is a small fraction of the pre level, below the median persistence ratio of ordinary day boundaries (pseudo-switches) of regime I; τ_old < 8 active h (P3).
- HH123's lag reading for this transition: M_1's CI excludes 0 and R₁ ≥ the pseudo-switch median.
- Verdict rule (card): *supported* (lag) if M_pre > 0, M_1 > 0 and R₁ ≥ the pseudo median; *failed* (quench) if M_pre > 0 and either M_1's CI includes 0 or R₁'s CI lies below the pseudo median; *mixed* otherwise; *descriptive* if M_pre's CI includes 0.

## Result
*Run 2026-10-04 (`analysis/run.py`; non-holdout; bge primary, gte check).* 7 agents, 19 placebo old states, old-state order q = 0.260.

| Quantity | bge | gte | Null / reference |
| --- | --- | --- | --- |
| M_pre (old-state excess, pre day) | 0.301 [0.193, 0.403] | 0.197 [0.122, 0.290] | 0 |
| M_1 (day 1 after the switch) | 0.134 [0.059, 0.188] | 0.125 [0.098, 0.158] | 0 |
| R₁ = M_1 / M_pre | 0.44 [0.19, 0.85] | 0.63 [0.46, 0.89] | pseudo-switch median 0.85 |
| τ_old (active h) | 5.30 [0.10, 19.53] | 8.60 [3.92, 34.46] | quench ≪ 1 h |
| τ_sw switching time, A1 (active h; 500 = no decline) | 42.5 [12.6, 500.0] | 500.0 [7.5, 500.0] | – |
| old kickoff R₁ (O6) | – [-15.07, 0.05] | – | |
| new-kickoff depth A_K, day 1 | 0.706 [0.641, 0.750] | 0.682 [0.614, 0.727] | 0 |

**Verdict (card rule):** bge mixed; gte mixed. M_exc by bin (active h 0.3, 0.7, 1.4, 3.0, 6.2, 8.5): 0.045, 0.135, 0.147, 0.131, 0.188, 0.128.

## Scorecard (period-specific axes)
- **C:** placebo old states and pseudo-switches as nulls; **D:** R₁ and τ_old are unfitted relative to the pre level; **F:** synthetic recovery at this transition's counts (`synthetic/synthetic.json`).

## Notes
- Data: `data/processed/H96-goal-switch-hysteresis/results/transitions_{bge_small,gte_modernbert}_style_resid32.json` (key P = 12).
