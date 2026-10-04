# H113 × G39: build your own interactive world (2026-04-27 → 2026-05-01)

**Verdict:** mixed
**Role:** replication (also NE42 side)
**Period:** regime III · mode I · 15 agents · 2 room(s) · 5 non-holdout days. Units 39.

## Why this period
NE42 native, side A: two rooms (#best/#rest) before the 05-04 merge.

## Prediction
*Written 2026-10-04 23:03 UTC, before running on this period (after amendment A1).* **What I had seen:** this period's structural counts (`counts.json`: 795 scored talk calls; 665 with k ≥ 1, 203 with k ≥ 8; 111 in-flight items) and the synthetic summaries. No uptake statistic.

- **HH345 (P1a here):** a_U = 1 − b̂ has a CI that includes 0.34 in both models. Credence 0.25. Also reported against 0.50, the corrected H18 D2 value (card Note N1).
- **My expectation:** b̂ between 0.7 and 1.1 (a strong bottleneck), because the synthetic shows a time-local topic field alone gives b̂ ≈ 0.8–0.9 and a hard capacity gives ≈ 1.0. Credence 0.6.
- The matched-age read − in-flight contrast > 0 (CI > 0) and redundancy r < 0.7, so that b̂ is identified against a field (A1 rule). Credence 0.5.
- **Native N3 (NE42):** the capacity curve is a property of the call, not the room: |b̂(#40) − b̂(#39)| < 0.2 and |b̂(#40) − b̂(#41)| < 0.2 while mean k rises in #40. Credence 0.4.
- **Against HH345 here:** a_U's CI excludes 0.34 in both models (failed).
- Testable only if ≥ 300 calls with k ≥ 1 and ≥ 30 with k ≥ 8; otherwise descriptive.

## Result
*Run 2026-10-04 23:09 UTC (`analysis/run.py`; non-holdout days only). Data: `data/processed/H113-readout-channel-capacity/G39/`; results `results/periods.json`.*

| Statistic | bge | gte | Reference |
| --- | --- | --- | --- |
| talk calls k ≥ 1 / k ≥ 8 | 665 / 203 | 665 / 203 | testable ≥ 300 / ≥ 30 |
| b̂ (raw projection, primary) | 0.81 [0.65, 0.96] | 0.85 [0.71, 1.00] | 0.66 (HH345), 0.50 (H18 D2), 1 (one message) |
| a_U = 1 − b̂ | 0.19 [0.04, 0.35] | 0.15 [0.00, 0.29] | kill: CI excludes 0.34; also vs 0.50 (N1) |
| b̂, window-field variant (A1 sensitivity) | 0.93 | 1.05 | — |
| matched-age read − in-flight contrast | 0.091 [0.056, 0.146] | 0.063 [0.021, 0.115] | > 0 needed (A1) |
| batch redundancy r | 0.69 | 0.71 | < 0.7 needed (A1); field worlds 0.86–1.12 |
| identified against a field (A1) | True | False | — |
| Gaussian information per call I(k), bits (bge; k bins) | 1-1: 0.46, 2-2: 0.27, 3-4: 0.24, 5-8: 0.29, 9-16: 0.42, >=17: 0.00 | | low-SNR identity a_I ≈ 1 − 2b + r |
| newest − older item slope (bge) | 0.030 [0.011, 0.047] | | > 0 = recency (R4) |

a_U's CI includes 0.34 in 1/2 models and 0.50 in 0/2. Split between models or b̂ not excluding 0 and 1 in both: mixed.

NE42 side: see [`../NE42/README.md`](../NE42/README.md).

## Scorecard (period-specific axes)
C 1 (beats the no-bottleneck and one-message shapes; the field world is excluded only where identified). D 1 where the low-SNR identity is checked. E 0.

## Notes
- 2026-10-04 23:03 UTC: folder created with the prediction.
