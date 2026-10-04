# H48 × G40: Connect your worlds into a 3D universe! (2026-05-04 → 2026-05-08)

**Verdict:** failed
**Role:** replication
**Period:** regime III · 15 agents on the kickoff roster · 1 room blocks (4) · 5 active days (20.3 active h, 4.1 h/day). Kickoff time from H54.

## Why this period
One phase-diagram point of the replication layer: the common estimators (S1 settling, read-out coverage, bulk mixing, λ₂ rivals) on a non-holdout period of ≥ 5 active days. Nothing period-specific is tested here.

## Prediction
*Templated replication prediction (card P1, P2), written 2026-10-04 ~07:25 UTC before the settling run on this period. Read-out predictors (no content) were already computed: direct coverage T90 = 0.569 active h, depth-5 T90 = 8.16 h, bulk mixing t_mix = 0.026 h, reading rate u = 41.8 /h, λ₂^w,sym (min block) = 47.0 /h.*
- S1 settling is detected (a decaying kickoff excess with ΔBIC ≥ 2).
- τ_S1 falls inside the 80% leave-one-period-out interval of the T90 model fitted on the other periods (the card's P1 rule applied to this point).
- Magnitude (card P2, expected to fail): τ_S1 / T90 ≤ 3.

## Result
| Prediction | Observed | Null | Verdict |
| --- | --- | --- | --- |
| S1 settling detected (bge; gte) | yes (ΔBIC 25.4); gte yes (ΔBIC 28.4) | constant excess | met |
| τ_S1 (active h), bge / gte | 17.26 / 17.26; excess 0.529 → 0.267 | – | – |
| inside the T90 model's 80% LOPO interval | no (pred 2.22 h) | constant model | not met |
| magnitude τ_S1 / T90 ≤ 3 | 30.3 (T90 0.569 h; depth-5 T90 8.16 h) | – | not met |
| H20 τ_q (days → h), H54 day τ_K (h) | – d → – h (not detected); 8.4 h | – | descriptive |

Verdict rule (replication): supported = detected, inside the T90 model's LOPO 80% interval and τ/T90 ≤ 3; mixed = inside the interval only; failed = outside; n/a = no detected settling. Figures: `../../figures/` (cross-period). Data: `data/processed/H48-settling-mixing-time/G40/`.

## Scorecard (period-specific axes)
- **C:** the T90 model's out-of-sample error for this point is 2.05 in log τ.
- **D:** magnitude prediction not met.

## Notes
- Data: `data/processed/H48-settling-mixing-time/G40/` (`coverage_curves.parquet`, `s1_series_<model>.parquet`); cross-period rows in `readout_period.parquet` and `settling_period.parquet`.
