# H113 × G30: adopt a park (2026-02-09 → 2026-02-13)

**Verdict:** descriptive
**Role:** replication
**Period:** regime I · mode C · 11 agents · 1 room(s) · 5 non-holdout days. Units 30a, 30b.

## Why this period
Regime I period with enough read-out calls for an exponent (2260 talk calls with k ≥ 1, 919 with k ≥ 8).

## Prediction
*Written 2026-10-04 23:03 UTC, before running on this period (after amendment A1).* **What I had seen:** this period's structural counts (`counts.json`: 2325 scored talk calls; 2260 with k ≥ 1, 919 with k ≥ 8; 1051 in-flight items) and the synthetic summaries. No uptake statistic.

- **HH345 (P1a here):** a_U = 1 − b̂ has a CI that includes 0.34 in both models. Credence 0.25. Also reported against 0.50, the corrected H18 D2 value (card Note N1).
- **My expectation:** b̂ between 0.7 and 1.1 (a strong bottleneck), because the synthetic shows a time-local topic field alone gives b̂ ≈ 0.8–0.9 and a hard capacity gives ≈ 1.0. Credence 0.6.
- The matched-age read − in-flight contrast > 0 (CI > 0) and redundancy r < 0.7, so that b̂ is identified against a field (A1 rule). Credence 0.5.
- **Against HH345 here:** a_U's CI excludes 0.34 in both models (failed).
- Testable only if ≥ 300 calls with k ≥ 1 and ≥ 30 with k ≥ 8; otherwise descriptive.

## Result
*Run 2026-10-04 23:09 UTC (`analysis/run.py`; non-holdout days only). Data: `data/processed/H113-readout-channel-capacity/G30/`; results `results/periods.json`.*

| Statistic | bge | gte | Reference |
| --- | --- | --- | --- |
| talk calls k ≥ 1 / k ≥ 8 | 2260 / 919 | 2260 / 919 | testable ≥ 300 / ≥ 30 |
| b̂ (raw projection, primary) | 0.69 [0.65, 0.73] | 0.71 [0.67, 0.75] | 0.66 (HH345), 0.50 (H18 D2), 1 (one message) |
| a_U = 1 − b̂ | 0.31 [0.27, 0.35] | 0.29 [0.25, 0.33] | kill: CI excludes 0.34; also vs 0.50 (N1) |
| b̂, window-field variant (A1 sensitivity) | 0.64 | 0.64 | — |
| matched-age read − in-flight contrast | 0.013 [-0.008, 0.036] | 0.006 [-0.009, 0.023] | > 0 needed (A1) |
| batch redundancy r | 0.73 | 0.76 | < 0.7 needed (A1); field worlds 0.86–1.12 |
| identified against a field (A1) | False | False | — |
| Gaussian information per call I(k), bits (bge; k bins) | 1-1: 0.86, 2-2: 1.73, 3-4: 1.95, 5-8: 2.24, 9-16: 2.93, >=17: 2.67 | | low-SNR identity a_I ≈ 1 − 2b + r |
| newest − older item slope (bge) | 0.031 [0.017, 0.044] | | > 0 = recency (R4) |

a_U's CI includes 0.34 in 1/2 models and 0.50 in 0/2. Testable but not identified against a time-local field by the A1 rule, so it is reported, not scored.

## Scorecard (period-specific axes)
Not scored (descriptive).

## Notes
- 2026-10-04 23:03 UTC: folder created with the prediction.
