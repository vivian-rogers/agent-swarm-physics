# H92 × G42: Run your own Youtube channel! (2026-05-19 → 2026-05-22, forecast target days)

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
| content_bge | 3 | 16 | +0.307 | -0.076 | -0.065 | -0.209 | E1_mean |
| content_gte | 3 | 16 | +0.231 | -0.074 | -0.098 | -0.129 | E1_mean |
| content_bge_style_resid_period | 3 | 16 | +0.283 | -0.141 | -0.123 | -0.228 | E1_mean |
| content_gte_style_resid_period | 3 | 16 | +0.277 | -0.039 | -0.070 | -0.103 | E1_mean |
| talk | 3 | 9 | +0.340 | +0.051 | -0.100 | -0.105 | E1_mean |
| act | 3 | 16 | +0.348 | -0.117 | -0.043 | -0.164 | E1_mean |

Data: `data/processed/H92-rmt-cleaned-forecast/periods.parquet`, `forecasts.parquet`. CIs are in the shared estimates table.

## Scorecard (period-specific axes)
- C (adequacy): the forecast comparison against the strongest rival on this period, as tabulated.
- H (comparative): E5 vs E3/E4 here.

## Notes
- Templated folder (replication layer), written by `analysis/write_period_folders.py`.
