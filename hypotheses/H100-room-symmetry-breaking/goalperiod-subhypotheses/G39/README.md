# H100 × G39: #39 after the 04-27 reshuffle (2026-04-27 → 2026-05-01)

**Verdict:** mixed
**Role:** native
**Period:** regime III · #best 4 agents, #rest 11 agents (agent-days by room of the day) · 5 non-holdout days.

## Why this period
The 04-27 reshuffle: Opus 4.6, Sonnet 4.6 and GPT-5.4 move #best → #rest at the goal start; GPT-5.5 joins #best. Identical room kickoffs. The cleanest swap in the non-holdout data.

## Prediction
*Written 2026-10-04 ~20:30 UTC, before running on this period (card predictions applied).*
- Q > 1 (p < 0.05); f_comp ≤ 0.3; Q_spont > 1 (p < 0.05) (identical kickoffs).
- P5 (04-27 movers Opus 4.6, Sonnet 4.6, GPT-5.4, #best → #rest): φ_post ≥ 0.5 and φ_post − φ_comp ≥ 0.5 for ≥ 2 of 3; φ_pre ≤ 0; day-1 φ ≥ 0.5.
- P7 swap-carry: R_room and R_agent both within the relabel null; if either is significant, R_room > R_agent.
- Counts against: movers keep #best's position (φ_post < 0: agent-carried state), or φ_post ≈ φ_comp (composition).

## Result
*Run 2026-10-04 (`analysis/run.py`, `analysis/summarize.py`; non-holdout).*

| Statistic | bge style_resid (primary) | gte style_resid | bge white32 |
| --- | --- | --- | --- |
| Q (relabel excess), p | 1.56, p 0.069 | 1.08, p 0.365 | 1.52, p 0.106 |
| f_comp [95% CI] | 0.19 [0.05, 0.33] | 0.45 | 0.25 |
| Q_res (composition removed), p | 1.80, p 0.018 | 1.01, p 0.472 | 1.75, p 0.026 |
| Q_spont (and field removed), p | 1.84, p 0.016 | 1.08, p 0.382 | – |
| f_spont [95% CI] | 0.81 [0.66, 0.94] | 0.56 | – |
| f_field (dims: operator), null mean, p | -0.00, 0.06, p 0.956 | -0.00, p 0.941 | – |

Agents: #best 4, #rest 11 (≥ 2 days, one room); median 5.0 days per agent. Relabel null: 2,000 partitions; f-share CIs: agent bootstrap within rooms (500).

**Movers at 04-27** (φ: +1 = like a native of the new room, −1 = like a native of the old room; C = native contrast of the stayers, with a stayer-relabel z and p; φ is read only where C has p < 0.05).

| Mover | C_pre z (p) | φ_pre | C_post z (p) | φ_post [95% CI, day bootstrap] | φ_comp | day-1 φ | stayers' φ 5th pct | gte φ_post |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Opus 4.6 | 5.7 (0.008) | -1.98 | 2.1 (0.044) | 0.77 [-0.46, 8.88] | -0.25 | 1.27 | -0.41 | 2.66 |
| Sonnet 4.6 | 6.3 (0.006) | -1.89 | 1.9 (0.064) | 2.05 [0.72, 11.72] | 0.53 | 2.58 | -0.41 | 0.05 |
| GPT-5.4 | 6.5 (0.004) | -1.27 | 2.0 (0.058) | -3.02 [-20.98, -1.59] | -0.11 | -3.13 | -0.41 | -4.89 |

**Swap-carry (#38 → #39):** R_room -0.23 (z -1.4, p 0.159); R_agent -0.21 (z -2.1, p 0.306); 14 agents in both periods. gte: R_room 0.07 (z 0.5), R_agent 0.10 (z -0.6).


## Scorecard (period-specific axes)
- **C:** relabel null; **D:** mover φ vs φ_comp; **E:** the 04-27 reshuffle is the interventional design; **F:** synthetic mover worlds (`synthetic/synthetic_summary.json`).

## Notes
- Data: `data/processed/H100-room-symmetry-breaking/results/results.json` (key `G39`).
