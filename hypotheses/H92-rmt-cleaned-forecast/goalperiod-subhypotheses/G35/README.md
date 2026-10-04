# H92 × G35: Test your game to make it as fun and functional as you can! (2026-03-17 → 2026-03-20, forecast target days)

**Verdict:** mixed
**Role:** replication (exploratory)
**Period:** regime II · forecasts within `period_units` units only (no forecast crosses a step change).

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
| content_bge | 4 | 12 | -0.029 | -0.065 | -0.060 | +0.437 | E6_clip_mp |
| content_gte | 4 | 12 | -0.038 | -0.079 | -0.075 | +0.478 | E6_clip_mp |
| content_bge_style_resid_period | 4 | 12 | -0.008 | -0.038 | -0.035 | +0.413 | E6_clip_mp |
| content_gte_style_resid_period | 4 | 12 | -0.009 | -0.044 | -0.048 | +0.455 | E6_clip_mp |
| talk | 4 | 12 | +0.112 | -0.089 | -0.121 | -0.137 | E1_mean |
| act | 4 | 11 | +0.189 | -0.296 | -0.110 | -0.132 | E3_lwi |

Data: `data/processed/H92-rmt-cleaned-forecast/periods.parquet`, `forecasts.parquet`. CIs are in the shared estimates table.

## Scorecard (period-specific axes)
- C (adequacy): the forecast comparison against the strongest rival on this period, as tabulated.
- H (comparative): E5 vs E3/E4 here.

## Notes
- Templated folder (replication layer), written by `analysis/write_period_folders.py`.
