# H102 × G44: room-specific instructions (2026-05-26 → 2026-05-29)

**Verdict:** mixed
**Role:** native
**Period:** regime III · 18 agents (home room 2: 6 stayer; home room 3: 12 stayer) · 4 non-holdout days.

## Why this period
Room-specific kickoffs (and heavy operator traffic in #best). No hoppers.

## Prediction
*Written 2026-10-04 ~20:32 UTC, before running on this period (card predictions applied).*
- D ≥ 2 with relabel p < 0.05 and I = 0 (P1, P4).
- P5: cos(u, u_f) above the 95th percentile of the direction null.
- P < 0.02.
- Counts against: positions not bimodal by room.

## Result
*Run 2026-10-04 (`analysis/run.py`, `analysis/summarize.py`; non-holdout).*

| Instrument | D | relabel D p95 | p | I (stayers) | stayers on their side |
| --- | --- | --- | --- | --- | --- |
| bge style_resid | 5.31 | 0.88 | 0.001 | 0.17 | 1.00 |
| gte style_resid | 5.65 | 0.92 | 0.001 | 0.11 | 1.00 |
| bge white32 | 5.30 | 0.88 | 0.005 | 0.22 | 1.00 |
| bge dedupe | 5.22 | 0.90 | 0.005 | 0.17 | 1.00 |

Stayers: home A (room 2) 6, home B (room 3) 12. Cross-domain read share: P_hop 0.0000 (items read while in the other room), P_dom 0.0000 (items from other-domain senders). Relabel null: 1,000 draws, axis refitted.

**Domain axis vs room-kickoff direction:** |cos| 0.27 (direction-null p95 0.34, p 0.145); gte 0.20 (p 0.446).

## Scorecard (period-specific axes)
- **C:** relabel null on D; **G:** room kickoffs; the axis is not the kickoff direction.

## Notes
- Data: `data/processed/H102-room-domain-walls/results/results.json` (key `G44`).
