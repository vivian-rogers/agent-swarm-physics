# H103 × NE43: the operator's daily bookends stop (2026-08-05, inside #51)

**Verdict:** supported
**Role:** native
**Period:** regime III · #51 non-holdout days 07-06 → 08-04 (before) vs 08-05 → 09-04 (after) · the 08-05 room split (#general / #focus) lands on the same day.

## Why this period
The operator's pause/resume messages framed every night until 2026-08-04; after that the runner still stops and starts the agents, but nobody announces it. If the night step needs the announcement, it changes here.

## Prediction
*Written 2026-10-04 21:45 UTC, before running (card N1).*
- Δβ_N = β_N(after) − β_N(before) has a CI that includes 0 [0.6]: the night step, whatever its size, does not depend on the bookends.
- *Against:* the CI excludes 0. Verdict: *supported* if the CI includes 0, *failed* otherwise. Confounded with the room split.

## Result
*Run 2026-10-04 (`analysis/run.py`; non-holdout).*

| Statistic | bge | gte |
| --- | --- | --- |
| β_N before (07-06 → 08-04) | +0.0008 [-0.0253, +0.0234] | -0.0008 [-0.0213, +0.0197] |
| β_N after (08-05 → 09-04) | +0.0234 [-0.0099, +0.0533] | +0.0201 [-0.0130, +0.0601] |
| Δβ_N | +0.0226 [-0.0168, +0.0620] | +0.0209 [-0.0199, +0.0617] |
| β_G before / after | -0.0008 [-0.0177, +0.0136] / -0.0053 [-0.0155, +0.0045] | |
| pairs before / after | 109140 / 104770 | |

**Verdict (card N1 rule):** bge supported; gte supported.
