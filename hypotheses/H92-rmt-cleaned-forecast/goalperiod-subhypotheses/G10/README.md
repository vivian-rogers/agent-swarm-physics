# H92 × G10: Complete as many games as you can in a week! (2025-08-19 → 2025-08-22, forecast target days)

**Verdict:** mixed
**Role:** replication (exploratory)
**Period:** regime I · forecasts within `period_units` units only (no forecast crosses a step change).

## Why this period
A replication point for the common estimator (layer 1). Every eligible goal period gets the same forecast comparison, so periods are comparable points, not independent tests.

## Prediction
*Templated from the card's replication rule, written 2026-10-04 ~20:15 UTC before any real-data forecast.*
- RMT clipping at the calibrated edge (E5) has the lowest mean next-day MSE among raw (E2), Ledoit–Wolf identity (E3), Ledoit–Wolf constant correlation (E4) and E5, in the content channel with both embedding models.
- *Supported* if that holds in both models; *failed* if E5's mean MSE exceeds raw's in both; *mixed* otherwise; *descriptive* with < 2 target days.

## Result
Relative gain of E5 over each rival, r = 1 − MSE_E5/MSE_rival, mean over target days (positive = clipping forecasts better). Expanding training window.

| Channel | target days | median N | vs raw | vs LW identity | vs LW const. corr. | vs mean field | best estimator |
| --- | --- | --- | --- | --- | --- | --- | --- |
| content_bge | 3 | 7 | +0.313 | -0.076 | +0.037 | -0.037 | E3_lwi |
| content_gte | 3 | 7 | +0.281 | -0.052 | -0.083 | -0.097 | E3_lwi |
| content_bge_style_resid_period | 3 | 7 | +0.340 | -0.084 | +0.097 | +0.101 | E3_lwi |
| content_gte_style_resid_period | 3 | 7 | +0.290 | +0.003 | -0.014 | +0.061 | E5_clip |
| talk | 3 | 7 | +0.025 | +0.000 | -0.263 | -0.263 | E1_mean |
| act | 3 | 6 | +0.150 | +0.125 | +0.012 | +0.069 | E5_clip |

Data: `data/processed/H92-rmt-cleaned-forecast/periods.parquet`, `forecasts.parquet`. CIs are in the shared estimates table.

## Scorecard (period-specific axes)
- C (adequacy): the forecast comparison against the strongest rival on this period, as tabulated.
- H (comparative): E5 vs E3/E4 here.

## Notes
- Templated folder (replication layer), written by `analysis/write_period_folders.py`.
