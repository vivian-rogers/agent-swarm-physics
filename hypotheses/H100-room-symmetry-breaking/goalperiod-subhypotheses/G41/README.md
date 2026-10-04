# H100 × G41: #41 after the NE42 split (2026-05-11 → 2026-05-15)

**Verdict:** supported
**Role:** native
**Period:** regime III · #best 4 agents, #rest 11 agents (agent-days by room of the day) · 5 non-holdout days.

## Why this period
Identical room kickoffs, rooms split back to #39's partition after the NE42 merge (#40). H47 found the rooms separated from day 0. Zero explicit field: the clean test of spontaneous divergence, and of remanence across the merge.

## Prediction
*Written 2026-10-04 ~20:30 UTC, before running on this period (card predictions applied).*
- Q_spont > 1 with p < 0.01 (P4, zero explicit field); f_spont ≥ 0.5.
- P6: remanence R(#39, #41) within the relabel null (|z| < 2): the divergence regenerates after the merge.
- Counts against: Q_spont within the null (the separation is composition) or R(#39, #41) > 0 with z ≥ 2 (room memory through the merge).

## Result
*Run 2026-10-04 (`analysis/run.py`, `analysis/summarize.py`; non-holdout).*

| Statistic | bge style_resid (primary) | gte style_resid | bge white32 |
| --- | --- | --- | --- |
| Q (relabel excess), p | 3.82, p < 0.001 | 4.77, p < 0.001 | 3.61, p 0.002 |
| f_comp [95% CI] | 0.18 [0.12, 0.26] | 0.20 | 0.20 |
| Q_res (composition removed), p | 4.29, p < 0.001 | 4.86, p < 0.001 | 4.49, p 0.002 |
| Q_spont (and field removed), p | 4.23, p < 0.001 | 4.85, p < 0.001 | – |
| f_spont [95% CI] | 0.82 [0.74, 0.88] | 0.80 | – |
| f_field | no distinct room field (kickoff cos ≥ 0.95, < 3 operator messages per room) |  |  |

Agents: #best 4, #rest 11 (≥ 2 days, one room); median 5.0 days per agent. Relabel null: 2,000 partitions; f-share CIs: agent bootstrap within rooms (500).
**Remanence #39 → #41 (across the NE42 merge):** R_spont -0.13 (z -1.6, p 0.745); gte -0.09 (z -1.1); raw room difference (composition kept) 0.12 (z -1.4).


## Scorecard (period-specific axes)
- **C:** relabel null after composition and field removal; **E:** NE42 (remanence across the merge).

## Notes
- Data: `data/processed/H100-room-symmetry-breaking/results/results.json` (key `G41`).
