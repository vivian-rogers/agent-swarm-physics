# H113 × G23: chess tournament (2025-12-15 → 2025-12-19)

**Verdict:** descriptive
**Role:** replication
**Period:** regime I · mode K · 10 agents · 1 room(s) · 5 non-holdout days. Units 23.

## Why this period
Regime I period with enough read-out calls for an exponent (1655 talk calls with k ≥ 1, 679 with k ≥ 8).

## Prediction
*Written 2026-10-04 23:03 UTC, before running on this period (after amendment A1).* **What I had seen:** this period's structural counts (`counts.json`: 1722 scored talk calls; 1655 with k ≥ 1, 679 with k ≥ 8; 548 in-flight items) and the synthetic summaries. No uptake statistic.

- **HH345 (P1a here):** a_U = 1 − b̂ has a CI that includes 0.34 in both models. Credence 0.25. Also reported against 0.50, the corrected H18 D2 value (card Note N1).
- **My expectation:** b̂ between 0.7 and 1.1 (a strong bottleneck), because the synthetic shows a time-local topic field alone gives b̂ ≈ 0.8–0.9 and a hard capacity gives ≈ 1.0. Credence 0.6.
- The matched-age read − in-flight contrast > 0 (CI > 0) and redundancy r < 0.7, so that b̂ is identified against a field (A1 rule). Credence 0.5.
- **Against HH345 here:** a_U's CI excludes 0.34 in both models (failed).
- Testable only if ≥ 300 calls with k ≥ 1 and ≥ 30 with k ≥ 8; otherwise descriptive.

## Result
*Run 2026-10-04 23:09 UTC (`analysis/run.py`; non-holdout days only). Data: `data/processed/H113-readout-channel-capacity/G23/`; results `results/periods.json`.*

| Statistic | bge | gte | Reference |
| --- | --- | --- | --- |
| talk calls k ≥ 1 / k ≥ 8 | 1655 / 679 | 1655 / 679 | testable ≥ 300 / ≥ 30 |
| b̂ (raw projection, primary) | 0.56 [0.46, 0.67] | 0.57 [0.47, 0.69] | 0.66 (HH345), 0.50 (H18 D2), 1 (one message) |
| a_U = 1 − b̂ | 0.44 [0.33, 0.54] | 0.43 [0.31, 0.53] | kill: CI excludes 0.34; also vs 0.50 (N1) |
| b̂, window-field variant (A1 sensitivity) | 0.43 | 0.37 | — |
| matched-age read − in-flight contrast | -0.012 [-0.034, 0.012] | -0.017 [-0.039, 0.012] | > 0 needed (A1) |
| batch redundancy r | 0.63 | 0.66 | < 0.7 needed (A1); field worlds 0.86–1.12 |
| identified against a field (A1) | False | False | — |
| Gaussian information per call I(k), bits (bge; k bins) | 1-1: 0.31, 2-2: 0.24, 3-4: 0.61, 5-8: 1.15, 9-16: 2.49, >=17: 1.34 | | low-SNR identity a_I ≈ 1 − 2b + r |
| newest − older item slope (bge) | -0.015 [-0.033, 0.005] | | > 0 = recency (R4) |

a_U's CI includes 0.34 in 2/2 models and 0.50 in 2/2. Testable but not identified against a time-local field by the A1 rule, so it is reported, not scored.

## Scorecard (period-specific axes)
Not scored (descriptive).

## Notes
- 2026-10-04 23:03 UTC: folder created with the prediction.
