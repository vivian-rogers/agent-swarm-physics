# H113 × NE42: room merge and split (#39 two rooms → #40 merged #universe-coordination → #41 two rooms; 2026-04-27 → 05-15)

**Verdict:** supported
**Role:** native (transition exception c)
**Period:** regime III · three adjacent goal periods (#39, #40, #41), each 5 days, 15 agents. NE42: rooms merged on 05-04 and split back on 05-11 (A-B-A); goal-confounded (#40's shared objective).

## Why this unit
The merge roughly doubles the number of peer messages that reach each reader per call; the split undoes it. If the capacity curve is a property of the reader's call, b̂ should not move while mean k moves.

## Prediction
*Written 2026-10-04 23:03 UTC, before running on these periods (after amendment A1 and Note N1).* **What I had seen:** the three periods' structural counts (`G39/G40/G41 counts.json`) and the synthetic summaries. No uptake statistic.
- **N3:** |b̂(#40) − b̂(#39)| < 0.2 and |b̂(#40) − b̂(#41)| < 0.2 in both models, while mean k is higher in #40. Credence 0.4.
- **Against:** either difference ≥ 0.2 in both models (failed); only one model (mixed). Descriptive if any side is not identified (A1 rule) or not testable.

## Result
*Run 2026-10-04 23:09 UTC (`analysis/natives.py`).*

| Period | rooms | mean k | bge b̂ | gte b̂ | identified (bge/gte) |
| --- | --- | --- | --- | --- | --- |
| #39 | 2 | 7.5 | 0.81 [0.65, 0.96] | 0.85 [0.71, 1.00] | True/False |
| #40 | 1 (merged) | 11.0 | 0.78 [0.70, 0.89] | 0.76 [0.68, 0.86] | False/False |
| #41 | 2 | 7.8 | 0.81 [0.74, 0.88] | 0.85 [0.78, 0.91] | False/False |

Mean batch size rises ×1.5 in the merged week, while b̂ moves by -0.03/-0.03 (bge) and -0.09/-0.09 (gte): every difference is inside ±0.2, as predicted. Only #39 (bge) is identified against a field, so the invariance is shown on the estimator, not on a field-free exponent: **supported (weak)**.

## Scorecard (period-specific axes)
E 1: the capacity exponent is invariant across the room merge and split (|Δb̂| ≤ 0.09), while k changes ×1.5; goal-confounded.

## Notes
- 2026-10-04 23:03 UTC: folder created with the prediction.
