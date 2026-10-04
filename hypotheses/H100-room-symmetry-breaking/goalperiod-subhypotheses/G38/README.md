# H100 × G38: room-specific instructions (2026-04-02 → 2026-04-24)

**Verdict:** mixed
**Role:** native
**Period:** regime III · #best 6 agents, #rest 8 agents (agent-days by room of the day) · 17 non-holdout days.

## Why this period
Room-specific kickoffs (cosine 0.86 between the two room kickoff vectors, H47): the only long period with an explicit room field. Sonnet 4.6 moves #rest → #best at its start (04-02).

## Prediction
*Written 2026-10-04 ~20:30 UTC, before running on this period (card predictions applied).*
- Q > 1 (p < 0.05); f_comp ≤ 0.3.
- P3: f_field along the room-kickoff direction ≥ 0.15 and above the direction null (p < 0.05).
- Q_spont > 1 (p < 0.05): a divergence beyond the field.
- P5 (04-02 mover, Sonnet 4.6, #rest → #best): φ_post ≥ 0.5 and φ_post − φ_comp ≥ 0.5; φ_pre ≤ 0; day-1 φ ≥ 0.5.
- Counts against: f_field at chance (≈ 0.03) or the mover staying with #rest (φ_post < 0).

## Result
*Run 2026-10-04 (`analysis/run.py`, `analysis/summarize.py`; non-holdout).*

| Statistic | bge style_resid (primary) | gte style_resid | bge white32 |
| --- | --- | --- | --- |
| Q (relabel excess), p | 6.85, p < 0.001 | 6.23, p < 0.001 | 6.38, p 0.002 |
| f_comp [95% CI] | 0.03 [-0.02, 0.13] | 0.03 | 0.07 |
| Q_res (composition removed), p | 5.90, p < 0.001 | 5.83, p < 0.001 | 5.80, p 0.002 |
| Q_spont (and field removed), p | 5.68, p < 0.001 | 6.19, p < 0.001 | – |
| f_spont [95% CI] | 0.79 [0.71, 0.86] | 0.97 | – |
| f_field (dims: kickoff_room, operator), null mean, p | 0.18, 0.16, p 0.360 | 0.00, p 0.989 | – |

Agents: #best 6, #rest 8 (≥ 2 days, one room); median 17.0 days per agent. Relabel null: 2,000 partitions; f-share CIs: agent bootstrap within rooms (500).

**Movers at 04-02** (φ: +1 = like a native of the new room, −1 = like a native of the old room; C = native contrast of the stayers, with a stayer-relabel z and p; φ is read only where C has p < 0.05).

| Mover | C_pre z (p) | φ_pre | C_post z (p) | φ_post [95% CI, day bootstrap] | φ_comp | day-1 φ | stayers' φ 5th pct | gte φ_post |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Sonnet 4.6 | 4.4 (0.010) | 2.04 | 5.3 (0.016) | 1.99 [1.86, 2.10] | 0.04 | 1.44 | 0.28 | 2.10 |


## Scorecard (period-specific axes)
- **C:** relabel and direction nulls; **D:** field share and mover φ are unfitted; **E:** the 04-02 move; **G:** room-specific kickoffs are known structure.

## Notes
- Data: `data/processed/H100-room-symmetry-breaking/results/results.json` (key `G38`).
