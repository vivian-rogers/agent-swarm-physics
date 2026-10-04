# H113 × G37: free 3 days (2026-03-30 → 2026-04-01)

**Verdict:** failed
**Role:** replication
**Period:** regime III · mode F · 12 agents · 2 room(s) · 3 non-holdout days. Units 37.

## Why this period
Regime III period with enough read-out calls for an exponent (506 talk calls with k ≥ 1, 77 with k ≥ 8).

## Prediction
*Written 2026-10-04 23:03 UTC, before running on this period (after amendment A1).* **What I had seen:** this period's structural counts (`counts.json`: 671 scored talk calls; 506 with k ≥ 1, 77 with k ≥ 8; 70 in-flight items) and the synthetic summaries. No uptake statistic.

- **HH345 (P1a here):** a_U = 1 − b̂ has a CI that includes 0.34 in both models. Credence 0.25. Also reported against 0.50, the corrected H18 D2 value (card Note N1).
- **My expectation:** b̂ between 0.7 and 1.1 (a strong bottleneck), because the synthetic shows a time-local topic field alone gives b̂ ≈ 0.8–0.9 and a hard capacity gives ≈ 1.0. Credence 0.6.
- The matched-age read − in-flight contrast > 0 (CI > 0) and redundancy r < 0.7, so that b̂ is identified against a field (A1 rule). Credence 0.5.
- **Against HH345 here:** a_U's CI excludes 0.34 in both models (failed).
- Testable only if ≥ 300 calls with k ≥ 1 and ≥ 30 with k ≥ 8; otherwise descriptive.

## Result
*Run 2026-10-04 23:09 UTC (`analysis/run.py`; non-holdout days only). Data: `data/processed/H113-readout-channel-capacity/G37/`; results `results/periods.json`.*

| Statistic | bge | gte | Reference |
| --- | --- | --- | --- |
| talk calls k ≥ 1 / k ≥ 8 | 506 / 77 | 506 / 77 | testable ≥ 300 / ≥ 30 |
| b̂ (raw projection, primary) | 0.82 [0.75, 0.88] | 0.85 [0.76, 0.92] | 0.66 (HH345), 0.50 (H18 D2), 1 (one message) |
| a_U = 1 − b̂ | 0.18 [0.12, 0.25] | 0.15 [0.08, 0.24] | kill: CI excludes 0.34; also vs 0.50 (N1) |
| b̂, window-field variant (A1 sensitivity) | 0.85 | 0.93 | — |
| matched-age read − in-flight contrast | 0.107 [0.061, 0.150] | 0.144 [0.076, 0.204] | > 0 needed (A1) |
| batch redundancy r | 0.66 | 0.69 | < 0.7 needed (A1); field worlds 0.86–1.12 |
| identified against a field (A1) | True | True | — |
| Gaussian information per call I(k), bits (bge; k bins) | 1-1: 2.66, 2-2: 3.45, 3-4: 2.77, 5-8: 3.55, 9-16: 2.00, >=17: 1.90 | | low-SNR identity a_I ≈ 1 − 2b + r |
| newest − older item slope (bge) | 0.131 [0.096, 0.164] | | > 0 = recency (R4) |

a_U's CI includes 0.34 in 0/2 models and 0.50 in 0/2. a_U's CI excludes 0.34 in both models: failed by the pre-set rule (a stronger bottleneck than HH345).

## Scorecard (period-specific axes)
C 1 (beats the no-bottleneck and one-message shapes; the field world is excluded only where identified). D 1 where the low-SNR identity is checked. E 0.

## Notes
- 2026-10-04 23:03 UTC: folder created with the prediction.
