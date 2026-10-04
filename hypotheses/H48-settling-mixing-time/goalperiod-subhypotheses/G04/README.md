# H48 × G04: Write a story and celebrate it with 100 people in person (2025-05-15 → 2025-06-18)

**Verdict:** n/a
**Role:** replication
**Period:** regime I · 4 agents on the kickoff roster · one room (#general) · 25 active days (57.2 active h, 2.0 h/day). Kickoff time from H54.

## Why this period
One phase-diagram point of the replication layer: the common estimators (S1 settling, read-out coverage, bulk mixing, λ₂ rivals) on a non-holdout period of ≥ 5 active days. Nothing period-specific is tested here.

## Prediction
*Templated replication prediction (card P1, P2), written 2026-10-04 ~07:25 UTC before the settling run on this period. Read-out predictors (no content) were already computed: direct coverage T90 = 0.101 active h, depth-5 T90 = 0.24 h, bulk mixing t_mix = 0.014 h, reading rate u = 57.3 /h, λ₂^w,sym (min block) = 119 /h.*
- S1 settling is detected (a decaying kickoff excess with ΔBIC ≥ 2).
- τ_S1 falls inside the 80% leave-one-period-out interval of the T90 model fitted on the other periods (the card's P1 rule applied to this point).
- Magnitude (card P2, expected to fail): τ_S1 / T90 ≤ 3.

## Result
| Prediction | Observed | Null | Verdict |
| --- | --- | --- | --- |
| S1 settling detected (bge; gte) | no (ΔBIC 1.0); gte no (ΔBIC 0.3) | constant excess | not met |
| τ_S1 (active h), bge / gte | 1.70 / 1.58; excess 0.284 → 0.094 | – | – |
| inside the T90 model's 80% LOPO interval | – | constant model | – |
| magnitude τ_S1 / T90 ≤ 3 | – (T90 0.101 h; depth-5 T90 0.24 h) | – | – |
| H20 τ_q (days → h), H54 day τ_K (h) | 4.56 d → 9.1 h (detected); 1.5 h | – | descriptive |

Verdict rule (replication): supported = detected, inside the T90 model's LOPO 80% interval and τ/T90 ≤ 3; mixed = inside the interval only; failed = outside; n/a = no detected settling. Figures: `../../figures/` (cross-period). Data: `data/processed/H48-settling-mixing-time/G04/`.

## Scorecard (period-specific axes)
- **C:** not scored (no detected settling).
- **D:** magnitude prediction not scored.

## Notes
- Data: `data/processed/H48-settling-mixing-time/G04/` (`coverage_curves.parquet`, `s1_series_<model>.parquet`); cross-period rows in `readout_period.parquet` and `settling_period.parquet`.
