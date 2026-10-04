# H92 × G39: Build your own interactive world! (2026-04-28 → 2026-05-01, forecast target days)

**Verdict:** mixed
**Role:** replication (exploratory)
**Period:** regime III · forecasts within `period_units` units only (no forecast crosses a step change).

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
| content_bge | 4 | 15 | +0.262 | -0.057 | -0.068 | -0.146 | E1_mean |
| content_gte | 4 | 15 | +0.229 | -0.071 | -0.038 | -0.115 | E1_mean |
| content_bge_style_resid_period | 4 | 15 | +0.302 | -0.006 | +0.019 | -0.042 | E1_mean |
| content_gte_style_resid_period | 4 | 15 | +0.319 | +0.018 | +0.058 | -0.020 | E1_mean |
| talk | 4 | 6 | +0.180 | -3.641 | -0.416 | -0.950 | E3_lwi |
| act | 4 | 15 | +0.413 | +0.011 | +0.023 | -0.003 | E1_mean |

Data: `data/processed/H92-rmt-cleaned-forecast/periods.parquet`, `forecasts.parquet`. CIs are in the shared estimates table.

## Scorecard (period-specific axes)
- C (adequacy): the forecast comparison against the strongest rival on this period, as tabulated.
- H (comparative): E5 vs E3/E4 here.

## Notes
- Templated folder (replication layer), written by `analysis/write_period_folders.py`.
