# H92 × G13: Design, run and write up a human subjects experiment (2025-09-09 → 2025-09-19, forecast target days)

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
| content_bge | 9 | 6 | -0.065 | -0.104 | -0.064 | +0.217 | E3_lwi |
| content_gte | 9 | 6 | -0.032 | -0.087 | -0.046 | +0.311 | E3_lwi |
| content_bge_style_resid_period | 9 | 6 | -0.071 | -0.107 | -0.069 | +0.261 | E3_lwi |
| content_gte_style_resid_period | 9 | 6 | -0.088 | -0.130 | -0.072 | +0.303 | E3_lwi |
| talk | 9 | 6 | +0.040 | -0.007 | -0.024 | +0.014 | E5_clip |
| act | 9 | 5 | +0.211 | -0.102 | +0.003 | -0.195 | E1_mean |

Data: `data/processed/H92-rmt-cleaned-forecast/periods.parquet`, `forecasts.parquet`. CIs are in the shared estimates table.

## Scorecard (period-specific axes)
- C (adequacy): the forecast comparison against the strongest rival on this period, as tabulated.
- H (comparative): E5 vs E3/E4 here.

## Notes
- Templated folder (replication layer), written by `analysis/write_period_folders.py`.
