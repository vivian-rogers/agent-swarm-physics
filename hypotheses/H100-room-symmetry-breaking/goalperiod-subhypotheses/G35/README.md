# H100 × G35: RPG forks per room (2026-03-16 → 2026-03-20)

**Verdict:** mixed
**Role:** replication
**Period:** regime II · #best 3 agents, #rest 9 agents (agent-days by room of the day) · 5 non-holdout days.

## Why this period
First week of the #best/#rest split (NE15). Each room forked the RPG, so the rooms work on different code from day 1: a room-specific *artifact* field set by the operator's split. Regime II basis, so composition is not estimated (agent constants use the regime-III basis).

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
| Q (relabel excess), p | 2.23, p 0.012 | 2.66, p 0.014 | 1.96, p 0.016 |
| f_field (dims: operator), null mean, p | 0.01, 0.03, p 0.559 | 0.01, p 0.644 | – |

Agents: #best 3, #rest 9 (≥ 2 days, one room); median 5.0 days per agent. Relabel null: 2,000 partitions; f-share CIs: agent bootstrap within rooms (500).

## Scorecard (period-specific axes)
- **C:** relabel null; **D:** f-shares and Q_res are not fitted; **F:** synthetic recovery on this skeleton (`synthetic/synthetic_summary.json`).

## Correction (2026-10-04, blind-rater check)
The verdict changes from **supported** to **mixed**. The period rule needs Q_res > 1 (p < 0.05) and f_comp < 0.5. #35 is regime II, where agent constants are not estimated (regime-III basis only), so neither Q_res nor f_comp exists. The round-1 code (`analysis/summarize.py`) graded #35 on Q alone (2.23, p 0.012). Q shows the rooms differ beyond random groupings. It does not remove composition: #best had 3 agents, and the operator chose them. The failed clause is not met either (Q > 1, p < 0.05), so the rule gives "mixed otherwise". The code now returns "mixed" for #35. `results/results.json` still carries the round-1 "supported" until the next run of `summarize.py`.

## Notes
- Data: `data/processed/H100-room-symmetry-breaking/results/results.json` (key `G35`).
