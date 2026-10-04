# H113 × G16: free week with operator rules (2025-10-06 → 2025-10-10)

**Verdict:** mixed
**Role:** replication
**Period:** regime I · mode F · 7 agents · 1 room(s) · 5 non-holdout days. Units 16.

## Why this period
Regime I period with enough read-out calls for an exponent (1664 talk calls with k ≥ 1, 391 with k ≥ 8).

## Prediction
*Written 2026-10-04 23:03 UTC, before running on this period (after amendment A1).* **What I had seen:** this period's structural counts (`counts.json`: 1889 scored talk calls; 1664 with k ≥ 1, 391 with k ≥ 8; 1108 in-flight items) and the synthetic summaries. No uptake statistic.

- **HH345 (P1a here):** a_U = 1 − b̂ has a CI that includes 0.34 in both models. Credence 0.25. Also reported against 0.50, the corrected H18 D2 value (card Note N1).
- **My expectation:** b̂ between 0.7 and 1.1 (a strong bottleneck), because the synthetic shows a time-local topic field alone gives b̂ ≈ 0.8–0.9 and a hard capacity gives ≈ 1.0. Credence 0.6.
- The matched-age read − in-flight contrast > 0 (CI > 0) and redundancy r < 0.7, so that b̂ is identified against a field (A1 rule). Credence 0.5.
- **Against HH345 here:** a_U's CI excludes 0.34 in both models (failed).
- Testable only if ≥ 300 calls with k ≥ 1 and ≥ 30 with k ≥ 8; otherwise descriptive.

## Result
*Run 2026-10-04 23:09 UTC (`analysis/run.py`; non-holdout days only). Data: `data/processed/H113-readout-channel-capacity/G16/`; results `results/periods.json`.*

| Statistic | bge | gte | Reference |
| --- | --- | --- | --- |
| talk calls k ≥ 1 / k ≥ 8 | 1664 / 391 | 1664 / 391 | testable ≥ 300 / ≥ 30 |
| b̂ (raw projection, primary) | 0.75 [0.63, 0.86] | 0.79 [0.67, 0.90] | 0.66 (HH345), 0.50 (H18 D2), 1 (one message) |
| a_U = 1 − b̂ | 0.25 [0.14, 0.37] | 0.21 [0.10, 0.33] | kill: CI excludes 0.34; also vs 0.50 (N1) |
| b̂, window-field variant (A1 sensitivity) | 0.71 | 0.80 | — |
| matched-age read − in-flight contrast | 0.018 [-0.000, 0.035] | 0.026 [0.002, 0.045] | > 0 needed (A1) |
| batch redundancy r | 0.65 | 0.69 | < 0.7 needed (A1); field worlds 0.86–1.12 |
| identified against a field (A1) | False | True | — |
| Gaussian information per call I(k), bits (bge; k bins) | 1-1: 0.29, 2-2: 0.44, 3-4: 0.42, 5-8: 0.44, 9-16: 0.46, >=17: 0.22 | | low-SNR identity a_I ≈ 1 − 2b + r |
| newest − older item slope (bge) | 0.030 [0.011, 0.050] | | > 0 = recency (R4) |

a_U's CI includes 0.34 in 1/2 models and 0.50 in 0/2. Split between models or b̂ not excluding 0 and 1 in both: mixed.

## Scorecard (period-specific axes)
C 1 (beats the no-bottleneck and one-message shapes; the field world is excluded only where identified). D 1 where the low-SNR identity is checked. E 0.

## Notes
- 2026-10-04 23:03 UTC: folder created with the prediction.
