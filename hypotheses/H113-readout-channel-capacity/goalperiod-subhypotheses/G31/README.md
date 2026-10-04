# H113 × G31: free week (3.7 Sonnet farewell) (2026-02-16 → 2026-02-20)

**Verdict:** descriptive
**Role:** replication
**Period:** regime I · mode F · 11–12 agents · 1 room(s) · 5 non-holdout days. Units 31a, 31b, 31c, 31d.

## Why this period
Regime I period with enough read-out calls for an exponent (2663 talk calls with k ≥ 1, 1216 with k ≥ 8).

## Prediction
*Written 2026-10-04 23:03 UTC, before running on this period (after amendment A1).* **What I had seen:** this period's structural counts (`counts.json`: 2726 scored talk calls; 2663 with k ≥ 1, 1216 with k ≥ 8; 1349 in-flight items) and the synthetic summaries. No uptake statistic.

- **HH345 (P1a here):** a_U = 1 − b̂ has a CI that includes 0.34 in both models. Credence 0.25. Also reported against 0.50, the corrected H18 D2 value (card Note N1).
- **My expectation:** b̂ between 0.7 and 1.1 (a strong bottleneck), because the synthetic shows a time-local topic field alone gives b̂ ≈ 0.8–0.9 and a hard capacity gives ≈ 1.0. Credence 0.6.
- The matched-age read − in-flight contrast > 0 (CI > 0) and redundancy r < 0.7, so that b̂ is identified against a field (A1 rule). Credence 0.5.
- **Against HH345 here:** a_U's CI excludes 0.34 in both models (failed).
- Testable only if ≥ 300 calls with k ≥ 1 and ≥ 30 with k ≥ 8; otherwise descriptive.

## Result
*Run 2026-10-04 23:09 UTC (`analysis/run.py`; non-holdout days only). Data: `data/processed/H113-readout-channel-capacity/G31/`; results `results/periods.json`.*

| Statistic | bge | gte | Reference |
| --- | --- | --- | --- |
| talk calls k ≥ 1 / k ≥ 8 | 2663 / 1216 | 2663 / 1216 | testable ≥ 300 / ≥ 30 |
| b̂ (raw projection, primary) | 0.71 [0.66, 0.76] | 0.74 [0.69, 0.78] | 0.66 (HH345), 0.50 (H18 D2), 1 (one message) |
| a_U = 1 − b̂ | 0.29 [0.24, 0.34] | 0.26 [0.22, 0.31] | kill: CI excludes 0.34; also vs 0.50 (N1) |
| b̂, window-field variant (A1 sensitivity) | 0.68 | 0.69 | — |
| matched-age read − in-flight contrast | 0.007 [-0.011, 0.026] | 0.015 [-0.003, 0.034] | > 0 needed (A1) |
| batch redundancy r | 0.72 | 0.74 | < 0.7 needed (A1); field worlds 0.86–1.12 |
| identified against a field (A1) | False | False | — |
| Gaussian information per call I(k), bits (bge; k bins) | 1-1: 0.37, 2-2: 0.78, 3-4: 1.11, 5-8: 1.78, 9-16: 1.97, >=17: 1.00 | | low-SNR identity a_I ≈ 1 − 2b + r |
| newest − older item slope (bge) | 0.030 [0.017, 0.044] | | > 0 = recency (R4) |

a_U's CI includes 0.34 in 0/2 models and 0.50 in 0/2. Testable but not identified against a time-local field by the A1 rule, so it is reported, not scored.

## Scorecard (period-specific axes)
Not scored (descriptive).

## Notes
- 2026-10-04 23:03 UTC: folder created with the prediction.
