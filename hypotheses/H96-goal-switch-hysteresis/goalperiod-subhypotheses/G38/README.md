# H96 × G38: old-state remanence after the #37 → #38 switch (2026-04-02 → 2026-04-24)

**Verdict:** failed
**Role:** replication
**Period:** regime III · transition #37 → #38 · pre day 2026-04-01 · old-state days 2026-03-30, 2026-03-31 · post days 2026-04-02, 2026-04-03, 2026-04-06 · 5 placebo old states.

## Why this period
The common estimator (card O1–O3, O5) at the transition #37 → #38: both periods non-holdout and in regime III. The row belongs to the new period. It is one point for the card-level order test (O4): its old-state order q and its inertia time τ_old.

## Prediction
*Written 2026-10-04 21:40 UTC, before running on this period (card predictions applied).*
- The old state is identified: M_pre's agent-bootstrap CI excludes 0.
- Quench (card P1, expected): day-1 remanence is a small fraction of the pre level, below the median persistence ratio of ordinary day boundaries (pseudo-switches) of regime III; τ_old < 8 active h (P3).
- HH123's lag reading for this transition: M_1's CI excludes 0 and R₁ ≥ the pseudo-switch median.
- Verdict rule (card): *supported* (lag) if M_pre > 0, M_1 > 0 and R₁ ≥ the pseudo median; *failed* (quench) if M_pre > 0 and either M_1's CI includes 0 or R₁'s CI lies below the pseudo median; *mixed* otherwise; *descriptive* if M_pre's CI includes 0.

## Result
*Run 2026-10-04 (`analysis/run.py`; non-holdout; bge primary, gte check).* 12 agents, 5 placebo old states, old-state order q = 0.279.

| Quantity | bge | gte | Null / reference |
| --- | --- | --- | --- |
| M_pre (old-state excess, pre day) | 0.200 [0.125, 0.291] | 0.214 [0.074, 0.305] | 0 |
| M_1 (day 1 after the switch) | 0.022 [-0.018, 0.108] | 0.059 [-0.018, 0.135] | 0 |
| R₁ = M_1 / M_pre | 0.11 [-0.08, 0.73] | 0.28 [-0.10, 1.15] | pseudo-switch median 0.89 |
| τ_old (active h) | 0.16 [0.05, 500.00] | 1.75 [0.25, 500.00] | quench ≪ 1 h |
| τ_sw switching time, A1 (active h; 500 = no decline) | 26.5 [7.0, 500.0] | 5.2 [3.8, 500.0] | – |
| old kickoff R₁ (O6) | – [-28.63, -15.18] | – | |
| new-kickoff depth A_K, day 1 | 0.066 [-0.021, 0.158] | 0.078 [0.003, 0.167] | 0 |

**Verdict (card rule):** bge failed; gte failed. M_exc by bin (active h 0.2, 0.8, 1.5, 3.0, 6.1, 10.0): 0.042, 0.065, 0.028, 0.053, 0.155, 0.178.

## Scorecard (period-specific axes)
- **C:** placebo old states and pseudo-switches as nulls; **D:** R₁ and τ_old are unfitted relative to the pre level; **F:** synthetic recovery at this transition's counts (`synthetic/synthetic.json`).

## Notes
- Data: `data/processed/H96-goal-switch-hysteresis/results/transitions_{bge_small,gte_modernbert}_style_resid32.json` (key P = 38).
