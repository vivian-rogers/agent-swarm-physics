# H102 × G35: RPG forks per room (2026-03-16 → 2026-03-20)

**Verdict:** mixed
**Role:** replication
**Period:** regime II · 12 agents (home room 2: 3 stayer; home room 3: 1 hopper; home room 3: 8 stayer) · 5 non-holdout days.

## Why this period
The rooms forked the RPG and worked on separate code (H07): a work split. Fixed rooms, no hoppers.

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
| bge style_resid | 1.57 | 1.01 | 0.007 | 0.45 | 0.73 |
| gte style_resid | 2.53 | 0.99 | 0.013 | 0.45 | 0.91 |
| bge white32 | 1.23 | 0.71 | 0.025 | 0.36 | 0.82 |
| bge dedupe | 1.50 | 1.03 | 0.015 | 0.45 | 0.73 |

Stayers: home A (room 2) 3, home B (room 3) 8. Cross-domain read share: P_hop 0.0729 (items read while in the other room), P_dom 0.0198 (items from other-domain senders). Relabel null: 1,000 draws, axis refitted.

**Hoppers** (wall coordinate s: 0 = home domain centroid, 1 = other domain). Home stayers: median 0.32, 95th percentile 0.53.

| Hopper | statements home / other room | hop-days | s(all) | s(home) | s(statements in other room) | gte s(all) |
| --- | --- | --- | --- | --- | --- | --- |
| Claude Haiku 4.5 | 316 / 15 | 3 | -0.17 | -0.19 | -0.12 | 0.14 |


## Scorecard (period-specific axes)
- **C:** relabel null on D (axis refitted); **F:** D size and power on fixed-room skeletons (Amendment 1).

## Notes
- Data: `data/processed/H102-room-domain-walls/results/results.json` (key `G35`).
