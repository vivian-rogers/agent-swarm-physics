# H48 × G35: Test your game to make it as fun and functional as you can! (2026-03-16 → 2026-03-20)

**Verdict:** supported
**Role:** replication
**Period:** regime II · 12 agents on the kickoff roster · 2 room blocks (2,3) · 5 active days (19.9 active h, 4.0 h/day). Kickoff time from H54.

## Why this period
One phase-diagram point of the replication layer: the common estimators (S1 settling, read-out coverage, bulk mixing, λ₂ rivals) on a non-holdout period of ≥ 5 active days. Nothing period-specific is tested here.

## Prediction
*Templated replication prediction (card P1, P2), written 2026-10-04 ~07:25 UTC before the settling run on this period. Read-out predictors (no content) were already computed: direct coverage T90 = 0.619 active h, depth-5 T90 = 2.61 h, bulk mixing t_mix = 0.025 h, reading rate u = 43.0 /h, λ₂^w,sym (min block) = 24.2 /h.*
- S1 settling is detected (a decaying kickoff excess with ΔBIC ≥ 2).
- τ_S1 falls inside the 80% leave-one-period-out interval of the T90 model fitted on the other periods (the card's P1 rule applied to this point).
- Magnitude (card P2, expected to fail): τ_S1 / T90 ≤ 3.

## Result
| Prediction | Observed | Null | Verdict |
| --- | --- | --- | --- |
| S1 settling detected (bge; gte) | yes (ΔBIC 2.1); gte yes (ΔBIC 4.2) | constant excess | met |
| τ_S1 (active h), bge / gte | 0.64 / 0.99; excess 0.289 → 0.079 | – | – |
| inside the T90 model's 80% LOPO interval | yes (pred 3.89 h) | constant model | met |
| magnitude τ_S1 / T90 ≤ 3 | 1.0 (T90 0.619 h; depth-5 T90 2.61 h) | – | met |
| H20 τ_q (days → h), H54 day τ_K (h) | – d → – h (not detected); 1.0 h | – | descriptive |

Verdict rule (replication): supported = detected, inside the T90 model's LOPO 80% interval and τ/T90 ≤ 3; mixed = inside the interval only; failed = outside; n/a = no detected settling. Figures: `../../figures/` (cross-period). Data: `data/processed/H48-settling-mixing-time/G35/`.

## Scorecard (period-specific axes)
- **C:** the T90 model's out-of-sample error for this point is 1.80 in log τ.
- **D:** magnitude prediction met.

## Notes
- Data: `data/processed/H48-settling-mixing-time/G35/` (`coverage_curves.parquet`, `s1_series_<model>.parquet`); cross-period rows in `readout_period.parquet` and `settling_period.parquet`.
