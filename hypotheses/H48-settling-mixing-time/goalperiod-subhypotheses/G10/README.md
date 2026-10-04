# H48 × G10: Complete as many games as you can in a week! (2025-08-18 → 2025-08-22)

**Verdict:** supported
**Role:** replication
**Period:** regime I · 7 agents on the kickoff roster · one room (#general) · 5 active days (14.2 active h, 3.0 h/day). Kickoff time from H54.

## Why this period
One phase-diagram point of the replication layer: the common estimators (S1 settling, read-out coverage, bulk mixing, λ₂ rivals) on a non-holdout period of ≥ 5 active days. Nothing period-specific is tested here.

## Prediction
*Templated replication prediction (card P1, P2), written 2026-10-04 ~07:25 UTC before the settling run on this period. Read-out predictors (no content) were already computed: direct coverage T90 = 0.811 active h, depth-5 T90 = 0.96 h, bulk mixing t_mix = 0.031 h, reading rate u = 32.0 /h, λ₂^w,sym (min block) = 68.6 /h.*
- S1 settling is detected (a decaying kickoff excess with ΔBIC ≥ 2).
- τ_S1 falls inside the 80% leave-one-period-out interval of the T90 model fitted on the other periods (the card's P1 rule applied to this point).
- Magnitude (card P2, expected to fail): τ_S1 / T90 ≤ 3.

## Result
| Prediction | Observed | Null | Verdict |
| --- | --- | --- | --- |
| S1 settling detected (bge; gte) | yes (ΔBIC 10.1); gte yes (ΔBIC 14.1) | constant excess | met |
| τ_S1 (active h), bge / gte | 0.98 / 2.57; excess 0.417 → 0.235 | – | – |
| inside the T90 model's 80% LOPO interval | yes (pred 4.36 h) | constant model | met |
| magnitude τ_S1 / T90 ≤ 3 | 1.2 (T90 0.811 h; depth-5 T90 0.96 h) | – | met |
| H20 τ_q (days → h), H54 day τ_K (h) | – d → – h (not detected); 5.4 h | – | descriptive |

Verdict rule (replication): supported = detected, inside the T90 model's LOPO 80% interval and τ/T90 ≤ 3; mixed = inside the interval only; failed = outside; n/a = no detected settling. Figures: `../../figures/` (cross-period). Data: `data/processed/H48-settling-mixing-time/G10/`.

## Scorecard (period-specific axes)
- **C:** the T90 model's out-of-sample error for this point is 1.49 in log τ.
- **D:** magnitude prediction met.

## Notes
- Data: `data/processed/H48-settling-mixing-time/G10/` (`coverage_curves.parquet`, `s1_series_<model>.parquet`); cross-period rows in `readout_period.parquet` and `settling_period.parquet`.
