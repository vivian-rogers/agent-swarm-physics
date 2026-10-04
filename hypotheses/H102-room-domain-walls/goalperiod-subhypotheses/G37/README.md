# H102 × G37: identical kickoffs (2026-03-30 → 2026-04-01)

**Verdict:** mixed
**Role:** replication
**Period:** regime III · 12 agents (home room 2: 3 stayer; home room 3: 1 hopper; home room 3: 8 stayer) · 3 non-holdout days.

## Why this period
Identical kickoffs; rooms barely separated in H47 (C_B 0.55). Fixed rooms, no hoppers: the identical-task comparison for the bimodality half.

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
| bge style_resid | 1.70 | 1.45 | 0.039 | 0.36 | 0.82 |
| gte style_resid | 1.85 | 1.40 | 0.015 | 0.18 | 0.91 |
| bge white32 | 1.59 | 1.47 | 0.040 | 0.36 | 0.82 |
| bge dedupe | 1.75 | 0.91 | 0.035 | 0.36 | 0.82 |

Stayers: home A (room 2) 3, home B (room 3) 8. Cross-domain read share: P_hop 0.0101 (items read while in the other room), P_dom 0.0138 (items from other-domain senders). Relabel null: 1,000 draws, axis refitted.

**Hoppers** (wall coordinate s: 0 = home domain centroid, 1 = other domain). Home stayers: median 0.24, 95th percentile 0.47.

| Hopper | statements home / other room | hop-days | s(all) | s(home) | s(statements in other room) | gte s(all) |
| --- | --- | --- | --- | --- | --- | --- |
| DeepSeek-V3.2 | 176 / 7 | 1 | -0.12 | -0.13 | 0.13 | -0.13 |


## Scorecard (period-specific axes)
- **C:** relabel null on D (axis refitted); **F:** D size and power on fixed-room skeletons (Amendment 1).

## Notes
- Data: `data/processed/H102-room-domain-walls/results/results.json` (key `G37`).
