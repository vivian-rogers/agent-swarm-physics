# H92 × G16: Choose your own goal! (2025-10-07 → 2025-10-10, forecast target days)

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
| content_bge | 4 | 7 | +0.075 | -0.060 | -0.003 | -0.030 | E1_mean |
| content_gte | 4 | 7 | +0.105 | -0.015 | +0.029 | +0.009 | E5_clip |
| content_bge_style_resid_period | 4 | 7 | +0.105 | -0.084 | -0.058 | -0.138 | E1_mean |
| content_gte_style_resid_period | 4 | 7 | +0.165 | -0.021 | +0.009 | -0.011 | E1_mean |
| talk | 4 | 7 | +0.245 | +0.079 | +0.029 | -0.036 | E1_mean |
| act | 4 | 7 | +0.075 | -0.225 | +0.078 | +0.017 | E3_lwi |

Data: `data/processed/H92-rmt-cleaned-forecast/periods.parquet`, `forecasts.parquet`. CIs are in the shared estimates table.

## Scorecard (period-specific axes)
- C (adequacy): the forecast comparison against the strongest rival on this period, as tabulated.
- H (comparative): E5 vs E3/E4 here.

## Notes
- Templated folder (replication layer), written by `analysis/write_period_folders.py`.
