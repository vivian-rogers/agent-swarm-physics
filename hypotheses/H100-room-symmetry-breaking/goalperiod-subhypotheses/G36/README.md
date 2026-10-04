# H100 × G36: #36 (2026-03-24 → 2026-03-27)

**Verdict:** mixed
**Role:** replication
**Period:** regime III · #best 4 agents, #rest 9 agents (agent-days by room of the day) · 4 non-holdout days (36b + 36c; 36a is regime II).

## Why this period
Identical room kickoffs (H47). The regime-III days (36b, 36c) only; DeepSeek-V3.2 visits #best on 03-26/27 and is dropped from O1 here (it is H102's hopper).

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
| Q (relabel excess), p | 1.68, p 0.121 | 1.10, p 0.358 | 1.39, p 0.214 |
| f_comp [95% CI] | 0.36 [0.18, 0.78] | 0.34 | 0.38 |
| Q_res (composition removed), p | 1.01, p 0.451 | 1.07, p 0.388 | 1.06, p 0.449 |
| Q_spont (and field removed), p | 1.02, p 0.431 | 1.08, p 0.383 | – |
| f_spont [95% CI] | 0.64 [0.22, 0.82] | 0.66 | – |
| f_field | no distinct room field (kickoff cos ≥ 0.95, < 3 operator messages per room) |  |  |

Agents: #best 3, #rest 8 (≥ 2 days, one room); median 4.0 days per agent. Relabel null: 2,000 partitions; f-share CIs: agent bootstrap within rooms (500).

## Scorecard (period-specific axes)
- **C:** relabel null; **D:** f-shares and Q_res are not fitted; **F:** synthetic recovery on this skeleton (`synthetic/synthetic_summary.json`).

## Notes
- Data: `data/processed/H100-room-symmetry-breaking/results/results.json` (key `G36`).
