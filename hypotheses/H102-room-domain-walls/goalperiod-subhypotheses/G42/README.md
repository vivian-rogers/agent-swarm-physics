# H102 × G42: identical kickoffs (2026-05-18 → 2026-05-22)

**Verdict:** supported
**Role:** replication
**Period:** regime III · 16 agents (home room 2: 5 stayer; home room 3: 11 stayer) · 5 non-holdout days.

## Why this period
Identical kickoffs. Fixed rooms, no hoppers.

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
| bge style_resid | 2.35 | 1.00 | 0.001 | 0.38 | 0.88 |
| gte style_resid | 2.72 | 0.84 | 0.002 | 0.25 | 1.00 |
| bge white32 | 2.05 | 0.90 | 0.005 | 0.50 | 0.88 |
| bge dedupe | 2.48 | 0.82 | 0.005 | 0.44 | 0.88 |

Stayers: home A (room 2) 5, home B (room 3) 11. Cross-domain read share: P_hop 0.0000 (items read while in the other room), P_dom 0.0000 (items from other-domain senders). Relabel null: 1,000 draws, axis refitted.

## Scorecard (period-specific axes)
- **C:** relabel null on D (axis refitted); **F:** D size and power on fixed-room skeletons (Amendment 1).

## Notes
- Data: `data/processed/H102-room-domain-walls/results/results.json` (key `G42`).
