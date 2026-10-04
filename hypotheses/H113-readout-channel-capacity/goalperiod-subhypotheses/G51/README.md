# H113 × G51: maximize your private assigned role (2026-07-06 → 2026-09-04)

**Verdict:** failed
**Role:** native (also replication)
**Period:** regime III · mode I/K · 21–32 agents · 2 room(s) · 45 non-holdout days. Units 51a, 51b, 51c, 51d, 51e, 51f, 51g, 51h, 51i, 51j, 51k, 51l.

## Why this period
The largest regime-III unit set, and the D2 native: timer-wake batches whose size is set by others' talk while the reader slept (k not chosen by the reader).

## Prediction
*Written 2026-10-04 23:03 UTC, before running on this period (after amendment A1).* **What I had seen:** this period's structural counts (`counts.json`: 39857 scored talk calls; 33235 with k ≥ 1, 15395 with k ≥ 8; 12662 in-flight items) and the synthetic summaries. No uptake statistic.

- **HH345 (P1a here):** a_U = 1 − b̂ has a CI that includes 0.34 in both models. Credence 0.25. Also reported against 0.50, the corrected H18 D2 value (card Note N1).
- **My expectation:** b̂ between 0.7 and 1.1 (a strong bottleneck), because the synthetic shows a time-local topic field alone gives b̂ ≈ 0.8–0.9 and a hard capacity gives ≈ 1.0. Credence 0.6.
- The matched-age read − in-flight contrast > 0 (CI > 0) and redundancy r < 0.7, so that b̂ is identified against a field (A1 rule). Credence 0.5.
- **Native N1 (D2 wakes):** b̂ on timer-wake batches within ±0.15 of b̂ on talk calls (both models). Credence 0.5.
- **Against HH345 here:** a_U's CI excludes 0.34 in both models (failed).
- Testable only if ≥ 300 calls with k ≥ 1 and ≥ 30 with k ≥ 8; otherwise descriptive.

## Result
*Run 2026-10-04 23:09 UTC (`analysis/run.py`; non-holdout days only). Data: `data/processed/H113-readout-channel-capacity/G51/`; results `results/periods.json`.*

| Statistic | bge | gte | Reference |
| --- | --- | --- | --- |
| talk calls k ≥ 1 / k ≥ 8 | 33235 / 15395 | 33235 / 15395 | testable ≥ 300 / ≥ 30 |
| b̂ (raw projection, primary) | 0.86 [0.84, 0.88] | 0.90 [0.87, 0.92] | 0.66 (HH345), 0.50 (H18 D2), 1 (one message) |
| a_U = 1 − b̂ | 0.14 [0.12, 0.16] | 0.10 [0.08, 0.13] | kill: CI excludes 0.34; also vs 0.50 (N1) |
| b̂, window-field variant (A1 sensitivity) | 0.94 | 0.96 | — |
| matched-age read − in-flight contrast | 0.038 [0.032, 0.044] | 0.047 [0.041, 0.054] | > 0 needed (A1) |
| batch redundancy r | 0.66 | 0.68 | < 0.7 needed (A1); field worlds 0.86–1.12 |
| identified against a field (A1) | True | True | — |
| Gaussian information per call I(k), bits (bge; k bins) | 1-1: 0.59, 2-2: 0.62, 3-4: 0.48, 5-8: 0.44, 9-16: 0.36, >=17: 0.10 | | low-SNR identity a_I ≈ 1 − 2b + r |
| newest − older item slope (bge) | 0.064 [0.058, 0.068] | | > 0 = recency (R4) |

a_U's CI includes 0.34 in 0/2 models and 0.50 in 0/2. a_U's CI excludes 0.34 in both models: failed by the pre-set rule (a stronger bottleneck than HH345).

**Native N1 (D2 timer-wake batches, exogenous k; co-primary after Note N1):** bge b̂ 0.69 [0.63, 0.75], a_U 0.31 [0.25, 0.37]; gte b̂ 0.71 [0.66, 0.76], a_U 0.29 [0.24, 0.34]; placebo contrast 0.044 [0.032, 0.055], r 0.52 (identified). Talk-call b̂ is 0.17–0.19 higher (0.86 / 0.90), so N1 (|Δb| ≤ 0.15) **failed**. The wake design includes 0.34 (bge) or touches it (gte upper bound 0.340) and excludes 0.50 in both models.

## Scorecard (period-specific axes)
C 1 (beats the no-bottleneck and one-message shapes; the field world is excluded only where identified). D 1 where the low-SNR identity is checked. E 0.

## Notes
- 2026-10-04 23:03 UTC: folder created with the prediction.
