# H92 × G20: Start a Substack and join the blogosphere (2025-11-18 → 2025-11-28, forecast target days)

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
| content_bge | 6 | 10 | +0.093 | +0.092 | +0.029 | +0.233 | E5_clip |
| content_gte | 6 | 10 | +0.059 | +0.057 | +0.012 | +0.223 | E4_lwcc |
| content_bge_style_resid_period | 6 | 10 | +0.091 | +0.105 | +0.026 | +0.236 | E5_clip |
| content_gte_style_resid_period | 6 | 10 | +0.061 | +0.076 | +0.019 | +0.233 | E4_lwcc |
| talk | 6 | 10 | +0.156 | -0.065 | -0.174 | -0.240 | E1_mean |
| act | 6 | 9 | +0.328 | -0.004 | +0.044 | -0.012 | E1_mean |

Data: `data/processed/H92-rmt-cleaned-forecast/periods.parquet`, `forecasts.parquet`. CIs are in the shared estimates table.

## Scorecard (period-specific axes)
- C (adequacy): the forecast comparison against the strongest rival on this period, as tabulated.
- H (comparative): E5 vs E3/E4 here.

## Notes
- Templated folder (replication layer), written by `analysis/write_period_folders.py`.
