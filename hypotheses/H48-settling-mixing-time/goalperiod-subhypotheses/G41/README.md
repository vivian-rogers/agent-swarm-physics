# H48 × G41: Perform novel research! (2026-05-11 → 2026-05-15)

**Verdict:** mixed
**Role:** replication
**Period:** regime III · 15 agents on the kickoff roster · 2 room blocks (2,3) · 5 active days (20.1 active h, 4.0 h/day). Kickoff time from H54.

## Why this period
One phase-diagram point of the replication layer: the common estimators (S1 settling, read-out coverage, bulk mixing, λ₂ rivals) on a non-holdout period of ≥ 5 active days. Nothing period-specific is tested here.

## Prediction
*Templated replication prediction (card P1, P2), written 2026-10-04 ~07:25 UTC before the settling run on this period. Read-out predictors (no content) were already computed: direct coverage T90 = 0.147 active h, depth-5 T90 = 2.35 h, bulk mixing t_mix = 0.032 h, reading rate u = 35.7 /h, λ₂^w,sym (min block) = 22.9 /h.*
- S1 settling is detected (a decaying kickoff excess with ΔBIC ≥ 2).
- τ_S1 falls inside the 80% leave-one-period-out interval of the T90 model fitted on the other periods (the card's P1 rule applied to this point).
- Magnitude (card P2, expected to fail): τ_S1 / T90 ≤ 3.

## Result
| Prediction | Observed | Null | Verdict |
| --- | --- | --- | --- |
| S1 settling detected (bge; gte) | yes (ΔBIC 14.8); gte yes (ΔBIC 29.3) | constant excess | met |
| τ_S1 (active h), bge / gte | 6.98 / 11.58; excess 0.199 → -0.005 | – | – |
| inside the T90 model's 80% LOPO interval | yes (pred 1.53 h) | constant model | met |
| magnitude τ_S1 / T90 ≤ 3 | 47.5 (T90 0.147 h; depth-5 T90 2.35 h) | – | not met |
| H20 τ_q (days → h), H54 day τ_K (h) | – d → – h (not detected); 6.8 h | – | descriptive |

Verdict rule (replication): supported = detected, inside the T90 model's LOPO 80% interval and τ/T90 ≤ 3; mixed = inside the interval only; failed = outside; n/a = no detected settling. Figures: `../../figures/` (cross-period). Data: `data/processed/H48-settling-mixing-time/G41/`.

## Scorecard (period-specific axes)
- **C:** the T90 model's out-of-sample error for this point is 1.52 in log τ.
- **D:** magnitude prediction not met.

## Notes
- Data: `data/processed/H48-settling-mixing-time/G41/` (`coverage_curves.parquet`, `s1_series_<model>.parquet`); cross-period rows in `readout_period.parquet` and `settling_period.parquet`.
