# H96 × G26: old-state remanence after the #25 → #26 switch (2026-01-05 → 2026-01-09)

**Verdict:** failed
**Role:** replication
**Period:** regime I · transition #25 → #26 · pre day 2026-01-02 · old-state days 2025-12-30, 2025-12-31, 2026-01-01 · post days 2026-01-05, 2026-01-06, 2026-01-07 · 19 placebo old states.

## Why this period
The common estimator (card O1–O3, O5) at the transition #25 → #26: both periods non-holdout and in regime I. The row belongs to the new period. It is one point for the card-level order test (O4): its old-state order q and its inertia time τ_old.

## Prediction
*Written 2026-10-04 21:40 UTC, before running on this period (card predictions applied).*
- The old state is identified: M_pre's agent-bootstrap CI excludes 0.
- Quench (card P1, expected): day-1 remanence is a small fraction of the pre level, below the median persistence ratio of ordinary day boundaries (pseudo-switches) of regime I; τ_old < 8 active h (P3).
- HH123's lag reading for this transition: M_1's CI excludes 0 and R₁ ≥ the pseudo-switch median.
- Verdict rule (card): *supported* (lag) if M_pre > 0, M_1 > 0 and R₁ ≥ the pseudo median; *failed* (quench) if M_pre > 0 and either M_1's CI includes 0 or R₁'s CI lies below the pseudo median; *mixed* otherwise; *descriptive* if M_pre's CI includes 0.

## Result
*Run 2026-10-04 (`analysis/run.py`; non-holdout; bge primary, gte check).* 10 agents, 19 placebo old states, old-state order q = 0.697.

| Quantity | bge | gte | Null / reference |
| --- | --- | --- | --- |
| M_pre (old-state excess, pre day) | 0.712 [0.595, 0.802] | 0.838 [0.791, 0.886] | 0 |
| M_1 (day 1 after the switch) | 0.217 [0.140, 0.285] | 0.084 [0.027, 0.209] | 0 |
| R₁ = M_1 / M_pre | 0.30 [0.21, 0.39] | 0.10 [0.03, 0.25] | pseudo-switch median 0.85 |
| τ_old (active h) | 0.59 [0.17, 1.01] | 0.13 [0.11, 0.20] | quench ≪ 1 h |
| τ_sw switching time, A1 (active h; 500 = no decline) | 4.0 [2.2, 12.2] | 1.5 [0.8, 3.2] | – |
| old kickoff R₁ (O6) | -0.08 [-0.23, 0.06] | – | |
| new-kickoff depth A_K, day 1 | 0.314 [0.228, 0.396] | 0.277 [0.176, 0.384] | 0 |

**Verdict (card rule):** bge failed; gte failed. M_exc by bin (active h 0.2, 0.8, 1.5, 3.2, 5.8): 0.219, 0.255, 0.286, 0.025, 0.128.

## Scorecard (period-specific axes)
- **C:** placebo old states and pseudo-switches as nulls; **D:** R₁ and τ_old are unfitted relative to the pre level; **F:** synthetic recovery at this transition's counts (`synthetic/synthetic.json`).

## Notes
- Data: `data/processed/H96-goal-switch-hysteresis/results/transitions_{bge_small,gte_modernbert}_style_resid32.json` (key P = 26).
