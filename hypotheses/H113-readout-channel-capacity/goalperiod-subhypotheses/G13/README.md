# H113 × G13: human-subjects experiment (2025-09-08 → 2025-09-19)

**Verdict:** supported
**Role:** replication
**Period:** regime I · mode C · 6 agents · 1 room(s) · 10 non-holdout days. Units 13.

## Why this period
Regime I period with enough read-out calls for an exponent (3730 talk calls with k ≥ 1, 742 with k ≥ 8).

## Prediction
*Written 2026-10-04 23:03 UTC, before running on this period (after amendment A1).* **What I had seen:** this period's structural counts (`counts.json`: 4507 scored talk calls; 3730 with k ≥ 1, 742 with k ≥ 8; 2963 in-flight items) and the synthetic summaries. No uptake statistic.

- **HH345 (P1a here):** a_U = 1 − b̂ has a CI that includes 0.34 in both models. Credence 0.25. Also reported against 0.50, the corrected H18 D2 value (card Note N1).
- **My expectation:** b̂ between 0.7 and 1.1 (a strong bottleneck), because the synthetic shows a time-local topic field alone gives b̂ ≈ 0.8–0.9 and a hard capacity gives ≈ 1.0. Credence 0.6.
- The matched-age read − in-flight contrast > 0 (CI > 0) and redundancy r < 0.7, so that b̂ is identified against a field (A1 rule). Credence 0.5.
- **Against HH345 here:** a_U's CI excludes 0.34 in both models (failed).
- Testable only if ≥ 300 calls with k ≥ 1 and ≥ 30 with k ≥ 8; otherwise descriptive.

## Result
*Run 2026-10-04 23:09 UTC (`analysis/run.py`; non-holdout days only). Data: `data/processed/H113-readout-channel-capacity/G13/`; results `results/periods.json`.*

| Statistic | bge | gte | Reference |
| --- | --- | --- | --- |
| talk calls k ≥ 1 / k ≥ 8 | 3730 / 742 | 3730 / 742 | testable ≥ 300 / ≥ 30 |
| b̂ (raw projection, primary) | 0.67 [0.60, 0.75] | 0.70 [0.63, 0.77] | 0.66 (HH345), 0.50 (H18 D2), 1 (one message) |
| a_U = 1 − b̂ | 0.33 [0.25, 0.40] | 0.30 [0.23, 0.37] | kill: CI excludes 0.34; also vs 0.50 (N1) |
| b̂, window-field variant (A1 sensitivity) | 0.74 | 0.76 | — |
| matched-age read − in-flight contrast | 0.029 [0.016, 0.041] | 0.027 [0.012, 0.039] | > 0 needed (A1) |
| batch redundancy r | 0.65 | 0.68 | < 0.7 needed (A1); field worlds 0.86–1.12 |
| identified against a field (A1) | True | True | — |
| Gaussian information per call I(k), bits (bge; k bins) | 1-1: 0.24, 2-2: 0.34, 3-4: 0.41, 5-8: 0.52, 9-16: 0.42, >=17: 0.47 | | low-SNR identity a_I ≈ 1 − 2b + r |
| newest − older item slope (bge) | 0.009 [-0.002, 0.020] | | > 0 = recency (R4) |

a_U's CI includes 0.34 in 2/2 models and 0.50 in 0/2. a_U's CI includes 0.34 and b̂ excludes 0 and 1 in both models: supported by the pre-set rule.

## Scorecard (period-specific axes)
C 1 (beats the no-bottleneck and one-message shapes; the field world is excluded only where identified). D 1 where the low-SNR identity is checked. E 0.

## Notes
- 2026-10-04 23:03 UTC: folder created with the prediction.
