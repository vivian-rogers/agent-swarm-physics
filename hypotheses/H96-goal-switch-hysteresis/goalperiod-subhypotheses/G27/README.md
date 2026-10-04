# H96 × G27: old-state remanence after the #26 → #27 switch (2026-01-12 → 2026-01-23)

**Verdict:** failed
**Role:** replication
**Period:** regime I · transition #26 → #27 · pre day 2026-01-09 · old-state days 2026-01-06, 2026-01-07, 2026-01-08 · post days 2026-01-12, 2026-01-13, 2026-01-14 · 20 placebo old states.

## Why this period
The common estimator (card O1–O3, O5) at the transition #26 → #27: both periods non-holdout and in regime I. The row belongs to the new period. It is one point for the card-level order test (O4): its old-state order q and its inertia time τ_old.

## Prediction
*Written 2026-10-04 21:40 UTC, before running on this period (card predictions applied).*
- The old state is identified: M_pre's agent-bootstrap CI excludes 0.
- Quench (card P1, expected): day-1 remanence is a small fraction of the pre level, below the median persistence ratio of ordinary day boundaries (pseudo-switches) of regime I; τ_old < 8 active h (P3).
- HH123's lag reading for this transition: M_1's CI excludes 0 and R₁ ≥ the pseudo-switch median.
- Verdict rule (card): *supported* (lag) if M_pre > 0, M_1 > 0 and R₁ ≥ the pseudo median; *failed* (quench) if M_pre > 0 and either M_1's CI includes 0 or R₁'s CI lies below the pseudo median; *mixed* otherwise; *descriptive* if M_pre's CI includes 0.

## Result
*Run 2026-10-04 (`analysis/run.py`; non-holdout; bge primary, gte check).* 10 agents, 20 placebo old states, old-state order q = 0.537.

| Quantity | bge | gte | Null / reference |
| --- | --- | --- | --- |
| M_pre (old-state excess, pre day) | 0.265 [0.170, 0.344] | 0.384 [0.268, 0.469] | 0 |
| M_1 (day 1 after the switch) | 0.078 [-0.011, 0.137] | -0.123 [-0.144, -0.085] | 0 |
| R₁ = M_1 / M_pre | 0.29 [-0.03, 0.62] | -0.32 [-0.47, -0.20] | pseudo-switch median 0.85 |
| τ_old (active h) | 0.13 [0.05, 2.03] | 0.05 [0.05, 0.13] | quench ≪ 1 h |
| τ_sw switching time, A1 (active h; 500 = no decline) | 8.1 [4.4, 500.0] | – [–, –] | – |
| old kickoff R₁ (O6) | 0.47 [0.02, 3.54] | – | |
| new-kickoff depth A_K, day 1 | 0.626 [0.595, 0.661] | 0.532 [0.507, 0.560] | 0 |

**Verdict (card rule):** bge failed; gte failed. M_exc by bin (active h 0.2, 0.7, 1.5, 3.1, 6.0, 10.1): 0.043, 0.024, -0.000, 0.129, 0.011, 0.062.

## Scorecard (period-specific axes)
- **C:** placebo old states and pseudo-switches as nulls; **D:** R₁ and τ_old are unfitted relative to the pre level; **F:** synthetic recovery at this transition's counts (`synthetic/synthetic.json`).

## Notes
- Data: `data/processed/H96-goal-switch-hysteresis/results/transitions_{bge_small,gte_modernbert}_style_resid32.json` (key P = 27).
