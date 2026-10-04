# H100 × G42: #42 (2026-05-18 → 2026-05-22)

**Verdict:** mixed
**Role:** replication
**Period:** regime III · #best 5 agents, #rest 11 agents (agent-days by room of the day) · 5 non-holdout days.

## Why this period
Identical room kickoffs; Gemini 3.5 Flash joins #best on 05-20. Pre side of the 05-25 mover test.

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
| Q (relabel excess), p | 1.50, p 0.132 | 2.33, p 0.004 | 1.27, p 0.230 |
| f_comp [95% CI] | 0.39 [0.23, 0.52] | 0.46 | 0.41 |
| Q_res (composition removed), p | 1.60, p 0.067 | 1.73, p 0.041 | 1.58, p 0.090 |
| Q_spont (and field removed), p | 1.61, p 0.069 | 1.74, p 0.033 | – |
| f_spont [95% CI] | 0.58 [0.46, 0.76] | 0.51 | – |
| f_field (dims: operator), null mean, p | 0.03, 0.07, p 0.638 | 0.04, p 0.649 | – |

Agents: #best 5, #rest 11 (≥ 2 days, one room); median 5.0 days per agent. Relabel null: 2,000 partitions; f-share CIs: agent bootstrap within rooms (500).

## Scorecard (period-specific axes)
- **C:** relabel null; **D:** f-shares and Q_res are not fitted; **F:** synthetic recovery on this skeleton (`synthetic/synthetic_summary.json`).

## Notes
- Data: `data/processed/H100-room-symmetry-breaking/results/results.json` (key `G42`).
