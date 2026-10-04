# H48 × G08: Design the AI Village benchmark for open-ended goal pursuit – and test yourselves on it! (2025-07-18 → 2025-08-12)

**Verdict:** n/a
**Role:** replication
**Period:** regime I · 4 agents on the kickoff roster · one room (#general) · 18 active days (53.6 active h, 3.0 h/day). Kickoff time from H54.

## Why this period
One phase-diagram point of the replication layer: the common estimators (S1 settling, read-out coverage, bulk mixing, λ₂ rivals) on a non-holdout period of ≥ 5 active days. Nothing period-specific is tested here.

## Prediction
*Templated replication prediction (card P1, P2), written 2026-10-04 ~07:25 UTC before the settling run on this period. Read-out predictors (no content) were already computed: direct coverage T90 = 0.049 active h, depth-5 T90 = 0.65 h, bulk mixing t_mix = 0.023 h, reading rate u = 39.3 /h, λ₂^w,sym (min block) = 50.0 /h.*
- S1 settling is detected (a decaying kickoff excess with ΔBIC ≥ 2).
- τ_S1 falls inside the 80% leave-one-period-out interval of the T90 model fitted on the other periods (the card's P1 rule applied to this point).
- Magnitude (card P2, expected to fail): τ_S1 / T90 ≤ 3.

## Result
| Prediction | Observed | Null | Verdict |
| --- | --- | --- | --- |
| S1 settling detected (bge; gte) | no (ΔBIC -2.2); gte no (ΔBIC 3.8) | constant excess | not met |
| τ_S1 (active h), bge / gte | 0.34 / 116; excess 0.336 → 0.169 | – | – |
| inside the T90 model's 80% LOPO interval | – | constant model | – |
| magnitude τ_S1 / T90 ≤ 3 | – (T90 0.049 h; depth-5 T90 0.65 h) | – | – |
| H20 τ_q (days → h), H54 day τ_K (h) | 2.32 d → 6.9 h (detected); 0.7 h | – | descriptive |

Verdict rule (replication): supported = detected, inside the T90 model's LOPO 80% interval and τ/T90 ≤ 3; mixed = inside the interval only; failed = outside; n/a = no detected settling. Figures: `../../figures/` (cross-period). Data: `data/processed/H48-settling-mixing-time/G08/`.

## Scorecard (period-specific axes)
- **C:** not scored (no detected settling).
- **D:** magnitude prediction not scored.

## Notes
- Data: `data/processed/H48-settling-mixing-time/G08/` (`coverage_curves.parquet`, `s1_series_<model>.parquet`); cross-period rows in `readout_period.parquet` and `settling_period.parquet`.
