# H102 × G38: room-specific instructions (2026-04-02 → 2026-04-24)

**Verdict:** mixed
**Role:** native
**Period:** regime III · 14 agents (home room 2: 1 hopper; home room 2: 5 stayer; home room 3: 8 stayer) · 17 non-holdout days.

## Why this period
Room-specific kickoffs: the domains are set by an operator field. No hoppers, so the wall should be empty, and the domain axis should lie along the room-kickoff difference.

## Prediction
*Written 2026-10-04 ~20:32 UTC, before running on this period (card predictions applied).*
- D ≥ 2 with relabel p < 0.05 and I = 0 (P1, P4).
- P5: cos(u, u_f) above the 95th percentile of the direction null.
- P < 0.02 (no hopping read-outs).
- Counts against: positions not bimodal by room, or an axis unrelated to the instructions.

## Result
*Run 2026-10-04 (`analysis/run.py`, `analysis/summarize.py`; non-holdout).*

| Instrument | D | relabel D p95 | p | I (stayers) | stayers on their side |
| --- | --- | --- | --- | --- | --- |
| bge style_resid | 5.40 | 1.02 | 0.003 | 0.08 | 1.00 |
| gte style_resid | 5.04 | 1.02 | 0.001 | 0.08 | 0.92 |
| bge white32 | 5.30 | 1.09 | 0.005 | 0.08 | 1.00 |
| bge dedupe | 5.27 | 1.14 | 0.005 | 0.08 | 1.00 |

Stayers: home A (room 2) 5, home B (room 3) 8. Cross-domain read share: P_hop 0.0001 (items read while in the other room), P_dom 0.0004 (items from other-domain senders). Relabel null: 1,000 draws, axis refitted.

**Domain axis vs room-kickoff direction:** |cos| 0.02 (direction-null p95 0.49, p 0.949); gte 0.03 (p 0.904).

**Hoppers** (wall coordinate s: 0 = home domain centroid, 1 = other domain). Home stayers: median 0.01, 95th percentile 0.21.

| Hopper | statements home / other room | hop-days | s(all) | s(home) | s(statements in other room) | gte s(all) |
| --- | --- | --- | --- | --- | --- | --- |
| 21 | 292 / 1 | 1 | -0.10 | -0.10 | 0.22 | -0.16 |


## Scorecard (period-specific axes)
- **C:** relabel null on D; **G:** room-specific kickoffs are known structure; the axis is not the kickoff direction.

## Notes
- Data: `data/processed/H102-room-domain-walls/results/results.json` (key `G38`).
