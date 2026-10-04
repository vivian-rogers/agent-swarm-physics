# H48 × G42: Run your own Youtube channel! (2026-05-18 → 2026-05-22)

**Verdict:** n/a
**Role:** replication
**Period:** regime III · 15 agents on the kickoff roster · 2 room blocks (2,3) · 5 active days (20.1 active h, 4.0 h/day). Kickoff time from H54.

## Why this period
One phase-diagram point of the replication layer: the common estimators (S1 settling, read-out coverage, bulk mixing, λ₂ rivals) on a non-holdout period of ≥ 5 active days. Nothing period-specific is tested here.

## Prediction
*Templated replication prediction (card P1, P2), written 2026-10-04 ~07:25 UTC before the settling run on this period. Read-out predictors (no content) were already computed: direct coverage T90 = 5.647 active h, depth-5 T90 = 17.26 h, bulk mixing t_mix = 0.048 h, reading rate u = 25.1 /h, λ₂^w,sym (min block) = 9.4 /h.*
- S1 settling is detected (a decaying kickoff excess with ΔBIC ≥ 2).
- τ_S1 falls inside the 80% leave-one-period-out interval of the T90 model fitted on the other periods (the card's P1 rule applied to this point).
- Magnitude (card P2, expected to fail): τ_S1 / T90 ≤ 3.

## Result
| Prediction | Observed | Null | Verdict |
| --- | --- | --- | --- |
| S1 settling detected (bge; gte) | no (ΔBIC -1.4); gte yes (ΔBIC 9.1) | constant excess | not met |
| τ_S1 (active h), bge / gte | 4.99 / 2.78; excess 0.369 → 0.317 | – | – |
| inside the T90 model's 80% LOPO interval | – | constant model | – |
| magnitude τ_S1 / T90 ≤ 3 | – (T90 5.647 h; depth-5 T90 17.26 h) | – | – |
| H20 τ_q (days → h), H54 day τ_K (h) | – d → – h (not detected); 1.0 h | – | descriptive |

Verdict rule (replication): supported = detected, inside the T90 model's LOPO 80% interval and τ/T90 ≤ 3; mixed = inside the interval only; failed = outside; n/a = no detected settling. Figures: `../../figures/` (cross-period). Data: `data/processed/H48-settling-mixing-time/G42/`.

## Scorecard (period-specific axes)
- **C:** not scored (no detected settling).
- **D:** magnitude prediction not scored.

## Notes
- Data: `data/processed/H48-settling-mixing-time/G42/` (`coverage_curves.parquet`, `s1_series_<model>.parquet`); cross-period rows in `readout_period.parquet` and `settling_period.parquet`.
