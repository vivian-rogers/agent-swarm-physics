# H113 × NE03: chat fetch limit inside #10 complete games (#10a 2025-08-18/19 vs #10b 08-20 → 22)

**Verdict:** descriptive
**Role:** native (transition exception c)
**Period:** regime I · mode I · 7 agents · 1 room(s) · 5 non-holdout days. Units 10a, 10b.

## Why this period
NE03 native (#10a 08-18/19 vs #10b 08-20→22): the 2025-08-20 chat fetch limit caps how much of a large batch reaches the context.

## Prediction
*Written 2026-10-04 23:03 UTC, before running on this period (after amendment A1).* **What I had seen:** this period's structural counts (`counts.json`: 1077 scored talk calls; 940 with k ≥ 1, 255 with k ≥ 8; 695 in-flight items) and the synthetic summaries. No uptake statistic.

- **HH345 (P1a here):** a_U = 1 − b̂ has a CI that includes 0.34 in both models. Credence 0.25. Also reported against 0.50, the corrected H18 D2 value (card Note N1).
- **My expectation:** b̂ between 0.7 and 1.1 (a strong bottleneck), because the synthetic shows a time-local topic field alone gives b̂ ≈ 0.8–0.9 and a hard capacity gives ≈ 1.0. Credence 0.6.
- The matched-age read − in-flight contrast > 0 (CI > 0) and redundancy r < 0.7, so that b̂ is identified against a field (A1 rule). Credence 0.5.
- **Native N2 (NE03):** b̂(#10b) > b̂(#10a) (the cap removes deep-queue uptake). Credence 0.3. Descriptive unless each side has ≥ 300 calls with k ≥ 1 and ≥ 30 with k ≥ 8.
- **Against HH345 here:** a_U's CI excludes 0.34 in both models (failed).
- Testable only if ≥ 300 calls with k ≥ 1 and ≥ 30 with k ≥ 8; otherwise descriptive.

## Result
*Run 2026-10-04 23:09 UTC (`analysis/natives.py`).* 

| Side | bge b̂ | gte b̂ | calls k ≥ 1 / k ≥ 8 |
| --- | --- | --- | --- |
| #10a | 0.60 [0.32, 0.78] | 0.76 [0.49, 0.96] | 288 / 91 |
| #10b | 0.63 [0.55, 0.74] | 0.69 [0.59, 0.79] | 652 / 164 |

Δb̂ (#10b − #10a): bge +0.03, gte -0.07. #10a has 288 calls with k ≥ 1 (< 300), so by the pre-set rule the native is **descriptive**; the point estimates show no steepening after the fetch limit (bge +0.03, gte −0.07). Whole period #10 (replication fit): bge b̂ 0.62 [0.51, 0.74], gte 0.71 [0.61, 0.83]; not identified against a field (placebo CI includes 0).

## Scorecard (period-specific axes)
E: not informed (underpowered).

## Notes
- 2026-10-04 23:03 UTC: folder created with the prediction.
