# H100 × G44: room-specific instructions (2026-05-26 → 2026-05-29)

**Verdict:** mixed
**Role:** native
**Period:** regime III · #best 6 agents, #rest 12 agents (agent-days by room of the day) · 4 non-holdout days.

## Why this period
Room-specific kickoffs (cosine 0.81) and heavy operator traffic in #best (57 human messages vs 2 in #rest). Gemini 3.1 Pro moves #best → #rest at its start (05-25).

## Prediction
*Written 2026-10-04 ~20:30 UTC, before running on this period (card predictions applied).*
- Q > 1 (p < 0.05); f_comp ≤ 0.3.
- P3: f_field along the room-kickoff direction ≥ 0.15 and above the direction null (p < 0.05).
- P5 (05-25 mover, Gemini 3.1 Pro, #best → #rest): φ_post ≥ 0.5 and φ_post − φ_comp ≥ 0.5; φ_pre ≤ 0.
- Counts against: f_field at chance, or the mover staying with #best.

## Result
*Run 2026-10-04 (`analysis/run.py`, `analysis/summarize.py`; non-holdout).*

| Statistic | bge style_resid (primary) | gte style_resid | bge white32 |
| --- | --- | --- | --- |
| Q (relabel excess), p | 5.09, p < 0.001 | 6.79, p < 0.001 | 4.56, p 0.002 |
| f_comp [95% CI] | 0.08 [0.00, 0.18] | 0.10 | 0.07 |
| Q_res (composition removed), p | 5.29, p < 0.001 | 6.58, p < 0.001 | 5.25, p 0.002 |
| Q_spont (and field removed), p | 5.20, p < 0.001 | 6.49, p < 0.001 | – |
| f_spont [95% CI] | 0.85 [0.74, 0.92] | 0.86 | – |
| f_field (dims: kickoff_room), null mean, p | 0.08, 0.03, p 0.088 | 0.04, p 0.433 | – |

Agents: #best 6, #rest 12 (≥ 2 days, one room); median 4.0 days per agent. Relabel null: 2,000 partitions; f-share CIs: agent bootstrap within rooms (500).

**Movers at 05-25** (φ: +1 = like a native of the new room, −1 = like a native of the old room; C = native contrast of the stayers, with a stayer-relabel z and p; φ is read only where C has p < 0.05).

| Mover | C_pre z (p) | φ_pre | C_post z (p) | φ_post [95% CI, day bootstrap] | φ_comp | day-1 φ | stayers' φ 5th pct | gte φ_post |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Gemini 3.1 Pro | 1.5 (0.076) | -3.29 | 6.5 (0.002) | 0.98 [0.76, 1.27] | -0.20 | 0.88 | -0.00 | 0.79 |


## Scorecard (period-specific axes)
- **C:** relabel and direction nulls; **D:** field share and mover φ; **E:** the 05-25 move; **G:** room kickoffs.

## Notes
- Data: `data/processed/H100-room-symmetry-breaking/results/results.json` (key `G44`).
