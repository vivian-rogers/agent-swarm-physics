# H92 × G07: Holiday: do whatever you prefer! Next goal will begin soon (2025-07-17 → 2025-07-17, forecast target days)

**Verdict:** descriptive
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
| content_bge | 1 | 4 | +0.253 | +0.097 | +0.156 | +0.094 | E5_clip |
| content_gte | 1 | 4 | +0.190 | +0.063 | +0.116 | -0.001 | E1_mean |
| content_bge_style_resid_period | 1 | 4 | +0.152 | -0.063 | +0.003 | -1.119 | E1_mean |
| content_gte_style_resid_period | 1 | 4 | +0.431 | +0.276 | +0.301 | -0.244 | E1_mean |
| talk | 1 | 4 | -0.025 | +0.000 | -0.788 | -0.788 | E4_lwcc |

Data: `data/processed/H92-rmt-cleaned-forecast/periods.parquet`, `forecasts.parquet`. CIs are in the shared estimates table.

## Scorecard (period-specific axes)
- C (adequacy): the forecast comparison against the strongest rival on this period, as tabulated.
- H (comparative): E5 vs E3/E4 here.

## Notes
- Templated folder (replication layer), written by `analysis/write_period_folders.py`.
