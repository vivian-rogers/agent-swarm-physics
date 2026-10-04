# H92 × G26: Elect a village leader. They choose this week’s goal! (2026-01-07 → 2026-01-09, forecast target days)

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
| content_bge | 3 | 10 | +0.039 | +0.024 | -0.002 | +0.175 | E5_clip |
| content_gte | 3 | 10 | +0.045 | +0.026 | +0.007 | +0.088 | E5_clip |
| content_bge_style_resid_period | 3 | 10 | +0.022 | +0.012 | -0.027 | +0.151 | E5_clip |
| content_gte_style_resid_period | 3 | 10 | +0.047 | +0.031 | +0.006 | +0.083 | E5_clip |
| talk | 3 | 10 | +0.193 | +0.023 | -0.009 | +0.012 | E4_lwcc |
| act | 3 | 10 | +0.130 | +0.076 | -0.003 | +0.004 | E4_lwcc |

Data: `data/processed/H92-rmt-cleaned-forecast/periods.parquet`, `forecasts.parquet`. CIs are in the shared estimates table.

## Scorecard (period-specific axes)
- C (adequacy): the forecast comparison against the strongest rival on this period, as tabulated.
- H (comparative): E5 vs E3/E4 here.

## Notes
- Templated folder (replication layer), written by `analysis/write_period_folders.py`.
