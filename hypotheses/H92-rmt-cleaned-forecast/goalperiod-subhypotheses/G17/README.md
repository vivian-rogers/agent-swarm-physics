# H92 × G17: Each agent: build your own personal website (2025-10-14 → 2025-10-17, forecast target days)

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
| content_bge | 4 | 7 | +0.044 | +0.022 | +0.009 | +0.358 | E5_clip |
| content_gte | 4 | 7 | +0.066 | +0.059 | +0.056 | +0.387 | E5_clip |
| content_bge_style_resid_period | 4 | 7 | -0.040 | -0.064 | -0.050 | +0.310 | E3_lwi |
| content_gte_style_resid_period | 4 | 7 | +0.010 | -0.032 | -0.001 | +0.351 | E5_clip |
| talk | 4 | 7 | -0.061 | +0.062 | -0.091 | +0.098 | E2_raw |
| act | 4 | 6 | +0.085 | +0.025 | +0.003 | +0.084 | E5_clip |

Data: `data/processed/H92-rmt-cleaned-forecast/periods.parquet`, `forecasts.parquet`. CIs are in the shared estimates table.

## Scorecard (period-specific axes)
- C (adequacy): the forecast comparison against the strongest rival on this period, as tabulated.
- H (comparative): E5 vs E3/E4 here.

## Notes
- Templated folder (replication layer), written by `analysis/write_period_folders.py`.
