# H113 × G35: test your game (forked per room) (2026-03-16 → 2026-03-20)

**Verdict:** supported
**Role:** replication
**Period:** regime II · mode C · 12 agents · 2 room(s) · 5 non-holdout days. Units 35.

## Why this period
Regime II period with enough read-out calls for an exponent (1748 talk calls with k ≥ 1, 566 with k ≥ 8).

## Prediction
*Written 2026-10-04 23:03 UTC, before running on this period (after amendment A1).* **What I had seen:** this period's structural counts (`counts.json`: 2022 scored talk calls; 1748 with k ≥ 1, 566 with k ≥ 8; 442 in-flight items) and the synthetic summaries. No uptake statistic.

- **HH345 (P1a here):** a_U = 1 − b̂ has a CI that includes 0.34 in both models. Credence 0.25. Also reported against 0.50, the corrected H18 D2 value (card Note N1).
- **My expectation:** b̂ between 0.7 and 1.1 (a strong bottleneck), because the synthetic shows a time-local topic field alone gives b̂ ≈ 0.8–0.9 and a hard capacity gives ≈ 1.0. Credence 0.6.
- The matched-age read − in-flight contrast > 0 (CI > 0) and redundancy r < 0.7, so that b̂ is identified against a field (A1 rule). Credence 0.5.
- **Against HH345 here:** a_U's CI excludes 0.34 in both models (failed).
- Testable only if ≥ 300 calls with k ≥ 1 and ≥ 30 with k ≥ 8; otherwise descriptive.

## Result
*Run 2026-10-04 23:09 UTC (`analysis/run.py`; non-holdout days only). Data: `data/processed/H113-readout-channel-capacity/G35/`; results `results/periods.json`.*

| Statistic | bge | gte | Reference |
| --- | --- | --- | --- |
| talk calls k ≥ 1 / k ≥ 8 | 1748 / 566 | 1748 / 566 | testable ≥ 300 / ≥ 30 |
| b̂ (raw projection, primary) | 0.68 [0.63, 0.73] | 0.70 [0.65, 0.75] | 0.66 (HH345), 0.50 (H18 D2), 1 (one message) |
| a_U = 1 − b̂ | 0.32 [0.27, 0.37] | 0.30 [0.25, 0.35] | kill: CI excludes 0.34; also vs 0.50 (N1) |
| b̂, window-field variant (A1 sensitivity) | 0.65 | 0.67 | — |
| matched-age read − in-flight contrast | 0.030 [-0.004, 0.068] | 0.049 [0.018, 0.089] | > 0 needed (A1) |
| batch redundancy r | 0.58 | 0.61 | < 0.7 needed (A1); field worlds 0.86–1.12 |
| identified against a field (A1) | False | True | — |
| Gaussian information per call I(k), bits (bge; k bins) | 1-1: 1.01, 2-2: 0.93, 3-4: 1.67, 5-8: 1.65, 9-16: 1.96, >=17: 1.18 | | low-SNR identity a_I ≈ 1 − 2b + r |
| newest − older item slope (bge) | 0.064 [0.046, 0.080] | | > 0 = recency (R4) |

a_U's CI includes 0.34 in 2/2 models and 0.50 in 0/2. a_U's CI includes 0.34 and b̂ excludes 0 and 1 in both models: supported by the pre-set rule.

## Scorecard (period-specific axes)
C 1 (beats the no-bottleneck and one-message shapes; the field world is excluded only where identified). D 1 where the low-SNR identity is checked. E 0.

## Notes
- 2026-10-04 23:03 UTC: folder created with the prediction.
