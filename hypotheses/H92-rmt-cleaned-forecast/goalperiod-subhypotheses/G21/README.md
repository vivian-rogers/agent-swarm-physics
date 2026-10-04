# H92 × G21: Forecast the abilities and effects of AI (2025-12-02 → 2025-12-05, forecast target days)

**Verdict:** failed
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
| content_bge | 3 | 8 | -0.017 | -0.092 | -0.033 | +0.233 | E3_lwi |
| content_gte | 3 | 8 | +0.025 | -0.026 | -0.011 | +0.293 | E3_lwi |
| content_bge_style_resid_period | 3 | 8 | +0.097 | -0.042 | +0.018 | +0.272 | E3_lwi |
| content_gte_style_resid_period | 3 | 8 | +0.087 | +0.016 | +0.041 | +0.329 | E5_clip |
| talk | 3 | 8 | -0.021 | +0.072 | -0.194 | -0.096 | E4_lwcc |
| act | 3 | 8 | -0.034 | -0.040 | -0.187 | -0.130 | E4_lwcc |

Data: `data/processed/H92-rmt-cleaned-forecast/periods.parquet`, `forecasts.parquet`. CIs are in the shared estimates table.

## Scorecard (period-specific axes)
- C (adequacy): the forecast comparison against the strongest rival on this period, as tabulated.
- H (comparative): E5 vs E3/E4 here.

## Notes
- Templated folder (replication layer), written by `analysis/write_period_folders.py`.
