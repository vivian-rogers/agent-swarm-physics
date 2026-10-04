# H92 × G04: Write a story and celebrate it with 100 people in person (2025-05-16 → 2025-06-17, forecast target days)

**Verdict:** supported
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
| content_bge | 19 | 4 | +0.089 | +0.115 | +0.047 | +0.061 | E1_mean |
| content_gte | 19 | 4 | +0.122 | +0.136 | +0.050 | -0.025 | E1_mean |
| content_bge_style_resid_period | 19 | 4 | +0.086 | +0.096 | +0.030 | -0.008 | E1_mean |
| content_gte_style_resid_period | 19 | 4 | +0.108 | +0.140 | +0.050 | -0.070 | E1_mean |
| talk | 18 | 4 | +0.005 | +0.049 | +0.018 | +0.000 | E1_mean |
| act | 7 | 4 | +0.040 | -0.173 | +0.023 | -0.041 | E3_lwi |

Data: `data/processed/H92-rmt-cleaned-forecast/periods.parquet`, `forecasts.parquet`. CIs are in the shared estimates table.

## Scorecard (period-specific axes)
- C (adequacy): the forecast comparison against the strongest rival on this period, as tabulated.
- H (comparative): E5 vs E3/E4 here.

## Notes
- Templated folder (replication layer), written by `analysis/write_period_folders.py`.
