# H102 × G36: one hopper (DeepSeek-V3.2's #best stint) (2026-03-24 → 2026-03-27)

**Verdict:** mixed
**Role:** native
**Period:** regime III · 12 agents (home room 2: 3 stayer; home room 3: 1 hopper; home room 3: 8 stayer) · 4 non-holdout days (36b + 36c).

## Why this period
DeepSeek-V3.2 moves #rest → #best on 03-26 (19:48 UTC) and back on 03-30 (17:43, first day of #37): the only within-period hopper in the two-room era. One agent, about two days inside.

## Prediction
*Written 2026-10-04 ~20:32 UTC, before running on this period (card predictions applied).*
- P6: DeepSeek-V3.2's s on its #best-stint statements exceeds its pre-stint s by ≥ 0.3; after the stint (#37 days, #37 axis) it falls back toward 0.
- Counts against: no shift during the stint (s change < 0.1).

## Result
*Run 2026-10-04 (`analysis/run.py`, `analysis/summarize.py`; non-holdout).*

| Instrument | D | relabel D p95 | p | I (stayers) | stayers on their side |
| --- | --- | --- | --- | --- | --- |
| bge style_resid | 1.86 | 1.24 | 0.017 | 0.36 | 0.73 |
| gte style_resid | 1.21 | 1.20 | 0.049 | 0.55 | 0.73 |
| bge white32 | 1.53 | 1.42 | 0.030 | 0.45 | 0.73 |
| bge dedupe | 1.75 | 0.85 | 0.015 | 0.45 | 0.82 |

Stayers: home A (room 2) 3, home B (room 3) 8. Cross-domain read share: P_hop 0.0270 (items read while in the other room), P_dom 0.0392 (items from other-domain senders). Relabel null: 1,000 draws, axis refitted.

**Hoppers** (wall coordinate s: 0 = home domain centroid, 1 = other domain). Home stayers: median 0.04, 95th percentile 0.40.

| Hopper | statements home / other room | hop-days | s(all) | s(home) | s(statements in other room) | gte s(all) |
| --- | --- | --- | --- | --- | --- | --- |
| DeepSeek-V3.2 | 71 / 43 | 2 | 0.01 | -0.09 | 0.16 | -0.09 |


## Scorecard (period-specific axes)
- **D:** one hopper's wall coordinate before, during and after; **E:** the 03-26 → 03-30 stint.

## Notes
- Data: `data/processed/H102-room-domain-walls/results/results.json` (key `G36`).
