# H92 × G08: Design the AI Village benchmark for open-ended goal pursuit – and test yourselves on it! (2025-07-21 → 2025-08-12, forecast target days)

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
| content_bge | 16 | 4 | -0.015 | -0.090 | -0.006 | +0.031 | E3_lwi |
| content_gte | 16 | 4 | +0.069 | +0.003 | +0.043 | +0.006 | E3_lwi |
| content_bge_style_resid_period | 16 | 4 | +0.044 | -0.055 | +0.028 | +0.035 | E5_clip |
| content_gte_style_resid_period | 16 | 4 | +0.099 | +0.027 | +0.073 | +0.020 | E3_lwi |
| talk | 15 | 4 | +0.073 | -0.038 | +0.037 | +0.013 | E3_lwi |
| act | 4 | 4 | +0.045 | -0.244 | +0.013 | -0.006 | E3_lwi |

Data: `data/processed/H92-rmt-cleaned-forecast/periods.parquet`, `forecasts.parquet`. CIs are in the shared estimates table.

## Scorecard (period-specific axes)
- C (adequacy): the forecast comparison against the strongest rival on this period, as tabulated.
- H (comparative): E5 vs E3/E4 here.

## Notes
- Templated folder (replication layer), written by `analysis/write_period_folders.py`.
