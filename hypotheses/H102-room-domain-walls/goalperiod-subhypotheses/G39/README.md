# H102 × G39: identical kickoffs after the 04-27 reshuffle (2026-04-27 → 2026-05-01)

**Verdict:** mixed
**Role:** replication
**Period:** regime III · 15 agents (home room 2: 4 stayer; home room 3: 11 stayer) · 5 non-holdout days.

## Why this period
Identical kickoffs after the 04-27 reshuffle. Fixed rooms within the period.

## Prediction
*Written 2026-10-04 ~20:32 UTC, before running on this period (card predictions applied; templated replication prediction).*
- D ≥ 2 with relabel p < 0.05 (P1); for G35 and G41 (work split) this is the card's P1 core; for G37, G39, G42 (identical kickoffs) D is expected lower than the split periods' median.
- Stayers' interior occupancy I ≤ 0.15 in split periods (P1).
- Cross-domain read share P < 0.02 (fixed rooms; H41 cage) (P4).
- Verdict rule: supported if D ≥ 2 with p < 0.05; failed if D < 1 or p > 0.2; mixed otherwise.
- Counts against: D within the relabel null.

## Result
*Run 2026-10-04 (`analysis/run.py`, `analysis/summarize.py`; non-holdout).*

| Instrument | D | relabel D p95 | p | I (stayers) | stayers on their side |
| --- | --- | --- | --- | --- | --- |
| bge style_resid | 1.45 | 0.98 | 0.011 | 0.47 | 0.93 |
| gte style_resid | 0.49 | 0.95 | 0.155 | 0.53 | 0.73 |
| bge white32 | 1.34 | 1.11 | 0.035 | 0.40 | 0.93 |
| bge dedupe | 1.46 | 0.89 | 0.005 | 0.47 | 0.93 |

Stayers: home A (room 2) 4, home B (room 3) 11. Cross-domain read share: P_hop 0.0012 (items read while in the other room), P_dom 0.0012 (items from other-domain senders). Relabel null: 1,000 draws, axis refitted.

## Scorecard (period-specific axes)
- **C:** relabel null on D (axis refitted); **F:** D size and power on fixed-room skeletons (Amendment 1).

## Notes
- Data: `data/processed/H102-room-domain-walls/results/results.json` (key `G39`).
