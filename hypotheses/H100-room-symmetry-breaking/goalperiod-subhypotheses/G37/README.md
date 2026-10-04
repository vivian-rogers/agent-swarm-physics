# H100 × G37: #37 (2026-03-30 → 2026-04-01)

**Verdict:** supported
**Role:** replication
**Period:** regime III · #best 3 agents, #rest 9 agents (agent-days by room of the day) · 3 non-holdout days.

## Why this period
Identical room kickoffs; three days. The 04-02 move happens at its end (pre side of the G38 mover test).

## Prediction
*Written 2026-10-04 ~20:30 UTC, before running on this period (card predictions applied; templated replication prediction).*
- Q > 1 with relabel p < 0.05 (P1).
- f_comp ≤ 0.3 (P2; not estimated for #35).
- Identical-kickoff periods (#36, #37, #42): Q_spont > 1 with p < 0.05 and f_spont ≥ 0.5 (P4); f_field along the operator-message direction ≤ 0.1 (P3).
- #35: f_field along the operator-message direction ≤ 0.1; the fork artifact field is not measured, so the divergence counts as spontaneous/endogenous by the card's rule.
- Verdict rule: supported if Q_res > 1 (p < 0.05) and f_comp < 0.5; failed if Q ≤ 1 (p > 0.2) or f_comp ≥ 0.7.
- Counts against: Q within the relabel null, or a room difference that is all composition.

## Result
*Run 2026-10-04 (`analysis/run.py`, `analysis/summarize.py`; non-holdout).*

| Statistic | bge style_resid (primary) | gte style_resid | bge white32 |
| --- | --- | --- | --- |
| Q (relabel excess), p | 2.30, p 0.043 | 2.61, p 0.016 | 2.05, p 0.058 |
| f_comp [95% CI] | 0.09 [-0.02, 0.31] | 0.07 | 0.14 |
| Q_res (composition removed), p | 2.46, p 0.023 | 2.68, p 0.014 | 2.38, p 0.022 |
| Q_spont (and field removed), p | 2.55, p 0.027 | 2.75, p 0.018 | – |
| f_spont [95% CI] | 0.91 [0.69, 1.02] | 0.93 | – |
| f_field | no distinct room field (kickoff cos ≥ 0.95, < 3 operator messages per room) |  |  |

Agents: #best 3, #rest 9 (≥ 2 days, one room); median 3.0 days per agent. Relabel null: 2,000 partitions; f-share CIs: agent bootstrap within rooms (500).

## Scorecard (period-specific axes)
- **C:** relabel null; **D:** f-shares and Q_res are not fitted; **F:** synthetic recovery on this skeleton (`synthetic/synthetic_summary.json`).

## Notes
- Data: `data/processed/H100-room-symmetry-breaking/results/results.json` (key `G37`).
