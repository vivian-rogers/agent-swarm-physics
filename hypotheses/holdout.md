# Locked holdout

Locked 2026-10-03, **before any dynamics or exploratory analysis was run.** Machine-readable copy: [`holdout.json`](holdout.json), which every analysis script reads to mask these windows. Exploratory work must exclude them. They're used only to confirm predictions written beforehand on a hypothesis card.

## What's held out

**Natural-experiment windows** (PT dates; end exclusive), reserved because they are the strongest interventional tests:

| Window | Dates | Why |
| --- | --- | --- |
| NE12 | 2026-02-23 → 03-02 | rooms channel cut (S4, S5, H01 D3.2) |
| NE21 + NE23 | 2026-06-08 → 07-06 | hours reversal (4→8→4→8 h) and nudger off/on (S3) |
| NE30 | 2026-03-05 → 03-16 | same-family succession, Gemini 3 Pro → 3.1 Pro (H01 D5.1.b) |
| #51 tail | 2026-09-07 → 09-21 | last two weeks of the private-role era |

**Goal periods** held out in full: **#1, #9, #14, #15, #22, #28, #29, #32, #34, #43, #45, #46, #47, #48, #49, #50** (16 of 51).
- **Blocked by the windows above:** #32, #34, #46–#50.
- **Drawn at random,** stratified by coupling mode (seed 20261003) from the remaining periods (excluding #51):
  - C: #1, #15, #28, #45
  - F: #9, #22
  - I: #14, #43
  - K: #29
  - M: none (only one left in the pool)

## Consequences
- S1's leader test (#45) and the memory week (#43) are now **confirmation-only**.
- The free-week pool for S6 loses #9 and #22 to confirmation; #11, #16, #31 and #37 remain for exploration.
- The quench-lab month (#46–#50) is confirmation-only. S3's predictions are already written in `promotion-shortlist.md`.

## History
The first draw started the NE21 window on Sunday 2026-06-07, which blocked #45 through a single weekend-day overlap. The window was corrected to start on Monday 06-08 (the first 8-hour weekday) and redrawn once with the same seed, still before any data had been examined. The redraw then selected #45 at random anyway. The draw stands; redrawing again would defeat the purpose.
