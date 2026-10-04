# H96 × G40: old-state remanence after the #39 → #40 switch (2026-05-04 → 2026-05-08)

**Verdict:** supported
**Role:** replication
**Period:** regime III · transition #39 → #40 · pre day 2026-05-01 · old-state days 2026-04-28, 2026-04-29, 2026-04-30 · post days 2026-05-04, 2026-05-05, 2026-05-06 · 5 placebo old states.

## Why this period
The common estimator (card O1–O3, O5) at the transition #39 → #40: both periods non-holdout and in regime III. The row belongs to the new period. It is one point for the card-level order test (O4): its old-state order q and its inertia time τ_old.

## Prediction
*Written 2026-10-04 21:40 UTC, before running on this period (card predictions applied).*
- The old state is identified: M_pre's agent-bootstrap CI excludes 0.
- Quench (card P1, expected): day-1 remanence is a small fraction of the pre level, below the median persistence ratio of ordinary day boundaries (pseudo-switches) of regime III; τ_old < 8 active h (P3).
- HH123's lag reading for this transition: M_1's CI excludes 0 and R₁ ≥ the pseudo-switch median.
- Verdict rule (card): *supported* (lag) if M_pre > 0, M_1 > 0 and R₁ ≥ the pseudo median; *failed* (quench) if M_pre > 0 and either M_1's CI includes 0 or R₁'s CI lies below the pseudo median; *mixed* otherwise; *descriptive* if M_pre's CI includes 0.

## Result
*Run 2026-10-04 (`analysis/run.py`; non-holdout; bge primary, gte check).* 15 agents, 5 placebo old states, old-state order q = 0.220.

| Quantity | bge | gte | Null / reference |
| --- | --- | --- | --- |
| M_pre (old-state excess, pre day) | 0.227 [0.161, 0.337] | 0.344 [0.232, 0.462] | 0 |
| M_1 (day 1 after the switch) | 0.325 [0.277, 0.386] | 0.446 [0.359, 0.516] | 0 |
| R₁ = M_1 / M_pre | 1.43 [1.03, 1.92] | 1.30 [0.98, 1.70] | pseudo-switch median 0.89 |
| τ_old (active h) | 500.00 [233.42, 500.00] | 488.59 [31.68, 500.00] | quench ≪ 1 h |
| τ_sw switching time, A1 (active h; 500 = no decline) | 55.4 [22.1, 500.0] | 22.5 [12.9, 67.6] | – |
| old kickoff R₁ (O6) | 0.48 [0.19, 1.22] | – | |
| new-kickoff depth A_K, day 1 | 0.570 [0.489, 0.639] | 0.544 [0.471, 0.604] | 0 |

**Verdict (card rule):** bge supported; gte supported. M_exc by bin (active h 0.2, 0.8, 1.5, 3.1, 6.1, 10.1): 0.273, 0.348, 0.300, 0.314, 0.354, 0.305.

## Scorecard (period-specific axes)
- **C:** placebo old states and pseudo-switches as nulls; **D:** R₁ and τ_old are unfitted relative to the pre level; **F:** synthetic recovery at this transition's counts (`synthetic/synthetic.json`).

## Notes
- Data: `data/processed/H96-goal-switch-hysteresis/results/transitions_{bge_small,gte_modernbert}_style_resid32.json` (key P = 40).
