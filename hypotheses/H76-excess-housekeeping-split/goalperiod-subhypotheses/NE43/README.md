# H76 × NE43 (G51): the operator's daily bookends stop after 2026-08-04

**Verdict:** failed
**Role:** native (exploratory)
**Period:** #51 head; active days within 7 calendar days before 08-05 (07-29 → 08-04) vs after (08-05 → 08-11); placebo boundaries 07-13, 07-20, 07-27, 08-12 with the same windows. 08-05 also starts the #general / #focus room split (H49 note).

## Why this period
- The bookends (pause/resume messages) were a candidate day-edge drive. H49: the edge-induced activity excess persists at ×0.77 after they stop, so the runner's schedule, not the messages, drives the edges.

## Prediction
*Written 2026-10-04 ~20:15 UTC, after the synthetic validation (amendment A1), before running on this period.*
- N1: the after/before ratio of the median daily edge σ_ex (untrimmed) and of the median daily σ_hk (trimmed) both lie inside the placebo range (min–max) → supported. Edge σ_ex below the placebo minimum → failed. Credence 0.6.

## Result
*Run 2026-10-04 ~21:00 UTC (`analysis/run.py: ne43`; `data/processed/H76-excess-housekeeping-split/NE43/results.json`).* Edge excess = debiased σ_ex of the first and last 30-min blocks per agent per day (untrimmed); housekeeping = σ_hk per agent-step on the trimmed grid (days with a trimmed window).

| Boundary | days before / after | edge σ_ex ratio (after/before) | σ_hk ratio (trimmed) |
| --- | --- | --- | --- |
| **08-05 (bookends stop)** | 5 / 5 | **0.34** (0.56 → 0.19 nats/agent/day) | 1.44 |
| 2026-07-13 | 4 / 5 | 0.73 | n/a |
| 2026-07-20 | 5 / 5 | 1.18 | n/a |
| 2026-07-27 | 5 / 5 | 0.92 | 1.54 |
| 2026-08-12 | 5 / 5 | 2.51 | 0.47 |

- Placebo ranges: edge [0.73, 2.51]; σ_hk [0.47, 1.54] (two finite placebo values).
- The edge excess falls to ×0.34 in the week after 08-05, below the placebo minimum (0.73). It recovers the next week: the 08-12 placebo ratio is 2.51. Housekeeping stays inside its placebo range.

**Verdict: failed** (by the pre-set rule: edge σ_ex below the placebo minimum). Reading: a one-week dip in end-of-day excess at the bookend stop, which coincides with the #general/#focus room split (H49 note). With 5 + 5 days and a recovery in the next week, this is a transient, not a step. It does not show that the bookends drove the edges; H49's activity result (×0.77) also argues against that.
